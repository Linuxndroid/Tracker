// -----------------------------
//  CROSS DOMAIN PIXEL TRACKER
//  Zero CORS, Zero OPTIONS, Works 100%
// -----------------------------

(function () {
    console.log("Pixel Tracker Loaded:", window.location.href);

    // Data bucket
    let tracker = {
        clicks: 0,
        scrollDepth: 0,
        timeSpent: 0,
        startTime: Date.now(),
        page: "external",
        url: window.location.href,
        origin: window.location.origin,
        userAgent: navigator.userAgent,
    };

    // FingerprintJS integration (optional)
    let fpVisitorId = null;

    const fpScript = document.createElement("script");
    fpScript.src = "https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js";
    fpScript.onload = () => {
        FingerprintJS.load().then(fp => fp.get()).then(result => {
            fpVisitorId = result.visitorId;
        });
    };
    document.head.appendChild(fpScript);

    // Activity tracking
    document.addEventListener("click", () => tracker.clicks++);

    document.addEventListener("scroll", () => {
        const depth = Math.round(
            (window.scrollY + window.innerHeight) / document.body.scrollHeight * 100
        );
        tracker.scrollDepth = Math.max(tracker.scrollDepth, depth);
    });

    setInterval(() => {
        tracker.timeSpent = Math.round((Date.now() - tracker.startTime) / 1000);
    }, 1000);

    // Build payload
    function buildPayload() {
        return {
            ...tracker,
            fpVisitorId: fpVisitorId
        };
    }

    // Pixel SEND function (never blocked by CORS)
    function sendPixel() {
        const payload = JSON.stringify(buildPayload());
        const url =
            "http://192.168.139.48:5000/track.gif?data=" +
            encodeURIComponent(payload);

        // Send using tracking pixel
        const img = new Image();
        img.src = url;

        console.log("Pixel Sent:", url);
    }

    // Trigger when tab hidden
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            sendPixel();
        }
    });

    // Trigger every 5 seconds for live analytics
    setInterval(sendPixel, 5000);

})();
