from flask import (
    Flask, request, jsonify, render_template_string,
    make_response, redirect, session, url_for
)
from flask_socketio import SocketIO
from flask_cors import CORS
import json, os, time, uuid
from datetime import datetime
import requests   # for geo lookup

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET_KEY"   # change this
ADMIN_PASSWORD = "admin123"              # change this
PROFILE_FILE = "profiles.json"

# CORS (extra safety, even though pixel tracking doesn't need it)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": "*",
    "methods": ["GET", "POST", "OPTIONS"],
}})

socketio = SocketIO(app, cors_allowed_origins="*")


# -------------------------
# BLOG DATA
# -------------------------
BLOGS = [
    {
        "slug": "top-5-tech-trends-2025",
        "cat_slug": "tech",
        "category": "Tech",
        "title": "Top 5 Tech Trends You Must Watch in 2025",
        "thumb": "https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg",
        "excerpt": "From AI copilots to quantum-safe security, these trends will reshape how we work, code, and stay secure."
    },
    {
        "slug": "how-hackers-track-you-online",
        "cat_slug": "cybersecurity",
        "category": "Cybersecurity",
        "title": "How Hackers Track You Online Using Pixels and Cookies",
        "thumb": "https://images.pexels.com/photos/5380664/pexels-photo-5380664.jpeg",
        "excerpt": "Tiny JavaScript and invisible images can follow your clicks, scrolls, and interests across websites."
    },
    {
        "slug": "todays-breaking-digital-news",
        "cat_slug": "news",
        "category": "News",
        "title": "Today’s Breaking Digital News You Might Have Missed",
        "thumb": "https://images.pexels.com/photos/3944454/pexels-photo-3944454.jpeg",
        "excerpt": "A quick wrap-up of the latest security breaches, policy changes, and tech announcements."
    },
    {
        "slug": "stock-market-and-tech-stocks",
        "cat_slug": "stock",
        "category": "Stock",
        "title": "How Big Tech Stocks Drive the Market",
        "thumb": "https://images.pexels.com/photos/669610/pexels-photo-669610.jpeg",
        "excerpt": "Tech giants can move entire indices with a single earnings report. Here’s what that means for small investors."
    },
    {
        "slug": "instagram-algorithm-secrets",
        "cat_slug": "instagram",
        "category": "Instagram",
        "title": "Instagram Algorithm Secrets: What It Really Likes",
        "thumb": "https://images.pexels.com/photos/1092671/pexels-photo-1092671.jpeg",
        "excerpt": "Reels, saves, and watch time matter more than likes. Learn the signals that actually move your content."
    },
    {
        "slug": "simple-cyber-hygiene-checklist",
        "cat_slug": "cybersecurity",
        "category": "Cybersecurity",
        "title": "Simple Cyber Hygiene Checklist for Everyday Users",
        "thumb": "https://images.pexels.com/photos/5380595/pexels-photo-5380595.jpeg",
        "excerpt": "A minimal set of habits that dramatically reduces your risk of being hacked."
    },
]


def find_blog(cat_slug, slug):
    for b in BLOGS:
        if b["cat_slug"] == cat_slug and b["slug"] == slug:
            return b
    return None


# -------------------------
# FILE DB HELPERS
# -------------------------
def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_profiles(data):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# -------------------------
# GEO LOOKUP
# -------------------------
def get_geo(ip: str):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = r.json()
        if data.get("status") == "success":
            return {
                "country": data.get("country", "Unknown"),
                "state": data.get("regionName", "Unknown"),
                "city": data.get("city", "Unknown"),
            }
    except Exception:
        pass
    return {"country": "Unknown", "state": "Unknown", "city": "Unknown"}


# -------------------------
# USER-AGENT PARSER
# -------------------------
def parse_user_agent(ua: str):
    ua = (ua or "").lower()
    device, os_name, browser = "Desktop", "Unknown", "Unknown"

    if "android" in ua:
        os_name, device = "Android", "Mobile"
    if "iphone" in ua or "ios" in ua:
        os_name, device = "iOS", "Mobile"
    if "windows" in ua:
        os_name = "Windows"
    if "mac os" in ua or "macintosh" in ua:
        os_name = "macOS"
    if "linux" in ua:
        os_name = "Linux"

    if "edg" in ua:
        browser = "Edge"
    elif "chrome" in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"

    return {"device": device, "os": os_name, "browser": browser}


# -------------------------
# CORS HEADERS
# -------------------------
@app.after_request
def cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*" 
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


# -------------------------
# TRACKER JS – PIXEL USING /track.gif
# -------------------------
TRACKER_JS = r"""
<script>
let tracker = {
  clicks: 0,
  scrollDepth: 0,
  timeSpent: 0,
  startTime: Date.now(),
  page: window.location.pathname
};

document.addEventListener("click", () => { tracker.clicks++; });

document.addEventListener("scroll", () => {
  const d = Math.round((window.scrollY + window.innerHeight) / document.body.scrollHeight * 100);
  tracker.scrollDepth = Math.max(tracker.scrollDepth, d);
});

setInterval(() => {
  tracker.timeSpent = Math.round((Date.now() - tracker.startTime) / 1000);
}, 1000);

// FingerprintJS (optional)
let fpVisitorId = null;
const fpScript = document.createElement("script");
fpScript.src = "https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js";
fpScript.async = true;
fpScript.onload = () => {
  FingerprintJS.load()
    .then(fp => fp.get())
    .then(result => {
      fpVisitorId = result.visitorId;
    })
    .catch(() => {});
};
document.head.appendChild(fpScript);

function buildPayload() {
  return {
    clicks: tracker.clicks,
    scrollDepth: tracker.scrollDepth,
    timeSpent: tracker.timeSpent,
    page: tracker.page,
    screen: `${screen.width}x${screen.height}`,
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    referrer: document.referrer,
    url: location.href,
    origin: location.origin,
    fpVisitorId: fpVisitorId
  };
}

function sendTracking() {
  const payload = JSON.stringify(buildPayload());
  const url = "{{ tracker_url }}" + "?data=" + encodeURIComponent(payload);

  const img = new Image();
  img.src = url;
  console.log("Pixel sent:", url);
}

// send on tab hide and every 5s
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") sendTracking();
});
setInterval(sendTracking, 5000);
</script>
"""


# -------------------------
# BASE PAGE TEMPLATE
# -------------------------
BASE_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{{ title }}</title>
<style>
 body { background:#020617; color:#e5e7eb; font-family:system-ui; margin:0; }
 header {
   padding:16px 24px;
   border-bottom:1px solid #111827;
   background:#020617dd;
   backdrop-filter:blur(10px);
   position:sticky; top:0; z-index:10;
 }
 .logo { font-weight:700; font-size:12px; letter-spacing:0.08em; color:#22d3ee; }
 main { max-width:960px; margin:24px auto 40px; padding:0 16px; }
 .grid { display:grid; gap:18px; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }
 .card {
   background:#020617; border-radius:16px; border:1px solid #111827;
   box-shadow:0 18px 40px rgba(0,0,0,.7); overflow:hidden;
 }
 .thumb { width:100%; height:160px; object-fit:cover; display:block; }
 .meta { padding:14px 16px; }
 .pill { display:inline-block; padding:3px 9px; border-radius:999px;
         border:1px solid #1f2937; font-size:10px; color:#9ca3af; margin-bottom:6px; }
 h3 { margin:4px 0 6px; font-size:16px; }
 p { margin:0; font-size:13px; color:#9ca3af; }
 a { color:inherit; text-decoration:none; }
 a:hover h3 { text-decoration:underline; }
</style>
</head>
<body>
<header><div class="logo">LINUXNDROID • BLOG DEMO</div></header>
<main>{{ body|safe }}</main>
{{ tracker|safe }}
</body>
</html>
"""


def render_page(title, body_html):
    tracker_html = render_template_string(
        TRACKER_JS,
        tracker_url=url_for("track_gif", _external=True),
    )
    return render_template_string(
        BASE_TEMPLATE,
        title=title,
        body=body_html,
        tracker=tracker_html,
    )


# -------------------------
# LANDING PAGE – PURE BLOG HOMEPAGE
# -------------------------
@app.route("/")
def landing():
    import random
    posts = BLOGS.copy()
    random.shuffle(posts)

    cards = []
    for b in posts:
        url = url_for("blog_post", cat_slug=b["cat_slug"], slug=b["slug"])
        card = f"""
        <article class="card">
          <a href="{url}">
            <img class="thumb" src="{b['thumb']}" alt="{b['title']}">
            <div class="meta">
              <div class="pill">{b['category']}</div>
              <h3>{b['title']}</h3>
              <p>{b['excerpt']}</p>
            </div>
          </a>
        </article>
        """
        cards.append(card)

    body = f"""
    <section class="grid">
      {''.join(cards)}
    </section>
    """

    html = render_page("Blog Home", body)
    resp = make_response(html)
    if "tracking_id" not in request.cookies:
        resp.set_cookie("tracking_id", str(uuid.uuid4()), max_age=31536000)
    return resp


# -------------------------
# BLOG POST PAGE
# -------------------------
@app.route("/blog/<cat_slug>/<slug>")
def blog_post(cat_slug, slug):
    blog = find_blog(cat_slug, slug)
    if not blog:
        return "Blog not found", 404

    body = f"""
    <article class="card" style="overflow:hidden;">
      <img class="thumb" src="{blog['thumb']}" alt="{blog['title']}">
      <div class="meta" style="padding:18px 18px 22px;">
        <div class="pill">{blog['category']}</div>
        <h3 style="font-size:20px;margin-top:6px;margin-bottom:10px;">{blog['title']}</h3>
        <p style="margin-bottom:10px;">{blog['excerpt']}</p>
        <p style="font-size:13px;color:#9ca3af;">
          This is a demo article page. The real point here is that just by reading
          this blog, your interest profile is updated in the admin dashboard under
          the category <b>{blog['category']}</b>.
        </p>
      </div>
    </article>
    """
    return render_page(blog["title"], body)


# -------------------------
# ADMIN LOGIN
# -------------------------
LOGIN_TEMPLATE = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Admin Login</title>
<style>
 body { background:#020617; color:#e5e7eb; font-family:system-ui;
        display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
 .card {
   background:#020617; border-radius:16px; border:1px solid #111827;
   padding:24px; width:280px; box-shadow:0 18px 40px rgba(0,0,0,.7);
 }
 input {
   width:100%; padding:8px 10px; border-radius:8px; border:1px solid #1f2937;
   background:#020617; color:#e5e7eb; margin-top:10px;
 }
 button {
   margin-top:14px; width:100%; padding:8px 10px; border-radius:999px;
   border:none; background:linear-gradient(135deg,#22c55e,#22d3ee);
   color:#020617; font-weight:600; cursor:pointer;
 }
 h2 { margin:0 0 6px; font-size:18px; }
 p { margin:0; font-size:13px; color:#9ca3af; }
</style>
</head>
<body>
<form class="card" method="post">
  <h2>Admin Dashboard</h2>
  <p>Enter password to view analytics.</p>
  <input type="password" name="password" placeholder="Password">
  <button type="submit">Login</button>
</form>
</body>
</html>
"""


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect("/admin")
        return render_template_string(
            LOGIN_TEMPLATE.replace(
                "</h2>",
                "</h2><p style='color:#f97373;margin-bottom:4px;'>Wrong password</p>",
                1,
            )
        )
    return render_template_string(LOGIN_TEMPLATE)


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return redirect("/admin/login")


# -------------------------
# STATS HELPER
# -------------------------
def compute_stats(profiles):
    total_visitors = len(profiles)
    total_visits = 0
    page_views = {}
    interests_count = {}
    site_counts = {}

    for profile in profiles.values():
        visits = profile.get("visit_history", [])
        total_visits += len(visits)

        for v in visits:
            page = v.get("page", "unknown")
            page_views[page] = page_views.get(page, 0) + 1

        for i in profile.get("interests", []):
            interests_count[i] = interests_count.get(i, 0) + 1

        for s in profile.get("sites", []):
            site_counts[s] = site_counts.get(s, 0) + 1

    return {
        "total_visitors": total_visitors,
        "total_visits": total_visits,
        "page_views": page_views,
        "interests_count": interests_count,
        "site_counts": site_counts,
    }


# -------------------------
# ADMIN DASHBOARD
# -------------------------
ADMIN_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Admin Analytics</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<style>
 body { background:#020617; color:#e5e7eb; font-family:system-ui; margin:0; }
 header {
   padding:16px 24px; border-bottom:1px solid #111827; background:#020617;
   display:flex; justify-content:space-between; align-items:center;
 }
 .logo { font-weight:700; font-size:12px; letter-spacing:0.08em; color:#22d3ee; }
 main { max-width:1100px; margin:24px auto 40px; padding:0 16px; }
 .grid { display:grid; gap:16px; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }
 .card { background:#020617; border-radius:16px; border:1px solid #111827; padding:16px; box-shadow:0 18px 40px rgba(0,0,0,.7); }
 h2 { margin:0 0 10px; font-size:18px; }
 .stat { font-size:26px; font-weight:700; }
 button {
   border:none; border-radius:999px; padding:6px 12px; font-size:12px;
   font-weight:600; cursor:pointer; background:#111827; color:#e5e7eb;
 }
 #liveFeed { font-size:12px; max-height:200px; overflow:auto; background:#020617; border-radius:12px; border:1px solid #111827; padding:8px; }
 a { color:#22d3ee; text-decoration:none; }
</style>
</head>
<body>
<header>
  <div class="logo">TRACKING DEMO • ADMIN</div>
  <div>
    <a href="/admin/list">Visitors</a>
    <form style="display:inline;" method="post" action="/admin/logout">
      <button type="submit">Logout</button>
    </form>
  </div>
</header>
<main>
  <section class="grid">
    <div class="card">
      <h2>Visitors</h2>
      <div class="stat" id="statVisitors">{{ stats.total_visitors }}</div>
      <p style="font-size:12px;color:#9ca3af;">Unique profiles tracked.</p>
    </div>
    <div class="card">
      <h2>Visits</h2>
      <div class="stat" id="statVisits">{{ stats.total_visits }}</div>
      <p style="font-size:12px;color:#9ca3af;">Total page views.</p>
    </div>
  </section>

  <section class="grid" style="margin-top:18px;">
    <div class="card">
      <h2>Page Views</h2>
      <canvas id="pageViewsChart" height="180"></canvas>
    </div>
    <div class="card">
      <h2>Interest Segments</h2>
      <canvas id="interestsChart" height="180"></canvas>
    </div>
  </section>

  <section class="grid" style="margin-top:18px;">
    <div class="card">
      <h2>Cross-Domain Sites</h2>
      <canvas id="sitesChart" height="160"></canvas>
    </div>
    <div class="card">
      <h2>Live Events</h2>
      <div id="liveFeed"></div>
    </div>
  </section>
</main>

<script>
const stats = {{ stats_json|safe }};

function buildChart(ctxId, labels, data, type="bar") {
  if (!labels.length) return;
  const ctx = document.getElementById(ctxId).getContext("2d");
  new Chart(ctx, {
    type,
    data: { labels, datasets: [{ data, borderWidth: 1 }] },
    options: {
      plugins: { legend: { display:false } },
      scales: {
        x: { ticks:{ color:"#9ca3af" } },
        y: { ticks:{ color:"#9ca3af" }, beginAtZero:true }
      }
    }
  });
}

buildChart("pageViewsChart",
  Object.keys(stats.page_views),
  Object.values(stats.page_views),
  "bar"
);

buildChart("interestsChart",
  Object.keys(stats.interests_count),
  Object.values(stats.interests_count),
  "doughnut"
);

buildChart("sitesChart",
  Object.keys(stats.site_counts),
  Object.values(stats.site_counts),
  "bar"
);

// Realtime via Socket.IO
const socket = io();

socket.on("stats_update", data => {
  if (data.total_visitors !== undefined)
    document.getElementById("statVisitors").innerText = data.total_visitors;
  if (data.total_visits !== undefined)
    document.getElementById("statVisits").innerText = data.total_visits;
});

socket.on("live_event", ev => {
  const feed = document.getElementById("liveFeed");
  const line = `[${new Date(ev.timestamp * 1000).toLocaleTimeString()}] `
    + `${ev.profile_key} → ${ev.page} (${ev.origin || "unknown origin"})`
    + ` eng=${ev.engagement} | ${ev.country || "Unknown"}, ${ev.state || "Unknown"}`;
  const div = document.createElement("div");
  div.textContent = line;
  feed.prepend(div);
  const children = feed.children;
  if (children.length > 100) feed.removeChild(feed.lastChild);
});
</script>
</body>
</html>
"""


@app.route("/admin")
def admin_home():
    if not session.get("is_admin"):
        return redirect("/admin/login")
    profiles = load_profiles()
    stats = compute_stats(profiles)
    return render_template_string(
        ADMIN_TEMPLATE,
        stats=stats,
        stats_json=json.dumps(stats),
    )


# -------------------------
# ADMIN LIST VISITORS
# -------------------------
@app.route("/admin/list")
def admin_list():
    if not session.get("is_admin"):
        return redirect("/admin/login")
    profiles = load_profiles()
    rows = []
    for pid, profile in profiles.items():
        visits = profile.get("visit_history", [])
        interests = ", ".join(profile.get("interests", []))
        country = state = "Unknown"
        if visits:
            last = visits[-1]
            country = last.get("country", "Unknown")
            state = last.get("state", "Unknown")
        rows.append(
            f"<tr>"
            f"<td><a href='/admin/user/{pid}'>{pid}</a></td>"
            f"<td>{interests}</td>"
            f"<td>{country}</td>"
            f"<td>{state}</td>"
            f"<td>{len(visits)}</td>"
            f"</tr>"
        )

    html = f"""
    <html><head><meta charset='utf-8'><title>Visitors</title>
    <style>
      body {{ background:#020617;color:#e5e7eb;font-family:system-ui; }}
      table {{ border-collapse:collapse;width:100%;margin-top:20px; }}
      th,td {{ padding:8px 6px;border-bottom:1px solid #111827;font-size:13px; }}
      a {{ color:#22d3ee; text-decoration:none; }}
    </style>
    </head><body>
    <h2 style='padding:20px;'>Visitors</h2>
    <table>
      <tr><th>Profile ID</th><th>Interests</th><th>Country</th><th>State</th><th>Visits</th></tr>
      {''.join(rows)}
    </table>
    <p style='padding:20px;'><a href='/admin'>← Back to Dashboard</a></p>
    </body></html>
    """
    return html


# -------------------------
# ADMIN VISITOR DETAIL
# -------------------------
VISITOR_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Visitor {{ pid }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
 body { background:#020617;color:#e5e7eb;font-family:system-ui;margin:0; }
 header { padding:16px 24px;border-bottom:1px solid #111827;background:#020617; }
 main { max-width:900px;margin:24px auto 40px;padding:0 16px; }
 .card { background:#020617;border-radius:16px;border:1px solid #111827;padding:16px;box-shadow:0 18px 40px rgba(0,0,0,.7);margin-bottom:16px; }
 table { width:100%;border-collapse:collapse;font-size:13px; }
 td { padding:6px 0;border-bottom:1px solid #111827; }
 pre { background:#020617;border-radius:12px;border:1px solid #111827;padding:10px;font-size:11px;max-height:260px;overflow:auto; }
 a { color:#22d3ee;text-decoration:none; }
</style>
</head>
<body>
<header><h2>Visitor {{ pid }}</h2></header>
<main>
  <div class="card">
    <h3>Device & Location</h3>
    <table>
      <tr><td>Device</td><td>{{ device.device }}</td></tr>
      <tr><td>OS</td><td>{{ device.os }}</td></tr>
      <tr><td>Browser</td><td>{{ device.browser }}</td></tr>
      <tr><td>Fingerprint</td><td>{{ profile.fingerprint }}</td></tr>
      <tr><td>Cookies</td><td>{{ profile.tracking_ids }}</td></tr>
      <tr><td>Country</td><td>{{ last_visit.country }}</td></tr>
      <tr><td>State</td><td>{{ last_visit.state }}</td></tr>
      <tr><td>City</td><td>{{ last_visit.city }}</td></tr>
      <tr><td>IP Address</td><td>{{ last_visit.ip }}</td></tr>
      <tr><td>First Seen</td><td>{{ first_seen }}</td></tr>
      <tr><td>Last Seen</td><td>{{ last_seen }}</td></tr>
    </table>
  </div>

  <div class="card">
    <h3>Interests</h3>
    <pre>{{ interests }}</pre>
  </div>

  <div class="card">
    <h3>Cross-Domain Sites</h3>
    <pre>{{ sites }}</pre>
  </div>

  <div class="card">
    <h3>Engagement Over Time</h3>
    <canvas id="engChart" height="120"></canvas>
  </div>

  <div class="card">
    <h3>Visit History</h3>
    <pre>{{ visits }}</pre>
  </div>

  <p><a href="/admin/list">← Back to Visitors</a></p>
</main>

<script>
const labels = {{ labels|safe }};
const values = {{ values|safe }};
if (labels.length) {
  const ctx = document.getElementById("engChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: { labels, datasets: [{ label:"Engagement", data: values, borderWidth:2 }] },
    options: { scales: { y: { beginAtZero:true } } }
  });
}
</script>
</body>
</html>
"""


@app.route("/admin/user/<pid>")
def admin_user(pid):
    if not session.get("is_admin"):
        return redirect("/admin/login")
    profiles = load_profiles()
    if pid not in profiles:
        return "Profile not found"
    profile = profiles[pid]
    visits = profile.get("visit_history", [])
    if visits:
        first_seen = datetime.fromtimestamp(visits[0]["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        last_seen = datetime.fromtimestamp(visits[-1]["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        ua = visits[-1].get("userAgent", "")
        device = parse_user_agent(ua)
        labels = [f"Visit {i+1}" for i in range(len(visits))]
        values = [v.get("engagement", 0) for v in visits]
        last_visit = visits[-1]
    else:
        first_seen = last_seen = "No data"
        device = {"device": "Unknown", "os": "Unknown", "browser": "Unknown"}
        labels, values = [], []
        last_visit = {"country": "Unknown", "state": "Unknown", "city": "Unknown", "ip": "Unknown"}

    return render_template_string(
        VISITOR_TEMPLATE,
        pid=pid,
        profile=profile,
        device=device,
        first_seen=first_seen,
        last_seen=last_seen,
        last_visit=last_visit,
        interests=json.dumps(profile.get("interests", []), indent=2),
        sites=json.dumps(profile.get("sites", []), indent=2),
        visits=json.dumps(visits, indent=2),
        labels=json.dumps(labels),
        values=json.dumps(values),
    )


# -------------------------
# TRACKING ENDPOINT – PIXEL
# -------------------------
@app.route("/track.gif")
def track_gif():
    import base64

    raw = request.args.get("data", "")
    try:
        payload = json.loads(raw)
    except Exception:
        payload = {"error": "decode_failed", "raw": raw}

    profiles = load_profiles()

    fp = payload.get("fpVisitorId")
    tid = request.cookies.get("tracking_id")
    page = payload.get("page")
    origin = payload.get("origin")

    if fp:
        key = f"fp_{fp}"
    elif tid:
        key = f"ck_{tid}"
    else:
        key = "unknown_" + str(uuid.uuid4())

    if key not in profiles:
        profiles[key] = {
            "fingerprint": fp,
            "tracking_ids": [],
            "interests": [],
            "sites": [],
            "visit_history": [],
            "total_engagement": 0,
        }

    profile = profiles[key]

    if tid and tid not in profile["tracking_ids"]:
        profile["tracking_ids"].append(tid)

    if origin and origin not in profile["sites"]:
        profile["sites"].append(origin)

    clicks = payload.get("clicks", 0)
    scroll = payload.get("scrollDepth", 0)
    timeSpent = payload.get("timeSpent", 0)
    engagement = timeSpent + scroll * 2 + clicks * 5
    profile["total_engagement"] += engagement

    # GEO from IP
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    geo = get_geo(user_ip)

    visit_entry = {
        "timestamp": time.time(),
        "origin": origin,
        "page": page,
        "url": payload.get("url"),
        "clicks": clicks,
        "scroll": scroll,
        "timeSpent": timeSpent,
        "engagement": engagement,
        "userAgent": payload.get("userAgent"),
        "country": geo["country"],
        "state": geo["state"],
        "city": geo["city"],
        "ip": user_ip,
    }
    profile["visit_history"].append(visit_entry)

    # ------- Interest tagging from BLOG CATEGORY -------
    new_interests = []

    # If URL is a blog page
    if page and page.startswith("/blog/"):
        parts = page.split("/")
        if len(parts) >= 3:
            cat_slug = parts[2]
            mapping = {
                "tech": "Tech",
                "cybersecurity": "Cybersecurity",
                "news": "News",
                "stock": "Stock",
                "instagram": "Instagram",
            }
            cat_name = mapping.get(cat_slug, f"Blog: {cat_slug.title()}")
            new_interests.append(cat_name)

    # Keep for cross-domain external pages too
    url_lower = (payload.get("url") or "").lower()
    if "instagram" in url_lower:
        new_interests.append("Instagram")
    if "stock" in url_lower or "market" in url_lower:
        new_interests.append("Stock")

    for tag in new_interests:
        if tag not in profile["interests"]:
            profile["interests"].append(tag)
    # ---------------------------------------------------

    save_profiles(profiles)

    stats = compute_stats(profiles)
    socketio.emit("stats_update", stats, broadcast=True)
    socketio.emit(
        "live_event",
        {
            "profile_key": key,
            "page": page,
            "origin": origin,
            "engagement": engagement,
            "timestamp": time.time(),
            "country": geo["country"],
            "state": geo["state"],
        },
        broadcast=True,
    )

    gif = base64.b64decode(
        "R0lGODlhAQABAPAAAP///wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="
    )

    return gif, 200, {"Content-Type": "image/gif"}


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
