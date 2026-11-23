# coding:utf-8
"""
日语字幕 -> 中文翻译工具
读取 faster-whisper-GUI 导出的日语 SRT，调用本地 Sakura-7B 模型翻译成简体中文。

用法:
    python translate_srt.py 日语字幕.srt            # 输出 日语字幕.zh.srt
    python translate_srt.py 日语字幕.srt 自定义名.srt
    python translate_srt.py 目录                    # 批量处理目录下所有 .srt

前提:
    先运行 启动翻译服务.bat，等窗口显示 "listening on http://127.0.0.1:18080"
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "http://127.0.0.1:18080/completion"

SYSTEM_PROMPT = (
    "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，"
    "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
)

# 一次送多少条字幕给模型（太少慢，太多容易串味）
BATCH_SIZE = 8
MAX_RETRY = 3


def parse_srt(path):
    """解析 SRT，返回 [(序号, 时间轴, 原文)]"""
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    blocks = re.split(r"\n\s*\n", raw.strip())
    items = []
    for b in blocks:
        lines = [x for x in b.split("\n") if x.strip() != ""]
        if len(lines) < 2:
            continue
        idx = lines[0].strip()
        timeline = lines[1].strip() if "-->" in lines[1] else None
        text_start = 2 if timeline else 1
        text = "\n".join(lines[text_start:]).strip()
        if not timeline or not text:
            continue
        items.append((idx, timeline, text))
    return items


def write_srt(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for i, (idx, timeline, text) in enumerate(items, 1):
            f.write(f"{i}\n{timeline}\n{text}\n\n")


def call_model(text):
    """把一条字幕交给模型翻译"""
    prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n将下面的日文文本翻译成中文：{text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    body = json.dumps(
        {
            "prompt": prompt,
            "n_predict": 400,
            "temperature": 0.3,
            "top_p": 0.8,
            "repeat_penalty": 1.05,
            "stop": ["<|im_end|>", "\n<|im_start|>"],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        API, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = data.get("content", "").strip()
    # 清理模型偶尔带出来的标记
    out = out.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()
    return out


def translate_text(text, retry=MAX_RETRY):
    """带重试的单条翻译"""
    for attempt in range(1, retry + 1):
        try:
            result = call_model(text)
            if result:
                return result
        except urllib.error.URLError as e:
            if attempt == retry:
                raise RuntimeError(
                    f"无法连接翻译服务（{API}）。请先运行 启动翻译服务.bat。原始错误: {e}"
                )
            time.sleep(2)
        except Exception:
            if attempt == retry:
                raise
            time.sleep(1)
    return text  # 全部失败时保留原文，避免丢行


def translate_file(src, dst=None):
    if dst is None:
        base, ext = os.path.splitext(src)
        dst = f"{base}.zh{ext}"

    items = parse_srt(src)
    if not items:
        print(f"[跳过] {src} 没解析出字幕")
        return None

    print(f"\n=== {os.path.basename(src)} ===")
    print(f"共 {len(items)} 条字幕，开始翻译 -> {os.path.basename(dst)}")

    out_items = []
    t0 = time.time()
    for i, (idx, timeline, text) in enumerate(items):
        zh = translate_text(text)
        out_items.append((idx, timeline, zh))
        elapsed = time.time() - t0
        done = i + 1
        eta = elapsed / done * (len(items) - done)
        print(
            f"  [{done}/{len(items)}] {text[:24]}... -> {zh[:24]}..."
            f"  (已用 {elapsed:.0f}s, 预计剩余 {eta:.0f}s)",
            flush=True,
        )
        # 每 20 条落盘一次，防止中断全丢
        if done % 20 == 0:
            write_srt(dst, out_items)

    write_srt(dst, out_items)
    print(f"[完成] {dst}  (总耗时 {time.time() - t0:.0f}s)")
    return dst


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n缺少输入路径。把 .srt 文件拖到本脚本上，或在命令行里传路径。")
        input("按回车退出...")
        return

    target = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None

    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in sorted(os.listdir(target))
                 if f.lower().endswith(".srt") and not f.lower().endswith(".zh.srt")]
        if not files:
            print("目录里没有 .srt 文件")
            return
        print(f"批量处理 {len(files)} 个文件")
        for f in files:
            translate_file(f)
    else:
        translate_file(target, dst)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[出错] {e}")
        input("按回车退出...")
