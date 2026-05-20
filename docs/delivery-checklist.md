# ERP 模块交付检查点

## 10 步检查点

每个 ERP 模块必须按顺序完成以下 10 个步骤才能声称 DONE：

```
1. dict        补字典数据
2. sql         建表 DDL
3. domain      Domain 类
4. mapper      Mapper 接口 + XML
5. service     Service 接口 + ServiceImpl
6. controller  Controller（含业务动词接口）
7. frontend-api 前端 API 文件
8. frontend-page 前端页面
9. approval    审批流/打印/扫码（如适用）
10. live-verify 生产环境验证
```

## 每步详细要求

### Step 1: dict（字典数据）

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

### Step 2: sql（建表 DDL）

- 必须幂等（`CREATE TABLE IF NOT EXISTS`）
- 必须包含标准审计字段（create_by/create_time/update_by/update_time/del_flag）
- 状态字段用 `TINYINT`
- 金额字段用 `DECIMAL(15,4)`
- 编号字段用 `VARCHAR`

### Step 3: domain（Domain 类）

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class ErpPlan extends BaseEntity {
    @Excel(name = "计划单号")
    private String planNo;
    
    @Excel(name = "状态", readConverterExp = "0=草稿,1=已提交,2=已审批")
    private Integer status;
    
    // 审批字段
    private String approveBy;
    private Date approveTime;
    private String approveRemark;
}
```

### Step 4: mapper（Mapper 接口 + XML）

Mapper XML 必须包含：
- `selectList`（带分页条件）
- `selectById`
- `insert`
- `update`
- `deleteById`（逻辑删除，设 del_flag = '2'）

### Step 5: service（Service 接口 + ServiceImpl）

ServiceImpl 必须包含：
- 业务校验（编号唯一性、状态流转合法性）
- 状态流转方法（submit/approve/reject）
- 多表写操作加 `@Transactional`

### Step 6: controller（Controller）

Controller 必须包含：
- `list` — 分页列表（@PreAuthorize list）
- `getInfo` — 详情（@PreAuthorize query）
- `add` — 新增（@PreAuthorize add）
- `edit` — 修改（@PreAuthorize edit）
- `remove` — 删除（@PreAuthorize remove）
- `submit` — 提交审批（@PreAuthorize submit，如适用）
- `approve` — 审批通过（@PreAuthorize approve，如适用）
- `reject` — 审批拒绝（@PreAuthorize approve，如适用）

### Step 7: frontend-api（前端 API 文件）

```typescript
// src/api/erp/plan.ts
import request from '@/utils/request';

export const planApi = {
  list: (params: PlanQuery) => request.get('/erp/plan/list', { params }),
  getInfo: (planId: number) => request.get(`/erp/plan/${planId}`),
  add: (data: PlanForm) => request.post('/erp/plan', data),
  edit: (data: PlanForm) => request.put('/erp/plan', data),
  remove: (planIds: number[]) => request.delete(`/erp/plan/${planIds.join(',')}`),
  submit: (planId: number) => request.put(`/erp/plan/submit/${planId}`),
  approve: (data: ApproveForm) => request.put('/erp/plan/approve', data),
};
```

### Step 8: frontend-page（前端页面）

页面必须包含：
- 列表视图（分页、搜索、筛选）
- 表单视图（新增/编辑，含验证）
- 状态标签（颜色区分状态）
- 操作按钮（含权限控制）
- 源头只读字段（来自上游单据的字段设为 disabled）

### Step 9: approval（审批流/打印/扫码）

仅在以下情况适用：
- 模块有审批节点（销售订单、BOM 冻结、计划下达等）
- 模块需要打印（工序卡、出货单等）
- 模块需要扫码（报工、检验等）

### Step 10: live-verify（生产环境验证）

验证清单：
- [ ] 使用真实数据创建记录
- [ ] 验证状态流转（草稿→提交→审批）
- [ ] 验证权限控制（不同角色看到不同操作）
- [ ] 验证数据继承（下游单据正确继承上游字段）
- [ ] 验证逻辑删除（删除后不在列表显示）

## DONE 定义

只有同时满足以下条件才能声称模块 DONE：

- [x] 已实现（10 步检查点全部完成）
- [x] 已补 Spec（`docs/specs/[module]-spec.md` 存在）
- [x] 已独立验证（live verify 通过，有截图或记录）
- [x] tracker 已同步（`docs/audit/AUDIT_TRACKER.md` 已更新）
- [x] handoff 已更新（`docs/session-handoff.md` 已更新）
