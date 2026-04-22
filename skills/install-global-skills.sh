#!/usr/bin/env bash
# 全局 skill 安装脚本
# 重建 ~/.claude/skills/ 下所有全局 skill
# 用法：bash install-global-skills.sh

set -e

SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_DIR"

echo "=== 安装全局 skills ==="

# ── Superpowers 套件 ──────────────────────────────────────────
echo "[1/3] obra/superpowers"
TMP=$(mktemp -d)
git clone --depth=1 https://github.com/obra/superpowers.git "$TMP/superpowers" 2>/dev/null
cp -r "$TMP/superpowers/skills/"* "$SKILLS_DIR/"
rm -rf "$TMP"
echo "  ✓ brainstorming, writing-plans, executing-plans, test-driven-development,"
echo "    systematic-debugging, requesting-code-review, dispatching-parallel-agents,"
echo "    verification-before-completion, using-git-worktrees, writing-skills,"
echo "    finishing-a-development-branch, subagent-driven-development, using-superpowers"

# ── Trail of Bits 套件 ────────────────────────────────────────
echo "[2/3] trailofbits/skills"
TMP=$(mktemp -d)
git clone --depth=1 https://github.com/trailofbits/skills.git "$TMP/tob" 2>/dev/null
cp -r "$TMP/tob/plugins/differential-review/skills/differential-review" "$SKILLS_DIR/"
cp -r "$TMP/tob/plugins/insecure-defaults/skills/insecure-defaults" "$SKILLS_DIR/"
rm -rf "$TMP"
echo "  ✓ differential-review, insecure-defaults"

# ── Gstack 套件 ───────────────────────────────────────────────
echo "[3/3] gstack"
echo "  gstack 需要通过官方安装器安装，请运行："
echo "  curl -fsSL https://gstack.dev/install.sh | bash"
echo "  或参考：https://github.com/gstack-dev/gstack"

echo ""
echo "=== 完成 ==="
echo "全局 skills 位置：$SKILLS_DIR"
echo "项目本地 skills：D:/erp/.claude/skills/"
