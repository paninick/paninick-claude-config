#!/usr/bin/env python3
import os
import re
import sys

# Constants
ROOT = os.path.join(os.path.dirname(__file__), "../../../../RuoYi-Vue")
MAPPER_DIR = os.path.join(ROOT, "ruoyi-admin/src/main/resources/mapper/erp")
SERVICE_DIR = os.path.join(ROOT, "ruoyi-admin/src/main/java/com/ruoyi/erp/service/impl")

issues = []

def scan_xml_injections():
    if not os.path.isdir(MAPPER_DIR):
        return
    for root, _, files in os.walk(MAPPER_DIR):
        for file in files:
            if not file.endswith(".xml"): continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find usages of ${} that are NOT params.dataScope or orderByColumn
            # Ignore standard comment blocks or CDATA if necessary, but simple regex is fine
            matches = re.finditer(r'\$\{([^}]+)\}', content)
            for m in matches:
                var = m.group(1).strip()
                if var not in ["params.dataScope", "orderByColumn", "params.factoryDataScope"]:
                    issues.append(f"[安全门禁] {file}: 禁止在 MyBatis 中使用 `${{{var}}}` 进行未经转义的动态注入，请改用 `#{{}}`。")

def scan_del_flag_in_joins():
    if not os.path.isdir(MAPPER_DIR):
        return
    for root, _, files in os.walk(MAPPER_DIR):
        for file in files:
            if not file.endswith(".xml"): continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            selects = re.finditer(r'<select[^>]*>(.*?)</select>', content, re.DOTALL)
            for select in selects:
                select_body = select.group(1)
                # Quick check if join sys_user or sys_dept exists
                if re.search(r'left\s+join\s+sys_(user|dept)', select_body, re.IGNORECASE):
                    if 'del_flag' not in select_body.lower():
                        issues.append(f"[数据门禁] {file}: 检测到关联 sys_user/sys_dept 但未检查 del_flag='0'。")

def scan_datascope_consistency():
    if not os.path.isdir(SERVICE_DIR):
        return
    for root, _, files in os.walk(SERVICE_DIR):
        for file in files:
            if not file.endswith('.java'): continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.finditer(r'@DataScope\([^)]*\)\s*(?:@Override\s*)?(?:public|protected|private)\s+List<[^>]+>\s+([a-zA-Z0-9_]+)\(', content)
            for match in matches:
                method_name = match.group(1)
                xml_file = file.replace('ServiceImpl.java', 'Mapper.xml')
                xml_path = os.path.join(MAPPER_DIR, xml_file)
                if os.path.exists(xml_path):
                    with open(xml_path, 'r', encoding='utf-8') as xf:
                        xml_content = xf.read()
                    
                    select_match = re.search(f'<select\s+id="{method_name}"[^>]*>(.*?)</select>', xml_content, re.DOTALL)
                    if select_match:
                        if '${params.dataScope}' not in select_match.group(1):
                            issues.append(f"[越权门禁] {xml_file} -> {method_name}: Java 层配置了 @DataScope，但 XML 对应查询缺少 `${{params.dataScope}}` 注入。")

if __name__ == "__main__":
    scan_xml_injections()
    scan_del_flag_in_joins()
    scan_datascope_consistency()

    print("=== ERP V4.0 架构纪律静态门禁 ===")
    if not issues:
        print("[OK] 架构规则扫描全部通过。")
        sys.exit(0)
    else:
        for i in set(issues):
            print(f"[ERROR] {i}")
        print(f"\n触发了 {len(set(issues))} 项硬性门禁规则，请修正后重试提交。")
        sys.exit(1)
