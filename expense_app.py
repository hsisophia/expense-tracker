"""Member A - Web UI for the expense tracker (standard library only).

Run:  python expense_app.py   then open http://127.0.0.1:8000
"""
import html
import io
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import expense_chart
from expense_input import delete_expense, load_expenses, parse_amount, parse_date, save_expense

PORT = 8000


def fmt_amount(value):
    v = float(value)
    return f"{v:,.0f}" if v == int(v) else f"{v:,.1f}"

CSS = """
:root{--bg:#f4f3ef;--card:#fff;--ink:#0b0b0b;--ink2:#52514e;--line:#e4e3dd;--blue:#2a78d6;--red:#e34948}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,"Segoe UI","Noto Sans TC","PingFang TC",sans-serif}
header{padding:28px 32px 8px}h1{margin:0;font-size:26px}header p{margin:2px 0 0;color:var(--ink2)}
main{max-width:1100px;margin:0 auto;padding:12px 24px 40px;display:grid;gap:18px;grid-template-columns:340px 1fr}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}
.stats{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.stat small{color:var(--ink2);text-transform:uppercase;letter-spacing:.06em;font-size:12px}
.stat b{display:block;font-size:28px;margin-top:4px}
h2{margin:0 0 14px;font-size:17px}label{display:block;font-size:13px;color:var(--ink2);margin:12px 0 4px}
input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:9px;font:inherit}
input:focus{outline:2px solid var(--blue);border-color:transparent}
button{margin-top:18px;width:100%;padding:11px;border:0;border-radius:9px;background:var(--blue);
color:#fff;font:inherit;font-weight:600;cursor:pointer}button:hover{filter:brightness(1.08)}
.err{background:#fdecec;color:#a02424;border-radius:9px;padding:9px 12px;margin-bottom:6px;font-size:14px}
.tabs{display:flex;gap:8px;margin-bottom:12px}.tabs a{padding:6px 14px;border-radius:99px;text-decoration:none;
color:var(--ink2);border:1px solid var(--line);font-size:14px}.tabs a.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.chart img{width:100%;height:auto;display:block}.empty{color:var(--ink2);padding:40px 0;text-align:center}
.wide{grid-column:1/-1}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px 8px;
border-bottom:1px solid var(--line)}th{font-size:12px;color:var(--ink2);text-transform:uppercase;letter-spacing:.05em}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
button.del{margin:0;width:auto;padding:4px 12px;background:#fff;color:var(--red);border:1px solid var(--line);font-weight:500}
button.del:hover{background:#fdecec;filter:none}td.act{text-align:right;width:1%}
@media(max-width:820px){main{grid-template-columns:1fr}.stats{grid-template-columns:1fr}}
"""


def render_page(error="", chart="pie"):
    expenses = load_expenses()
    totals = expense_chart.totals_by_category(expenses) if expenses else {}
    total = sum(totals.values())
    top = next(iter(totals), "-")
    rows = "".join(
        f"<tr><td>{html.escape(e['date'])}</td><td>{html.escape(e['category'])}</td>"
        f"<td class='n'>{fmt_amount(e['amount'])}</td><td>{html.escape(e.get('notes') or '')}</td>"
        f"<td class='act'><form method='post' action='/delete' onsubmit=\"return confirm('Delete this expense?')\">"
        f"<input type='hidden' name='index' value='{i}'><button class='del'>Delete</button></form></td></tr>"
        for i, e in reversed(list(enumerate(expenses))[-15:]))
    err = f"<div class='err'>{html.escape(error)}</div>" if error else ""
    if expenses:
        tabs = "".join(f"<a href='/?chart={k}' class='{'on' if chart == k else ''}'>{n}</a>"
                       for k, n in (("pie", "Donut chart"), ("bar", "Bar chart")))
        chart_html = f"<div class='tabs'>{tabs}</div><img src='/chart.png?kind={chart}&n={len(expenses)}' alt='chart'>"
    else:
        chart_html = "<div class='empty'>No data yet. Add your first expense on the left.</div>"
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Expense Tracker</title><style>{CSS}</style>
<header><h1>Expense Tracker</h1><p>Add expenses and see where your money goes.</p></header>
<main>
<section class="stats">
<div class="card stat"><small>Total spent</small><b>{total:,.0f}</b></div>
<div class="card stat"><small>Records</small><b>{len(expenses)}</b></div>
<div class="card stat"><small>Top category</small><b>{html.escape(top)}</b></div></section>
<section class="card"><h2>Add expense</h2>{err}
<form method="post" action="/add">
<label>Date</label><input type="date" name="date" required>
<label>Amount</label><input type="number" name="amount" step="0.1" min="0.1" placeholder="e.g. 120 or 45.5" required>
<label>Category</label><input name="category" list="cats" placeholder="Food, Transport..." required>
<datalist id="cats"><option>Food<option>Transport<option>Shopping<option>Entertainment<option>Education</datalist>
<label>Notes (optional)</label><input name="notes" placeholder="Lunch with friends">
<button>Add expense</button></form>
<script>document.querySelector('input[type=date]').valueAsDate=new Date()</script></section>
<section class="card chart"><h2>Spending by category</h2>{chart_html}</section>
<section class="card wide"><h2>Recent expenses</h2>
<table><tr><th>Date</th><th>Category</th><th class="n">Amount</th><th>Notes</th><th></th></tr>{rows}</table></section>
</main></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, ctype="text/html; charset=utf-8", status=200):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == "/chart.png":
            expenses = load_expenses()
            if not expenses:
                return self._send("no data", "text/plain", 404)
            totals = expense_chart.totals_by_category(expenses)
            fn = expense_chart.make_bar if q.get("kind", ["pie"])[0] == "bar" else expense_chart.make_pie
            buf = io.BytesIO()
            fn(totals, buf)
            return self._send(buf.getvalue(), "image/png")
        if url.path == "/":
            return self._send(render_page(chart=q.get("chart", ["pie"])[0]))
        self._send("not found", "text/plain", 404)

    def do_POST(self):
        if self.path not in ("/add", "/delete"):
            return self._send("not found", "text/plain", 404)
        form = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode())
        get = lambda k: form.get(k, [""])[0].strip()
        if self.path == "/delete":
            try:
                delete_expense(int(get("index")))
            except (ValueError, IndexError):
                pass
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
            return
        try:
            save_expense({"date": parse_date(get("date")), "amount": parse_amount(get("amount")),
                          "category": get("category") or "Other", "notes": get("notes")})
        except ValueError as e:
            return self._send(render_page(error=f"Invalid input: {e}"), status=400)
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Expense Tracker running at {url}  (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBye!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
