# coding:utf-8
"""修正 SRT 的超长时间戳

faster-whisper 在 VAD 过滤后，容易把大段静音并进一个 segment，
出现一条字幕挂两三分钟的情况。这里按字数比例把长条拆开。

规则：
  单条最长 6 秒（超过就拆）
  拆开时按字符数比例分配时间
  拆完每块至少 1.2 秒，太短就并回前一块
  切分点优先落在标点或日语助词后面

用法：
    python fix_srt_timing.py 字幕.srt            # 覆盖原文件（备份 .bak）
    python fix_srt_timing.py 字幕.srt 输出.srt
"""
import re
import shutil
import sys

MAX_DUR = 6.0      # 单条上限
MIN_DUR = 1.2      # 单条下限
GAP = 0.02         # 相邻条之间的空隙
SEC_PER_CHAR = 0.25   # 日语大致 0.25 秒读一个字
READ_SLACK = 1.0      # 额外留白

# 优先在这些字符之后断开
BREAK_AFTER = "。！？!?、，,.…‥」』）)"
PARTICLES = "はがをにでとへもやねよかなわの"

_TS = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")


def to_sec(x):
    h, m, s, ms = _TS.match(x.strip()).groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")[:3]) / 1000


def to_ts(v):
    v = max(0.0, v)
    h = int(v // 3600)
    m = int((v % 3600) // 60)
    s = v % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def parse(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        raw = f.read()
    out = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) >= 2 and "-->" in lines[1]:
            a, b = lines[1].split("-->")
            txt = " ".join(lines[2:]) if len(lines) > 2 else ""
            out.append([to_sec(a), to_sec(b), txt])
    return out


def split_text(text, parts):
    """把文本切成 parts 段，尽量在标点或助词后断。"""
    text = text.strip()
    if parts <= 1 or not text:
        return [text]

    target = len(text) / parts
    chunks, cur = [], ""
    for ch in text:
        cur += ch
        if len(cur) >= target and ch in BREAK_AFTER + PARTICLES:
            chunks.append(cur)
            cur = ""
    if cur:
        if chunks:
            chunks[-1] += cur
        else:
            chunks.append(cur)

    # 段数不够就硬切
    while len(chunks) < parts:
        longest = max(range(len(chunks)), key=lambda i: len(chunks[i]))
        s = chunks[longest]
        if len(s) < 2:
            break
        mid = len(s) // 2
        chunks[longest:longest + 1] = [s[:mid], s[mid:]]
    return chunks


def fix(segments):
    result = []
    for start, end, text in segments:
        dur = end - start
        if dur <= MAX_DUR or not text.strip():
            result.append([start, end, text])
            continue

        # 时长远超文本量（一句话配了几分钟静音）—— 直接缩短，不要硬拆。
        # 硬拆会把几个字摊到几分钟里，看着还是一直挂着。
        need = len(text.strip()) * SEC_PER_CHAR + READ_SLACK
        if dur > need * 1.5:
            result.append([start, min(end, start + max(MIN_DUR, need)), text])
            continue

        n = max(2, int(dur / MAX_DUR) + (1 if dur % MAX_DUR else 0))
        chunks = split_text(text, n)
        n = len(chunks)

        total_chars = sum(len(c) for c in chunks) or 1
        t = start
        for i, chunk in enumerate(chunks):
            share = len(chunk) / total_chars
            piece = dur * share
            e = min(end, t + piece)
            if e - t < MIN_DUR:
                # 太短，并进上一块
                if result and result[-1][1] >= t - 0.05:
                    result[-1][1] = e
                    result[-1][2] = (result[-1][2] + " " + chunk).strip()
                else:
                    result.append([t, min(end, t + MIN_DUR), chunk])
                    t = min(end, t + MIN_DUR)
                    continue
            else:
                result.append([t, e, chunk])
            t = e

        if t < end - 0.01 and result:
            result[-1][1] = end

    # 去掉重叠、补最小间隔
    for i in range(1, len(result)):
        if result[i][0] < result[i - 1][1] + GAP:
            result[i][0] = min(result[i - 1][1] + GAP, result[i][1] - 0.1)
    return result


def write(path, segments):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for i, (a, b, txt) in enumerate(segments, 1):
            f.write(f"{i}\n{to_ts(a)} --> {to_ts(b)}\n{txt}\n\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src

    segs = parse(src)
    before = [b - a for a, b, _ in segs]
    fixed = fix(segs)
    after = [b - a for a, b, _ in fixed]

    if dst == src:
        shutil.copy2(src, src + ".bak")

    write(dst, fixed)
    print(f"{src}: {len(segs)} 条 -> {len(fixed)} 条")
    print(f"  最长 {max(before):.1f}s -> {max(after):.1f}s")
    print(f"  超过 6s: {sum(1 for d in before if d > 6)} -> {sum(1 for d in after if d > 6)}")
    print(f"  平均时长 {sum(before)/len(before):.2f}s -> {sum(after)/len(after):.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
