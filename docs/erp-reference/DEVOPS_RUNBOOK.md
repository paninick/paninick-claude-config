# 运维手册 — 针织服装工贸一体 ERP

> 版本：2026-05-04 | 基于本项目实际踩坑经验整理，每条故障均有真实案例来源。

---

## 一、环境要求

| 组件 | 版本要求 | 验证命令 |
|------|---------|---------|
| JDK | 17（必须，低于 17 启动报 `@SpringBootConfiguration` 找不到） | `java -version` |
| Maven | 3.8+ | `mvn -version` |
| Node.js | 18+ | `node -v` |
| MySQL | 8.0.x | `mysql --version` |
| Redis | 6+ | `redis-cli --version` |

---

## 二、启动流程

### 2.1 后端（Spring Boot，端口 8080）

```bash
# 进入后端目录
cd D:/ERP/RuoYi-Vue

# 设置必须的环境变量（缺任何一个会启动失败）
export JWT_SECRET="dev-secret-change-in-production-32chars!!"
export DB_PASSWORD=""          # 本地 MySQL 无密码时留空
export REDIS_PASSWORD=""       # 本地 Redis 无密码时留空
export DRUID_PASSWORD="druid123"

# 启动
mvn spring-boot:run -pl ruoyi-admin
```

**PowerShell 版本（Windows）：**
```powershell
$env:JWT_SECRET    = "dev-secret-change-in-production-32chars!!"
$env:DB_PASSWORD   = ""
$env:REDIS_PASSWORD = ""
$env:DRUID_PASSWORD = "druid123"
mvn spring-boot:run -pl ruoyi-admin
```

> 脚本位置：`D:\ERP\RuoYi-Vue\scripts\start-backend.ps1`

### 2.2 前端 React（ERP-UI-2，端口 3000）

```bash
cd D:/ERP/ERP-UI-2
npm install        # 首次或 package.json 变更后
npm run dev        # 开发模式，热更新
npm run build      # 生产构建，输出到 dist/
```

### 2.3 前端 Vue2（ruoyi-ui，端口 80/8081）

```bash
cd D:/ERP/RuoYi-Vue/ruoyi-ui
npm install
npm run dev        # 默认 8080，与后端冲突时改 vue.config.js port
```

> **注意**：Vue2 前端已冻结，不再主动开发。React (ERP-UI-2) 是唯一主前端。

---

## 三、环境变量完整清单

| 变量名 | 用途 | 默认值 | 生产环境要求 |
|--------|------|--------|------------|
| `JWT_SECRET` | JWT 签名密钥 | 无（必须设置） | 32+ 字符随机串，**禁止使用默认值** |
| `DB_PASSWORD` | MySQL 密码 | `""` (空) | 生产环境必须设置强密码 |
| `REDIS_PASSWORD` | Redis 密码 | `""` (空) | 生产环境必须设置 |
| `DRUID_PASSWORD` | Druid 监控密码 | `druid123` | 生产环境必须修改 |
| `DB_HOST` | MySQL 地址 | `localhost` | 生产环境填实际地址 |
| `DB_PORT` | MySQL 端口 | `3306` | — |
| `DB_NAME` | 数据库名 | `ry-vue` | — |
| `REDIS_HOST` | Redis 地址 | `localhost` | — |
| `REDIS_PORT` | Redis 端口 | `6379` | — |

---

## 四、常见故障排查（真实案例）

### 4.1 后端无法启动

| 现象 | 原因 | 处置 |
|------|------|------|
| `Unable to find @SpringBootConfiguration` | JDK 版本 < 17 | 安装 JDK 17，设置 `JAVA_HOME` |
| `JWT_SECRET must be set` / 启动即报错 | 未设置 `JWT_SECRET` 环境变量 | 见 §2.1 设置环境变量 |
| `Access denied for user 'root'@'localhost'` | `DB_PASSWORD` 不匹配 | 本地无密码时设 `DB_PASSWORD=""` |
| `NOAUTH Authentication required` | Redis 有密码但未设置 `REDIS_PASSWORD` | 检查 Redis 是否需要密码；本地开发可重启 Redis 服务（以管理员身份）清除内存密码 |
| `Port 8080 was already in use` | 端口被占用 | `netstat -ano \| findstr :8080` 找到 PID，`taskkill /F /PID <pid>` |
| `Druid 监控页 403` | Druid 账号未配置 | 设置 `DRUID_PASSWORD` 环境变量 |

### 4.2 前端无法启动

| 现象 | 原因 | 处置 |
|------|------|------|
| `EADDRINUSE 3000` | 端口被占用 | `netstat -ano \| findstr :3000`，kill 进程 |
| 白屏，控制台 `Cannot GET /` | SPA 路由未配置 | Nginx `try_files $uri /index.html` |
| Vue2 路由报 `"path" is required` | 数据库 `sys_menu` 存在 `path` 为空的记录 | `UPDATE sys_menu SET path = 'placeholder' WHERE path IS NULL OR path = ''` |
| 登录后 401 | Redis 连不通 / Token 失效 | 检查 Redis 服务状态，`redis-cli ping` |
| 登录后白屏 | 前端 API 地址配置错误 | 检查 `.env.development` 中 `VITE_APP_BASE_API` |

### 4.3 数据库问题

| 现象 | 原因 | 处置 |
|------|------|------|
| 表不存在 | SQL 脚本未执行 | 按顺序执行 `sql/` 目录下 `phase*.sql` |
| 字段不存在 | 增量 SQL 未执行 | 找到对应 `phase*.sql`，手动执行 |
| 重复键冲突 | 幂等脚本未用 `ON DUPLICATE KEY` | 检查脚本，改用 `INSERT ... ON DUPLICATE KEY UPDATE` |

### 4.4 Redis 特殊情况（Windows 本地）

Windows 本地 Redis 服务有时会在内存中保留密码（即使 `redis.conf` 未配置）。
处置步骤：
1. 以**管理员身份**打开 PowerShell
2. `Stop-Service Redis`
3. `Start-Service Redis`
4. `redis-cli ping` → 应返回 `PONG`

---

## 五、数据库操作

### 5.1 连接

```bash
mysql -h localhost -u root -p
use ry-vue;
```

### 5.2 SQL 脚本执行顺序

```
sql/
├── ry_20210924.sql          # RuoYi 基础表（首次初始化）
├── quartz.sql               # 定时任务表
├── phase01_*.sql            # ERP 基础主数据
├── phase02_*.sql
├── ...
└── phase{N}_*.sql           # 按编号顺序执行
```

> **禁止**修改已执行的 SQL 文件。新增字段/索引写新的 `phase{N+1}_*.sql`，使用幂等写法：
```sql
SET @col_exists := (SELECT COUNT(1) FROM information_schema.COLUMNS
    WHERE table_schema = DATABASE() AND table_name = 't_erp_xxx' AND column_name = 'new_col');
SET @sql := IF(@col_exists = 0, 'ALTER TABLE t_erp_xxx ADD COLUMN new_col VARCHAR(64)', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
```

### 5.3 常用诊断查询

```sql
-- 查看所有 ERP 表
SELECT table_name, table_rows FROM information_schema.tables
WHERE table_schema = 'ry-vue' AND table_name LIKE 't_erp_%'
ORDER BY table_name;

-- 查看菜单（排查路由问题）
SELECT menu_id, menu_name, path, component FROM sys_menu
WHERE path IS NULL OR path = '' ORDER BY menu_id;

-- 查看角色权限
SELECT r.role_name, m.menu_name, m.perms
FROM sys_role r
JOIN sys_role_menu rm ON r.role_id = rm.role_id
JOIN sys_menu m ON rm.menu_id = m.menu_id
WHERE r.role_id = 100;
```

---

## 六、日志查看

```bash
# 后端日志（Spring Boot 控制台）
# 日志文件位置（默认）
tail -f D:/ERP/RuoYi-Vue/logs/sys-info.log
tail -f D:/ERP/RuoYi-Vue/logs/sys-error.log

# 前端构建日志
cd D:/ERP/ERP-UI-2 && npm run build 2>&1 | tee build.log
```

---

## 七、生产部署检查清单

```
□ JWT_SECRET 已替换为 32+ 字符随机串
□ DB_PASSWORD 已设置强密码
□ REDIS_PASSWORD 已设置
□ DRUID_PASSWORD 已修改
□ Nginx try_files 已配置 SPA 兜底
□ HTTPS 证书已配置
□ ReportController @PreAuthorize 已补全（P0-1）
□ 角色菜单权限已配置（P0-3）
□ 所有 phase*.sql 已按顺序执行
□ Redis 持久化已开启（AOF 或 RDB）
□ MySQL 定期备份已配置
```

---

## 八、快速健康检查

```bash
# 后端健康
curl http://localhost:8080/actuator/health

# 前端可访问
curl -I http://localhost:3000

# Redis
redis-cli ping

# MySQL
mysql -u root -e "SELECT 1" ry-vue
```
