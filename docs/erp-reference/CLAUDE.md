# CLAUDE.md

> ERP 针织服装工贸一体系统 · 项目级 AI 协作规范
> 治理 v3.8 · 硬门禁 + Skill 路由（精简版）· 完整方法论见 [docs/GOVERNANCE.md](docs/GOVERNANCE.md)
>
> **模型无关**：规则以自然语言写成，有效性来自机械门禁（pre-commit hook、编译检查），
> 不来自模型对规则的"理解"。同等适用于任何遵循 Markdown 指令的 AI。
>
> **项目配置**：项目特定设置见 [PROJECT_CONFIG.md](PROJECT_CONFIG.md)。

---

## 0. 意图分类（IntentGate — 第一步，先分类再行动）

| 意图关键词 | 意图类别 | 允许 | 禁止 |
|-----------|---------|------|------|
| 检查/审查/验证/看看/查一下 | **只读审查** | 读文件、搜索、分析、报告 | **禁止修改任何文件** |
| 修复/改/修正 | **定向修复** | 只改 fix-checklist 中列出的文件/行号 | 禁止 scope creep、禁止顺手重构 |
| 实现/开发/新增/加 | **新功能开发** | 先写 Spec → 等待确认 → 编码 | 禁止无 Spec 直接写代码 |
| 重构/整理/优化 | **代码重构** | 先写变更计划 → 等待确认 → 分步提交 | 禁止功能变更与重构混在同一个 commit |
| UI/设计/美化/样式/界面/页面/组件/UX/前端 | **UI/UX 设计** | **必须先调 Skill**：`Skill("web-design-guidelines")` / `Skill("frontend-design")` / `Skill("ui-ux-pro-max")` / `Skill("design-consultation")` 至少其一，获取标准化规则 → 交叉验证项目一致性 → 最后写代码 | 禁止凭主观审美直接写 UI 代码；禁止不引用 skill 规则就做设计决策 |
| 安全/审计/漏洞/权限/SQL/注入 | **安全审计** | `Skill("differential-review")` / `Skill("insecure-defaults")` → 读 AUDIT_TRACKER → 生成报告 | 禁止未读 AUDIT_TRACKER 就开始新任务 |
| 默认密码/硬编码/配置审计 | **不安全默认值** | `Skill("insecure-defaults")` → 全量 YML/Properties/Mapper XML 扫描 | 禁止跳过任何配置文件 |
| React/性能/优化/最佳实践 | **React 工程** | `Skill("vercel-react-best-practices")` → 分析组件 → 实施优化 | 禁止无度量凭感觉优化 |
| SEO/搜索引擎/排名 | **SEO** | `Skill("seo-audit")` → 抓取页面 → 问题列表 | — |
| 安装skill/查找技能 | **Skill 发现** | `Skill("find-skills")` → 搜索生态 → 安装 | — |

**无法确定意图 → 停下，向用户确认。**

---

## 1. 强制门禁（每次会话启动 + 上下文压缩恢复后，逐条执行，不可跳过）

> **上下文压缩恢复 = 新会话**：压缩丢失了此前的门禁状态和 skill 执行结果。
> 压缩恢复后必须重新执行全部 6 步，不得假设"之前已经执行过"。

**压缩恢复检测信号**（任一出现即确认压缩恢复）：
- 上下文中出现 `<summary>` / `<compaction>` / `<conversation_history_summary>` 标签
- 上下文开头出现 `This session is being continued from a previous conversation` 或同类系统提示
- 上下文长度骤降（完整对话突然变摘要）

0. 检测上述信号 → 确认压缩恢复 → 门禁状态清零 → 显式声明"检测到压缩恢复，重新执行 §1 全部门禁" → 重新执行全部步骤
1. 读取 `docs/audit/AUDIT_TRACKER.md`，检查是否存在 `status != "CLOSED"` 且 `severity = "P0"` 的记录
2. **存在 P0 未关闭 → 禁止任何新开发任务**，只能做 P0 修复
3. 读取 `docs/KNOWN_ISSUES.md`，按触发条件查表（不确定时必查，人脑记不住所有坑）
4. 读取 `docs/session-handoff.md` 了解上次会话上下文和遗留问题
5. 读取 `C:/Users/91306/.claude/projects/d--erp/memory/MEMORY.md` 了解用户偏好和项目背景

**跳过任一步骤 → 产出无效。这不是建议，是入口条件。**

> **Adaptive Thinking 注意**：本项目运行在 Claude 4.X（Opus 4.7/Sonnet 4.6），模型自行判断思考深度。
> **禁止**使用 "be thorough / think carefully / do not be lazy" 类旧式提示 — 在新模型上反而导致过思考和输出膨胀。
> 正确做法：信任 Adaptive Thinking，用 `effort` 级别（low/medium/high/max）而非手动 budget_tokens 控制深度。

---

## 2. No Spec No Code

任何新功能/修复任务开始前，必须填写 `docs/templates/task-spec-template.md`，经人工确认后方可写代码。跳过 Spec 直接生成 → 可用率 <30%。

---

## 3. 会话结束

更新 `docs/session-handoff.md`：
- 时间 / 最后 commit / 当前任务 / 遗留问题 / 下一步 / 注意事项

**禁止不写交接直接结束。**

---

## 4. 门禁响应规则

pre-commit hook 阻断时：
1. 阅读阻断消息 → 找到引用文件 → 修复根因 → 重新运行门禁 → 通过后提交
2. **禁止**：说"缓存状态"就绕过、不看阻断消息就 `--no-verify`、阻塞后不修根因直接提交

---

## 5. git add 前质量自检（PostToolUse）

执行 `git add` 之前，运行 `git diff` 逐条过：
- [ ] **[M-GA01]** 每个 `+` 行：注解类型是否已存在于该文件？（不存在 → scope creep，撤销）
- [ ] **[M-GA02]** import 行是否有重复？（有 → 删除）
- [ ] **[M-GA03]** 变更是否全部来自 fix-checklist 或 Spec？（不是 → 撤销）
- [ ] **[M-GA04]** 是否有 `// ...` 不完整实现或 TODO？（有 → 完成后再 add）
- [ ] **[M-GA05]** 是否有注释掉的代码？（有 → 删除，用 git 历史追溯）
- [ ] **[M-GA06]** 是否有硬编码配置值（URL、密钥、端口号）？（有 → 移到配置文件）

**任何一项不通过 → 不得 git add → 不得 commit。**
> 规则标签说明：`[M]`=强制(阻断) `[S]`=建议(警告) `[C]`=参考。完整规则目录见 [docs/RULE_CATALOG.md](docs/RULE_CATALOG.md)

---

## 6. 提交前自查

- [ ] `git diff --cached --stat` — 文件列表只含预期变更？
- [ ] `git diff --cached` — 无重复 import、多余空行、遗留注释、scope creep？
- [ ] `mvn compile -f ruoyi-admin/pom.xml` — 编译通过
- [ ] `bash .git/hooks/pre-commit` — 门禁放行

**全部通过后方可 `git commit`。**

---

## 7. 禁止行为

- ❌ **[M-P001]** 收到审计报告后不读取 AUDIT_TRACKER.md 就开始其他任务
- ❌ **[M-P002]** 自验自宣告"修复通过"（必须调用独立 skill 验证）
- ❌ **[M-P003]** 带着 OPEN P0 开始新功能开发
- ❌ **[M-P004]** 合并"修复"与"新功能"在同一个 commit
- ❌ **[M-P005]** 修复审计问题时 scope creep（顺手加校验注解/重构/改注释语言）
- ❌ **[M-P006]** `git commit` 前不做 `git diff --cached` 自查
- ❌ **[M-P007]** commit 后不等审查反馈就直接开始下一个任务
- ❌ **[M-P008]** 在修复 commit 中混入 fix-checklist 未要求的注解类型（P0 契约变更）
- ❌ **[M-P009]** 没有 Spec 确认就直接写代码（No Spec No Code）
- ❌ **[M-P010]** `git add` 前不做质量自检（6 项）
- ❌ **[M-P011]** 会话结束前不更新 session-handoff.md
- ❌ **[M-P012]** 因成本考虑在安全审计/架构决策/P0 修复验证中使用弱模型
- ❌ **[M-P013]** 能力不足时不声明、不停止、继续输出低质量代码
- ❌ **[M-P014]** 上下文压缩恢复后跳过 §1 门禁，假设"之前已执行过"
- ❌ **[M-P015]** 对不确定的事实/代码路径/配置值，以确定语气陈述推测内容（必须显式标注置信度：`确定`/`推测`/`未知`；引用来源：`来源：文件名:行号` 或 `来源：WebSearch`）

---

## 8. 项目框架约定

**详见 [PROJECT_CONFIG.md](PROJECT_CONFIG.md) §框架约定**。关键约束摘要：
- MyBatis SQL：用户输入 `#{}`，禁止 `${}` 拼接
- 事务：多表写操作 `@Transactional(rollbackFor = Exception.class)`
- 权限：Controller 端点 `@PreAuthorize("@ss.hasPermi('erp:模块:动作')")`
- Domain：新增字段后 `mvn compile` 再 commit（Lombok/MyBatis 方法签名可能被静默替换）
- DDL：PREPARED STATEMENT + INFORMATION_SCHEMA 幂等
- 模块边界：`ruoyi-framework/` 禁止修改

---

## 9. 治理体系索引

| 需要什么 | 去哪里 |
|---------|--------|
| 完整方法论（SDD/审计流程/修复约束/成本策略） | [docs/GOVERNANCE.md](docs/GOVERNANCE.md) |
| 故障决策表（触发条件→检查项→历史案例） | [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) |
| 审计追踪（P0/P1 状态机） | [docs/audit/AUDIT_TRACKER.md](docs/audit/AUDIT_TRACKER.md) |
| 研究整合（95+ 来源洞察） | [docs/RESEARCH_SYNTHESIS.md](docs/RESEARCH_SYNTHESIS.md) |
| 项目目录（65 项目 T1-T5+可信度） | [docs/PROJECT_CATALOG.md](docs/PROJECT_CATALOG.md) |
| 规则总目录（所有规则的 ID/等级/可检性） | [docs/RULE_CATALOG.md](docs/RULE_CATALOG.md) |
| Spec 模板 | [docs/templates/task-spec-template.md](docs/templates/task-spec-template.md) |
| 模块契约模板 | [docs/templates/module-claude-template.md](docs/templates/module-claude-template.md) |
| 治理模板（新项目实例化） | [docs/templates/governance/](docs/templates/governance/) |
| 会话交接 | [docs/session-handoff.md](docs/session-handoff.md) |
| 项目配置（技术栈/构建/约定） | [PROJECT_CONFIG.md](PROJECT_CONFIG.md) |

---

## 项目结构

- **后端**：`RuoYi-Vue/` (git submodule, Java 17 + Spring Boot 4.x + MyBatis)
- **前端**：双前端并存
  - `RuoYi-Vue/ruoyi-ui/` (Vue 2，当前稳定交付面)
  - `ERP-UI-2/` (React + TypeScript，当前活跃演进面)
- **SQL 脚本**：`RuoYi-Vue/sql/`
- **技术栈**：MySQL 8.0 · 针织服装行业工贸一体 ERP
- **完整配置**：见 [PROJECT_CONFIG.md](PROJECT_CONFIG.md)
