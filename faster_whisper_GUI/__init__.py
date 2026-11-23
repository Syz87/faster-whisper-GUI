# coding:utf-8
# whisperX 是可选依赖（词级对齐 / 说话人分离用）。
#
# 注意：torch + whisperx 的导入要 30 秒以上（要加载 torch、pyannote、
# transformers、lightning 等一大堆东西）。如果在包的 __init__ 里导入，
# 整个软件启动都会被拖慢半分钟。
#
# 所以这里不做任何导入，改由实际用到的地方按需加载：
#   from .whisper_x import ensure_whisperx
#   if ensure_whisperx():
#       ...
