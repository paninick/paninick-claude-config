"""
V2 物料批次谱系回归

验证目标：
1. materialBatch 权限链可访问
2. 单出库明细可按 FIFO 自动拆到两个批次
3. syncByStockOut 可按 alloc 生成两条 consume
4. traceForward / traceBackward 在多批次场景可命中真实数据
5. cancelConfirm 后批次余量、alloc、兼容 batch_id 可正确回滚
"""

import datetime as dt
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

import pymysql

BASE = "http://127.0.0.1:8080"
DB = dict(host="localhost", port=3306, user="root", password="", db="ry_vue", charset="utf8mb4")
results = []
SEED = {
    "prefix": "CODEX-V2-MULTI",
    "material_id": 910002,
    "batch_no_1": "CODEX-V2-MULTI-BATCH-001",
    "batch_no_2": "CODEX-V2-MULTI-BATCH-002",
    "stock_out_sn": "CODEX-V2-MULTI-STOCKOUT-001",
    "stock_out_item_sn": "CODEX-V2-MULTI-ITEM-001",
    "serial_no": "CODEX-V2-MULTI-SERIAL-001",
    "material_no": "CODEX-V2-MULTI-MAT-001",
    "material_name": "Codex V2 Multi Yarn Seed",
    "remark": "CODEX_V2_MATERIAL_BATCH_MULTI_REGRESSION",
}


def api(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        return {"code": exc.code, "msg": exc.read().decode("utf-8", "ignore")[:500]}


def check(label, cond, detail=""):
    results.append((label, cond, detail))
    marker = "OK" if cond else "!!"
    print(f"  [{marker}] {label}" + (f": {detail}" if detail else ""))


def as_text_decimal(value):
    if value is None:
        return None
    text = str(value)
    if "." not in text:
        return text + ".00"
    return text


def has_column(cur, table, column):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    return cur.fetchone()[0] > 0


def cleanup_seed(cur):
    cur.execute("DELETE FROM t_erp_product_serial WHERE serial_no = %s OR remark = %s", (SEED["serial_no"], SEED["remark"]))
    cur.execute("DELETE FROM t_erp_produce_material_consume WHERE remark = %s", (SEED["remark"],))
    cur.execute(
        """
        DELETE a
        FROM t_erp_stock_out_item_batch_alloc a
        JOIN t_erp_stock_out_item i ON i.id = a.stock_out_item_id
        WHERE i.remark = %s
        """,
        (SEED["remark"],),
    )
    cur.execute("DELETE FROM t_erp_stock_out_item WHERE sn = %s OR material_no = %s OR remark = %s", (SEED["stock_out_item_sn"], SEED["material_no"], SEED["remark"]))
    cur.execute("DELETE FROM t_erp_stock_out WHERE sn = %s OR remark = %s", (SEED["stock_out_sn"], SEED["remark"]))
    cur.execute("DELETE FROM t_erp_material_batch WHERE batch_no IN (%s, %s) OR remark = %s", (SEED["batch_no_1"], SEED["batch_no_2"], SEED["remark"]))


def select_seed_context(cur):
    cur.execute("SELECT user_id, user_name, dept_id FROM sys_user WHERE user_name = 'admin' LIMIT 1")
    user = cur.fetchone()
    if not user:
        raise RuntimeError("admin 用户不存在，无法构造回归样例")
    _, username, dept_id = user

    cur.execute(
        """
        SELECT id, factory_id, produce_plan_id, order_id, job_no
        FROM t_erp_produce_job
        WHERE produce_plan_id IS NOT NULL
          AND (factory_id = %s OR factory_id IS NULL)
        ORDER BY CASE WHEN factory_id = %s THEN 0 ELSE 1 END, id DESC
        LIMIT 1
        """,
        (dept_id, dept_id),
    )
    job = cur.fetchone()
    if not job:
        raise RuntimeError("缺少可用生产工单样例，无法构造批次谱系回归")

    cur.execute("SELECT id, code, name FROM t_erp_warehouse ORDER BY id DESC LIMIT 1")
    warehouse = cur.fetchone()
    if not warehouse:
        raise RuntimeError("缺少仓库样例，无法构造批次谱系回归")

    return {
        "username": username,
        "factory_id": dept_id,
        "job_id": job[0],
        "job_factory_id": job[1],
        "produce_plan_id": job[2],
        "order_id": job[3] or 900001,
        "job_no": job[4],
        "warehouse_id": warehouse[0],
        "warehouse_code": warehouse[1],
        "warehouse_name": warehouse[2],
    }


def insert_material_batch(cur, ctx, batch_no, qty, remaining_qty, source_item_id):
    now = dt.datetime.now()
    cur.execute(
        """
        INSERT INTO t_erp_material_batch
        (batch_no, material_id, material_type, source_type, source_id, source_item_id,
         qty, remaining_qty, unit, status, warehouse_id, factory_id, remark, create_by, create_time, update_by, update_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            batch_no,
            SEED["material_id"],
            "YARN",
            "MANUAL_SEED",
            ctx["produce_plan_id"],
            source_item_id,
            qty,
            remaining_qty,
            "KG",
            "ACTIVE",
            ctx["warehouse_id"],
            ctx["factory_id"],
            SEED["remark"],
            ctx["username"],
            now,
            ctx["username"],
            now,
        ),
    )
    return cur.lastrowid


def insert_stock_out(cur, ctx):
    now = dt.datetime.now()
    cur.execute(
        """
        INSERT INTO t_erp_stock_out
        (factory_id, src_bill_type, src_bill_id, src_bill_no, sn, out_date, out_type, confirm_status,
         applicant, apply_date, plan_id, out_description, create_by, create_time, update_by, update_time, version, remark)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            ctx["factory_id"],
            "PLAN",
            ctx["produce_plan_id"],
            ctx["job_no"],
            SEED["stock_out_sn"],
            now,
            1,
            "0",
            ctx["username"],
            now,
            ctx["produce_plan_id"],
            SEED["remark"],
            ctx["username"],
            now,
            ctx["username"],
            now,
            0,
            SEED["remark"],
        ),
    )
    return cur.lastrowid


def insert_stock_out_item(cur, ctx, stock_out_id):
    now = dt.datetime.now()
    cur.execute(
        """
        INSERT INTO t_erp_stock_out_item
        (out_id, batch_id, sn, material_id, material_type, material_no, name, count, warehouse_id, create_by, create_time, update_by, update_time, remark)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            stock_out_id,
            None,
            SEED["stock_out_item_sn"],
            SEED["material_id"],
            "1",
            SEED["material_no"],
            SEED["material_name"],
            "7.0000",
            ctx["warehouse_id"],
            ctx["username"],
            now,
            ctx["username"],
            now,
            SEED["remark"],
        ),
    )
    return cur.lastrowid


def insert_product_serial(cur, ctx):
    now = dt.datetime.now()
    cur.execute(
        """
        INSERT INTO t_erp_product_serial
        (factory_id, serial_no, order_id, job_id, produce_plan_id, current_process_id, current_process_name, status, create_time, remark)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            ctx["factory_id"],
            SEED["serial_no"],
            ctx["order_id"],
            ctx["job_id"],
            ctx["produce_plan_id"],
            1,
            "纱线领用",
            "0",
            now,
            SEED["remark"],
        ),
    )
    return cur.lastrowid


def seed_real_chain():
    conn = pymysql.connect(**DB, autocommit=False)
    try:
        cur = conn.cursor()
        cleanup_seed(cur)
        ctx = select_seed_context(cur)
        batch_id_1 = insert_material_batch(cur, ctx, SEED["batch_no_1"], "4.0000", "4.0000", ctx["job_id"])
        batch_id_2 = insert_material_batch(cur, ctx, SEED["batch_no_2"], "6.0000", "6.0000", ctx["job_id"] + 1)
        stock_out_id = insert_stock_out(cur, ctx)
        stock_out_item_id = insert_stock_out_item(cur, ctx, stock_out_id)
        serial_id = insert_product_serial(cur, ctx)
        conn.commit()
        return {
            "ctx": ctx,
            "batch_id_1": batch_id_1,
            "batch_id_2": batch_id_2,
            "stock_out_id": stock_out_id,
            "stock_out_item_id": stock_out_item_id,
            "serial_id": serial_id,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_db_before_confirm(seed_ids):
    conn = pymysql.connect(**DB)
    try:
        cur = conn.cursor()
        cur.execute("SELECT remaining_qty FROM t_erp_material_batch WHERE id = %s", (seed_ids["batch_id_1"],))
        qty1 = cur.fetchone()
        cur.execute("SELECT remaining_qty FROM t_erp_material_batch WHERE id = %s", (seed_ids["batch_id_2"],))
        qty2 = cur.fetchone()
    finally:
        conn.close()
    check("批次1 初始余量为 4", bool(qty1 and as_text_decimal(qty1[0]).startswith("4.0")), f"qty={qty1[0] if qty1 else None}")
    check("批次2 初始余量为 6", bool(qty2 and as_text_decimal(qty2[0]).startswith("6.0")), f"qty={qty2[0] if qty2 else None}")


def verify_after_confirm(seed_ids):
    conn = pymysql.connect(**DB)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT batch_id, batch_no, alloc_qty
            FROM t_erp_stock_out_item_batch_alloc
            WHERE stock_out_item_id = %s
            ORDER BY id ASC
            """,
            (seed_ids["stock_out_item_id"],),
        )
        allocs = cur.fetchall()
        cur.execute(
            "SELECT batch_id FROM t_erp_stock_out_item WHERE id = %s",
            (seed_ids["stock_out_item_id"],),
        )
        compat_batch = cur.fetchone()
        cur.execute(
            """
            SELECT batch_id, actual_qty
            FROM t_erp_produce_material_consume
            WHERE stock_out_item_id = %s
            ORDER BY batch_id ASC
            """,
            (seed_ids["stock_out_item_id"],),
        )
        consumes = cur.fetchall()
        cur.execute("SELECT remaining_qty, status FROM t_erp_material_batch WHERE id = %s", (seed_ids["batch_id_1"],))
        batch1 = cur.fetchone()
        cur.execute("SELECT remaining_qty, status FROM t_erp_material_batch WHERE id = %s", (seed_ids["batch_id_2"],))
        batch2 = cur.fetchone()
    finally:
        conn.close()

    alloc_ok = (
        len(allocs) == 2
        and allocs[0][0] == seed_ids["batch_id_1"]
        and as_text_decimal(allocs[0][2]).startswith("4.0")
        and allocs[1][0] == seed_ids["batch_id_2"]
        and as_text_decimal(allocs[1][2]).startswith("3.0")
    )
    check("FIFO 自动拆成两条 alloc", alloc_ok, f"allocs={allocs}")
    check(
        "stock_out_item.batch_id 兼容指向首批次",
        bool(compat_batch and compat_batch[0] == seed_ids["batch_id_1"]),
        f"batchId={compat_batch[0] if compat_batch else None}",
    )
    consume_ok = (
        len(consumes) == 2
        and consumes[0][0] == seed_ids["batch_id_1"]
        and as_text_decimal(consumes[0][1]).startswith("4.0")
        and consumes[1][0] == seed_ids["batch_id_2"]
        and as_text_decimal(consumes[1][1]).startswith("3.0")
    )
    check("syncByStockOut 生成两条多批次 consume", consume_ok, f"consumes={consumes}")
    check("批次1 扣减后变 0 且 CONSUMED", bool(batch1 and as_text_decimal(batch1[0]).startswith("0.0") and batch1[1] == "CONSUMED"), f"row={batch1}")
    check("批次2 扣减后余量为 3", bool(batch2 and as_text_decimal(batch2[0]).startswith("3.0")), f"row={batch2}")


def verify_after_cancel(seed_ids):
    conn = pymysql.connect(**DB)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM t_erp_stock_out_item_batch_alloc WHERE stock_out_item_id = %s", (seed_ids["stock_out_item_id"],))
        alloc_count = cur.fetchone()[0]
        cur.execute("SELECT batch_id FROM t_erp_stock_out_item WHERE id = %s", (seed_ids["stock_out_item_id"],))
        compat_batch = cur.fetchone()
        cur.execute("SELECT remaining_qty, status FROM t_erp_material_batch WHERE id = %s", (seed_ids["batch_id_1"],))
        batch1 = cur.fetchone()
        cur.execute("SELECT remaining_qty, status FROM t_erp_material_batch WHERE id = %s", (seed_ids["batch_id_2"],))
        batch2 = cur.fetchone()
    finally:
        conn.close()

    check("cancelConfirm 后 alloc 已清空", alloc_count == 0, f"allocCount={alloc_count}")
    check("cancelConfirm 后兼容 batch_id 已清空", bool(compat_batch and compat_batch[0] is None), f"batchId={compat_batch[0] if compat_batch else None}")
    check("cancelConfirm 后批次1 余量回滚到 4", bool(batch1 and as_text_decimal(batch1[0]).startswith("4.0") and batch1[1] == "ACTIVE"), f"row={batch1}")
    check("cancelConfirm 后批次2 余量回滚到 6", bool(batch2 and as_text_decimal(batch2[0]).startswith("6.0") and batch2[1] == "ACTIVE"), f"row={batch2}")


def main():
    print("=== V2 物料批次谱系回归（多批次/FIFO）===\n")

    login = api("POST", "/login", {"username": "admin", "password": "admin123"})
    if login.get("code") != 200:
        print("FATAL: 登录失败")
        sys.exit(1)
    token = login["token"]

    list_resp = api("GET", "/erp/materialBatch/list?pageNum=1&pageSize=5", token=token)
    check("materialBatch 列表接口可访问", list_resp.get("code") == 200, str(list_resp.get("msg", ""))[:60])

    seed_ids = seed_real_chain()
    check(
        "已构造多批次样例骨架",
        all(seed_ids.get(key) for key in ("batch_id_1", "batch_id_2", "stock_out_id", "stock_out_item_id", "serial_id")),
        f"stockOutId={seed_ids['stock_out_id']}, serialId={seed_ids['serial_id']}",
    )
    verify_db_before_confirm(seed_ids)

    confirm_resp = api("PUT", f"/erp/stockOut/confirm/{seed_ids['stock_out_id']}", token=token)
    check("stockOut confirm 成功", confirm_resp.get("code") == 200, str(confirm_resp.get("msg", ""))[:120])

    sync_resp = api("POST", f"/erp/materialconsume/syncByStockOut/{seed_ids['stock_out_id']}", token=token)
    sync_data = sync_resp.get("data") or {}
    check(
        "syncByStockOut 成功且生成 2 条用料",
        sync_resp.get("code") == 200 and int(sync_data.get("insertedCount", 0)) == 2,
        str(sync_data),
    )
    verify_after_confirm(seed_ids)

    forward_1 = api("GET", f"/erp/materialBatch/trace/forward?batchId={seed_ids['batch_id_1']}", token=token)
    rows_1 = forward_1.get("data") or []
    hit_1 = any(str(row.get("serial_no")) == SEED["serial_no"] for row in rows_1 if isinstance(row, dict))
    check("traceForward 命中批次1 样例", forward_1.get("code") == 200 and hit_1, f"rows={len(rows_1)}")

    forward_2 = api("GET", f"/erp/materialBatch/trace/forward?batchId={seed_ids['batch_id_2']}", token=token)
    rows_2 = forward_2.get("data") or []
    hit_2 = any(str(row.get("serial_no")) == SEED["serial_no"] for row in rows_2 if isinstance(row, dict))
    check("traceForward 命中批次2 样例", forward_2.get("code") == 200 and hit_2, f"rows={len(rows_2)}")

    backward = api("GET", f"/erp/materialBatch/trace/backward?serialId={seed_ids['serial_id']}", token=token)
    backward_rows = backward.get("data") or []
    backward_batch_nos = sorted(str(row.get("batch_no")) for row in backward_rows if isinstance(row, dict))
    check(
        "traceBackward 反查到两个原料批次",
        backward.get("code") == 200 and backward_batch_nos == sorted([SEED["batch_no_1"], SEED["batch_no_2"]]),
        f"batchNos={backward_batch_nos}",
    )

    cancel_resp = api("PUT", f"/erp/stockOut/cancelConfirm/{seed_ids['stock_out_id']}", token=token)
    check("stockOut cancelConfirm 成功", cancel_resp.get("code") == 200, str(cancel_resp.get("msg", ""))[:120])
    verify_after_cancel(seed_ids)

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print(f"\n=== 汇总: PASS {passed}/{len(results)} ===")
    if failed:
        for label, ok, detail in results:
            if not ok:
                print(f"  - {label}: {detail}")
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
