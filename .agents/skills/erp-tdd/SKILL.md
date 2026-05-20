---
name: erp-tdd
version: 1.0.0
description: ERP项目测试驱动开发。新增或修改 Service 方法时强制先写测试，RED-GREEN-REFACTOR 流程。关闭 WH-001（零测试覆盖）。当用户说"写测试"、"补测试"、"TDD"、"test"时触发。
triggers:
  - 写测试
  - 补测试
  - tdd
  - test driven
  - 新增service
  - 单元测试
  - 集成测试
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Edit
  - Write
---

# erp-tdd — ERP 测试驱动开发

WH-001 修复 skill。每次新增或修改 Service 方法时强制执行，不可跳过。

## 项目测试约定

| 项目 | 约定 |
|------|------|
| 测试框架 | JUnit 5 + Spring Boot Test |
| 测试目录 | `RuoYi-Vue/ruoyi-admin/src/test/java/com/ruoyi/erp/` |
| 数据隔离 | `@Transactional` 回滚，不污染本地库 |
| 测试类型 | 纯逻辑用单元测试（无 Spring 上下文），多表写操作用集成测试 |
| 运行命令 | `mvn test -f RuoYi-Vue/ruoyi-admin/pom.xml` |

## 已有测试参考（必须先读）

- `ProcessRouteValidatorTest.java` — 纯逻辑单元测试范例
- `ProduceJobProcessDependencyTest.java` — 依赖图测试范例

## RED-GREEN-REFACTOR 流程

### 第一步：RED — 先写失败的测试

1. 读目标 Service 方法的签名和业务规则
2. 在 `src/test/java/com/ruoyi/erp/` 新建或追加测试类
3. 写测试用例，覆盖：
   - 正常路径（happy path）
   - 边界条件（空值、零值、最大值）
   - 异常路径（非法状态、权限不足、数据不存在）
4. 运行测试，**确认失败**（RED）

```bash
mvn test -f RuoYi-Vue/ruoyi-admin/pom.xml -Dtest=目标TestClass -q
```

### 第二步：GREEN — 最小实现让测试通过

1. 只写让测试通过的最小代码，不做多余实现
2. 运行测试，**确认全部通过**（GREEN）

```bash
mvn test -f RuoYi-Vue/ruoyi-admin/pom.xml -Dtest=目标TestClass -q
```

### 第三步：REFACTOR — 重构，保持绿灯

1. 清理重复代码、改善命名、提取常量
2. 运行全量测试，**确认没有回归**

```bash
mvn test -f RuoYi-Vue/ruoyi-admin/pom.xml -q
```

## 测试模板

### 纯逻辑单元测试（无 Spring 上下文，速度快）

```java
package com.ruoyi.erp;

import com.ruoyi.common.exception.ServiceException;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class XxxServiceTest {

    @Test
    public void should_描述预期行为_when_触发条件() {
        // Arrange
        // ...

        // Act + Assert
        assertDoesNotThrow(() -> /* 调用 */);
        // 或
        ServiceException ex = assertThrows(ServiceException.class, () -> /* 调用 */);
        assertEquals("期望的错误信息", ex.getMessage());
    }
}
```

### 集成测试（需要 Spring 上下文 + DB）

```java
package com.ruoyi.erp;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional  // 测试结束自动回滚，不污染数据库
public class XxxServiceIntegrationTest {

    @Autowired
    private IXxxService xxxService;

    @Test
    public void should_描述预期行为() {
        // Arrange
        // ...

        // Act
        // ...

        // Assert
        // ...
    }
}
```

## 优先级：哪些方法必须先补测试

按 WH-001 要求，优先覆盖核心审批流：

1. `submit / approve / reject` 类方法（状态机流转）
2. `confirm / cancelConfirm` 类方法（确认/回滚）
3. 多表写操作的 Service 方法（事务边界验证）
4. 带业务规则校验的方法（如"未放行工序不能完工入库"）

## 完成标准

- [ ] 新增测试覆盖目标方法的正常路径
- [ ] 新增测试覆盖至少 1 个异常路径
- [ ] `mvn test` 全量通过，无新增失败
- [ ] 测试类命名：`XxxServiceTest.java` 或 `XxxServiceIntegrationTest.java`
- [ ] 测试方法命名：`should_预期行为_when_条件()`

## 关联

- 验证通过后调用 `erp-verify` 做完整检查
- 测试文件变更也需要通过 pre-commit hook
