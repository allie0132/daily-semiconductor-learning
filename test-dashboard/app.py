"""Flask backend for the semiconductor test dashboard."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, request
import mock_data as md

app = Flask(__name__)
md.init_db()   # no-op if DB already exists


def _where(args, table="w"):
    """Build SQL WHERE clause + params for wafers table queries."""
    clauses, params = [], []
    t = f"{table}."

    date_from = args.get("date_from", "")
    date_to   = args.get("date_to",   "")
    if date_from:
        clauses.append(f"{t}test_date >= ?"); params.append(date_from)
    if date_to:
        clauses.append(f"{t}test_date <= ?"); params.append(date_to)

    for col in ("product", "tp_rev", "test_step", "proc_node", "tester", "socket"):
        val = args.get(col, "ALL")
        if val and val != "ALL":
            clauses.append(f"{t}{col} = ?"); params.append(val)

    lot = args.get("lot", "ALL")
    if lot and lot != "ALL":
        clauses.append(f"{t}lot_id = ?"); params.append(lot)

    sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return sql, params


def _where_tr(args):
    """Build JOIN+WHERE for test_results queries (joins with lots for metadata)."""
    clauses, params = [], []

    date_from = args.get("date_from", "")
    date_to   = args.get("date_to",   "")
    if date_from:
        clauses.append("tr.test_date >= ?"); params.append(date_from)
    if date_to:
        clauses.append("tr.test_date <= ?"); params.append(date_to)

    # lots table has product, tp_rev, test_step, proc_node
    for col in ("product", "tp_rev", "test_step", "proc_node"):
        val = args.get(col, "ALL")
        if val and val != "ALL":
            clauses.append(f"l.{col} = ?"); params.append(val)

    lot = args.get("lot", "ALL")
    if lot and lot != "ALL":
        clauses.append("tr.lot_id = ?"); params.append(lot)

    join_sql = "JOIN lots l ON tr.lot_id = l.lot_id"
    if clauses:
        join_sql += " WHERE " + " AND ".join(clauses)
    return join_sql, params


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/meta")
def api_meta():
    conn = md.get_conn()
    c    = conn.cursor()
    def vals(col):
        return [r[0] for r in c.execute(
            f"SELECT DISTINCT {col} FROM wafers ORDER BY {col}")]
    products   = vals("product")
    tp_revs    = vals("tp_rev")
    test_steps = vals("test_step")
    proc_nodes = vals("proc_node")
    testers    = vals("tester")
    sockets    = vals("socket")
    dr = dict(c.execute(
        "SELECT MIN(test_date) AS min_d, MAX(test_date) AS max_d FROM wafers"
    ).fetchone())
    lots = [dict(r) for r in c.execute(
        "SELECT lot_id, product, tp_rev, test_step, proc_node, yield_pct, start_date "
        "FROM lots ORDER BY start_date DESC LIMIT 200"
    )]
    conn.close()
    return jsonify({
        "products":   products,
        "tp_revs":    tp_revs,
        "test_steps": test_steps,
        "proc_nodes": proc_nodes,
        "testers":    testers,
        "sockets":    sockets,
        "date_min":   dr["min_d"],
        "date_max":   dr["max_d"],
        "lots":       lots,
    })


@app.route("/api/summary")
def api_summary():
    where, params = _where(request.args)
    conn = md.get_conn()
    row  = conn.execute(
        f"SELECT COUNT(DISTINCT w.lot_id), COUNT(*), SUM(w.total_dies), "
        f"SUM(w.pass_dies), SUM(w.fail_dies), AVG(w.yield_pct), AVG(w.test_time_s) "
        f"FROM wafers w {where}", params
    ).fetchone()
    conn.close()
    if not row or not row[1]:
        return jsonify({"lots":0,"wafers":0,"total_dies":0,"pass_dies":0,
                        "fail_dies":0,"yield_pct":0,"avg_test_time_s":0})
    total  = row[2] or 0
    passed = row[3] or 0
    return jsonify({
        "lots":            row[0],
        "wafers":          row[1],
        "total_dies":      total,
        "pass_dies":       passed,
        "fail_dies":       total - passed,
        "yield_pct":       round(passed / total * 100, 2) if total else 0,
        "avg_test_time_s": round(row[6] or 0, 1),
    })


@app.route("/api/yield_trend")
def api_yield_trend():
    where, params = _where(request.args)
    group_by = request.args.get("group_by", "date")
    conn     = md.get_conn()

    if group_by == "lot":
        rows = conn.execute(
            f"SELECT w.lot_id, AVG(w.yield_pct) FROM wafers w {where} "
            f"GROUP BY w.lot_id ORDER BY MIN(w.test_date) LIMIT 60", params
        ).fetchall()
        result = [{"label": r[0], "yield_pct": round(r[1], 2)} for r in rows]
    else:
        rows = conn.execute(
            f"SELECT w.test_date, AVG(w.yield_pct) FROM wafers w {where} "
            f"GROUP BY w.test_date ORDER BY w.test_date", params
        ).fetchall()
        result = [{"label": r[0], "yield_pct": round(r[1], 2)} for r in rows]

    conn.close()
    return jsonify(result)


@app.route("/api/top_fail_tests")
def api_top_fail():
    join_where, params = _where_tr(request.args)
    n    = min(int(request.args.get("n", 30)), len(md.TEST_DEFS))
    conn = md.get_conn()
    rows = conn.execute(
        f"SELECT tr.test_name, tr.category, tr.unit, tr.bin, "
        f"SUM(tr.fail_count) AS fc, SUM(tr.total_count) AS tc, AVG(tr.avg_time_ms) "
        f"FROM test_results tr {join_where} "
        f"GROUP BY tr.test_name ORDER BY fc DESC LIMIT ?",
        params + [n]
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        tc = r[5] or 1
        out.append({
            "name": r[0], "category": r[1], "unit": r[2], "bin": r[3],
            "fail_count": r[4], "total_count": tc,
            "fail_rate":  round(r[4] / tc * 100, 3),
            "avg_time_ms": round(r[6], 1),
        })
    return jsonify(out)


@app.route("/api/top_time_tests")
def api_top_time():
    join_where, params = _where_tr(request.args)
    n    = min(int(request.args.get("n", 30)), len(md.TEST_DEFS))
    conn = md.get_conn()
    rows = conn.execute(
        f"SELECT tr.test_name, tr.category, tr.unit, tr.bin, "
        f"SUM(tr.fail_count) AS fc, SUM(tr.total_count) AS tc, AVG(tr.avg_time_ms) AS atm "
        f"FROM test_results tr {join_where} "
        f"GROUP BY tr.test_name ORDER BY atm DESC LIMIT ?",
        params + [n]
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        tc = r[5] or 1
        out.append({
            "name": r[0], "category": r[1], "unit": r[2], "bin": r[3],
            "fail_count": r[4], "total_count": tc,
            "fail_rate":  round(r[4] / tc * 100, 3),
            "avg_time_ms": round(r[6], 1),
        })
    return jsonify(out)


@app.route("/api/bin_summary")
def api_bin_summary():
    join_where, params = _where_tr(request.args)
    conn = md.get_conn()
    rows = conn.execute(
        f"SELECT tr.bin, SUM(tr.fail_count) FROM test_results tr {join_where} GROUP BY tr.bin",
        params
    ).fetchall()
    conn.close()
    result = {}
    for r in rows:
        b = r[0]
        result[b] = {
            "label": md.BINS.get(b, {}).get("label", b),
            "color": md.BINS.get(b, {}).get("color", "#666"),
            "count": r[1],
        }
    return jsonify(result)


@app.route("/api/wafer_map")
def api_wafer_map():
    where, params = _where(request.args)
    conn     = md.get_conn()
    # default: last lot's first wafer
    lot_id   = request.args.get("lot", "")
    wafer_id = request.args.get("wafer", "W01")
    if not lot_id:
        row = conn.execute("SELECT lot_id FROM lots ORDER BY start_date DESC LIMIT 1").fetchone()
        lot_id = row[0] if row else "LOT2026001"
    row = conn.execute(
        "SELECT yield_pct FROM wafers WHERE lot_id=? AND wafer_id=?",
        (lot_id, wafer_id)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(md.generate_wafer_map(lot_id, wafer_id, row[0]))


@app.route("/api/wafers_in_lot")
def api_wafers_in_lot():
    lot_id = request.args.get("lot", "")
    conn   = md.get_conn()
    rows   = conn.execute(
        "SELECT DISTINCT wafer_id FROM wafers WHERE lot_id=? ORDER BY wafer_id",
        (lot_id,)
    ).fetchall()
    conn.close()
    return jsonify([r[0] for r in rows])


@app.route("/api/lots")
def api_lots():
    """Filtered lot list (respects date/product/etc. filters)."""
    where, params = _where(request.args)
    conn  = md.get_conn()
    rows  = conn.execute(
        f"SELECT DISTINCT w.lot_id, l.product, l.tp_rev, l.test_step, "
        f"l.proc_node, l.yield_pct, l.start_date "
        f"FROM wafers w JOIN lots l ON w.lot_id = l.lot_id {where} "
        f"ORDER BY l.start_date DESC LIMIT 200", params
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    print("Starting dashboard on http://localhost:5001")
    app.run(debug=True, port=5001)
