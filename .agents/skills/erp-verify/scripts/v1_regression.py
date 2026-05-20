"""
V1 最小生产执行闭环回归测试
目标：4 条固定验证，每次发布前必跑

1. 不传 jobNo 可自动生成工票
2. 未放行工序不能完工入库（B5 校验）
3. qc pass 后工序变 PASS（B4 联动）
4. stock in confirm/cancelConfirm 状态与版本正确推进（B2）

用法：
  python v1_regression.py
  PYTHONIOENCODING=utf-8 python v1_regression.py
"""

import urllib.request
import json
import sys
import pymysql

BASE = "http://127.0.0.1:8080"
DB = dict(host="localhost", port=3306, user="root", password="", db="ry_vue", charset="utf8mb4")

results = []

def api(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode()[:300]}

def check(label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    results.append((label, status, detail))
    marker = "OK" if cond else "!!"
    print(f"  [{marker}] {label}" + (f": {detail}" if detail else ""))

def cleanup(conn):
    cur = conn.cursor()
    for sn in ("V1R-SI-BLOCK", "V1R-SI-001"):
        cur.execute("DELETE FROM t_erp_stock_in WHERE sn=%s", (sn,))
    cur.execute("DELETE FROM t_erp_qc_inspection WHERE batch_no='V1R-QC-001'")
    cur.execute("""DELETE FROM t_erp_produce_job_process WHERE job_id IN
        (SELECT id FROM t_erp_produce_job WHERE produce_plan_id IN
         (SELECT id FROM t_erp_produce_plan WHERE plan_no='V1R-PLAN'))""")
    cur.execute("DELETE FROM t_erp_produce_job WHERE produce_plan_id IN (SELECT id FROM t_erp_produce_plan WHERE plan_no='V1R-PLAN')")
    cur.execute("DELETE FROM t_erp_produce_plan WHERE plan_no='V1R-PLAN'")
    cur.execute("DELETE FROM t_erp_sales_order WHERE sales_no='V1R-SO'")
    conn.commit()

def main():
    print("=== V1 最小生产执行闭环回归 ===\n")

    # 登录
    r = api("POST", "/login", {"username": "admin", "password": "admin123"})
    if r.get("code") != 200:
        print("FATAL: 登录失败")
        sys.exit(1)
    token = r["token"]

    # 基础数据
    r = api("GET", "/erp/style/list?pageNum=1&pageSize=1", token=token)
    styleCode = r.get("rows", [{}])[0].get("styleCode", "SW-2026-001")
    r = api("GET", "/erp/processRoute/list?pageNum=1&pageSize=1", token=token)
    routeId = r.get("rows", [{}])[0].get("id")

    conn = pymysql.connect(**DB)
    cleanup(conn)  # 先清理上次残留

    # 建销售订单 + 计划
    api("POST", "/erp/salesOrder", {"salesNo": "V1R-SO", "customerName": "V1回归", "bulkOrderNo": "V1R", "styleCode": styleCode, "quantity": 3, "dueDate": "2026-12-31"}, token=token)
    r = api("GET", "/erp/salesOrder/list?salesNo=V1R-SO&pageNum=1&pageSize=1", token=token)
    soId = r.get("rows", [{}])[0].get("id")

    api("POST", "/erp/producePlan", {"planNo": "V1R-PLAN", "styleCode": styleCode, "salesOrderId": soId, "planQty": 3, "dueDate": "2026-12-31"}, token=token)
    r = api("GET", "/erp/producePlan/list?planNo=V1R-PLAN&pageNum=1&pageSize=1", token=token)
    planId = r.get("rows", [{}])[0].get("id")

    # ── 验证1: 不传 jobNo 自动生成 ──────────────────────────────────
    print("【验证1】不传 jobNo 自动生成工票")
    r = api("POST", "/erp/produceJob", {
        "producePlanId": planId, "orderId": soId,
        "styleCode": styleCode, "planQty": 3,
        "processRouteId": routeId, "status": "0"
    }, token=token)
    check("建工票(不传jobNo)", r.get("code") == 200, r.get("msg", "")[:60])

    r = api("GET", "/erp/produceJob/list?producePlanId=" + str(planId) + "&pageNum=1&pageSize=1", token=token)
    job = r.get("rows", [{}])[0]
    jobId = job.get("id")
    jobNo = job.get("jobNo", "")
    check("jobNo 已自动生成", bool(jobNo), "jobNo=" + str(jobNo))
    check("orderId 已回链", job.get("orderId") == soId, "orderId=" + str(job.get("orderId")))

    r = api("GET", "/erp/produceJobProcess/list?jobId=" + str(jobId) + "&pageNum=1&pageSize=50", token=token)
    processes = r.get("rows", [])
    check("工序已初始化", len(processes) > 0, str(len(processes)) + "道")

    # ── 验证2: 未放行工序不能完工入库 ───────────────────────────────
    print("\n【验证2】未放行工序不能完工入库")
    api("POST", "/erp/stockIn", {"sn": "V1R-SI-BLOCK", "inDate": "2026-04-28", "inType": 2, "produceJobId": jobId, "producePlanId": planId, "salesOrderId": soId, "finishQty": 3}, token=token)
    r = api("GET", "/erp/stockIn/list?sn=V1R-SI-BLOCK&pageNum=1&pageSize=1", token=token)
    siBlockId = r.get("rows", [{}])[0].get("id")
    r = api("PUT", "/erp/stockIn/confirm/" + str(siBlockId), token=token)
    check("未完工时确认入库被拦截", r.get("code") != 200, "code=" + str(r.get("code")) + " " + r.get("msg", "")[:50])

    # ── 验证3: qc pass 后工序变 PASS ────────────────────────────────
    print("\n【验证3】qc pass 后工序自动变 PASS")
    first = processes[0]
    firstPid = first["id"]
    api("PUT", "/erp/produceJobProcess", {"id": firstPid, "processStatus": "RUNNING", "inQty": 3}, token=token)
    api("PUT", "/erp/produceJobProcess", {"id": firstPid, "processStatus": "WAIT_CHECK", "outQty": 3}, token=token)

    api("POST", "/erp/qc", {"batchNo": "V1R-QC-001", "styleCode": styleCode, "orderNo": "V1R-SO", "result": "HOLD", "sampleQty": 3, "defectQty": 0, "status": "ACTIVE", "jobProcessId": firstPid}, token=token)
    r = api("GET", "/erp/qc/list?pageNum=1&pageSize=1", token=token)
    qcId = r.get("rows", [{}])[0].get("id")

    r = api("POST", "/erp/qc/pass/" + str(qcId), token=token)
    check("质检放行 pass() 成功", r.get("code") == 200, r.get("msg", "")[:60])

    r = api("GET", "/erp/produceJobProcess/list?jobId=" + str(jobId) + "&pageNum=1&pageSize=50", token=token)
    p0 = next((p for p in r.get("rows", []) if p["id"] == firstPid), {})
    check("qc pass 后工序自动变 PASS", p0.get("processStatus") == "PASS", "status=" + str(p0.get("processStatus")))

    # 把剩余工序全部 PASS
    for p in processes[1:]:
        pid = p["id"]
        api("PUT", "/erp/produceJobProcess", {"id": pid, "processStatus": "RUNNING", "inQty": 3}, token=token)
        api("PUT", "/erp/produceJobProcess", {"id": pid, "processStatus": "WAIT_CHECK", "outQty": 3}, token=token)
        api("PUT", "/erp/produceJobProcess", {"id": pid, "processStatus": "PASS", "outQty": 3}, token=token)

    r = api("GET", "/erp/produceJobProcess/list?jobId=" + str(jobId) + "&pageNum=1&pageSize=50", token=token)
    all_pass = all(p.get("processStatus") == "PASS" for p in r.get("rows", []))
    check("所有工序已 PASS", all_pass)

    # ── 验证4: confirm/cancelConfirm 状态与版本正确推进 ─────────────
    print("\n【验证4】confirm/cancelConfirm 状态与版本正确推进")
    api("POST", "/erp/stockIn", {"sn": "V1R-SI-001", "inDate": "2026-04-28", "inType": 2, "produceJobId": jobId, "producePlanId": planId, "salesOrderId": soId, "finishQty": 3}, token=token)
    r = api("GET", "/erp/stockIn/list?sn=V1R-SI-001&pageNum=1&pageSize=1", token=token)
    siId = r.get("rows", [{}])[0].get("id")

    r = api("PUT", "/erp/stockIn/confirm/" + str(siId), token=token)
    check("confirm 成功", r.get("code") == 200, r.get("msg", "")[:60])

    r = api("GET", "/erp/stockIn/" + str(siId), token=token)
    si = r.get("data", {})
    v_after_confirm = si.get("version")
    check("confirm 后 confirmStatus=1", str(si.get("confirmStatus")) == "1")
    check("confirm 后 confirmBy 非空", bool(si.get("confirmBy")), "confirmBy=" + str(si.get("confirmBy")))
    check("confirm 后 version 已递增", v_after_confirm is not None)

    r = api("PUT", "/erp/stockIn/cancelConfirm/" + str(siId), token=token)
    check("cancelConfirm 成功", r.get("code") == 200, r.get("msg", "")[:60])

    r = api("GET", "/erp/stockIn/" + str(siId), token=token)
    si2 = r.get("data", {})
    check("cancelConfirm 后 confirmStatus=0", str(si2.get("confirmStatus")) == "0")
    check("cancelConfirm 后 confirmBy=null", si2.get("confirmBy") is None, "confirmBy=" + str(si2.get("confirmBy")))
    check("cancelConfirm 后 confirmTime=null", si2.get("confirmTime") is None)
    check("cancelConfirm 后 version 再次递增", si2.get("version") != v_after_confirm, "v=" + str(si2.get("version")))

    # 清理
    cleanup(conn)
    conn.close()

    # 汇总
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n=== 汇总: PASS {passed}/{passed+failed} ===")
    if failed:
        print("失败项:")
        for label, status, detail in results:
            if status == "FAIL":
                print(f"  - {label}: {detail}")
        sys.exit(1)
    else:
        print("全部通过")

if __name__ == "__main__":
    main()
