import sqlite3
import pandas as pd
from flask import Flask, render_template_string, send_file

app = Flask(__name__)
DB = "results.db"

PAGE = """
<!doctype html>
<html>
<head>
  <title>OCR Results</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; }
    table { border-collapse: collapse; margin-bottom: 30px; }
    th, td { border: 1px solid #ccc; padding: 8px 14px; text-align: left; }
    th { background: #f0f0f0; }
    a.btn { display: inline-block; margin-bottom: 15px; padding: 8px 14px;
            background: #2563eb; color: white; text-decoration: none; border-radius: 4px; }
  </style>
</head>
<body>
  <h2>OCR Results (chalk markings on steel bars)</h2>
  <a class="btn" href="/download">Download Excel report</a>

  <h3>Most frequent readings</h3>
  <table>
    <tr><th>Video</th><th>Text</th><th>Times seen</th><th>Avg confidence</th></tr>
    {% for r in summary %}
    <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ "%.2f"|format(r[3]) }}</td></tr>
    {% endfor %}
  </table>

  <h3>All readings ({{ rows|length }})</h3>
  <table>
    <tr><th>ID</th><th>Video</th><th>Time (s)</th><th>Text</th><th>Confidence</th></tr>
    {% for r in rows %}
    <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ r[3] }}</td><td>{{ "%.2f"|format(r[4]) }}</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""

ALL = "SELECT id, video, timestamp, text, confidence FROM ocr_results ORDER BY video, timestamp, id"
SUMMARY = """
SELECT video, text, COUNT(*) AS times_seen, AVG(confidence) AS avg_conf
FROM ocr_results GROUP BY video, text ORDER BY times_seen DESC, avg_conf DESC
"""

@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    rows = conn.execute(ALL).fetchall()
    summary = conn.execute(SUMMARY).fetchall()
    conn.close()
    return render_template_string(PAGE, rows=rows, summary=summary)

@app.route("/download")
def download():
    conn = sqlite3.connect(DB)
    df_all = pd.read_sql_query(ALL, conn)
    df_sum = pd.read_sql_query(SUMMARY, conn)
    conn.close()
    with pd.ExcelWriter("report.xlsx") as w:
        df_all.to_excel(w, sheet_name="All readings", index=False)
        df_sum.to_excel(w, sheet_name="Summary", index=False)
    return send_file("report.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)