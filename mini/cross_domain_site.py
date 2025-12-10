from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>External Site (Cross Domain)</title>
    <style>
        body {
            font-family: Arial;
            background: #eef;
            padding: 30px;
        }
        .box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            max-width: 600px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        h1 { margin-top: 0; }
    </style>
</head>
<body>

<div class="box">
    <h1>Cross Domain Demo Site</h1>
    <p>This page is hosted on <b>another port/server/domain</b>.</p>
    <p>But it loads the pixel tracker from <b>http://192.168.4.48:5000</b>.</p>
    <p>Every 5 seconds + on tab close, pixel events are sent.</p>
    <p>Check your Admin Dashboard → Live Events to see logs.</p>
</div>

<!-- Load cross-domain pixel tracker -->
<script src="http://192.168.139.48:5000/static/cross_tracker.js"></script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
