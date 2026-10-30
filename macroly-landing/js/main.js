/* =============================================================================
   MACROLY LANDING PAGE - CORE CONFIGURATION & INTERACTION
   ============================================================================= */

// Global App & Download Config
const MACROLY_CONFIG = {
  webAppUrl: "/", // Points to the actual hosted web app on root
  androidApkUrl: "/apk/macroly-latest.apk", // Configurable APK link
  supportEmail: "support@macroly.app",
};

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initCtaButtons();
  initProgressRings();
});

/* -----------------------------------------------------------------------------
   Navbar Scroll Response & Mobile Menu
   ----------------------------------------------------------------------------- */
function initNavbar() {
  const navbar = document.getElementById("mainNavbar");
  const mobileToggle = document.getElementById("mobileToggle");
  const navLinks = document.getElementById("navLinks");

  // Sticky compact navbar on scroll
  window.addEventListener("scroll", () => {
    if (window.scrollY > 40) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

  // Mobile menu toggle
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });

    // Close menu when clicking link
    navLinks.querySelectorAll("a").forEach(link => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("open");
      });
    });
  }
}

/* -----------------------------------------------------------------------------
   CTA Buttons & Download Toast
   ----------------------------------------------------------------------------- */
function initCtaButtons() {
  const tryWebBtns = document.querySelectorAll(".btn-try-web");
  const downloadApkBtns = document.querySelectorAll(".btn-download-apk");

  tryWebBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.href = MACROLY_CONFIG.webAppUrl;
    });
  });

  downloadApkBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      // Show modern floating notification toast if APK is generating or direct download
      showApkDownloadToast();
    });
  });
}

function showApkDownloadToast() {
  let toast = document.getElementById("landingApkToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "landingApkToast";
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(11, 43, 30, 0.94);
      border: 1px solid rgba(197, 244, 103, 0.35);
      backdrop-filter: blur(14px);
      color: #FFFFFF;
      padding: 16px 20px;
      border-radius: 16px;
      box-shadow: 0 16px 40px rgba(0,0,0,0.5);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.92rem;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    `;
    toast.innerHTML = `
      <div style="width:36px;height:36px;border-radius:10px;background:rgba(197,244,103,0.18);color:#C5F467;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">
        🤖
      </div>
      <div>
        <div style="font-weight:700;color:#C5F467;">Android APK Package</div>
        <div style="font-size:0.82rem;color:#B4C7BA;">Macroly v1.1.2 build is compiling for download!</div>
      </div>
      <button style="margin-left:12px;color:#7E9786;cursor:pointer;" onclick="this.parentElement.style.opacity=0;setTimeout(()=>this.parentElement.remove(),350);">✕</button>
    `;
    document.body.appendChild(toast);
  }

  setTimeout(() => {
    toast.style.transform = "translateY(0)";
    toast.style.opacity = "1";
  }, 10);

  setTimeout(() => {
    if (toast) {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(100px)";
      setTimeout(() => toast.remove(), 400);
    }
  }, 5000);
}

/* -----------------------------------------------------------------------------
   SVG Circular Progress Initializer
   ----------------------------------------------------------------------------- */
function initProgressRings() {
  document.querySelectorAll(".gauge-circle-bar").forEach(circle => {
    const radius = circle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
  });
}
