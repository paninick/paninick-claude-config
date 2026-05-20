# AGENTS.md

> ERP 针织服装工贸一体系统 · 最小有效治理
> 治理 v4.0 · 目标：减少文档负担，只保留高价值决策规则；把可检查规则下沉为机械门禁

---

## 1. 核心原则

- 文档规则只负责表达决策边界，不负责“假装阻断”。
- 真正有效的门禁必须来自机械检查：`pre-commit`、编译、测试、审计脚本。
- 不能被脚本、编译器、测试或 reviewer 明确验证的长 checklist，默认降级为参考，不作为硬门禁。
- 先减少错误，再减少流程；不是先堆流程再希望错误变少。

---

## 2. 意图分类

收到任务后先判断意图，再行动：

| 意图 | 允许 | 禁止 |
|------|------|------|
| 审查/验证/检查 | 只读、搜索、分析、报告 | 修改文件 |
| 修复 | 直接定位并修复已确认问题 | 顺手重构、扩 scope |
| 新功能 | 先写 Spec，确认后编码 | 无 Spec 直接写代码 |
| 重构 | 先写变更计划，确认后执行 | 功能变更与重构混提 |
| UI/UX | 先调 skill，再改代码 | 纯主观改界面 |
| 安全/审计 | 先调审计 skill，再出结论 | 跳过审计 skill 直接下结论 |

无法判断意图时，再向用户确认。

---

## 3. 必用 Skill 路由

以下任务必须先调用对应 skill：

- UI/UX：`web-design-guidelines` / `frontend-design` / `ui-ux-pro-max`
- 安全审计：优先 `differential-review` / `insecure-defaults`
- React 工程：`vercel-react-best-practices`
- SEO：`seo-audit`
- 技能发现/安装：`find-skills` / `skill-installer`

如果本地没有所需 skill：

1. 先用 `find-skills` 查找高质量 skill
2. 再尝试安装
3. 若安装失败，明确说明原因，并按公开规则或官方文档降级执行

---

## 4. 新功能规则

- No Spec No Code：任何新功能、明显的行为变更、接口契约变更，必须先写 Spec。
- Spec 至少说明：
  - 目标
  - 范围
  - 非目标
  - 影响文件
  - 风险点
- 修复类任务如果只是修正已确认 bug，可不强制单独写 Spec，但禁止扩 scope。

模板：`docs/templates/task-spec-template.md`

---

## 5. 机械门禁优先级

提交前真正必须依赖的检查只有这些：

1. `RuoYi-Vue/.git/hooks/pre-commit`
2. `mvn compile -f ruoyi-admin/pom.xml`
3. 必要时 `mvn test -f ruoyi-admin/pom.xml`
4. 审计类任务使用对应审计 skill 或等价自动化检查
5. `git diff --cached` 人工复核，确认没有 scope creep

说明：

- 文档里的长篇“自检清单”不再视为硬门禁。
- 新增规则时，优先改 hook / 脚本 / 测试，不优先扩写 Markdown。

---

## 6. 项目硬约束

这些仍然是必须遵守的项目边界：

- `ruoyi-framework/` 禁止修改
- `ruoyi-common/`、`ruoyi-system/` 属于框架核心，改动需额外谨慎
- MyBatis 用户输入必须用 `#{}`，禁止 `${}` 拼接用户输入
- 多表写操作必须有 `@Transactional(rollbackFor = Exception.class)`
- Controller 端点必须有 `@PreAuthorize`
- DDL 脚本必须走幂等写法，禁止裸 `ADD COLUMN IF NOT EXISTS`
- 新增 Java domain 字段后必须重新编译

详见：`PROJECT_CONFIG.md`

---

## 7. 审计与验证

- 审计结论优先基于审计 skill、源码证据、编译、测试，而不是主观判断。
- 修复完成不等于验证完成。
- 如果任务是“验证是否修复”，默认不改代码，只做只读验证。
- 如发现问题是系统性模式，应明确指出“不是单点问题”。
- **禁止只依据 `docs/audit/AUDIT_TRACKER.md` 判断“已完成/未完成”。**
- 任何完成度、完成状态、剩余项判断，必须同时核对三源：
  - `docs/audit/AUDIT_TRACKER.md`
  - `docs/session-handoff.md`
  - 对应代码 / 页面 / 测试文件
- 输出状态判断时必须分开写：
  - `代码实际状态`
  - `文档记录状态`
  - `是否一致`
  - `若不一致，哪份文档过时`
- **禁止把“代码已存在”等同于“已验收关闭”。**
- 只有同时满足以下条件，才可对外声称 `CLOSED`：
  - 已实现
  - 已补 Spec（如适用）
  - 已独立验证
  - tracker / handoff 已同步
- 如果发现“代码现实 > 文档现实”或“文档现实 > 代码现实”，必须在本轮明确标记为“状态漂移”。
- **执行者不得自报 `VERIFIED` 或 `CLOSED`。**
- **执行者最多只能建议状态到 `BUILD_PASSED`。**
- **执行者交付必须使用 `docs/plans/deepseek-delivery-template.md` 的结构化回报格式；不按该格式回报，默认状态无效。**
- **`session-handoff` 顶部对外状态只能由复核者更新，执行者只能写证据与建议状态。**

---

## 8. 会话结束要求

会话结束前更新：

- `docs/session-handoff.md`

至少写清：

- 当前任务
- 已确认问题
- 是否已修改代码
- 是否已验证
- 下一步建议

---

## 9. Agent 系统

本项目使用多层 Agent 体系协作开发：

| 层级 | Agent | 职责 |
|------|-------|------|
| Tier 1 (Opus) | erp-cto, erp-pm, erp-product-owner | 战略决策、规划、业务规则 |
| Tier 2 (Sonnet) | erp-lead-backend, erp-lead-frontend, erp-lead-qa, erp-lead-db, erp-release-manager | 技术领导、代码审查 |
| Tier 3 (Sonnet/Haiku) | erp-backend-dev, erp-frontend-dev, erp-security, erp-perf, erp-qa-tester, erp-devops, erp-i18n | 具体实现 |

详见：`.claude/docs/agent-roster.md`

---

## 10. 文件索引

- 审计追踪：`docs/audit/AUDIT_TRACKER.md`
- 已知问题：`docs/KNOWN_ISSUES.md`
- 会话交接：`docs/session-handoff.md`
- 项目配置：`PROJECT_CONFIG.md`
- 治理方法论：`docs/GOVERNANCE.md`
- Spec 模板：`docs/templates/task-spec-template.md`
- Agent 名册：`.claude/docs/agent-roster.md`
- 协作规则：`.claude/docs/coordination-rules.md`
- 编码规范：`.claude/docs/coding-standards.md`
- 交付检查点：`.claude/docs/delivery-checklist.md`

---

## 10. 一句话版本

少写规则，多写自动化；少靠自觉，多靠验证；没有机械检查支撑的门禁，不算真正门禁。
