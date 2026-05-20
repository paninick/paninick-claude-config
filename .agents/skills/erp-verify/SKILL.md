---
name: erp-verify
version: 2.0.0
description: ERP项目工作验证。在完成Java后端(Domain/Mapper/Service/Controller)、前端Vue页面、SQL迁移脚本变更后，或准备/ship前调用。检查BigDecimal金额、验证注解、Mapper XML规范、权限注解、SQL迁移规范、框架文件保护。
triggers:
  - erp verify
  - 验证代码
  - 提交前检查
  - backend changed
  - sql migration
  - vue page done
  - ready to ship
voice-triggers:
  - "check before commit"
  - "run erp checks"
  - "verify my changes"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Edit
  - Write
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-framework.sh"
          statusMessage: "检查是否触碰 ruoyi-framework/ 保护目录..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-framework.sh"
          statusMessage: "检查是否触碰 ruoyi-framework/ 保护目录..."
---

# erp-verify — ERP 工作验证

每次完成功能开发、SQL 变更、接口新增后调用。验证通过才能 `/ship`。

## 触发时机（必须调用，不可跳过）

| 场景 | 触发条件 |
|------|---------|
| 后端变更 | 新增/修改 Domain / Mapper / Service / Controller |
| 前端变更 | 新增/修改 `.vue` 页面或 API `.js` 文件 |
| SQL 变更 | 新增迁移脚本 |
| 提交前 | 任何准备 `/ship` 的时刻 |

## 验证流程

1. 根据本次变更类型，从 `reference.md` 加载对应检查项
2. 逐项执行，发现问题立即修复
3. 运行 `scripts/check.py` 做自动化扫描
4. 全部通过后输出验证报告，再调用 `/ship`

## 输出格式

```
=== erp-verify 验证报告 ===
[后端] ✅ BigDecimal / ❌ 问题：OrderItem.price 用了 double → 已修复
[SQL]  ✅ 脚本命名规范
[前端] ✅ 组件 PascalCase
结论：通过 → 可执行 /ship
```

## 关联 Skills

- 验证通过 → `/ship`
- 发现 bug → `/investigate`（Iron Law：必须找到根因再修）
- 新功能方向讨论 → `/office-hours`
- 代码质量评分 → `/health`

## 文件导航

- `reference.md` — 完整检查项细则（按模块分类）
- `examples.md` — 典型问题案例与修复示例
- `scripts/check.py` — 自动化扫描脚本
- `bin/check-framework.sh` — PreToolUse hook：Edit/Write 前自动拦截 framework 目录
