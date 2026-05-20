# Skill 注册表

> 最后更新：2026-04-26 | 功能完成计数：6（Phase 29 审计 + 外部资源注册 + 流程skill注册 + 5仓库入库 + Anthropic集成 + 7个高质量审计资源入库并验证）| 下次迭代报告：第 7 次

---

## 本地 Skill（D:/erp/.claude/skills/）

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| erp-verify | active | 0 | 0 | — | — | keep | 核心验证 skill，覆盖后端/前端/SQL |
| knit-erp-workflow | active | 0 | 0 | — | — | keep | 工序流转专用，业务知识密集 |
| skill-registry | active | 0 | 0 | — | — | keep | 本体系治理 skill |

---

## 全局 Skill 使用记录（~/.claude/skills/）

### Superpowers 套件

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| brainstorming | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| writing-plans | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| executing-plans | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| test-driven-development | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| systematic-debugging | probation | 0 | 0 | — | — | watch | 与 gstack/investigate 重叠，观察哪个更有效 |
| requesting-code-review | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| dispatching-parallel-agents | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| verification-before-completion | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| using-git-worktrees | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| writing-skills | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| finishing-a-development-branch | probation | 0 | 0 | — | — | watch | 新引入，待验证 |
| subagent-driven-development | probation | 0 | 0 | — | — | watch | 新引入，待验证 |

### Gstack 套件

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| investigate | active | 0 | 0 | — | — | keep | 与 systematic-debugging 重叠，观察期对比 |
| ship | active | 0 | 0 | — | — | keep | 提交流程核心 |
| review | active | 0 | 0 | — | — | keep | 与 requesting-code-review、differential-review 三方对比 |
| health | probation | 0 | 0 | — | — | watch | 与 erp-verify 部分重叠，观察是否互补 |
| qa | probation | 0 | 0 | — | — | watch | 前端测试场景待验证 |
| context-save | active | 0 | 0 | — | — | keep | 跨会话保存进度 |
| context-restore | active | 0 | 0 | — | — | keep | 跨会话恢复进度 |

### 审计套件（2026-04-26 建立）

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| differential-review | **active** | 1 | 1 | 100% | 2026-04-26 | keep | Phase 29 安全审计中命中 3 CRITICAL+ HIGH：发现表名错误、事务缺失、并发竞态；methodology 分层完善 |
| insecure-defaults | **active** | 1 | 1 | 100% | 2026-04-26 | keep | Phase 29 安全默认值审计中命中 5 项（4 fail-open 配置 + 2 MyBatis ${} 遗留），与 erp-verify 互补确认 |
| cso | probation | 0 | 0 | — | — | watch | **新引入** — OWASP/STRIDE/供应链/CI-CD 安全，补 differential-review 未覆盖的 infra 层；two modes: daily(8/10) + monthly comprehensive(2/10) |
| codex | probation | 0 | 0 | — | — | watch | **新引入** — OpenAI Codex 独立 code review，作为 differential-review 的第二意见；需 codex CLI 可用，无 CLI 时降级为 manual 对比 |

### Trail of Bits 套件

（已迁移至上方「审计套件」）

### 流程规范套件（2026-04-26 注册）

| name | status | invoke | hit | hit_rate | last_used | verdict | verdict_reason |
|------|--------|--------|-----|----------|-----------|---------|----------------|
| receiving-code-review | probation | 0 | 0 | — | — | watch | 规范"接收审计意见的AI"行为：逐条技术验证、禁止盲从、禁止表演式同意；直接对接 audit→fix 链路 |
| plan-eng-review | probation | 0 | 0 | — | — | watch | 架构计划审查：在实现前拦截设计问题，补审计矩阵"事前预防"盲区 |

---

## 已知冲突对

| skill A | skill B | skill C | 冲突类型 | 当前策略 |
|---------|---------|---------|---------|---------|
| systematic-debugging | investigate | — | 功能重叠（根因调试） | 并行观察，命中率高者保留 |
| requesting-code-review | review | differential-review | receiving-code-review | 功能重叠（代码审查4方） | review=通用PR，differential=安全专项，codex=独立二评，requesting=请求审查，receiving=接收审计意见；各司其职 |
| health | erp-verify | insecure-defaults | 部分重叠（代码质量/安全） | erp-verify=业务规范，insecure-defaults=安全默认值，health=综合评分，cso=infra安全 |
| differential-review | cso | insecure-defaults | 部分重叠（安全审计） | **分三层**：differential-review=代码diff级，insecure-defaults=配置/默认值级，cso=infra/OWASP/供应链级 |

## 审计 Skill 矩阵（2026-04-26）

| 层级 | Skill | 覆盖范围 | Java/Spring 适用度 |
|------|-------|---------|-------------------|
| **L1 代码变更** | `differential-review` | 安全 diff 审查、攻击场景、爆炸半径 | ⭐⭐⭐⭐⭐ 已验证命中 |
| **L2 安全配置** | `insecure-defaults` | 硬编码密钥、JWT回退、DEBUG/CORS、弱加密 | ⭐⭐⭐⭐⭐ Spring配置天然适配 |
| **L3 基础设施** | `cso` | OWASP TOP10、STRIDE建模、供应链、CI/CD | ⭐⭐⭐⭐ Maven依赖/CI配置可审查 |
| **L4 独立二评** | `codex` | AI独立 review（需Codex CLI） | ⭐⭐⭐ 取决于Codex CLI可用性 |
| **L5 代码质量** | `health` | 编译/lint/测试/死代码综合评分 | ⭐⭐⭐⭐ 可包装Maven/ESLint |
| **L5 通用PR** | `review` | 通用 PR review（非安全专项） | ⭐⭐⭐ 已有differential可降频 |

---

## 链路断裂记录

| 断裂节点 | 次数 | 最近发生 |
|---------|------|---------|
| （暂无） | — | — |

---

## 迭代历史

| 轮次 | 日期 | 功能数 | 变更 |
|------|------|--------|------|
| 初始化 | 2026-04-22 | 0 | 建立注册表 |
| 第1次 | 2026-04-26 | 1 | Phase 29 审计（differential-review + insecure-defaults 验证通过） |
| 第2次 | 2026-04-26 | 2 | 注册 cso + codex + 建立审计矩阵 L1-L5 |
| 第3次 | 2026-04-26 | 3 | 注册 receiving-code-review + plan-eng-review + 外部审计资源（腾讯CoT方法论 + 公开审计repo） |
| 第4次 | 2026-04-26 | 5 | 5仓库入库：java-audit-skills(RuoJi6)+SecAuditAI(tgllsy)+skill-security-scanner(yzj1)+anthropics/claude-code-security-review+ez-lbz结构确认；集成 Anthropic /security-review |
| 第5次 | 2026-04-26 | 6 | 7个高质量审计资源入库验证：code-audit(3stoneBrother)+sast-skills(utkusen)+claude-code-owasp(agamm)+security-review-skill(dilaz)+trailofbits/skills+skill-threat-modeling(fr33d3m0n) |

---

## 外部审计资源

> 以下资源是经过克隆验证的外部仓库、独立工具或方法论参考。

### 方法论

| 来源 | 关键方法 | 适用场景 |
|------|---------|---------|
| [腾讯啄木鸟 CoT 审计法](https://security.tencent.com/index.php/blog/msg/210) | 思维链推理 → LLM+规则结合 → JSON结构化输出 → 多模型投票 | Prompt 工程参考 |
| [Anthropic `/security-review`](https://github.com/anthropics/claude-code-security-review) | 3-Phase + 17条硬排除规则 + 17条先例 + 置信度评分(>80%) | **首选！Claude Code 内置** |

---

### 🏆 第一梯队：专业安全审计 Skill（已验证，强烈推荐安装）

#### 1. code-audit（3stoneBrother）— 最全面的多语言审计

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/3stoneBrother/code-audit.git` |
| 定位 | **专业白盒安全审计 skill，覆盖 55+ 漏洞类型，双轨审计模型** |
| 安装 | `cp -r code-audit ~/.claude/skills/` |

**核心竞争力**：
- **9 语言 + 14 框架**：Java/Spring Boot/MyBatis、Python/Django/Flask、Go/Gin、PHP/Laravel 等
- **双轨审计模型**：Sink-driven（注入/RCE/XSS） + Control-driven（授权/业务逻辑），解决"搜不到缺失的安全控制"问题
- **WooYun 88,636 案例库**：内置 2010-2016 真实漏洞案例的统计驱动参数优先级 + 绕过技术库 + 逻辑漏洞模式
- **10 安全维度 (D1-D10)**：注入/认证/授权/反序列化/文件/SSRF/加密/配置/业务逻辑/供应链
- **143 项强制检测项**：按语言组织的检查清单
- **多 Agent 并行**：874+ Java 文件约 15 分钟
- **Docker 沙箱验证**：自动生成漏洞验证环境
- **攻击链构建**：自动串联多个发现为可利用攻击路径

**扫描模式**：Quick（CI/CD）/ Standard（OWASP Top 10）/ Deep（全覆盖+攻击链）

**对本项目** ⭐⭐⭐⭐⭐ — Spring Boot + MyBatis 原生支持

#### 2. sast-skills（utkusen）— 13 并行 SAST 扫描

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/utkusen/sast-skills.git` |
| 定位 | **零依赖 SAST 扫描器，13 个子 skill 并行运行** |
| 安装 | 复制项目到 `sast-files/`，Claude Code 自动编排 |

**13 个并行检测 skill**：SQLi / GraphQL injection / XSS / RCE / SSRF / IDOR / XXE / SSTI / JWT flaws / MissingAuth / PathTraversal / FileUpload / BusinessLogic

**工作流**：Codebase Analysis → 13 Parallel Scans → Consolidated Report (`sast/final-report.md`)

**对本项目** ⭐⭐⭐⭐ — 零依赖、广度覆盖、自动编排

#### 3. claude-code-owasp（agamm）— OWASP 标准覆盖

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/agamm/claude-code-owasp.git` |
| 定位 | **OWASP Top 10:2025 + ASVS 5.0 + Agentic AI Security 2026** |
| 安装 | `curl -sL https://raw.githubusercontent.com/agamm/claude-code-owasp/main/.claude/skills/owasp-security/SKILL.md -o .claude/skills/owasp-security/SKILL.md --create-dirs` |

**覆盖标准**：OWASP Top 10:2025 / ASVS 5.0.0 / OWASP Agentic AI 2026 (ASI01-ASI10)
**20+ 语言安全特性**：Java、Python、Go、Rust、C/C++、JS/TS、C#、Swift、Kotlin、PHP 等

**对本项目** ⭐⭐⭐⭐ — 标准合规检查首选

#### 4. security-review-skill（dilaz）— PoC 驱动审计

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/dilaz/security-review-skill.git` |
| 定位 | **铁律：No finding without working exploit** |
| 核心理念 | 怀疑漏洞无价值，必须证明可利用性 |

**工具链**：SAST (Semgrep/Bandit/ESLint/Gosec) + SCA (Trivy/Grype) + Secret Detection (Gitleaks/TruffleHog)
**工作流**：Auto Scan → Manual Review → Exploit PoC → Verify → Document → Report

**对本项目** ⭐⭐⭐⭐ — PoC 驱动方法论，可与 code-audit 互补

---

### 🏛️ 第二梯队：Trail of Bits 专业套件

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/trailofbits/skills.git` |
| 安装 | `/plugin marketplace add trailofbits/skills` |
| 定位 | **工业级安全审计 skill 市场（38 插件），Trail of Bits 出品** |

**审计相关核心插件**：

| 插件 | 功能 | 匹配度 |
|------|------|:---:|
| `differential-review` | diff 安全审查（git history + blast radius） | ⭐⭐⭐⭐⭐ |
| `insecure-defaults` | fail-open 配置、硬编码凭证检测 | ⭐⭐⭐⭐⭐ |
| `supply-chain-risk-auditor` | 依赖供应链威胁审计 | ⭐⭐⭐⭐ |
| `static-analysis` | CodeQL + Semgrep + SARIF | ⭐⭐⭐⭐⭐ |
| `variant-analysis` | 跨代码库相似漏洞搜索 | ⭐⭐⭐⭐ |
| `semgrep-rule-creator` | 自定义 Semgrep 规则创建 | ⭐⭐⭐⭐ |
| `fp-check` | 系统性误报验证 | ⭐⭐⭐⭐ |
| `sharp-edges` | 危险 API + 易错设计识别 | ⭐⭐⭐ |
| `constant-time-analysis` | 加密代码时序侧信道 | ⭐⭐ |
| `zeroize-audit` | 密钥清零缺失检测 | ⭐⭐ |
| `agentic-actions-auditor` | GitHub Actions AI 安全审计 | ⭐⭐⭐ |
| `second-opinion` | Codex/Gemini 独立二评 | ⭐⭐⭐⭐ |

---

### ☕ 第三梯队：Java 专项 + 工具

#### java-audit-skills（RuoJi6）

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/RuoJi6/java-audit-skills.git` |
| 安装 | 复制 `skills/` 到 Claude Code skills 目录 |

**9 个 Java 专项 skill + 全链路流水线**：路由映射/调用链追踪/鉴权审计(Security/Shiro/JWT)/SQL注入(MyBatis/JDBC/Hibernate)/文件上传/文件读取/XXE/组件CVE(130+)/全链路编排

**对本项目** ⭐⭐⭐⭐⭐ — 直接对标 RuoYi 框架

#### SecAuditAI（tgllsy）

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/tgllsy/SecAuditAI.git` |
| 类型 | Go CLI — CodeQL 污点追踪 + LLM 二次验证 + Payload 自动生成 |
| 安装 | `go build -o SecAuditAI.exe main.go`（需 CodeQL CLI） |

#### skill-security-scanner（yzj1）

| 属性 | 值 |
|------|-----|
| 仓库 | `https://gitee.com/yzj1/skill-security-scanner.git` |
| 类型 | Python — 18 种检测器 + CVSS 3.1 |
| 安装 | `pip install -r requirements.txt && pip install -e .` |

#### skill-threat-modeling（fr33d3m0n）

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/fr33d3m0n/skill-threat-modeling.git` |
| 定位 | **Code-First 威胁建模**：8 阶段（项目理解→DFD→信任边界→安全设计→STRIDE→风险验证→缓解→报告） |

---

### 私有/不可达仓库

| 仓库 | 状态 | 已知信息 |
|------|:---:|------|
| `ez-lbz/claude-code-security-skills` | 🔒 private | 结构：SKILL.md + resources/{audit-prompt, filtering-rules, hard-exclusion-patterns, customization-guide}.md。作者 = SpringBoot-Scan 贡献者 |
| `aideepcode/SecAuditAI` | ❌ 不存在 | — |

---

### 📊 审计体系总矩阵 (L0-L5)

| 层级 | 工具/Skill | 覆盖范围 | 来源 |
|------|-----------|---------|------|
| **L0 内置** | `/security-review` | diff 审查 + 17硬排除 + 误报过滤 | Anthropic 官方 |
| **L1 全面审计** | `code-audit` | 55+ 漏洞 / 10维度 / 双轨 / WooYun案例库 | 3stoneBrother |
| **L1 SAST扫描** | `sast-skills` | 13 并行 SAST + 零依赖 | utkusen |
| **L1 安全diff** | `differential-review` | diff 审查 + 攻击场景 + 爆炸半径 | ToB / 本地 ✅ |
| **L2 OWASP合规** | `claude-code-owasp` | Top10:2025 + ASVS 5.0 + Agentic AI | agamm |
| **L2 安全配置** | `insecure-defaults` | 硬编码密钥/JWT回退/DEBUG/CORS | ToB / 本地 ✅ |
| **L3 PoC验证** | `security-review-skill` | 铁律：无PoC不报告 | dilaz |
| **L3 Java专项** | `java-audit-skills` | 9 skill + agent team 全链路 | RuoJi6 |
| **L3 静态分析CLI** | `SecAuditAI` | CodeQL + AI 验证 + Payload 生成 | tgllsy |
| **L4 供应链+基础设施** | `cso` + `supply-chain-risk-auditor` (ToB) + `skill-security-scanner` | OWASP/STRIDE/供应链/CI-CD/CVSS | 多源 |
| **L4 威胁建模** | `skill-threat-modeling` | DFD + STRIDE + 信任边界 | fr33d3m0n |
| **L4 变体分析** | `variant-analysis` (ToB) | 跨代码库相似漏洞搜索 | ToB |
| **L5 独立二评** | `codex` + `second-opinion` (ToB) | Codex/Gemini 独立审查 | ToB / 本地 |
| **L5 代码质量** | `health` + `static-analysis` (ToB) | 编译/lint/测试 + CodeQL/Semgrep | ToB / 本地 |
| **L5 通用PR** | `review` | 通用 PR 审查 | 本地 |

### 🎯 推荐审计工作流

```
Phase 30+ 每次提交前：
  L0  /security-review              ← 内置，秒级 diff 扫描
  L1  code-audit quick              ← 快速高危扫描
  L2  insecure-defaults             ← 配置安全
  合入前：
  L1  code-audit standard/deep      ← 全面审计
  L3  java-audit-pipeline (RuoJi6)  ← Java 专项
  L4  skill-threat-modeling         ← 新功能威胁建模
  月度：
  L4  cso                           ← 基础设施审计
  L5  health                        ← 代码质量评分
```
