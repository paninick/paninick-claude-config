# erp-verify 典型问题案例

## 案例 1：金额字段用了 double

**问题代码**
```java
private double unitPrice;
private double totalAmount;
```

**修复**
```java
private BigDecimal unitPrice;
private BigDecimal totalAmount;
```

---

## 案例 2：Mapper XML `<set>` 标签缺失导致 SQL 报错

**问题代码**
```xml
<update id="updateOrder">
  UPDATE produce_order
  order_status = #{orderStatus},
  update_time = NOW()
  WHERE order_id = #{orderId}
</update>
```

**修复**
```xml
<update id="updateOrder">
  UPDATE produce_order
  <set>
    order_status = #{orderStatus},
    update_time = NOW()
  </set>
  WHERE order_id = #{orderId}
</update>
```

---

## 案例 3：Controller 缺少权限注解

**问题代码**
```java
@GetMapping("/list")
public TableDataInfo list(ProduceOrder order) { ... }
```

**修复**
```java
@PreAuthorize("@ss.hasPermi('erp:order:list')")
@GetMapping("/list")
public TableDataInfo list(ProduceOrder order) { ... }
```

---

## 案例 4：SQL 脚本直接修改已有文件

**错误做法**：在 `phase12_xxx.sql` 里追加新字段

**正确做法**：新建 `phase18_新描述.sql`，只写 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`

---

## 案例 5：前端金额显示原始字符串

**问题**：`{{ row.totalAmount }}` 显示 `12345.678900`

**修复**：`{{ parseFloat(row.totalAmount).toFixed(2) }}` 或用全局过滤器 `{{ row.totalAmount | money }}`
