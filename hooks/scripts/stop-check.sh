#!/bin/bash
# ============================================================
# Stop hook: 会话结束前检查
# 作用:
#   1. 本次会话有 Java/SQL/TSX 变更 → 强制跑回归，失败则阻断
#   2. session-handoff.md 超 2 小时未更新 → 警告
#   3. P0 OPEN 审计问题 → 警告
#
# Exit  0 = 允许停止
# Exit  2 = 阻止停止（强制 AI 继续修复）
# ============================================================

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
REGRESSION_V1="$REPO_ROOT/.agents/skills/erp-verify/scripts/v1_regression.py"
REGRESSION_V2="$REPO_ROOT/.agents/skills/erp-verify/scripts/v2_material_batch_regression.py"
BACKEND_UP=false

# ── 1. 检测本次会话是否有后端/SQL/前端变更 ──────────────────
CHANGED=$(git -C "$REPO_ROOT" diff --name-only HEAD 2>/dev/null)
CHANGED_STAGED=$(git -C "$REPO_ROOT" diff --name-only --cached 2>/dev/null)
ALL_CHANGED="$CHANGED $CHANGED_STAGED"

HAS_BACKEND=$(echo "$ALL_CHANGED" | grep -E '\.(java|xml|sql)$' | head -1)
HAS_FRONTEND=$(echo "$ALL_CHANGED" | grep -E '\.(tsx|ts|vue)$' | head -1)

# ── 2. 如果有变更，检测后端是否在线 ────────────────────────
if [ -n "$HAS_BACKEND" ] || [ -n "$HAS_FRONTEND" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:8080/captchaImage 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        BACKEND_UP=true
    fi
fi

# ── 3. 后端在线 + 有后端变更 → 跑 V1 回归 ──────────────────
if [ "$BACKEND_UP" = "true" ] && [ -n "$HAS_BACKEND" ]; then
    echo "🔄 检测到后端变更，运行 V1 回归..." >&2
    if command -v python3 &>/dev/null; then
        PY=python3
    else
        PY=python
    fi

    RESULT=$(PYTHONIOENCODING=utf-8 "$PY" "$REGRESSION_V1" 2>&1)
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ] || echo "$RESULT" | grep -qE 'FAIL|ERROR|Exception'; then
        echo "❌ V1 回归失败 — 禁止停止，请先修复：" >&2
        echo "$RESULT" | tail -20 >&2
        echo "" >&2
        echo "   修复后重新运行：PYTHONIOENCODING=utf-8 python $REGRESSION_V1" >&2
        exit 2
    else
        PASS_LINE=$(echo "$RESULT" | grep -E '[0-9]+/[0-9]+ PASS' | tail -1)
        echo "✅ V1 回归通过 $PASS_LINE" >&2
    fi

    # V2 回归（仅当涉及 materialBatch / stockOut / consume 相关文件时）
    V2_RELEVANT=$(echo "$ALL_CHANGED" | grep -iE 'materialBatch|StockOut|MaterialConsume|batch' | head -1)
    if [ -n "$V2_RELEVANT" ]; then
        echo "🔄 检测到 V2 相关变更，运行 V2 回归..." >&2
        RESULT2=$(PYTHONIOENCODING=utf-8 "$PY" "$REGRESSION_V2" 2>&1)
        EXIT_CODE2=$?

        if [ $EXIT_CODE2 -ne 0 ] || echo "$RESULT2" | grep -qE 'FAIL|ERROR|Exception'; then
            echo "❌ V2 回归失败 — 禁止停止，请先修复：" >&2
            echo "$RESULT2" | tail -20 >&2
            exit 2
        else
            PASS_LINE2=$(echo "$RESULT2" | grep -E '[0-9]+/[0-9]+ PASS' | tail -1)
            echo "✅ V2 回归通过 $PASS_LINE2" >&2
        fi
    fi
fi

# ── 4. session-handoff.md 更新检查 ──────────────────────────
HANDOFF="$REPO_ROOT/docs/session-handoff.md"
if [ -f "$HANDOFF" ]; then
    LAST_MOD=$(stat -c %Y "$HANDOFF" 2>/dev/null || stat -f %m "$HANDOFF" 2>/dev/null)
    NOW=$(date +%s)
    AGE=$((NOW - LAST_MOD))
    if [ "$AGE" -gt 7200 ]; then
        echo "⚠️  session-handoff.md 已超过 2 小时未更新，请在停止前补充交接。" >&2
    fi
fi

# ── 5. P0 OPEN 审计检查 ──────────────────────────────────────
AUDIT="$REPO_ROOT/docs/audit/AUDIT_TRACKER.md"
if [ -f "$AUDIT" ]; then
    P0_OPEN=$(grep -E '\| P0 \|' "$AUDIT" | grep -v 'CLOSED\|VERIFIED' | head -3)
    if [ -n "$P0_OPEN" ]; then
        echo "⚠️  存在未关闭的 P0 审计问题（仅警告，不阻断）：" >&2
        echo "$P0_OPEN" >&2
    fi
fi

exit 0
