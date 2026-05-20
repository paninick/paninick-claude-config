# 已知故障知识库

> 每次遇到不确定的技术决策时，先查本文。本文是决策表（非叙事），触发条件 → 检查项 → 历史案例。
> 最后更新：2026-04-26 | 来源：审计报告 + 项目文档 + 官方文档 + Web 搜索

---

## 一、MyBatis Mapper XML

### 1.1 SQL 注入防护

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 每次写动态 SQL 条件 | 用户输入值用 `#{}`，禁止 `${}` | Phase 29 审计：FinInvoiceMapper.xml:45 / QcInspectionMapper.xml:54 遗留 `${params.factoryDataScope}`（框架级，非用户输入） |
| 必须用 `${}` 时（动态表名/列名/ORDER BY） | 参数必须来自白名单枚举，不能直接接收前端输入 | — |
| LIKE 模糊查询 | 用 `CONCAT('%', #{keyword}, '%')`，不用 `'%${keyword}%'` | — |
| IN 查询 | 用 `<foreach collection="list" item="id">#{id}</foreach>`，不用 `${ids}` | — |

**官方参考**：[MyBatis #{} vs ${}](https://mybatis.org/mybatis-3/sqlmap-xml.html#Parameters) · `#{}` = PreparedStatement 占位符（安全），`${}` = 字符串拼接（需白名单）

### 1.2 JOIN 表名验证

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 每次新增 SQL 中 JOIN 或 FROM 新表 | `grep -r "CREATE TABLE.*表名" sql/` 确认表存在 | **Phase 29 Fix-1**：`t_erp_piece_price` 不存在，正确表为 `t_erp_process_def` 或 `t_erp_employee_process_price` |

### 1.3 parameterType

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 新写 Mapper XML | `parameterType` 可省略（MyBatis 3 自动推断）；`resultType`/`resultMap` 不可省略 | **Wave 4 C4**：`deleteStockInByIds` 的 `parameterType="String"` 写错（应为 `Long[]` 或不写） |

### 1.4 REPLACE INTO 禁止

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 需要"存在则更新，不存在则插入" | **禁止** `REPLACE INTO`（先 DELETE 再 INSERT，导致：未指定字段重置为默认值、外键级联删除、自增 ID 跳跃）。用 `INSERT ... ON DUPLICATE KEY UPDATE` | **Wave 4 C2**：`StockInMapper.xml` REPLACE INTO 改为 ON DUPLICATE KEY UPDATE |

**官方参考**：[MySQL REPLACE vs INSERT ON DUPLICATE KEY](https://dev.mysql.com/doc/refman/8.0/en/replace.html)

---

## 二、Spring Boot 事务

### 2.1 @Transactional 覆盖

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 方法内部执行 ≥2 次不同表的 INSERT/UPDATE/DELETE | 必须加 `@Transactional(rollbackFor = Exception.class)` | **Phase 29 Fix-2**：`insertProduceMaterialConsume` 先 insert consume → 再 insert abnormal pool，无事务 → consume 入库但异常池丢失 |
| 方法被 Controller 直接调用（非内部调用） | 必须加 `@Transactional`，Controller 调用链无事务保护 | **Wave 4 I4**：`ErpCostSummaryServiceImpl` 缺事务 |

### 2.2 事务失效陷阱

| 触发条件 | 检查项 |
|----------|--------|
| 同类中方法互相调用 | 事务通过 AOP 代理生效，`this.method()` 绕过代理 → 事务失效。需要将方法移到另一个 Bean 或用 `AopContext.currentProxy()` |
| 方法非 public | Spring AOP 默认只代理 public 方法 |
| 异常被 try-catch 吞掉 | 捕获异常后未重新抛出 → 事务不回滚 |
| 抛出 Checked Exception 但未配置 `rollbackFor` | Spring 默认只对 RuntimeException 回滚，Checked Exception 不回滚 |

**官方参考**：[Spring @Transactional](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

---

## 三、MySQL DDL 幂等性

### 3.1 ALTER TABLE 幂等

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 写 SQL 迁移脚本（ADD COLUMN/ADD INDEX） | MySQL 不支持 `ADD COLUMN IF NOT EXISTS`。必须用 `INFORMATION_SCHEMA` 检查 + PREPARED STATEMENT 或调用存储过程 `sp_erp_add_column` | **Phase 29 Fix-10**：`phase29_material_consume_stockout_link.sql` 用了非标准语法 `ADD COLUMN IF NOT EXISTS` |

```sql
-- 正确写法（项目标准）
SET @col_exists := (SELECT COUNT(1) FROM information_schema.COLUMNS
    WHERE table_schema = DATABASE() AND table_name = '表名' AND column_name = '列名');
SET @sql := IF(@col_exists = 0, 'ALTER TABLE 表名 ADD COLUMN 列名 类型 COMMENT "备注"', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
```

### 3.2 索引类型选择

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 需要防止重复插入 | 用 `UNIQUE INDEX`，非普通 `INDEX`。普通索引不阻止重复 | **Phase 29 Fix-3**：`stock_out_item_id` 创建了普通索引 `idx_erp_pmc_stock_out_item`，无法防止并发重复记录 |

---

## 四、RuoYi-Vue 框架边界

### 4.1 模块边界

| 触发条件 | 检查项 |
|----------|--------|
| 修改代码 | `ruoyi-framework/` **禁止修改**。`ruoyi-common/` 仅新增。业务代码一律在 `ruoyi-admin/src/main/java/com/ruoyi/erp/` |

**来源**：[docs/06 §7](06-ruoyi-framework-introduction.md)

### 4.2 权限注解

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 每次新增 Controller 端点 | 必须加 `@PreAuthorize("@ss.hasPermi('erp:模块:动作')")` | Phase 29 审计确认 4 个新端点均已有权限 |

### 4.3 框架版本与已知 CVE

| CVE | 影响 | 本项目状态 |
|-----|------|-----------|
| CVE-2025-10384 | RuoYi ≤ 4.8.1 角色越权 | ⚠️ 需确认版本 |
| CVE-2025-10989 | RuoYi ≤ 4.8.1 权限分配错误 | ⚠️ 需确认版本 |
| CVE-2025-2040 | ruoyi-vue-pro ≤ 2.4.1 模板注入 | 本项目非 Pro 版本 |

**来源**：[RuoYi-Vue Common Errors & Best Practices (WebSearch 2026-04-26)]

---

## 五、Domain / Entity 层

### 5.1 toString() 完整性

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 给 Domain 类新增字段后 | 必须在 `toString()` 的 `ToStringBuilder` 中追加 `.append("field", field)` | **Phase 29 Fix-7**（已修）：`ProduceMaterialConsume` 缺 `unitCost/costAmount/eventSource`。**Wave 4 C1**（已修）：4 个 domain 补字段 |

### 5.2 @Excel 注解

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 给 Domain 新增字段 | 确认是否需要 `@Excel(name = "...")` 注解支持导出 | **Phase 29 Fix-5**：StockOutItem 缺 8 个 @Excel，StockInItem 缺 1 个 |

### 5.3 Lombok

| 触发条件 | 检查项 |
|----------|--------|
| 使用 `@Builder` + `@Accessors(chain = true)` | `@Builder` 覆盖全局 `chain=true`，setter 返回 void。需同时加 `@Accessors(chain = true)` |
| 加 Java domain 字段后 | 必须 `mvn compile` 再 commit（Lombok 生成的方法签名可能被 MyBatis 缓存） |

---

## 六、项目约定

### 6.1 编译验证

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 修改 Java 文件后 | `mvn compile -f ruoyi-admin/pom.xml` 必须通过 |

### 6.2 日志与注释

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 新增 Service 方法 | 接口方法补 Javadoc（至少 `@param` + `@return`） | **Phase 29 Fix-6**：`syncByStockOut`/`bindToJobProcess` 无注释 |
| Controller @Log | title 使用中文描述（本项目风格） | **Phase 29 Fix-9**：@Log title 为英文 "StockInItem" 应改为中文 |
| 异常消息 | 统一中文，避免中英混用 | **Phase 29 Fix-8**（已修） |

### 6.3 SQL 脚本

| 触发条件 | 检查项 |
|----------|--------|
| 新增 SQL 迁移文件 | 命名 `phase{编号}_{描述}.sql`，放 `RuoYi-Vue/sql/`。用幂等 PREPARED STATEMENT 风格。不改动已有脚本 |

---

## 七、流程 / 治理

### 7.1 审计修复闭环

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 收到审计报告后 | **必须先读** `docs/audit/AUDIT_TRACKER.md`，检查 P0 OPEN 项，不能跳过直接开始新任务 | **2026-04-26**：Phase 29 三份审计报告被跳过，AI 转而处理 Wave 4 问题并声称"全部通过" |
| 修复完成后 | **禁止自验自宣告**。必须调用独立 skill（review / differential-review）验证，更新 AUDIT_TRACKER.md 的 fix# 状态 |
| pre-commit hook 阻断时 | **禁止说"缓存状态"或绕过**。必须：读阻断消息→找到引用文件→修复根因→重新运行门禁→通过后提交 | **2026-04-26**：AI 看到 pre-commit 阻断 P0 未修复，说"缓存状态"就继续 commit |
| 修复审计问题时 | diff 范围只能含 fix-checklist 列出的文件/行号。禁止 scope creep（顺手加校验注解、整理 import、改注释语言） | **2026-04-26**：Fix-5 只要求恢复 @Excel，但提交中加了 10+ 个 @NotNull/@NotBlank |
| `git commit` 之前 | `git diff --cached` 自查：重复 import？多余空行？scope creep？ | **2026-04-26**：重复 `import @Transactional` 留在提交中 |
| commit 后 | **禁止**连续提交不等审查。commit 后必须输出摘要 + 等待用户/auditor 明确回复"通过"，审查反馈指出的问题在当前 commit 之上修复。`10/10 验证通过` ≠ 代码质量通过 | **2026-04-26**：executor 在 12 分钟内连续提交 3 个 commit，审查反馈追不上，两个质量问题（重复 import + @NotNull scope creep）遗留未修 |
| 修复审计问题时 | **禁止**新增 fix-checklist 未要求的注解类型（`@NotNull`/`@NotBlank`/`@NotEmpty`）。这不是"顺手加校验"，是 P0 契约变更：原来允许 null → 变为 400 Bad Request，所有未传该字段的调用方全部中断 | **2026-04-26**：Fix-5 只要求恢复 @Excel，executor 在 StockOutItem.java 中混杂 8 个 @NotNull/@NotBlank，且在 d8cdc245 中扩散到 ErpEmployee.java |
| 开始新任务时 | **No Spec No Code**：必须填写 `docs/templates/task-spec-template.md`，经人工确认后方可写代码。跳过 Spec 直接生成 → 可用率 <30%。Spec 是真相来源，代码服务于 Spec | **2026-04-26**：TD-12/13/14 无 Spec 直接编码，架构模式靠 AI 自行推断，导致与已有模式不一致 |
| 新功能设计时 | **模式复用优先**：必须先找到项目中已有的类似实现作为参考。找不到 → 先讨论架构，再写代码。禁止每次另起炉灶 | **四阶段崩塌模型**：每次都做局部最优 → 两个月后五种不同实现方式共存，无法判断哪个是正统 |
| 收到任何任务时 | **IntentGate 意图分类**：先判断意图类别（只读审查/定向修复/新功能开发/代码重构）再行动。无法确定 → 停下确认。禁止把"审查"当作"修复"执行 | **prompt 反模式研究**：AI 默认把所有任务理解为"写代码"，忽略"只看不碰"的指令 |
| `git add` 之前 | **PostToolUse 质量自检**（6 项）：注解类型存在性、import 去重、变更来源校验、不完整实现检查、注释代码检查、硬编码检查 | pre-commit 只检查"要提交的东西"，不检查"刚写完还没 add 的东西"。对标 ECC PostToolUse hook |
| 会话结束时 | **禁止不写交接直接结束**。必须更新 `docs/session-handoff.md`：当前任务、遗留问题、下一步。下次会话 CLAUDE.md 门禁第 9 步读取 | **跨会话架构漂移**：AI 每次新会话从零理解上下文，缺乏交接导致模式不一致。对标 Claude Code AutoDream + ECC SessionStart 记忆恢复 |

### 7.2 部署常见坑

| 现象 | 原因 | 处置 |
|------|------|------|
| 启动报 `Unable to find @SpringBootConfiguration` | JDK < 17 | 装 JDK 17 + 配 `JAVA_HOME` |
| 登录后立刻 401 | Redis 连不通 | 检查 `application.yml` + `redis-cli ping` |
| 页面白屏 | Nginx `try_files` 缺 `/index.html` | SPA 兜底规则 |
| Druid 监控页打不开 | Druid 账号默认值 | 改环境变量 `DRUID_PASSWORD` |

**来源**：[docs/06 §8](06-ruoyi-framework-introduction.md)

---

## 八、审计快速检查表

每次编写或审查代码时，按以下顺序自检：

```
□ 新增 SQL JOIN 了不存在的表？
□ 用户输入用了 ${} 而非 #{}？
□ 多表写操作有 @Transactional(rollbackFor = Exception.class)？
□ DDL 是否幂等（INFORMATION_SCHEMA 检查）？
□ 需要防重复的地方用了 UNIQUE INDEX（不是普通 INDEX）？
□ 新增字段后 toString() 和 @Excel 是否补齐？
□ Controller 端点有 @PreAuthorize？
□ mvn compile 通过？
□ 未提交代码中存在 OPEN P0 审计问题？
□ pre-commit gate 放行？
□ git diff --cached 无重复 import / scope creep？
□ 文件列表与 AUDIT_TRACKER fix-checklist 一致？
□ 新增的注解类型是否已存在于该文件其他字段上？（不存在 → scope creep，撤销）
□ commit 后是否已输出摘要并等待审查反馈？（不等 → 下一 commit 可能把同样错误带入）
□ 新任务开始前是否已填写 Spec 模板并经人工确认？（No Spec No Code）
□ 新功能是否已找到项目中已有的类似实现作为模式参考？
□ 收到任务后是否已做意图分类（只读/修复/开发/重构）？
□ Spec 非目标栏是否已填写"禁止触碰的文件"？
□ git add 前是否执行了 PostToolUse 质量自检（6 项）？
□ 会话结束时是否已更新 session-handoff.md？
```

---

## 九、测试覆盖率

### 9.1 零测试覆盖

| 触发条件 | 检查项 | 历史案例 |
|----------|--------|---------|
| 每次写新 Service/Controller 方法 | 是否补充了集成测试？当前 0 个测试文件，452 个 Java 文件。至少核心审批流（submit/approve/reject）需要集成测试 | **WH-001 (2026-04-27)**：周度健康检查发现全项目零测试覆盖 |

**参考**：Spring Boot Test + `@SpringBootTest` + `@Transactional` 回滚测试数据。

---

## 变更日志

- **2026-04-27 v1.6**：追加 §九 测试覆盖率（WH-001 周度健康检查发现 0 测试文件）+ 审计检查表追加测试检查项。来源：全量 `find test` 扫描。
- **2026-04-26 v1.3**：追加 3 条治理记录：No Spec No Code 门禁、模式复用优先、四阶段崩塌模型。审计快速检查表新增 2 项。治理体系从"刹车"升级为"刹车+方向盘"（v3.0）。配套落地文件：`docs/templates/task-spec-template.md`、`docs/templates/module-claude-template.md`、`ruoyi-admin/.../erp/CLAUDE.md`（模块级试点）。
- **2026-04-26 v1.2**：追加 2 条流程治理记录：commit 后不等审查连续提交、@NotNull/@NotBlank scope creep 定级 P0（契约变更，非风格问题）。审计快速检查表新增 2 项机械可判检查。
- **2026-04-26 v1.1**：追加 3 条流程治理记录：pre-commit 阻断响应、scope creep 禁止、提交前 diff 自查。来源：Phase 29 提交后代码质量审查。
