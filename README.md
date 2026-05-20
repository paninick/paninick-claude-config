# Claude Config

针织服装工贸一体 ERP 项目的 Claude Code 配置备份，包含 skill 体系、治理方法论、经验教训和模板。

> v2.0 · 2026-05-20 · 基于 ERP + 样衣项目实战经验全面升级

## 快速重建（安装体系）

```bash
# 1. 克隆本仓库
git clone https://github.com/paninick/paninick-claude-config.git
cd paninick-claude-config

# 2. 复制核心 skill 到全局目录
mkdir -p ~/.claude/skills
cp -r skills/erp-verify ~/.claude/skills/
cp -r skills/knit-erp-workflow ~/.claude/skills/
cp -r skills/skill-registry ~/.claude/skills/
cp -r skills/erp-devops-review ~/.claude/skills/
cp -r skills/erp-product-review ~/.claude/skills/
cp -r skills/erp-tdd ~/.claude/skills/

# 3. 安装全局第三方 skill（superpowers + Trail of Bits）
bash skills/install-global-skills.sh

# 4. 恢复 settings.json
cp settings.template.json ~/.claude/settings.json
# 用编辑器打开，将 YOUR_KEY_HERE 替换为你的实际 API key
```

## 目录结构

```
paninick-claude-config/
├── skills/                          # Skill 体系
│   ├── erp-verify/                  # ERP 项目验证（含 V1/V2/V4 回归脚本）
│   ├── knit-erp-workflow/           # 针织工艺流转专用
│   ├── skill-registry/              # Skill 注册与评估体系
│   ├── erp-devops-review/           # 运维/部署/发布准备评审
│   ├── erp-product-review/          # 产品完成度/偏离度评审
│   ├── erp-tdd/                     # 测试驱动开发（RED-GREEN-REFACTOR）
│   ├── genericagent-bridge/         # GenericAgent 桥接
│   └── install-global-skills.sh     # 全局第三方 skill 安装脚本
├── docs/                            # 文档体系
│   ├── coding-standards.md          # 编码规范（后端+前端+SQL）
│   ├── delivery-checklist.md        # 10步交付检查点
│   ├── context-management.md        # 上下文管理
│   ├── coordination-rules.md        # 协作规则
│   ├── agent-roster.md              # Agent 编制
│   ├── templates/                   # 模板（ADR/模块Spec/Sprint计划）
│   └── erp-reference/               # ERP 项目关键文档参考
│       ├── KNOWN_ISSUES.md          # 已知故障知识库
│       ├── DEVOPS_RUNBOOK.md        # 运维手册
│       ├── GOVERNANCE.md            # 治理方法论
│       ├── RULE_CATALOG.md          # 规则总目录
│       └── ARCHITECTURE_OVERVIEW.md # 架构概览
├── hooks/                           # Git hooks
│   └ scripts/                       # pre-commit/post-edit/stop-check 脚本
├── lessons-learned.md               # 跨项目经验教训（ERP + 样衣）
├── settings.template.json           # settings.json 模板（不含 key）
└── README.md
```

## Skill 资源

| Skill | 来源 | 说明 |
|-------|------|------|
| erp-verify | 本仓库 | ERP 业务验证 + V1/V2/V4 回归脚本 + 架构规则扫描 |
| knit-erp-workflow | 本仓库 | 针织工艺流转（18道工序+外发路由+品控门禁） |
| skill-registry | 本仓库 | Skill 注册与评估体系（使用率追踪+淘汰机制） |
| erp-devops-review | 本仓库 | 运维/部署/发布准备评审（v2新增） |
| erp-product-review | 本仓库 | 产品完成度/偏离度/路线图评审（v2新增） |
| erp-tdd | 本仓库 | 测试驱动开发（v2新增） |
| genericagent-bridge | 本仓库 | GenericAgent 桥接（v2新增） |
| superpowers 套件 | [obra/superpowers](https://github.com/obra/superpowers) | 由 install 脚本安装 |
| differential-review | [trailofbits/skills](https://github.com/trailofbits/skills) | 由 install 脚本安装 |
| insecure-defaults | [trailofbits/skills](https://github.com/trailofbits/skills) | 由 install 脚本安装 |

## v2.0 升级内容

相比 v1.0（2026-04-22），v2.0 新增：

1. **4 个新 Skill**：erp-devops-review / erp-product-review / erp-tdd / genericagent-bridge
2. **erp-verify 增强**：V1/V2/V4 回归脚本 + 架构规则扫描（pre-commit hook）
3. **lessons-learned.md**：跨项目经验教训（7大类，50+条踩坑+最佳实践）
4. **docs 体系**：编码规范/交付检查点/治理方法论/规则目录/运维手册
5. **hooks 体系**：pre-commit/post-edit/stop-check 自动门禁
6. **registry.md 更新**：从79行→338行，记录真实使用数据

## 注意

- 本仓库为 **public**，不要提交 API key 或文件
- `settings.template.json` 是去 key 的模板，真实 key 不要 commit
- `lessons-learned.md` 中的样衣项目经验来自实际业务场景
