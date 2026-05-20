"""解析 Claude Code hook stdin JSON，输出 shell 可 eval 的变量赋值。"""
import json
import sys
import base64

try:
    data = json.load(sys.stdin)
    ti = data.get("tool_input", {})
    fp = ti.get("file_path", "") or ti.get("command", "")
    ct = ti.get("content", "")
    print(f"FILE_PATH={fp}")
    # 用 base64 编码避免 bash 转义地狱
    print(f"CONTENT_B64={base64.b64encode(ct.encode()).decode()}")
except Exception:
    print("FILE_PATH=")
    print("CONTENT_B64=")
