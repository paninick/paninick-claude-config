# erp-verify 检查项细则

## 后端 Java

### Domain 类
- 金额字段必须 `BigDecimal`，禁止 `double`/`float`
- 必填字段加 `@NotNull`（对象）或 `@NotBlank`（字符串）
- 枚举字段加 `@Pattern` 或自定义校验

### Mapper XML
- `<update>` 语句必须用 `<set>` 标签，避免末尾逗号 bug
- `<insert>` 批量插入检查 `useGeneratedKeys="true"`
- 禁止 `SELECT *`，必须列出字段名

### Service
- 错误码在 `DemoErrorCode.java` 定义，范围 1000-9999
- 日志用 `DemoLogUtil`，禁止 `System.out.println` / `e.printStackTrace()`
- 事务方法加 `@Transactional`，只读查询加 `@Transactional(readOnly=true)`

### Controller
- 接口路径格式：`/erp/{module}/`
- 返回值统一用 `AjaxResult` 或 `TableDataInfo`
- 权限注解 `@PreAuthorize("@ss.hasPermi('erp:{module}:{action}')")`

---

## 前端 Vue

### 组件
- 文件名和组件名 PascalCase（如 `LossControl.vue`）
- 表单字段加 `:rules` 校验，必填项 `required: true`
- 金额展示用过滤器或 `toFixed(2)`，不显示原始 BigDecimal 字符串

### API 文件
- 每个模块对应 `src/api/erp/{module}.js`
- 函数命名：`list{Module}` / `get{Module}` / `add{Module}` / `update{Module}` / `del{Module}`

---

## SQL 迁移脚本

### 命名规范
- 格式：`phase{N}_{描述}.sql`
- 放在 `RuoYi-Vue/sql/` 目录

### 内容规范
- 字段新增用 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
- 禁止修改已有脚本，只新增
- 字典数据同步插入 `sys_dict_type` + `sys_dict_data`
- 执行完后更新 `sql/README.md` 顺序说明

---

## 架构约束

- 禁止修改 `ruoyi-framework/` 下任何文件
- 禁止硬编码数据库密码、密钥等敏感配置
- 新业务模块放 `ruoyi-demo/`，不新建顶级 module
