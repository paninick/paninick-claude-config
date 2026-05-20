#!/bin/bash
# ============================================================
# PostToolUse hook: 每次 Write/Edit 后立即检查
# 作用层面: Claude Code 工具调用层（平台级）
# 检查内容: 密钥硬编码 / TODO 标记 / 注释代码 / SQL注入
#
# Exit  0 = 通过（stdout 警告显示给 AI，不阻断）
# Exit  2 = 阻断（stderr 消息强制 AI 修复）
# ============================================================

INPUT=$(cat)

# 用独立 Python 解析器提取变量（base64 避免 bash 转义）
eval "$(echo "$INPUT" | python .claude/hooks/scripts/parse_hook_input.py)"

[ -z "$FILE_PATH" ] && exit 0
[ -z "$CONTENT_B64" ] && exit 0
CONTENT=$(echo "$CONTENT_B64" | base64 -d 2>/dev/null)
[ -z "$CONTENT" ] && exit 0

# 只检查源代码文件
if ! echo "$FILE_PATH" | grep -qE '\.(java|py|go|rs|ts|js|vue|xml|yml|yaml|sql|sh|tf|toml)$'; then
    exit 0
fi

HAS_BLOCKER=0

# ── [M-GA06] 密钥/密码/Token 硬编码 ──────────────
SECRETS=$(echo "$CONTENT" | grep -nE '(SECRET|PASSWORD|TOKEN|API_KEY|apiKey|password|token)\s*[:=]\s*"[^"]{8,}"' || true)
if [ -n "$SECRETS" ]; then
    echo "⛔ [M-GA06] 发现疑似硬编码密钥/密码/Token:" >&2
    echo "$SECRETS" | head -5 >&2
    HAS_BLOCKER=1
fi

# ── [M-SE01] SQL 注入: 字符串拼接构造查询 ────────
SQL_CONCAT=$(echo "$CONTENT" | grep -nE '(execute|executemany|raw)\s*\(.*(%|\.format|\+)' | grep -vE '(#|//|import|test_)' || true)
if [ -n "$SQL_CONCAT" ]; then
    echo "⛔ [M-SE01] 疑似 SQL 字符串拼接（应使用参数化查询）:" >&2
    echo "$SQL_CONCAT" | head -5 >&2
    HAS_BLOCKER=1
fi

# ── [M-SE01-J] MyBatis ${} 用户输入拼接 ──────────
if echo "$FILE_PATH" | grep -qi 'mapper' && echo "$FILE_PATH" | grep -q '\.xml$'; then
    DANGEROUS_SQL=$(echo "$CONTENT" | grep -nE '\$\{[^}]*\}' | grep -vE '\$\{(params\.(dataScope|factoryDataScope)|orderByColumn|orderByType)\}' || true)
    if [ -n "$DANGEROUS_SQL" ]; then
        echo "⛔ [M-SE01] Mapper XML 发现 \${} 用户输入拼接（SQL注入风险）:" >&2
        echo "$DANGEROUS_SQL" | head -5 >&2
        HAS_BLOCKER=1
    fi
fi

# ── 警告级（不阻断，但通知 AI）────────────────────

# [M-GA04] TODO/不完整实现
TODOS=$(echo "$CONTENT" | grep -nE '//.*(TODO|FIXME|XXX|HACK|待完成|待实现)' || true)
if [ -n "$TODOS" ]; then
    echo "💡 [M-GA04] 发现不完整实现标记，完成后请移除:" >&2
    echo "$TODOS" | head -3 >&2
fi

# [M-GA05] 注释掉的代码
COMMENTED=$(echo "$CONTENT" | grep -nE '^\s*//\s*(if\s*\(|for\s*\(|while\s*\(|public\s+|private\s+|SELECT\s+|INSERT\s+|UPDATE\s+)' || true)
if [ -n "$COMMENTED" ]; then
    echo "💡 [M-GA05] 发现注释掉的代码，应删除后用 git 追溯" >&2
fi

# ── 结果 ──────────────────────────────────────────

if [ "$HAS_BLOCKER" -eq 1 ]; then
    echo "" >&2
    echo "⛔ PostToolUse hook 阻断: $FILE_PATH 存在 [M] 级安全违规，请立即修复再继续。" >&2
    exit 2
fi

exit 0
