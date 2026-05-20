# ERP 上下文管理策略

## 会话状态文件

### 主动状态文件

```
production/session-state/active.md    ← 当前会话状态（每次会话更新）
docs/session-handoff.md               ← 跨会话交接文档
docs/audit/AUDIT_TRACKER.md           ← 决策审计记录
```

### 会话状态模板

```markdown
# 会话状态 - [日期]

## 当前 Sprint
Sprint [N]，目标：[目标描述]

## 今日工作
- [x] 已完成：[任务描述]
- [ ] 进行中：[任务描述]
- [ ] 待处理：[任务描述]

## 关键决策
- [决策描述] → [选择的方案] → [原因]

## 阻塞项
- [阻塞描述] → [负责人] → [预计解决时间]

## 下次会话优先事项
1. [优先事项 1]
2. [优先事项 2]
```

## 上下文压缩策略

### 压缩前（PreCompact Hook）

自动保存到 `production/session-state/active.md`：
- 当前工作状态
- 未完成的任务
- 关键决策记录
- 下一步行动

### 压缩后（PostCompact Hook）

会话恢复时：
1. 读取 `production/session-state/active.md`
2. 读取 `docs/session-handoff.md`
3. 检查 `docs/audit/AUDIT_TRACKER.md` 中的最新决策

## 长会话管理

### 何时主动压缩

- 完成一个完整的模块实现后
- 切换到不同业务领域前
- 上下文使用超过 60% 时

### 压缩前检查清单

- [ ] 当前任务状态已记录
- [ ] 未完成的代码变更已保存
- [ ] 关键决策已记录到 AUDIT_TRACKER.md
- [ ] 下一步行动已明确

## 跨会话上下文

### 会话开始时必读文件

1. `CLAUDE.md` — 项目规则和约束
2. `docs/session-handoff.md` — 上次会话交接
3. `production/session-state/active.md` — 当前状态
4. `docs/audit/AUDIT_TRACKER.md` — 最近决策（最后 10 条）

### 会话结束时必写文件

1. 更新 `docs/session-handoff.md`
2. 归档 `production/session-state/active.md` 到 `production/session-logs/[date].md`

## Agent 上下文传递

当委派工作给 sub-agent 时，必须在 prompt 中包含：

```
上下文：
- 项目：ERP 针织服装系统（RuoYi-Vue + React）
- 当前 Sprint：[N]，目标：[目标]
- 相关文件：[文件路径列表]
- 技术约束：[关键约束]
- 期望输出：[具体描述]
```
