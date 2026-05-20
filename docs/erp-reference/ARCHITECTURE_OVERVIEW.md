# 项目架构总览 — 针织服装工贸一体 ERP

> 版本：2026-05-04 | 面向新加入开发者，快速建立系统全貌认知。

---

## 一、系统全景

```
┌─────────────────────────────────────────────────────────────────┐
│                         浏览器 / 客户端                          │
│                                                                 │
│   ERP-UI-2 (React 19 + Vite 6 + TailwindCSS 4)                 │
│   端口 3000 | 唯一主前端 | 100+ 路由 | 三主题 (jtech/google/night) │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/JSON  (axios, /api/* 代理到 8080)
┌────────────────────────▼────────────────────────────────────────┐
│                  RuoYi-Vue 后端 (Spring Boot 3)                  │
│   端口 8080 | 65 Controller | RBAC + JWT | MyBatis + XML Mapper  │
│                                                                 │
│   ruoyi-admin    ← 主模块，含所有 ERP Controller                  │
│   ruoyi-system   ← 系统服务（用户/角色/菜单/字典）                  │
│   ruoyi-framework← 安全框架（JWT 过滤器、权限注解）                 │
│   ruoyi-common   ← 公共工具（分页、响应体、异常）                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ JDBC / MyBatis
┌────────────────────────▼────────────────────────────────────────┐
│   MySQL 8.x  (数据库 ry-vue)                                     │
│   Redis 6+   (Session / Token 缓存)                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、技术栈速查

| 层 | 技术 | 关键版本 | 备注 |
|---|---|---|---|
| 前端框架 | React | 19 | Concurrent Mode |
| 构建工具 | Vite | 6 | HMR 极快 |
| 样式 | TailwindCSS | 4 | `@theme` 设计 token |
| 动画 | framer-motion | — | AnimatePresence + spring |
| 状态管理 | Zustand | — | 轻量，无 Redux 样板 |
| 路由 | React Router | 7 | createBrowserRouter |
| 国际化 | i18next | — | 中文 / 日文双语 |
| HTTP | axios | — | 统一拦截器 + token 注入 |
| 后端框架 | Spring Boot | 3.x | JDK 17 必须 |
| 持久层 | MyBatis | — | XML Mapper，无 JPA |
| 权限 | RuoYi RBAC | — | `@PreAuthorize("@ss.hasPermi('...')")` |
| 认证 | JWT | — | 环境变量 `JWT_SECRET` 注入 |
| 数据库 | MySQL | 8.0.x | 数据库名 `ry-vue` |
| 缓存 | Redis | 6+ | Token 黑名单 + 字典缓存 |

---

## 三、业务单据编号继承链

这是整个系统最核心的数据关联关系。所有单据通过编号向上追溯到款号。

```
styleCode（款号档案）
  └── salesNo（销售订单）
        ├── techNo（样衣技术通知）
        │     └── bomVersion（BOM 版本）
        ├── noticeNo（打样通知）
        └── planNo（生产计划单号）
              ├── purchaseNo（采购单号）
              ├── outsourceNo（外协单号）
              └── jobNo（生产单号）
                    └── processCardNo（工序卡号）
                          └── inspectionNo（检验单号）
                                └── shipmentNo（出货单号）
```

**实际意义**：任何一张单据都能向上追溯到销售订单和款号，向下追溯到出货记录。这是"全链穿透"的数据基础。

---

## 四、业务域划分与 Controller 对应

### 4.1 主数据域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 款号档案 | StyleController | `/style` | `t_erp_style` |
| 客户 | CustomerController | `/customer` | `t_erp_customer` |
| 客户模板 | CustomerTemplateController | `/customer/customer-template` | `t_erp_customer_template` |
| 供应商 | SupplierController | `/supplier` | `t_erp_supplier` |
| 员工 | EmployeeController | `/employee` | `t_erp_employee` |
| 仓库 | WarehouseController | `/warehouse` | `t_erp_warehouse` |
| 主材料 | MainMaterialController | `/material/main` | `t_erp_material_main` |
| 辅料 | AuxiliaryMaterialController | `/material/auxiliary` | `t_erp_material_auxiliary` |
| 材料 SKU | MaterialSkuController | `/masterdata/material-sku` | `t_erp_material_sku` |
| 标准色 | StandardColorController | `/masterdata/standard-color` | `t_erp_standard_color` |
| 单位换算 | UnitConversionController | `/masterdata/unit-conversion` | `t_erp_unit_conversion` |
| 工序定义 | ProcessDefController | `/production/process-def` | `t_erp_process_def` |
| 工艺路线 | ProcessRouteController | `/production/process` | `t_erp_process_route` |
| 工序价格 | ProcessPriceController | `/masterdata/process-price` | `t_erp_process_price` |
| 损耗矩阵 | ProcessLossMatrixController | `/masterdata/process-loss-matrix` | `t_erp_process_loss_matrix` |

### 4.2 销售域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 销售订单 | SalesOrderController | `/sales/order` | `t_erp_sales_order` |
| 销售明细 | SalesItemController | `/sales/sales-item` | `t_erp_sales_item` |
| 打样通知 | ProofingNoticeController | `/sales/proofing-notice` | `t_erp_proofing_notice` |
| 样衣技术 | SampleTechController | `/sales/tech` | `t_erp_sample_tech` |
| 变更单 | ChangeOrderController | `/change/order` | `t_erp_change_order` |

### 4.3 计划与生产域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 生产计划 | ProducePlanController | `/production/plan` | `t_erp_produce_plan` |
| 计划服装明细 | PlanClothesController | `/production/plan-clothes` | `t_erp_plan_clothes` |
| 计划物料明细 | PlanMaterialController | `/production/plan-material` | `t_erp_plan_material` |
| 生产单 | ProduceJobController | `/production/job` | `t_erp_produce_job` |
| 工序报工 | JobProcessController | `/production/job-process` | `t_erp_job_process` |
| 报工日志 | ReportLogController | `/production/report-log` | `t_erp_report_log` |
| 物料退料 | MaterialReturnController | `/production/material-return` | `t_erp_material_return` |
| 生产看板 | KanbanController | `/production/kanban` | — (聚合查询) |
| 款号进度 | StyleProgressController | `/production/style-progress` | — (聚合查询) |
| 工作中心 | WorkCenterController | `/production/work-center` | `t_erp_work_center` |
| 车间产能 | WorkshopCapacityController | `/production/workshop-capacity` | `t_erp_workshop_capacity` |
| 班组任务池 | TeamTaskPoolController | `/production/team-task-pool` | `t_erp_team_task_pool` |

### 4.4 采购与外协域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 采购单 | PurchaseController | `/purchase` | `t_erp_purchase` |
| 外协单 | OutsourceController | `/outsource` | `t_erp_outsource` |

### 4.5 质检域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 检验单 | QualityInspectionController | `/quality/inspection` | `t_erp_quality_inspection` |
| 检品预约 | InspectionBookingController | `/quality/inspection-booking` | `t_erp_inspection_booking` |
| 日单放行 | JapanReleaseController | `/quality/japan-release` | `t_erp_japan_release` |
| 缺陷记录 | DefectController | `/quality/defect` | `t_erp_defect` |
| QC 缺陷 | QcDefectController | `/quality/qc-defect` | `t_erp_qc_defect` |
| 控制计划 | ControlPlanController | `/quality/control-plan` | `t_erp_control_plan` |
| 产品追溯 | ProductTraceController | `/quality/product-trace` | — (聚合查询) |
| 异常池 | BizAbnormalController | `/biz/abnormal` | `t_erp_biz_abnormal` |

### 4.6 仓储域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 入库单 | StockInController | `/inventory/stock-in` | `t_erp_stock_in` |
| 出库单 | StockOutController | `/inventory/stock-out` | `t_erp_stock_out` |
| 库存台账 | InventoryController | `/inventory/list` | `t_erp_inventory` |
| 库存日志 | StockLogController | `/inventory/stock-log` | `t_erp_stock_log` |
| 物料批次 | MaterialBatchController | `/inventory/material-batch` | `t_erp_material_batch` |
| 物料消耗 | MaterialConsumeController | `/inventory/material-consume` | `t_erp_material_consume` |
| 产品序列号 | ProductSerialController | `/inventory/product-serial` | `t_erp_product_serial` |
| 出货单 | ShipmentController | `/inventory/shipment` | `t_erp_shipment` |
| 仓库区域 | WarehouseAreaController | `/warehouse/warehouse-area` | `t_erp_warehouse_area` |
| 仓库位置 | WarehouseLocationController | `/warehouse/location` | `t_erp_warehouse_location` |

### 4.7 财务域

| 模块 | Controller | 前端路由 | 核心表 |
|---|---|---|---|
| 发票 | InvoiceController | `/finance/invoice` | `t_erp_invoice` |
| 企业发票 | CorpInvoiceController | `/finance/corp-invoice` | `t_erp_corp_invoice` |
| 计件工资 | PiecewageController | `/piecewage` | `t_erp_piecewage` |
| 成本汇总 | CostSummaryController | `/finance/cost-summary` | `t_erp_cost_summary` |
| 渠道结算 | ChannelSettlementController | `/finance/channel-settlement` | `t_erp_channel_settlement` |
| 渠道退货 | ChannelRefundController | `/finance/channel-refund` | `t_erp_channel_refund` |

### 4.8 系统域

| 模块 | 前端路由 | 说明 |
|---|---|---|
| 用户管理 | `/system/user` | RuoYi 内置 |
| 角色管理 | `/system/role` | RuoYi 内置 |
| 字典管理 | `/system/dict` | RuoYi 内置 |
| 组织架构 | `/system/org` | 分厂/车间/班组/工位 |
| 公司上下文 | `/system/company-context` | 多工厂映射 |
| 审批日志 | `/system/approvallog` | 统一审批记录 |
| 数据导入 | `/system/data-import` | Excel 批量导入 |

---

## 五、端到端业务流

```
① 接单
   客户档案 → 款号档案 → 销售订单（锁定客户/款号/数量/交期）

② 技术准备
   销售订单 → 打样通知 → 样衣技术通知 → BOM 版本冻结
                                        → 工艺路线确认

③ 计划下达
   销售订单 → 生产计划（锁定工厂/排期）
              ├── 计划服装明细（款色码数）
              └── 计划物料明细（用料清单）

④ 采购 / 外协
   生产计划 → 采购单（主辅料采购）
            → 外协单（外发加工）

⑤ 生产执行
   生产计划 → 生产单 → 工序卡（工序报工）
                      → 物料消耗记录
                      → 报工日志

⑥ 质量检验
   生产单 → 检验单（首件/过程/成品）
           → 缺陷记录
           → 日单检品预约 → 日单放行

⑦ 仓储出货
   质量放行 → 入库单 → 库存台账
   销售订单 → 出库单 → 出货单（含箱唛/物流追踪）

⑧ 财务结算
   出货单 → 发票
   工序报工 → 计件工资
   生产单 → 成本汇总
```

---

## 六、数据库规范

### 6.1 表命名

| 前缀 | 用途 | 示例 |
|---|---|---|
| `t_erp_` | 所有 ERP 业务表 | `t_erp_sales_order` |
| `sys_` | RuoYi 系统表（禁止修改结构） | `sys_user`, `sys_menu` |
| `qrtz_` | Quartz 定时任务表 | `qrtz_job_details` |

### 6.2 通用字段约定

每张 ERP 业务表必须包含：

```sql
id          BIGINT PRIMARY KEY AUTO_INCREMENT,
create_by   VARCHAR(64),
create_time DATETIME,
update_by   VARCHAR(64),
update_time DATETIME,
del_flag    CHAR(1) DEFAULT '0'   -- '0'=正常, '2'=删除（逻辑删除）
```

审批类单据额外包含：

```sql
status          VARCHAR(20)   -- 见字典 erp_xxx_status
audit_status    VARCHAR(20)   -- 见字典 erp_xxx_audit_status
submit_by       VARCHAR(64),
submit_time     DATETIME,
approve_by      VARCHAR(64),
approve_time    DATETIME,
reject_reason   VARCHAR(500)
```

### 6.3 字典命名规范

| 用途 | 命名模式 | 示例值 |
|---|---|---|
| 单据状态 | `erp_xxx_status` | `draft/submitted/approved/rejected` |
| 审批结果 | `erp_xxx_audit_status` | `pending/pass/reject` |
| 类型枚举 | `erp_xxx_type` | `normal/urgent/sample` |
| 结果枚举 | `erp_xxx_result` | `pass/fail/conditional` |

### 6.4 SQL 脚本执行顺序

```
sql/ry_20210924.sql     # RuoYi 基础表（首次初始化）
sql/quartz.sql          # 定时任务表
sql/phase01_*.sql       # ERP 基础主数据
sql/phase02_*.sql
...
sql/phase{N}_*.sql      # 按编号顺序执行，不可跳过
```

新增字段必须写新的 `phase{N+1}_*.sql`，使用幂等写法（`IF NOT EXISTS` 检查）。

---

## 七、后端 API 规范

### 7.1 URL 模式

```
GET    /erp/{module}/list          # 分页列表
GET    /erp/{module}/{id}          # 详情
POST   /erp/{module}               # 新增
PUT    /erp/{module}               # 更新
DELETE /erp/{module}/{ids}         # 删除（逗号分隔多 ID）

# 业务动词接口（审批流）
PUT    /erp/{module}/submit/{id}   # 提交审批
PUT    /erp/{module}/approve/{id}  # 审核通过
PUT    /erp/{module}/reject/{id}   # 驳回
```

### 7.2 权限注解

```java
@PreAuthorize("@ss.hasPermi('erp:salesOrder:list')")
@PreAuthorize("@ss.hasPermi('erp:salesOrder:add')")
@PreAuthorize("@ss.hasPermi('erp:salesOrder:edit')")
@PreAuthorize("@ss.hasPermi('erp:salesOrder:remove')")
```

权限标识格式：`erp:{模块驼峰}:{操作}`，操作固定为 `list/add/edit/remove`。

### 7.3 统一响应体

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": { ... }
}
```

分页列表额外包含：

```json
{
  "code": 200,
  "rows": [...],
  "total": 100
}
```

---

## 八、前端架构

### 8.1 目录结构

```
src/
├── api/           # 每个模块一个文件，与后端路由 1:1 对应
├── components/
│   ├── layout/    # MainLayout, Sidebar, Header
│   └── ui/        # CrudPage, BaseTable, BaseModal, SearchForm,
│                  # GenericForm, Pagination, Toast, ConfirmDialog
├── hooks/         # useCrud, useDictOptions, useApproval
├── i18n/          # zh.ts, ja.ts 双语翻译
├── pages/         # 按业务域分目录，与路由对应
├── stores/        # authStore, appStore (Zustand)
├── utils/         # request.ts (axios), documentTitle.ts
└── router.tsx     # 所有路由定义
```

### 8.2 核心组件模式

**CrudPage** — 标准增删改查页面容器：
- 内置搜索栏、操作按钮栏、表格、分页
- 通过 `useCrud` hook 管理状态

**GenericForm** — 通用表单：
- 字段配置驱动，支持 input/select/date/textarea
- 与 `useDictOptions` 联动加载字典选项

**BaseTable** — 数据表格：
- 行级 stagger 动画（framer-motion）
- 内置选择列、操作列

**BaseModal** — 弹窗：
- Spring 动画（stiffness 420, damping 32）
- 主题感知（jtech/google/night）

### 8.3 主题系统

三套主题通过 `appStore.uiTheme` 切换，持久化到 localStorage：

| 主题 | 背景 | 侧边栏 | 主色 | 适用场景 |
|---|---|---|---|---|
| `jtech` | 暖米色 `#f0ede6` | 深海军蓝 `#1a2035` | 琥珀 `#f59e0b` | 默认，日系科技感 |
| `google` | 浅蓝白 `#f7faff` | 白色玻璃 | 蓝 `#4285f4` | 简洁商务 |
| `night` | 深夜蓝 `#06101d` | 深夜蓝 | 琥珀 `#f59e0b` | 夜间使用 |

### 8.4 国际化

翻译文件位于 `src/i18n/zh.ts` 和 `src/i18n/ja.ts`。
语言选择持久化到 `localStorage`，key 为 `LANGUAGE_STORAGE_KEY`。

---

## 九、角色体系

| role_id | role_key | 角色名 | 主要权限域 |
|---|---|---|---|
| 1 | admin | 超级管理员 | 全部 |
| 100 | erp_produce_manager | 生产主管/厂长 | 生产、质检、仓储 |
| 101 | erp_technician | 技术员/工艺员 | 工艺、BOM、样衣 |
| 102 | erp_salesperson | 销售/跟单/单证 | 销售、客户、出货 |
| 103 | erp_finance | 财务/成本会计 | 财务、发票、工资 |
| 104 | erp_warehouse_admin | 仓库主管/仓管员 | 仓储、库存 |
| 105-115 | (待新增) | 采购员、品质、外协、PMC、车间主任、操作工等 | — |

---

## 十、审批流设计原则

只在**会造成交期、质量、成本责任锁定**的节点做审批，避免过度流程化：

| 审批节点 | 锁定内容 | 对应单据 |
|---|---|---|
| 销售订单生效 | 客户/款号/数量/交期 | `t_erp_sales_order` |
| BOM/工艺冻结 | 生产依据 | `t_erp_sample_tech` |
| 计划下达 | 工厂/排期 | `t_erp_produce_plan` |
| 报工数量复核 | 计件工资基数 | `t_erp_job_process` |
| 质量放行 | 日单检品放行 | `t_erp_japan_release` |
| 成本/结算确认 | 财务结算依据 | `t_erp_cost_summary` |

审批日志统一写入 `t_erp_approval_log`，前端通过 `ApprovalTimeline` 组件展示。

---

## 十一、多工厂支持

系统支持多工厂（柬埔寨工厂 + 国内工厂）。工厂维度通过以下机制实现：

- `sys_user` 扩展字段 `factory_id` — 用户归属工厂
- `t_erp_company_context` — 公司上下文映射表
- 所有业务单据含 `factory_id` 字段，查询时自动过滤

---

## 十二、打印 / 扫码

以下单据有独立打印页面（`/print/:id` 路由）：

- 销售订单：`/sales/order/print/:id`
- 生产计划：`/production/plan/print/:id`
- 生产单：`/production/job/print/:id`
- 检验单：`/quality/inspection/print/:id`

打印页面不含导航栏，直接调用 `window.print()`。
扫码功能通过 `DocumentCodeBoard` 和 `PrintCodeStrip` 组件实现二维码生成。

---

## 十三、P0 上线前必须完成

```
□ ReportController 补全 @PreAuthorize 注解（当前全部接口无权限保护）
□ JWT_SECRET 替换为 32+ 字符随机串（当前使用弱默认值）
□ 新增 11 个核心角色（role_id 105-115）
□ 角色菜单权限配置（sys_role_menu 数据）
□ 所有 phase*.sql 按顺序执行完毕
□ Redis 持久化开启（AOF 或 RDB）
□ MySQL 定期备份配置
```

---

*更多细节参见：*
- `D:\ERP\docs\DEVOPS_RUNBOOK.md` — 启动、故障排查、运维操作
- `D:\ERP\ERP_MASTER_PLAN.md` — P0-P5 完整落地规划
- `D:\ERP\docs\02-architecture-and-key-system.md` — 早期架构决策记录
