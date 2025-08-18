import csv
import json
import os
from wsgiref.simple_server import make_server

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'iris.csv')

def load_data():
    with open(DATA_FILE, newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

DATA = load_data()

# Precompute counts per species for chart
COUNTS = {}
for row in DATA:
    COUNTS[row['species']] = COUNTS.get(row['species'], 0) + 1

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
    <meta charset='utf-8'>
    <title>Iris Dashboard</title>
    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
</head>
<body>
    <h1>Iris Species Count</h1>
    <canvas id='chart'></canvas>
    <script>
    const labels = {labels};
    const values = {values};
    new Chart(document.getElementById('chart').getContext('2d'), {{
        type: 'bar',
        data: {{
            labels: labels,
            datasets: [{{ label: 'Count', data: values }}]
        }},
        options: {{responsive: true}}
    }});
    </script>
</body>
</html>"""


def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    if path == '/data':
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(DATA).encode('utf-8')]
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    labels = list(COUNTS.keys())
    values = [COUNTS[label] for label in labels]
    html = HTML_TEMPLATE.format(labels=json.dumps(labels), values=json.dumps(values))
    return [html.encode('utf-8')]


if __name__ == '__main__':
    with make_server('', 8000, app) as server:
        print('Serving on http://localhost:8000')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Server stopped')
