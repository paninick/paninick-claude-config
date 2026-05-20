# ERP 编码规范

## 后端规范（Spring Boot + MyBatis）

### 硬性规则（违反即阻塞 PR）

1. **禁止修改 ruoyi-framework/**
2. **SQL 注入防护**：用户输入必须用 `#{}`，禁止 `${}`
3. **事务完整性**：多表写操作必须有 `@Transactional(rollbackFor = Exception.class)`
4. **权限控制**：所有 Controller 端点必须有 `@PreAuthorize`
5. **DDL 幂等性**：DDL 脚本必须用 `IF NOT EXISTS`
6. **金额精度**：金额字段必须用 `BigDecimal`，禁止 `float/double`
7. **逻辑删除**：业务数据用 `del_flag` 逻辑删除，禁止物理删除

### 模块结构

```
ruoyi-admin/src/main/java/com/ruoyi/erp/[domain]/
├── domain/
│   └── ErpXxx.java              ← 继承 BaseEntity，含 @Excel 注解
├── mapper/
│   └── ErpXxxMapper.java        ← 继承 BaseMapper
├── service/
│   ├── IErpXxxService.java      ← 接口
│   └── impl/
│       └── ErpXxxServiceImpl.java ← 实现，含业务逻辑
└── controller/
    └── ErpXxxController.java    ← 继承 BaseController，含 @PreAuthorize

ruoyi-admin/src/main/resources/mapper/erp/[domain]/
└── ErpXxxMapper.xml             ← SQL 映射
```

### Controller 规范

```java
@RestController
@RequestMapping("/erp/plan")
public class ErpPlanController extends BaseController {

    @PreAuthorize("@ss.hasPermi('erp:plan:list')")
    @GetMapping("/list")
    public TableDataInfo list(ErpPlanQuery query) {
        startPage();
        List<ErpPlan> list = planService.selectList(query);
        return getDataTable(list);
    }

    @PreAuthorize("@ss.hasPermi('erp:plan:add')")
    @PostMapping
    public AjaxResult add(@Validated @RequestBody ErpPlan plan) {
        return toAjax(planService.insert(plan));
    }

    // 业务动词接口
    @PreAuthorize("@ss.hasPermi('erp:plan:submit')")
    @PutMapping("/{id}/submit")
    public AjaxResult submit(@PathVariable Long id) {
        return toAjax(planService.submit(id));
    }
}
```

### Service 规范

```java
@Service
public class ErpPlanServiceImpl implements IErpPlanService {

    @Transactional(rollbackFor = Exception.class)
    public int createWithRelated(ErpPlan plan) {
        // 多表写操作必须有事务
        int rows = planMapper.insert(plan);
        planDetailMapper.batchInsert(plan.getDetails());
        return rows;
    }
}
```

### Mapper XML 规范

```xml
<!-- 用 #{} 参数化，禁止 ${} 拼接 -->
<select id="selectList" resultType="ErpPlan">
    SELECT * FROM erp_plan
    WHERE del_flag = '0'
    <if test="status != null">AND status = #{status}</if>
    <if test="planNo != null and planNo != ''">AND plan_no LIKE CONCAT('%', #{planNo}, '%')</if>
</select>
```

## 前端规范（React + TypeScript）

### 硬性规则

1. **国际化**：所有用户可见文本用 `t('key')`，禁止硬编码中文
2. **字典值**：通过 `useDictOptions('erp_xxx_status')` 获取，禁止硬编码枚举
3. **类型安全**：禁止 `any` 类型，禁止 `@ts-ignore`
4. **源头字段**：来自上游单据的字段在表单中设为 `disabled`

### 文件结构

```
ERP-UI-2/src/
├── api/erp/[module].ts          ← API 函数，与后端路由 1:1 对应
├── pages/erp/[module]/
│   ├── index.tsx                ← 列表页
│   ├── form.tsx                 ← 表单组件（可选）
│   └── detail.tsx               ← 详情页（可选）
└── locales/
    ├── zh-CN/erp/[module].json  ← 中文翻译
    └── ja-JP/erp/[module].json  ← 日文翻译
```

### API 文件规范

```typescript
// src/api/erp/plan.ts
import request from '@/utils/request';

export const planApi = {
  list: (params: ErpPlanQuery) =>
    request.get<PageResult<ErpPlan>>('/erp/plan/list', { params }),
  
  getById: (id: number) =>
    request.get<ErpPlan>(`/erp/plan/${id}`),
  
  create: (data: ErpPlanForm) =>
    request.post<void>('/erp/plan', data),
  
  update: (id: number, data: ErpPlanForm) =>
    request.put<void>(`/erp/plan/${id}`, data),
  
  submit: (id: number) =>
    request.put<void>(`/erp/plan/${id}/submit`),
  
  delete: (ids: number[]) =>
    request.delete<void>(`/erp/plan/${ids.join(',')}`),
};
```

## 数据库规范（MySQL）

### 表结构规范

```sql
CREATE TABLE IF NOT EXISTS erp_plan (
    id          BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    plan_no     VARCHAR(50) NOT NULL COMMENT '计划单号',
    status      TINYINT NOT NULL DEFAULT 0 COMMENT '状态（0草稿 1已提交 2已审批）',
    factory_id  BIGINT COMMENT '工厂ID',
    -- 业务字段...
    create_by   VARCHAR(64) DEFAULT '' COMMENT '创建者',
    create_time DATETIME COMMENT '创建时间',
    update_by   VARCHAR(64) DEFAULT '' COMMENT '更新者',
    update_time DATETIME COMMENT '更新时间',
    del_flag    CHAR(1) DEFAULT '0' COMMENT '删除标志（0正常 2删除）',
    PRIMARY KEY (id),
    UNIQUE KEY uk_plan_no (plan_no),
    KEY idx_status_create_time (status, create_time)
) ENGINE=InnoDB COMMENT='生产计划';
```

### 字典规范

```sql
-- 字典类型
INSERT INTO sys_dict_type (dict_name, dict_type, status, remark)
VALUES ('计划状态', 'erp_plan_status', '0', '生产计划状态')
ON DUPLICATE KEY UPDATE dict_name = VALUES(dict_name);

-- 字典数据
INSERT INTO sys_dict_data (dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status)
VALUES
(1, '草稿', '0', 'erp_plan_status', '', 'default', 'N', '0'),
(2, '已提交', '1', 'erp_plan_status', '', 'primary', 'N', '0'),
(3, '已审批', '2', 'erp_plan_status', '', 'success', 'N', '0')
ON DUPLICATE KEY UPDATE dict_label = VALUES(dict_label);
```
