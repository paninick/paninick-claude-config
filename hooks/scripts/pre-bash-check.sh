#!/bin/bash
# ============================================================
# PreToolUse hook: Bash 命令执行前检查
# 作用: 拦截高风险命令（rm -rf / git push --force / curl 未知外网）
#
# Exit  0 = 放行
# Exit  2 = 阻断（要求用户审批）
# ============================================================

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python -c "
import json,sys
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    print(ti.get('command', ''))
except: pass
" 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# ── 阻断级：绝对危险命令 ──────────────────────────

# git push --force / --force-with-lease 需要审批
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force)'; then
    echo "⛔ [M-SE03] git push --force 需要明确审批。" >&2
    echo "   如果确需强制推送，请用户手动执行。" >&2
    exit 2
fi

# git reset --hard 需要审批
if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
    echo "⛔ [M-SE03] git reset --hard 会丢弃工作区变更，需要明确审批。" >&2
    exit 2
fi

# rm -rf 作用于非临时目录
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+/(?!tmp|var/tmp|dev/null)'; then
    echo "⛔ [M-SE03] rm -rf 作用于非临时目录，已阻断。" >&2
    exit 2
fi

# chmod 777
if echo "$COMMAND" | grep -qE 'chmod\s+777'; then
    echo "⛔ [M-SE03] chmod 777 过于宽松，已阻断。" >&2
    exit 2
fi

# curl/wget 到内网地址（潜在 SSRF）
if echo "$COMMAND" | grep -qE '(curl|wget)\s+.*(10\.|172\.1[6-9]|172\.2[0-9]|172\.3[0-1]|192\.168\.|127\.0\.0\.1|0\.0\.0\.0)'; then
    echo "⚠️  [M-SE03] 检测到对内网地址的请求，请确认。" >&2
    # 警告但不阻断（可能是合法的内部 API 调用）
fi

# ── 警告级：需注意的命令 ──────────────────────────

# git commit --no-verify
if echo "$COMMAND" | grep -qE 'git\s+commit\s+.*--no-verify'; then
    echo "⚠️  检测到 git commit --no-verify，跳过了 pre-commit 门禁。" >&2
    echo "   请确保在 commit body 中说明绕过理由。" >&2
fi

exit 0
