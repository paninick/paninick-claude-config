# Skill 注册表

> 最后更新：2026-04-22 | 功能完成计数：0 | 下次迭代报告：第 5 次

---

## 本地 Skill（D:/erp/.claude/skills/）

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| erp-verify | active | 0 | 0 | — | — | keep | 核心验证 skill，覆盖后端/前端/SQL |
| knit-erp-workflow | active | 0 | 0 | — | — | keep | 工序流转专用，业务知识密集 |
| skill-registry | active | 0 | 0 | — | — | keep | 本体系治理 skill |

---

## 全局 Skill 使用记录（~/.claude/skills/）

### Superpowers 套件

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| brainstorming | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| writing-plans | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| executing-plans | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| test-driven-development | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| systematic-debugging | probation | 0 | 0 | — | — | watch | 与 gstack/investigate 重叠，观察哪个更有效 |
| requesting-code-review | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| dispatching-parallel-agents | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| verification-before-completion | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| using-git-worktrees | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| writing-skills | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| finishing-a-development-branch | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| subagent-driven-development | probation | 0 | 0 | — | — | watch | 新引入，待验证 |

### Gstack 套件

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| investigate | active | 0 | 0 | — | — | keep | 与 systematic-debugging 重叠，观察期对比 |
| ship | active | 0 | 0 | — | — | keep | 提交流程核心 |
| review | active | 0 | 0 | — | — | keep | 与 requesting-code-review、differential-review 三方对比 |
| health | probation | 0 | 0 | — | — | watch | 与 erp-verify 部分重叠，观察是否互补 |
| qa | probation | 0 | 0 | — | — | watch | 前端测试场景待验证 |
| context-save | active | 0 | 0 | — | — | keep | 跨会话保存进度 |
| context-restore | active | 0 | 0 | — | — | keep | 跨会话恢复进度 |

### Trail of Bits 套件

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| differential-review | probation | 0 | 0 | — | — | watch | 安全 diff 审查，与 gstack/review 三方对比；有 methodology/adversarial/patterns 分层文档 |
| insecure-defaults | probation | 0 | 0 | — | — | watch | 检测硬编码凭证/fail-open，补充 erp-verify 安全层；fail-open vs fail-secure 区分设计值得学习 |

---

## 已知冲突对

| skill A | skill B | skill C | 冲突类型 | 当前策略 |
|---------|---------|---------|---------|---------|
| systematic-debugging | investigate | — | 功能重叠（根因调试） | 并行观察，命中率高者保留 |
| requesting-code-review | review | differential-review | 功能重叠（代码审查） | 三方对比：review=通用，requesting=子agent并行，differential=安全专项 |
| health | erp-verify | insecure-defaults | 部分重叠（代码质量/安全） | 观察分工：erp-verify=业务规范，insecure-defaults=安全专项，health=综合评分 |

---

## 链路断裂记录

| 断裂节点 | 次数 | 最近发生 |
|---------|------|---------|
| （暂无） | — | — |

---

## 迭代历史

| 轮次 | 日期 | 功能数 | 变更 |
|------|------|--------|------|
| 初始化 | 2026-04-22 | 0 | 建立注册表 |
