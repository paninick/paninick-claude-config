# Claude Config

个人 Claude Code 配置备份，包含自建 skill 体系和设置模板。

## 重建步骤（重装系统后）

```bash
# 1. 克隆此仓库
git clone https://github.com/paninick/paninick-claude-config.git
cd paninick-claude-config

# 2. 复制本地 skill 到全局目录
mkdir -p ~/.claude/skills
cp -r skills/erp-verify ~/.claude/skills/
cp -r skills/knit-erp-workflow ~/.claude/skills/
cp -r skills/skill-registry ~/.claude/skills/

# 3. 安装全局第三方 skill（superpowers + Trail of Bits）
bash skills/install-global-skills.sh

# 4. 恢复 settings.json
cp settings.template.json ~/.claude/settings.json
# 用编辑器打开，将 YOUR_KEY_HERE 替换为真实 API key
```

## 目录结构

```
paninick-claude-config/
├── skills/
│   ├── erp-verify/               ← ERP 项目验证 skill
│   ├── knit-erp-workflow/        ← 针织工序流转 skill
│   ├── skill-registry/           ← Skill 治理与迭代
│   └── install-global-skills.sh  ← 第三方 skill 安装脚本
├── settings.template.json        ← settings.json 模板（不含 key）
└── README.md
```

## Skill 来源

| Skill | 来源 | 说明 |
|-------|------|------|
| erp-verify | 本仓库 | ERP 业务验证，自建 |
| knit-erp-workflow | 本仓库 | 针织工序流转，自建 |
| skill-registry | 本仓库 | Skill 治理体系，自建 |
| superpowers 套件 | [obra/superpowers](https://github.com/obra/superpowers) | 由 install 脚本安装 |
| differential-review | [trailofbits/skills](https://github.com/trailofbits/skills) | 由 install 脚本安装 |
| insecure-defaults | [trailofbits/skills](https://github.com/trailofbits/skills) | 由 install 脚本安装 |
| gstack 套件 | gstack 官方 | 需单独安装，见 install 脚本提示 |

## 注意

- 本仓库已设为**公开（public）**，不要提交含 API key 的文件
- `settings.template.json` 是去掉 key 的模板，填入 key 后不要 commit
