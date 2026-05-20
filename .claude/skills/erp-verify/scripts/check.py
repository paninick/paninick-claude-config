#!/usr/bin/env python3
"""
erp-verify 自动化扫描脚本
扫描范围：ruoyi-demo/ 和 ruoyi-ui/src/views/erp/
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "../../../RuoYi-Vue")
DEMO_DIR = os.path.join(ROOT, "ruoyi-demo/src/main/java")
UI_DIR = os.path.join(ROOT, "ruoyi-ui/src/views/erp")
SQL_DIR = os.path.join(ROOT, "sql")
FRAMEWORK_DIR = os.path.join(ROOT, "ruoyi-framework")

issues = []

def check(condition, msg):
    if not condition:
        issues.append(msg)

def scan_java():
    for dirpath, _, files in os.walk(DEMO_DIR):
        for f in files:
            if not f.endswith(".java"):
                continue
            path = os.path.join(dirpath, f)
            content = open(path, encoding="utf-8", errors="ignore").read()

            # 禁止 double/float 金额
            for m in re.finditer(r'\b(double|float)\s+\w*(price|amount|cost|fee|total|money)\w*', content, re.IGNORECASE):
                issues.append(f"[后端] {f}: 金额字段用了 {m.group(1)}，应改为 BigDecimal → {m.group(0)}")

            # 禁止 System.out.println
            if "System.out.println" in content:
                issues.append(f"[后端] {f}: 含 System.out.println，应用 DemoLogUtil")

            # 禁止 e.printStackTrace
            if "e.printStackTrace" in content:
                issues.append(f"[后端] {f}: 含 e.printStackTrace，应用 DemoLogUtil")

def scan_framework():
    for dirpath, _, files in os.walk(FRAMEWORK_DIR):
        for f in files:
            path = os.path.join(dirpath, f)
            # 只检测是否被 git 标记为已修改（简单检测：mtime 近期变化不可靠，跳过）
            pass  # 框架保护由 git diff 检测更准确

def scan_sql():
    if not os.path.isdir(SQL_DIR):
        return
    for f in os.listdir(SQL_DIR):
        if not f.endswith(".sql"):
            continue
        path = os.path.join(SQL_DIR, f)
        content = open(path, encoding="utf-8", errors="ignore").read()
        # 检测是否有 DROP TABLE
        if re.search(r'\bDROP\s+TABLE\b', content, re.IGNORECASE):
            issues.append(f"[SQL] {f}: 含 DROP TABLE，迁移脚本禁止删表")
        # 检测是否有硬编码密码
        if re.search(r"password\s*=\s*['\"][^'\"]{4,}", content, re.IGNORECASE):
            issues.append(f"[SQL] {f}: 疑似硬编码密码")

def scan_vue():
    for dirpath, _, files in os.walk(UI_DIR):
        for f in files:
            if not f.endswith(".vue"):
                continue
            path = os.path.join(dirpath, f)
            content = open(path, encoding="utf-8", errors="ignore").read()
            # 检测金额字段未格式化（粗略：v-model 绑定含 amount/price 但无 toFixed）
            if re.search(r'(amount|price|cost|fee)', content, re.IGNORECASE):
                if "toFixed" not in content and "money" not in content and "filter" not in content:
                    issues.append(f"[前端] {f}: 含金额字段但未见格式化处理（toFixed/filter）")

if __name__ == "__main__":
    scan_java()
    scan_sql()
    scan_vue()

    print("=== erp-verify 自动扫描结果 ===")
    if not issues:
        print("✅ 全部通过，无问题")
        sys.exit(0)
    else:
        for i in issues:
            print(f"❌ {i}")
        print(f"\n共 {len(issues)} 个问题，修复后重新运行")
        sys.exit(1)
