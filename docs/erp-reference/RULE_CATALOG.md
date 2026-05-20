# 规则总目录

> 治理 v3.5 · 所有规则的唯一入口。每条规则有唯一 ID、等级标签、可检性标注。
> 标签体系：`[M]`=强制(阻断) `[S]`=建议(警告) `[C]`=参考

---

## 规则 ID 格式

```
{等级}-{域}{序号}  例: M-GA01 = 强制 · Git Add 域 · 第01条

域代码:
  GA = Git Add 质量自检    PE = 权限与安全
  AR = 架构约定            CR = 代码审查
  SE = 安全规范            AU = 审计流程
  SP = Spec 规范           CI = 提交前检查
```

---

## 一、Git Add 质量自检 (GA)

| ID | 等级 | 规则 | 可检性 |
|:--|:----:|------|:------:|
| M-GA01 | [M] | `+` 行注解类型必须已存在于该文件 | 正则/grep |
| M-GA02 | [M] | import 行不得重复 | 正则 |
| M-GA03 | [M] | 变更必须全部来自 fix-checklist 或 Spec | diff 对比 |
| M-GA04 | [M] | 禁止 `// ...` 不完整实现或 TODO | 正则 |
| M-GA05 | [M] | 禁止注释掉的代码 | 正则 |
| M-GA06 | [M] | 禁止硬编码配置值（URL/密钥/端口） | 正则 |

---

## 二、提交前检查 (CI)

| ID | 等级 | 规则 | 可检性 |
|:--|:----:|------|:------:|
| M-CI01 | [M] | `git diff --cached --stat` 文件列表只含预期变更 | diff 对比 |
| M-CI02 | [M] | `git diff --cached` 无重复 import/空行/遗留注释 | diff 对比 |
| M-CI03 | [M] | `mvn compile -f ruoyi-admin/pom.xml` 编译通过 | 编译 |
| M-CI04 | [M] | `bash .git/hooks/pre-commit` 门禁放行 | 脚本 |
| S-CI01 | [S] | 提交信息格式：`{type}: {描述}` (feat/fix/docs/refactor/test/chore) | 正则 |

---

## 三、禁止行为 (P)

| ID | 等级 | 规则 | 域 |
|:--|:----:|------|:--:|
| M-P001 | [M] | 禁止收到审计报告后不读 AUDIT_TRACKER 就开始其他任务 | AU |
| M-P002 | [M] | 禁止自验自宣告修复通过 | AU |
| M-P003 | [M] | 禁止带着 OPEN P0 开始新功能开发 | AU |
| M-P004 | [M] | 禁止合并修复与新功能在同一个 commit | CR |
| M-P005 | [M] | 禁止修复时 scope creep | CR |
| M-P006 | [M] | 禁止 commit 前不做 diff --cached 自查 | CR |
| M-P007 | [M] | 禁止 commit 后不等审查反馈就开始下一个任务 | CR |
| M-P008 | [M] | 禁止在修复 commit 中混入新注解类型 | AR |
| M-P009 | [M] | 禁止无 Spec 确认就写代码 | SP |
| M-P010 | [M] | 禁止 git add 前不做质量自检 | GA |
| M-P011 | [M] | 禁止会话结束前不更新 session-handoff | AU |
| M-P012 | [M] | 禁止关键任务使用弱模型 | PE |
| M-P013 | [M] | 禁止能力不足时不声明继续输出 | CR |

---

## 四、架构约定 (AR)

| ID | 等级 | 规则 | 域 |
|:--|:----:|------|:--:|
| M-AR01 | [M] | Controller 只做入参校验+转发，禁止业务逻辑 | 分层 |
| M-AR02 | [M] | 多表写操作必须 @Transactional(rollbackFor = Exception.class) | 事务 |
| M-AR03 | [M] | Mapper 只用 #{} 参数化，禁止 ${} 拼接用户输入 | SQL |
| M-AR04 | [M] | Controller 端点必须 @PreAuthorize | 权限 |
| M-AR05 | [M] | Domain 每个字段 @Excel(name = "...") | Domain |
| M-AR06 | [M] | Domain toString() 必须包含全部字段 | Domain |
| M-AR07 | [M] | ruoyi-framework/ 禁止修改 | 模块边界 |
| M-AR08 | [M] | 新增字段后 mvn compile 再 commit | 编译 |
| M-AR09 | [M] | DDL 用 PREPARED STATEMENT + INFORMATION_SCHEMA 幂等 | DDL |
| M-AR10 | [M] | 禁止 REPLACE INTO | SQL |
| M-AR11 | [M] | 禁止循环内单条 Mapper 查询（N+1） | 性能 |
| M-AR12 | [M] | 禁止 this.method() 调用需要事务的方法 | 事务 |
| S-AR01 | [S] | 新功能必须参考已有类似实现（模式复用） | 架构 |
| S-AR02 | [S] | 禁止私有方法参数加 @NotNull/@NotBlank | 校验 |
| S-AR03 | [S] | 异常不吞掉，转换为业务异常或 BizAbnormalPool | 异常 |

---

## 五、权限与安全 (PE/SE)

| ID | 等级 | 规则 | 可检性 |
|:--|:----:|------|:------:|
| M-SE01 | [M] | 用户输入 SQL 参数用 #{} 禁止 ${} | 正则 |
| M-SE02 | [M] | 低风险操作（读文件/grep/git status）自动放行 | 权限 |
| M-SE03 | [M] | 高风险操作（curl/rm/git push --force）要求审批 | 权限 |
| S-SE01 | [S] | 敏感文件（.env, *.pem, credentials.*）禁止读写 | Glob |
| S-SE02 | [S] | 依赖库定期 CVE 扫描（SBOM） | 工具 |

---

## 六、审计流程 (AU)

| ID | 等级 | 规则 |
|:--|:----:|------|
| M-AU01 | [M] | FIX_CLAIMED → VERIFIED 必须在新会话中完成（物理隔离） |
| M-AU02 | [M] | 修复范围只改 fix-checklist 列出的文件/行号 |
| M-AU03 | [M] | 发现额外问题 → 记录到 AUDIT_TRACKER，不在当前 commit 混入 |
| S-AU01 | [S] | 审计升级时限：P0=4h, P1=48h, P2=7d |

---

## 七、Spec 规范 (SP)

| ID | 等级 | 规则 |
|:--|:----:|------|
| M-SP01 | [M] | 新功能/修复必须先写 Spec，经人工确认后方可写代码 |
| M-SP02 | [M] | Spec 至少填写 1-5 项 |
| S-SP01 | [S] | Spec 应包含非目标声明（明确不做什么） |

---

## 八、编码规范（摘自多源研究）

| ID | 等级 | 规则 | 来源 | 可检性 |
|:--|:----:|------|------|:------:|
| S-CN01 | [S] | 类名 PascalCase | MS/Google/阿里 | 正则 |
| S-CN02 | [S] | 方法名 lowerCamelCase | MS/Google/阿里 | 正则 |
| S-CN03 | [S] | 常量 UPPER_SNAKE_CASE | MS/Google/阿里 | 正则 |
| S-CN04 | [S] | 禁止魔法值（数字/字符串直接量） | 阿里 | lint |
| S-CN05 | [S] | 方法不超过 50 行 | NASA/Google | 静态分析 |
| S-CN06 | [S] | 圈复杂度 ≤ 15 | NASA | 静态分析 |
| S-CN07 | [S] | 禁止 import * 或通配符导入 | 阿里 | 正则 |
| C-CN01 | [C] | 布尔变量前缀 is/has/can | 百度 Comate | 正则 |
| C-CN02 | [C] | 公共方法必须有 Javadoc | MS/Google | 正则 |

---

## 统计

| 等级 | 数量 | 占比 |
|:----:|:----:|:----:|
| [M] 强制 | 40 | 65% |
| [S] 建议 | 15 | 24% |
| [C] 参考 | 2 | 3% |
| 未分级 | 5 | 8% |
| **总计** | **62** | 100% |

> 规则演进：新增规则 → 先在 [S] 或 [C] 级别运行 → 验证效果 → 升级到 [M] 或废弃。
> 最后更新：2026-04-26 · 治理 v3.5
