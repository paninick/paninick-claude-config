#!/usr/bin/env python3
"""
skill-registry evaluate.py
统计 registry.md 中各 skill 的命中率，输出需要关注的条目。
用法：python evaluate.py [registry.md路径]
"""
import re
import sys
import io
from datetime import datetime, date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REGISTRY = sys.argv[1] if len(sys.argv) > 1 else "registry.md"

def parse_table_rows(content, section_marker):
    """提取指定 section 下的表格行"""
    rows = []
    in_section = False
    in_table = False
    for line in content.splitlines():
        if section_marker in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            in_section = False
        if in_section and line.startswith("| ") and "name" not in line and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 7:
                rows.append(parts)
    return rows

def evaluate(row):
    name, status, invoke_s, hit_s = row[0], row[1], row[2], row[3]
    try:
        invoke = int(invoke_s)
        hit = int(hit_s)
    except ValueError:
        return None

    hit_rate = hit / invoke if invoke > 0 else None

    if invoke == 0:
        verdict = "no-data"
    elif hit_rate >= 0.4:
        verdict = "keep"
    elif hit_rate >= 0.1:
        verdict = "watch"
    else:
        verdict = "remove-candidate"

    return {
        "name": name,
        "status": status,
        "invoke": invoke,
        "hit": hit,
        "hit_rate": hit_rate,
        "verdict": verdict,
    }

def main():
    try:
        content = open(REGISTRY, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"找不到 {REGISTRY}")
        sys.exit(1)

    print("=== Skill 评分报告 ===")
    print(f"生成时间：{date.today()}\n")

    sections = [
        ("## 本地 Skill", "本地"),
        ("## 全局 Skill", "全局"),
    ]

    remove_candidates = []
    watch_list = []

    for marker, label in sections:
        rows = parse_table_rows(content, marker)
        if not rows:
            continue
        print(f"[{label}]")
        for row in rows:
            result = evaluate(row)
            if not result:
                continue
            rate_str = f"{result['hit_rate']:.0%}" if result['hit_rate'] is not None else "—"
            flag = {"keep": "✅", "watch": "⚠️", "remove-candidate": "❌", "no-data": "·"}[result["verdict"]]
            print(f"  {flag} {result['name']:<35} 调用 {result['invoke']:>3}  命中 {result['hit']:>3}  命中率 {rate_str:>5}")
            if result["verdict"] == "remove-candidate":
                remove_candidates.append(result["name"])
            elif result["verdict"] == "watch":
                watch_list.append(result["name"])
        print()

    if remove_candidates:
        print(f"❌ 移除候选（需告知用户确认）：{', '.join(remove_candidates)}")
    if watch_list:
        print(f"⚠️  观察中：{', '.join(watch_list)}")
    if not remove_candidates and not watch_list:
        print("✅ 所有 skill 状态正常")

if __name__ == "__main__":
    main()
