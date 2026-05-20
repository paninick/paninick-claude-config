# ERP Agent 名册

## Tier 1 — 领导层（Opus）

| Agent | 角色 | 职责 | 使用场景 |
|-------|------|------|---------|
| `erp-cto` | 技术总监 | 架构决策、技术选型、跨系统冲突 | 架构级决策、技术评估 |
| `erp-pm` | 项目经理 | Sprint 计划、里程碑、风险管理 | 规划工作、跟踪进度 |
| `erp-product-owner` | 产品负责人 | 业务需求、优先级、验收标准 | 澄清业务规则、定义功能范围 |

## Tier 2 — 部门负责人（Sonnet）

| Agent | 角色 | 职责 | 使用场景 |
|-------|------|------|---------|
| `erp-lead-backend` | 后端主程 | Spring Boot/MyBatis 架构、代码审查 | 代码审查、API 设计、重构策略 |
| `erp-lead-frontend` | 前端主程 | React/TypeScript 架构、组件规范 | 前端架构决策、组件设计 |
| `erp-lead-qa` | QA 负责人 | 测试策略、Bug 分类、发布就绪 | 测试计划、Bug 优先级 |
| `erp-lead-db` | 数据库负责人 | MySQL 设计、索引、迁移 | 表结构设计、索引优化 |
| `erp-release-manager` | 发布经理 | 构建、版本、部署 | 发布规划、变更日志 |

## Tier 3 — 专家（Sonnet/Haiku）

| Agent | 角色 | 职责 | 模型 |
|-------|------|------|------|
| `erp-backend-dev` | 后端开发 | Controller/Service/Mapper 实现 | Sonnet |
| `erp-frontend-dev` | 前端开发 | React 页面、组件 | Sonnet |
| `erp-security` | 安全工程师 | JWT、@PreAuthorize、SQL 注入 | Sonnet |
| `erp-perf` | 性能分析师 | 慢查询、N+1、前端性能 | Sonnet |
| `erp-qa-tester` | QA 测试员 | 测试用例、Bug 报告 | Haiku |
| `erp-devops` | DevOps | CI/CD、Maven、Nginx | Haiku |
| `erp-i18n` | 国际化 | 中文/日文双语 | Haiku |

## 快速路由

| 我需要... | 使用 Agent |
|-----------|-----------|
| 决定用哪个技术方案 | `erp-cto` |
| 规划下个 Sprint | `erp-pm` |
| 澄清业务规则 | `erp-product-owner` |
| 审查后端代码 | `erp-lead-backend` |
| 审查前端代码 | `erp-lead-frontend` |
| 设计数据库表 | `erp-lead-db` |
| 制定测试计划 | `erp-lead-qa` |
| 规划发布 | `erp-release-manager` |
| 实现后端功能 | `erp-backend-dev` |
| 实现前端页面 | `erp-frontend-dev` |
| 修复安全漏洞 | `erp-security` |
| 优化性能 | `erp-perf` |
| 添加翻译 | `erp-i18n` |
| 编写测试用例 | `erp-qa-tester` |
| 配置部署 | `erp-devops` |

## 委派层级

```
用户
├── erp-cto (技术决策)
│   ├── erp-lead-backend
│   │   ├── erp-backend-dev
│   │   ├── erp-security
│   │   └── erp-perf
│   ├── erp-lead-frontend
│   │   ├── erp-frontend-dev
│   │   └── erp-i18n
│   └── erp-lead-db
├── erp-pm (项目协调)
│   ├── erp-lead-qa
│   │   └── erp-qa-tester
│   └── erp-release-manager
│       └── erp-devops
└── erp-product-owner (业务需求)
```
