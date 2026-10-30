/* =============================================================================
   MACROLY GSAP & SCROLLTRIGGER MOTION ENGINE (PASS 2 - MOTION ENGINEERING)
   Choreographed Entrance Timelines, 3D Device Parallax, Scroll Scrubbing & Kinetics
   ============================================================================= */

document.addEventListener("DOMContentLoaded", () => {
  // Check if GSAP is available
  if (typeof gsap === "undefined") {
    console.warn("GSAP library not loaded.");
    return;
  }

  // Register ScrollTrigger plugin
  if (typeof ScrollTrigger !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
  }

  // Respect user prefers-reduced-motion
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) {
    console.log("Reduced motion preference active — skipping motion choreographies.");
    return;
  }

  initHeroMotionTimeline();
  initHeroRollingShowcase();
  initHeroMouseParallax();
  initScrollTriggerSections();
  initSectionTransitionsAndPins();
  initFloatingBadgeKinetics();
  initCounterKinetics();
});

/* -----------------------------------------------------------------------------
   1. Fast 2-Second Master Entrance Timeline
   0–0.4s: Background lighting and hero content begin appearing.
   0.4–1.0s: Smartphones enter rapidly from distinct directions.
   1.0–1.5s: Phones rotate and settle into initial 3D curved composition.
   1.5–2.0s: Floating nutrition cards spring in, composition begins continuous rolling.
   ----------------------------------------------------------------------------- */
function initHeroMotionTimeline() {
  const masterTl = gsap.timeline({ defaults: { ease: "power2.out" } });

  // 0–0.4s: Background ambient glows bloom & navigation bar drops down
  masterTl.fromTo(".hero-ambient-glow", 
    { opacity: 0, scale: 0.6 }, 
    { opacity: 1, scale: 1, duration: 0.9, ease: "power2.out" }, 
    0
  );

  masterTl.fromTo(".site-navbar", 
    { y: -35, opacity: 0 }, 
    { y: 0, opacity: 1, duration: 0.55 }, 
    0.1
  );

  // Headline, description & CTA buttons enter with snappy jelly-spring feel
  masterTl.fromTo(".hero-headline", 
    { opacity: 0, y: 30, scale: 0.97 }, 
    { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: "power3.out" }, 
    0.2
  );

  masterTl.fromTo(".hero-description", 
    { opacity: 0, y: 18 }, 
    { opacity: 1, y: 0, duration: 0.55 }, 
    0.35
  );

  masterTl.fromTo(".hero-cta-group .btn", 
    { opacity: 0, y: 18, scale: 0.92 }, 
    { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.1, ease: "back.out(2)" }, 
    0.45
  );

  masterTl.fromTo(".hero-subline", 
    { opacity: 0, y: 12 }, 
    { opacity: 1, y: 0, duration: 0.4 }, 
    0.6
  );

  // 0.4–1.0s: 4 Phones enter from different spatial directions
  // Phone 1 (Main Foreground): Springs up from bottom front
  masterTl.fromTo("#heroPhone1", 
    { opacity: 0, y: 120, z: -100, rotateX: 20, scale: 0.8 }, 
    { opacity: 1, y: 0, z: 80, rotateX: 2, scale: 1, duration: 0.85, ease: "back.out(1.4)" }, 
    0.4
  );

  // Phone 2 (Left Behind): Glides in from left
  masterTl.fromTo("#heroPhone2", 
    { opacity: 0, x: -160, z: -150, rotateY: 35 }, 
    { opacity: 1, x: 0, z: -40, rotateY: 16, duration: 0.8, ease: "power3.out" }, 
    0.5
  );

  // Phone 3 (Right Orbit): Glides in from right
  masterTl.fromTo("#heroPhone3", 
    { opacity: 0, x: 160, z: -200, rotateY: -35 }, 
    { opacity: 1, x: 0, z: -90, rotateY: -20, duration: 0.8, ease: "power3.out" }, 
    0.6
  );

  // Phone 4 (Deep Background): Sinks into background depth
  masterTl.fromTo("#heroPhone4", 
    { opacity: 0, y: -80, z: -300, scale: 0.75 }, 
    { opacity: 1, y: 0, z: -180, scale: 0.92, duration: 0.75, ease: "power2.out" }, 
    0.7
  );

}

/* -----------------------------------------------------------------------------
   2. Continuous 3D Rolling Smartphone Carousel Engine
   - 4 Phones rotate smoothly and continuously along a 3D elliptical track.
   - Phones move seamlessly through foreground and background depths.
   - Zero overlapping card interference: cards are safely docked in outer perimeters.
   ----------------------------------------------------------------------------- */
function initHeroRollingShowcase() {
  if (window.innerWidth <= 768) return; // Keep single static focus on mobile

  // 4 Slot Definitions along a 3D horizontal elliptical orbit
  const orbitSlots = [
    { x: 0, y: 0, z: 90, rotateY: 0, rotateX: 2, scale: 1, brightness: 1, zIndex: 40 },
    { x: 210, y: 25, z: -70, rotateY: -18, rotateX: 5, scale: 0.88, brightness: 0.78, zIndex: 20 },
    { x: -50, y: -30, z: -170, rotateY: -6, rotateX: 2, scale: 0.84, brightness: 0.62, zIndex: 10 },
    { x: -200, y: 15, z: -30, rotateY: 18, rotateX: 4, scale: 0.92, brightness: 0.85, zIndex: 30 }
  ];

  const phones = [
    document.getElementById("heroPhone1"),
    document.getElementById("heroPhone2"),
    document.getElementById("heroPhone3"),
    document.getElementById("heroPhone4")
  ].filter(Boolean);

  if (phones.length < 4) return;

  // Seamless continuous rolling timeline
  const rollingTl = gsap.timeline({ repeat: -1, delay: 2.0 });
  const cycleDuration = 3.2;

  for (let step = 0; step < 4; step++) {
    rollingTl.addLabel(`step_${step}`);

    phones.forEach((phone, pIdx) => {
      const targetSlotIdx = (pIdx + step + 1) % 4;
      const target = orbitSlots[targetSlotIdx];

      rollingTl.to(phone, {
        x: target.x,
        y: target.y,
        z: target.z,
        rotateY: target.rotateY,
        rotateX: target.rotateX,
        scale: target.scale,
        filter: `brightness(${target.brightness})`,
        zIndex: target.zIndex,
        duration: cycleDuration,
        ease: "sine.inOut"
      }, `step_${step}`);
    });
  }

  // Scroll Interaction: Visitor scroll scrubs and dynamically influences the carousel roll
  if (typeof ScrollTrigger !== "undefined") {
    ScrollTrigger.create({
      trigger: "#hero",
      start: "top top",
      end: "bottom top",
      scrub: 1.2,
      onUpdate: (self) => {
        // Accelerate or modulate rotation smoothly based on scroll progress
        const scrollOffset = self.progress * 80;
        gsap.to("#heroCarouselTrack", {
          rotationY: scrollOffset * 0.4,
          y: scrollOffset * 0.5,
          duration: 0.5,
          ease: "power1.out",
          overwrite: "auto"
        });
      }
    });
  }
}

/* -----------------------------------------------------------------------------
   3. Desktop 3D Mouse Parallax (Interactive Tilt)
   ----------------------------------------------------------------------------- */
function initHeroMouseParallax() {
  if (window.innerWidth <= 1024) return;

  const stage = document.getElementById("heroPhoneStage");
  if (!stage) return;

  window.addEventListener("mousemove", (e) => {
    const mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    const mouseY = (e.clientY / window.innerHeight - 0.5) * 2;

    gsap.to("#heroCarouselTrack", {
      rotationY: mouseX * 9,
      rotationX: -mouseY * 6,
      duration: 1.4,
      ease: "power2.out",
      overwrite: "auto"
    });

    gsap.to(".hero-floating-card", {
      x: -mouseX * 15,
      y: -mouseY * 15,
      duration: 1.6,
      ease: "power1.out",
      overwrite: "auto"
    });
  });
}

/* -----------------------------------------------------------------------------
   3. ScrollTrigger Section Animations & Scroll-Scrubbed Progress
   ----------------------------------------------------------------------------- */
function initScrollTriggerSections() {
  if (typeof ScrollTrigger === "undefined") return;

  // Staggered section headers reveal
  gsap.utils.toArray(".landing-section").forEach(section => {
    const header = section.querySelector(".section-header");
    if (header) {
      gsap.fromTo(header.children, 
        { opacity: 0, y: 35 }, 
        {
          opacity: 1, 
          y: 0, 
          duration: 0.85, 
          stagger: 0.15, 
          ease: "power3.out",
          scrollTrigger: {
            trigger: section,
            start: "top 80%",
            toggleActions: "play none none none"
          }
        }
      );
    }
  });

  // Section 2: Showcase phone elevates as visitor scrolls into Section 2
  gsap.fromTo("#how-it-works .phone-mockup", 
    { y: 80, opacity: 0.8 }, 
    {
      y: 0, 
      opacity: 1, 
      duration: 1.1, 
      ease: "power3.out",
      scrollTrigger: {
        trigger: "#how-it-works",
        start: "top 75%",
        toggleActions: "play none none none"
      }
    }
  );

  // Section 3: Macro Dashboard phone and orbiting floating cards
  const dashPhone = document.querySelector("#dashboard-section .phone-mockup");
  if (dashPhone) {
    gsap.fromTo(dashPhone, 
      { scale: 0.9, opacity: 0.7, y: 50 }, 
      {
        scale: 1, 
        opacity: 1, 
        y: 0, 
        duration: 1.2, 
        ease: "power3.out",
        scrollTrigger: {
          trigger: "#dashboard-section",
          start: "top 70%",
          toggleActions: "play none none none"
        }
      }
    );
  }

  // Section 3: Circular SVG Gauge Animation (Calorie Arc)
  const calorieArc = document.getElementById("dashboardCalorieArc");
  if (calorieArc) {
    // Circumference for r=54 is 2*PI*54 ~= 339.29
    // Consuming 1450/2000 kcal leaves offset ~ 93
    ScrollTrigger.create({
      trigger: "#dashboard-section",
      start: "top 65%",
      onEnter: () => {
        gsap.to(calorieArc, {
          strokeDashoffset: 93,
          duration: 1.8,
          ease: "power3.out"
        });
      }
    });
  }

  // Section 3: Floating Macro Cards pop into view from four corners
  const floatingMacroCards = document.querySelectorAll("#dashboard-section .floating-glass-card");
  if (floatingMacroCards.length > 0) {
    gsap.fromTo(floatingMacroCards, 
      { opacity: 0, scale: 0.75, y: 30 }, 
      {
        opacity: 1, 
        scale: 1, 
        y: 0, 
        duration: 0.8, 
        stagger: 0.15, 
        ease: "back.out(1.4)",
        scrollTrigger: {
          trigger: "#dashboard-section",
          start: "top 65%",
          toggleActions: "play none none none"
        }
      }
    );
  }

  // Section 5: History Trend Bars grow upward
  const trendBars = document.querySelectorAll(".trend-bar-fill");
  if (trendBars.length > 0) {
    ScrollTrigger.create({
      trigger: "#history-section",
      start: "top 72%",
      onEnter: () => {
        gsap.fromTo(trendBars, 
          { scaleY: 0, transformOrigin: "bottom center" }, 
          { scaleY: 1, duration: 1.2, stagger: 0.1, ease: "power2.out" }
        );
      }
    });
  }

  // Section 6: Feature Bento Cards Staggered Entry
  const bentoCards = document.querySelectorAll(".feature-bento-card");
  if (bentoCards.length > 0) {
    gsap.fromTo(bentoCards, 
      { opacity: 0, y: 40, scale: 0.96 }, 
      {
        opacity: 1, 
        y: 0, 
        scale: 1, 
        duration: 0.75, 
        stagger: 0.12, 
        ease: "power3.out",
        scrollTrigger: {
          trigger: "#features-section",
          start: "top 75%",
          toggleActions: "play none none none"
        }
      }
    );
  }

  // Section 7: Final CTA Box Reveal
  const finalCta = document.querySelector(".final-cta-box");
  if (finalCta) {
    gsap.fromTo(finalCta, 
      { opacity: 0, y: 60, scale: 0.94 }, 
      {
        opacity: 1, 
        y: 0, 
        scale: 1, 
        duration: 1.1, 
        ease: "back.out(1.2)",
        scrollTrigger: {
          trigger: "#download-cta",
          start: "top 80%",
          toggleActions: "play none none none"
        }
      }
    );
  }
}

/* -----------------------------------------------------------------------------
   4. Section Transitions & Subtle Parallax Depth
   ----------------------------------------------------------------------------- */
function initSectionTransitionsAndPins() {
  if (typeof ScrollTrigger === "undefined" || window.innerWidth <= 1024) return;

  // Parallax on ambient green light orbs during scroll
  gsap.utils.toArray(".ambient-glow").forEach(orb => {
    gsap.to(orb, {
      y: -60,
      ease: "none",
      scrollTrigger: {
        trigger: orb.parentElement,
        start: "top bottom",
        end: "bottom top",
        scrub: 1.2
      }
    });
  });

  // Soft Parallax on Hero Phones as user scrolls into Section 2
  gsap.to(".hero-phone-stage", {
    y: 80,
    opacity: 0.85,
    ease: "none",
    scrollTrigger: {
      trigger: "#hero",
      start: "center center",
      end: "bottom top",
      scrub: 1
    }
  });
}

/* -----------------------------------------------------------------------------
   5. Floating Badge Kinetics (Subtle Ambient Hover)
   ----------------------------------------------------------------------------- */
function initFloatingBadgeKinetics() {
  document.querySelectorAll(".floating-glass-card").forEach((card, index) => {
    // Create random offset for natural organic motion
    const yOffset = index % 2 === 0 ? -12 : 12;
    const duration = 4.5 + (index * 0.7);

    gsap.to(card, {
      y: `+=${yOffset}`,
      rotation: index % 2 === 0 ? 0.9 : -0.9,
      duration: duration,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut"
    });
  });
}

/* -----------------------------------------------------------------------------
   6. Numerical Counter Kinetics (Scroll-Triggered Count Up)
   ----------------------------------------------------------------------------- */
function initCounterKinetics() {
  const counters = document.querySelectorAll("[data-counter]");
  counters.forEach(counter => {
    const targetVal = parseInt(counter.getAttribute("data-counter"), 10);
    if (isNaN(targetVal)) return;

    ScrollTrigger.create({
      trigger: counter,
      start: "top 85%",
      once: true,
      onEnter: () => {
        gsap.fromTo(counter, 
          { innerText: 0 }, 
          {
            innerText: targetVal,
            duration: 1.8,
            ease: "power2.out",
            snap: { innerText: 1 },
            onUpdate: function() {
              counter.innerText = Math.ceil(this.targets()[0].innerText).toLocaleString();
            }
          }
        );
      }
    });
  });
}
