#!/usr/bin/env bash
# 检查当前编辑目标是否触碰了 ruoyi-framework/ 框架核心目录
# 由 erp-verify hooks.PreToolUse 在每次 Edit/Write 前自动调用

FRAMEWORK_PATH="RuoYi-Vue/ruoyi-framework"

# Claude Code 会把目标文件路径通过环境变量或 stdin 传入
# 检查 CLAUDE_TOOL_INPUT 环境变量（file_path 字段）
TARGET="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"

if [ -z "$TARGET" ]; then
  exit 0  # 无法获取路径时放行，不阻断
fi

# 规范化路径分隔符
TARGET_NORM=$(echo "$TARGET" | tr '\\' '/')

if echo "$TARGET_NORM" | grep -q "$FRAMEWORK_PATH"; then
  echo "❌ [erp-verify] 禁止修改框架核心目录: $TARGET"
  echo "   ruoyi-framework/ 受保护，业务代码请放在 ruoyi-demo/"
  exit 1
fi

exit 0
