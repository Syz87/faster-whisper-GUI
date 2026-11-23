# coding:utf-8
"""把 SRT 字幕封装进视频（软字幕，不重编码）

优先用 ffmpeg（快、稳）；没有 ffmpeg 时退回 PyAV 直接 remux。

用法：
    python merge_subtitle.py 视频.mp4 字幕.srt [输出.mkv]

不重编码，只换容器，几分钟出结果，画质无损。
输出 MKV 是因为 MP4 对字幕轨支持差（只能 mov_text，样式丢失）。
"""
import os
import re
import shutil
import subprocess
import sys


def find_ffmpeg():
    """在常见位置找 ffmpeg。"""
    cands = []
    # imageio-ffmpeg 自带一份二进制，pip 装上就有，不用单独下载
    try:
        import imageio_ffmpeg
        cands.append(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        pass
    cands += [
        shutil.which("ffmpeg"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "ffmpeg", "bin", "ffmpeg.exe"),
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def parse_srt(path):
    """返回 [(start_sec, end_sec, text)]"""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        raw = f.read()

    def to_sec(x):
        x = x.strip().replace(",", ".")
        h, m, s = x.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    out = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) >= 2 and "-->" in lines[1]:
            a, b = lines[1].split("-->")
            txt = "\n".join(lines[2:]) if len(lines) > 2 else ""
            out.append((to_sec(a), to_sec(b), txt))
    return out


def merge_with_ffmpeg(ffmpeg, video, sub, out_path):
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "warning",
        "-i", video, "-i", sub,
        "-map", "0:v:0", "-map", "0:a?", "-map", "1:0",
        "-c", "copy",
        "-c:s", "srt",
        "-metadata:s:s:0", "language=chi",
        "-metadata:s:s:0", "title=简体中文",
        out_path,
    ]
    print("  调用 ffmpeg ...")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("  ffmpeg 输出：", (r.stderr or "")[-800:])
        return False
    return True


def merge_with_pyav(video, sub, out_path):
    """没有 ffmpeg 时的退路：PyAV 直接 remux。"""
    import av

    segs = parse_srt(sub)
    inp = av.open(video)
    out = av.open(out_path, "w", format="matroska")

    v_in = inp.streams.video[0]
    a_in = next((s for s in inp.streams if s.type == "audio"), None)

    v_out = out.add_stream_from_template(v_in)
    a_out = out.add_stream_from_template(a_in) if a_in else None

    from fractions import Fraction
    s_out = out.add_stream("srt", rate=1)
    s_out.time_base = Fraction(1, 1000)

    seg_iter = iter(segs)
    next_seg = next(seg_iter, None)

    # 视频/音频原样复制
    for packet in inp.demux(v_in, a_in) if a_in else inp.demux(v_in):
        if packet.dts is None:
            continue
        packet.stream = v_out if packet.stream.index == v_in.index else a_out
        out.mux(packet)

    # 字幕单独写
    for start, end, text in segs:
        pkt = av.Packet(text.encode("utf-8"))
        pkt.stream = s_out
        pkt.pts = int(start * 1000)
        pkt.dts = pkt.pts
        pkt.duration = max(1, int((end - start) * 1000))
        out.mux(pkt)

    out.close()
    inp.close()
    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    video, sub = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(video)[0] + ".chs.mkv"

    if not os.path.exists(video) or not os.path.exists(sub):
        print("文件不存在")
        return 1

    segs = parse_srt(sub)
    print(f"视频 {os.path.basename(video)}  {os.path.getsize(video)/1073741824:.2f} GB")
    print(f"字幕 {os.path.basename(sub)}  {len(segs)} 条")
    print(f"输出 {os.path.basename(out_path)}")

    ffmpeg = find_ffmpeg()
    if ffmpeg:
        print(f"  找到 ffmpeg: {ffmpeg}")
        ok = merge_with_ffmpeg(ffmpeg, video, sub, out_path)
    else:
        print("  没找到 ffmpeg，改用 PyAV remux")
        ok = merge_with_pyav(video, sub, out_path)

    if ok and os.path.exists(out_path):
        print(f"[完成] {out_path}  {os.path.getsize(out_path)/1073741824:.2f} GB")
        return 0
    print("[失败]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
