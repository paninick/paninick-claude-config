---
name: skill-registry
version: 1.0.0
description: Skill治理与迭代。每次完成一个功能后自动触发：记录本次调用的skill、更新命中率、检查调用链完整性、输出迭代建议。当发现skill评分触发阈值或新skill与现有skill冲突时提出替换/移除建议（需用户确认后执行）。
triggers:
  - skill report
  - skill迭代
  - 功能完成
  - update registry
  - skill health
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
---

# skill-registry — Skill 治理与迭代

## 核心原则

**我主导判断，skill 是工具不是规则。**

- registry 是记录判断过程的日志，不是约束行为的规则
- 实际命中率与 registry 评分不一致时，以我的实际判断为准并更新原因
- 移除任何 skill 前必须告知用户，确认后才执行

---

## 每次功能完成后执行

1. 读取 `registry.md`
2. 记录本次用了哪些 skill、是否命中（发现真实问题）
3. 检查调用链完整性（见下）
4. 更新各 skill 的 invoke_count / hit_count / hit_rate
5. 检查是否触发阈值 → 输出建议
6. 每累计 5 次功能完成 → 输出完整迭代报告
7. 写回 `registry.md`，然后继续 `/ship`

---

## 调用链完整性检查

标准链路：
```
brainstorming → writing-plans → executing-plans
                                      ↓
                                erp-verify ← test-driven-development
                                      ↓
                           requesting-code-review
                                      ↓
                        verification-before-completion
                                      ↓
                                    ship
```

- 调用了 `executing-plans` 但跳过 `erp-verify` → 记录链路断裂
- 调用了 `erp-verify` 但跳过 `verification-before-completion` → 记录链路断裂
- 同一节点断裂累计 3 次 → 标记为 `probation`，在报告中说明原因

---

## 评分规则（参考，不强制）

| 命中率 | 状态 |
|--------|------|
| ≥ 40% | active — keep |
| 10–40% | probation — 观察 |
| < 10% 且调用 ≥ 5 次 | 候选移除，告知用户 |
| 调用 0 次且存在 ≥ 30 天 | 候选移除，告知用户 |

若我的实际判断与上述规则不符，以判断为准，在 registry.md 的 `verdict_reason` 字段记录原因。

---

## 新 skill 引入流程

1. 在 registry.md 以 `probation` 状态注册
2. 判断与现有哪个 skill 功能重叠
3. 连续 5 次功能中至少调用 2 次
4. 命中率 ≥ 40% → 升为 `active`，评估是否替换重叠 skill
5. 命中率 < 10% → 告知用户，建议移除

---

## 迭代报告格式

```
=== Skill 迭代报告（第 N 轮）===
[keep]    erp-verify        调用 8，命中 5，命中率 62%
[watch]   health            调用 2，命中 0，命中率 0%  ← 再观察 3 次
[remove?] brainstorming     调用 0，30天未使用 ← 待你确认

链路断裂：executing-plans → erp-verify 断裂 2 次

建议：
- health：功能与 erp-verify 部分重叠，建议合并或移除
- brainstorming：本地副本与全局重复，建议移除本地副本
```

---

## 文件

- `registry.md` — 注册表数据
- `scripts/evaluate.py` — 统计脚本（辅助，不强制依赖）
