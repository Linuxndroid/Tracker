<h1>📡 Tracking Awareness Demo – Blog + Pixel Tracking System</h1>

<p>
A full-featured <b>tracking awareness demonstration platform</b> that shows users how websites silently collect:
</p>

<ul>
  <li>Behavioral signals (clicks, scroll depth, time spent)</li>
  <li>Cross-domain tracking using tracking pixels</li>
  <li>Fingerprint IDs (via FingerprintJS)</li>
  <li>Location details (Country, State, City)</li>
  <li>Interest profiling from visited pages</li>
</ul>

<hr>

<h2>🚀 Features</h2>

<ul>
  <li><b>Pixel tracking endpoint</b> (<code>/track.gif</code>) that receives data from any domain.</li>
  <li><b>Blog-style landing page</b> with thumbnails and auto-generated interest categories.</li>
  <li><b>Cross-domain mini site</b> that sends tracking pixels to your main server.</li>
  <li><b>Admin dashboard</b> with real-time charts & live event feed.</li>
  <li><b>Visitor profiling</b> (interests, device, browser, location, engagement score).</li>
  <li><b>Country + State + City detection</b> via ip-api.com.</li>
</ul>

<hr>

<h2>📂 Project Structure</h2>

<pre>
app.py                 → Main Flask tracking + blog + admin system
cross_domain_site.py   → Optional second-site that loads tracker JS
static/cross_tracker.js → Cross-domain pixel tracker script
profiles.json          → Auto-generated visitor database
README.html            → This file
</pre>

<hr>

<h2>📰 Blog Homepage</h2>

<p>The homepage shows a real blog layout with:</p>

<ul>
  <li>Thumbnail images</li>
  <li>Blog category tags</li>
  <li>Short excerpt</li>
  <li>Clickable blog URLs like:
    <code>/blog/tech/top-5-tech-trends-2025</code>
  </li>
</ul>

<h3>Interest Collection</h3>

<p>
When a visitor opens a blog page, the category (Tech, Cybersecurity, News, Stock, Instagram)
is added to their interest profile automatically.
</p>

<hr>

<h2>🎯 Tracking Pixel (Zero CORS, Zero Errors)</h2>

<p>
The system uses a bulletproof tracking pixel:
</p>

<pre>
<img src="/track.gif?data=ENCODED_JSON">
</pre>

<p>No CORS, no OPTIONS, no sendBeacon issues — works on:</p>

<ul>
  <li>Android Chrome</li>
  <li>Firefox</li>
  <li>Safari iOS</li>
  <li>All cross-domain environments</li>
</ul>

<hr>

<h2>📊 Admin Dashboard</h2>

<p>The admin panel includes:</p>

<ul>
  <li>Total visitors</li>
  <li>Total visits</li>
  <li>Page-view graph</li>
  <li>Interest chart</li>
  <li>Cross-domain site chart</li>
  <li>Live tracking feed (WebSocket real-time)</li>
</ul>

<h3>Visitor Detail Page</h3>

<p>Shows full analytics per profile:</p>

<ul>
  <li>Country, State, City, IP</li>
  <li>Device, OS, Browser</li>
  <li>Engagement graph</li>
  <li>Visit timeline</li>
  <li>Interest categories</li>
</ul>

<hr>

<h2>📡 Cross-Domain Tracking Setup</h2>

<p>Your second site simply loads:</p>

<pre>
<script src="http://YOUR-IP:5000/static/cross_tracker.js"></script>
</pre>

<p>This automatically sends:</p>

<ul>
  <li>Clicks</li>
  <li>Scroll depth</li>
  <li>Time spent</li>
  <li>Fingerprint ID</li>
  <li>Current page URL</li>
</ul>

<hr>

<h2>⚙️ Installation</h2>

<h3>1. Install dependencies</h3>

<pre>
pip install flask flask-cors flask-socketio requests
</pre>

<h3>2. Run main server</h3>

<pre>
python app.py
</pre>

<h3>3. Run optional cross-domain site</h3>

<pre>
python cross_domain_site.py
</pre>

<hr>

<h2>🔑 Admin Login</h2>

<p>
Visit: <code>/admin/login</code>
</p>

<p>Default password:</p>

<pre>admin123</pre>

<p>You SHOULD change it inside <code>app.py</code>.</p>

<hr>

<h2>🧠 How It Works (Simple Explanation)</h2>

<ol>
  <li>User opens your blog → Tracker JS loads silently</li>
  <li>Every few seconds + on page exit → sends pixel request</li>
  <li>Server decodes engagement + device + location + interests</li>
  <li>Admin panel displays analytics in real-time</li>
</ol>

<hr>

<h2>📸 Screenshot Suggestions for GitHub</h2>

<p>You may add:</p>

<ul>
  <li>Homepage screenshot</li>
  <li>Admin dashboard screenshot</li>
  <li>Visitor detail page screenshot</li>
</ul>

<hr>

<h2>📄 License</h2>

<p>This project is for educational & cyber-awareness purposes only.</p>

<hr>

<h2>❤️ Author</h2>

<p>
Created by <b>Nitish</b> (Linuxndroid) for cybersecurity education and awareness.
</p>

</body>
</html>
