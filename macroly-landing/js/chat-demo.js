/* =============================================================================
   MACROLY INTERACTIVE CHAT DEMONSTRATION ENGINE (Section 2 & 4)
   Realistic Natural Language Conversational Meal Logging & Corrections
   ============================================================================= */

document.addEventListener("DOMContentLoaded", () => {
  initChatDemoSection2();
  initCorrectionDemoSection4();
});

/* -----------------------------------------------------------------------------
   Section 2: Conversational Food Logging Timeline (Master Prompt Spec)
   Step 1: User message: "I had 2 boiled eggs, 200g rice and chicken curry."
   Step 2: AI typing indicator appears.
   Step 3: AI response appears: "Got it! I've identified your meal."
   Step 4: Three food cards appear (Boiled Eggs, Cooked Rice, Chicken Curry).
   Step 5: Nutrition summary appears (Calories, Protein, Carbs, Fats counting up).
   Step 6: Meal confirmation card appears ("Lunch successfully logged").
   ----------------------------------------------------------------------------- */
function initChatDemoSection2() {
  const chatContainer = document.getElementById("demoChatStream");
  const parsedCard = document.getElementById("demoParsedCard");
  const typingIndicator = document.getElementById("demoTypingIndicator");
  const replayBtn = document.getElementById("replayDemoBtn");
  const liveInput = document.getElementById("demoChatInput");
  const liveSendBtn = document.getElementById("demoSendBtn");
  const replayPromptBanner = document.getElementById("demoReplayPrompt");
  const phoneInteractive = document.getElementById("showcaseInteractivePhone");

  if (!chatContainer) return;

  let hasRun = false;
  let demoTimeouts = [];
  let typewriterInterval = null;
  let isPhoneHovered = false;
  let isCustomInputFocused = false;
  let isCycleCompleted = false;
  let mealCycleIndex = 0;

  // Preset demo meals that cycle continuously
  const demoMeals = [
    {
      userText: "I had 2 boiled eggs, 200g rice and chicken curry.",
      aiText: "Got it! I've identified your meal and calculated complete macronutrients.",
      badge: "🍛 Lunch Logged",
      calories: 685,
      items: [
        { name: "🥚 2 Boiled Eggs", macro: "156 kcal • 12g P" },
        { name: "🍚 200g Cooked Rice", macro: "260 kcal • 56g C" },
        { name: "🍗 Chicken Curry", macro: "269 kcal • 27g P" }
      ],
      confirmText: "Lunch successfully logged to daily dashboard"
    },
    {
      userText: "1 bowl Greek yogurt, fresh blueberries and almond butter.",
      aiText: "Identified high-protein snack! Parsed 3 ingredients with live macro sync.",
      badge: "🥣 Snack Logged",
      calories: 340,
      items: [
        { name: "🥣 Greek Yogurt (150g)", macro: "130 kcal • 15g P" },
        { name: "🫐 Fresh Blueberries", macro: "45 kcal • 10g C" },
        { name: "🥜 Almond Butter (1 tbsp)", macro: "165 kcal • 7g P" }
      ],
      confirmText: "Snack successfully logged to daily dashboard"
    }
  ];

  function clearAllTimeouts() {
    demoTimeouts.forEach(t => clearTimeout(t));
    demoTimeouts = [];
    if (typewriterInterval) {
      clearInterval(typewriterInterval);
      typewriterInterval = null;
    }
  }

  function queueTimeout(fn, delay) {
    const t = setTimeout(fn, delay);
    demoTimeouts.push(t);
    return t;
  }

  function fadeAndRestart(customText = null) {
    clearAllTimeouts();
    if (!customText) {
      mealCycleIndex = (mealCycleIndex + 1) % demoMeals.length;
    }
    
    // Dim the existing conversation slightly while the new meal types in the input
    const oldBubbles = chatContainer.querySelectorAll(".dynamic-demo-bubble");
    if (typeof gsap !== "undefined" && oldBubbles.length > 0) {
      gsap.to(oldBubbles, { opacity: 0.5, duration: 0.25 });
      if (parsedCard) gsap.to(parsedCard, { opacity: 0.5, duration: 0.25 });
    }

    runDemo(customText, true /* isTransitioning */);
  }

  // Fast, Snappy Typewriter simulation (Never blocked by hover or mouse interaction)
  function simulateTypewriter(text, onComplete) {
    if (!liveInput) {
      onComplete();
      return;
    }

    liveInput.value = "";
    liveInput.setAttribute("placeholder", "");
    let charIdx = 0;
    const chunkSize = 5; // Fast 5 chars per step: 50+ chars finish typing in ~110ms

    typewriterInterval = setInterval(() => {
      charIdx += chunkSize;
      if (charIdx > text.length) charIdx = text.length;
      liveInput.value = text.slice(0, charIdx);

      if (charIdx >= text.length) {
        clearInterval(typewriterInterval);
        typewriterInterval = null;

        // Snappy button press micro-animation (35ms + 50ms = 85ms)
        queueTimeout(() => {
          if (liveSendBtn) {
            liveSendBtn.style.transform = "scale(0.85)";
            liveSendBtn.style.backgroundColor = "#145638";
            queueTimeout(() => {
              liveSendBtn.style.transform = "scale(1)";
              liveSendBtn.style.backgroundColor = "";
              liveInput.value = "";
              liveInput.setAttribute("placeholder", "Describe your meal or snack...");
              onComplete();
            }, 50);
          } else {
            liveInput.value = "";
            onComplete();
          }
        }, 35);
      }
    }, 12);
  }

  function runDemo(customText = null, isTransitioning = false) {
    clearAllTimeouts();
    isCycleCompleted = false;

    // Only clear previous conversation if not smoothly transitioning
    if (!isTransitioning) {
      chatContainer.querySelectorAll(".dynamic-demo-bubble").forEach(el => el.remove());
      if (parsedCard) {
        parsedCard.style.display = "none";
        parsedCard.style.opacity = "0";
      }
    }
    if (typingIndicator) typingIndicator.style.display = "none";
    if (replayPromptBanner) replayPromptBanner.style.display = "none";

    const currentMeal = customText ? {
      userText: customText,
      aiText: "Identified your custom meal! Macronutrients calculated automatically.",
      badge: "🍽️ Meal Logged",
      calories: 520,
      items: [
        { name: customText.slice(0, 26) + (customText.length > 26 ? "..." : ""), macro: "520 kcal • 32g P" }
      ],
      confirmText: "Custom meal successfully logged to daily dashboard"
    } : demoMeals[mealCycleIndex];

    // Step 1: Ultra-fast typing begins immediately (15ms delay)
    queueTimeout(() => {
      simulateTypewriter(currentMeal.userText, () => {
        // Clear previous conversation now that the new message is ready to send
        chatContainer.querySelectorAll(".dynamic-demo-bubble").forEach(el => el.remove());
        if (parsedCard) {
          parsedCard.style.display = "none";
          parsedCard.style.opacity = "0";
        }

        // Step 2: User Message Bubble swoops in immediately
        const userBubble = document.createElement("div");
        userBubble.className = "chat-bubble chat-bubble-user dynamic-demo-bubble";
        userBubble.innerHTML = `
          ${currentMeal.userText}
          <div class="chat-time">${getCurrentTimeString()}</div>
        `;
        chatContainer.appendChild(userBubble);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        if (typeof gsap !== "undefined") {
          gsap.fromTo(userBubble, 
            { opacity: 0, y: 12, scale: 0.95 }, 
            { opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "back.out(1.2)" }
          );
        }

        // Step 3: AI Typing Indicator appears quickly (100ms)
        queueTimeout(() => {
          if (typingIndicator) {
            typingIndicator.style.display = "flex";
            chatContainer.appendChild(typingIndicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
          }
        }, 100);

        // Step 4: AI Reply Bubble appears (400ms)
        queueTimeout(() => {
          if (typingIndicator) typingIndicator.style.display = "none";

          const aiBubble = document.createElement("div");
          aiBubble.className = "chat-bubble chat-bubble-ai dynamic-demo-bubble";
          aiBubble.innerHTML = `
            ${currentMeal.aiText}
            <div class="chat-time">${getCurrentTimeString()}</div>
          `;
          chatContainer.appendChild(aiBubble);
          chatContainer.scrollTop = chatContainer.scrollHeight;

          if (typeof gsap !== "undefined") {
            gsap.fromTo(aiBubble, 
              { opacity: 0, y: 12, scale: 0.95 }, 
              { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power2.out" }
            );
          }
        }, 400);

        // Step 5: Parsed Food Card & Calorie Counter (750ms)
        queueTimeout(() => {
          const card = document.createElement("div");
          card.className = "parsed-meal-card dynamic-demo-bubble";
          card.style.display = "block";
          card.style.opacity = "1";
          card.innerHTML = `
            <div class="parsed-meal-header">
              <span class="meal-badge">${currentMeal.badge}</span>
              <span class="parsed-cal-counter" style="font-size:0.8rem;font-weight:800;color:var(--color-emerald);">0 kcal</span>
            </div>
            <div class="parsed-items-list">
              ${currentMeal.items.map(item => `
                <div class="parsed-item-row">
                  <span class="item-name-qty">${item.name}</span>
                  <span class="item-macros-brief">${item.macro}</span>
                </div>
              `).join("")}
            </div>
          `;
          chatContainer.appendChild(card);
          chatContainer.scrollTop = chatContainer.scrollHeight;

          if (typeof gsap !== "undefined") {
            gsap.fromTo(card, 
              { opacity: 0, y: 14, scale: 0.98 }, 
              { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "power3.out" }
            );

            const calBadge = card.querySelector(".parsed-cal-counter");
            if (calBadge && typeof gsap !== "undefined") {
              const calObj = { val: 0 };
              gsap.to(calObj, {
                val: currentMeal.calories,
                duration: 0.65,
                ease: "power2.out",
                onUpdate: () => {
                  calBadge.textContent = `${Math.round(calObj.val)} kcal`;
                }
              });
            }
          }
        }, 750);

        // Step 6: Confirmation Success Pill (1250ms)
        queueTimeout(() => {
          const confirmCard = document.createElement("div");
          confirmCard.className = "chat-confirmation-pill dynamic-demo-bubble";
          confirmCard.innerHTML = `
            <span class="confirm-check-disc">✓</span>
            <span>${currentMeal.confirmText}</span>
          `;
          chatContainer.appendChild(confirmCard);
          chatContainer.scrollTop = chatContainer.scrollHeight;

          if (typeof gsap !== "undefined") {
            gsap.fromTo(confirmCard, 
              { opacity: 0, scale: 0.9, y: 8 }, 
              { opacity: 1, scale: 1, y: 0, duration: 0.3, ease: "back.out(1.5)" }
            );
          }

          if (replayPromptBanner) {
            replayPromptBanner.style.display = "flex";
          }

          isCycleCompleted = true;
        }, 1250);

        // Step 7: Master Loop Delay (Hold full rich state for 5.0s before smoothly cycling)
        queueTimeout(() => {
          fadeAndRestart();
        }, 5800);
      });
    }, 15);
  }

  // Trigger on scroll via ScrollTrigger or IntersectionObserver
  if (typeof ScrollTrigger !== "undefined") {
    ScrollTrigger.create({
      trigger: "#how-it-works",
      start: "top 70%",
      once: true,
      onEnter: () => {
        if (!hasRun) {
          hasRun = true;
          runDemo();
        }
      }
    });
  } else {
    const section2 = document.getElementById("how-it-works");
    if (section2) {
      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !hasRun) {
          hasRun = true;
          runDemo();
        }
      }, { threshold: 0.35 });
      observer.observe(section2);
    }
  }

  // Interactive Replay Button
  if (replayBtn) {
    replayBtn.addEventListener("click", () => {
      fadeAndRestart();
    });
  }

  // Interactive Live Chat Input Demo (Custom user typing)
  if (liveSendBtn && liveInput) {
    const handleSend = () => {
      const text = liveInput.value.trim();
      if (text) {
        liveInput.value = "";
        fadeAndRestart(text);
      }
    };

    liveSendBtn.addEventListener("click", handleSend);
    liveInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleSend();
      }
    });
  }
}

/* -----------------------------------------------------------------------------
   Section 4: Conversational Meal Corrections Split-Screen
   User: "Actually, make that 3 rotis instead of 2."
   Macroly: "Updated your meal. Your nutrition totals have been recalculated."
   Shows smooth before/after morphing kinetics and numerical macro updates.
   ----------------------------------------------------------------------------- */
function initCorrectionDemoSection4() {
  const triggerBtn = document.getElementById("triggerCorrectionBtn");
  const rotiQtyElem = document.getElementById("correctionRotiQty");
  const mealCalsElem = document.getElementById("correctionMealCals");
  const mealStatusBadge = document.getElementById("correctionBadge");
  const aiCorrectionBubble = document.getElementById("aiCorrectionBubble");
  const carbStatElem = document.getElementById("correctionCarbStat");
  const proteinStatElem = document.getElementById("correctionProteinStat");
  const correctionHighlightCard = document.getElementById("correctionHighlightCard");

  let isCorrected = false;

  function toggleCorrection() {
    isCorrected = !isCorrected;

    if (isCorrected) {
      // 1. Reveal AI correction message
      if (aiCorrectionBubble) {
        aiCorrectionBubble.style.opacity = "1";
        if (typeof gsap !== "undefined") {
          gsap.fromTo(aiCorrectionBubble, 
            { scale: 0.95, y: 10 }, 
            { scale: 1, y: 0, duration: 0.4, ease: "back.out(1.2)" }
          );
        }
      }

      // 2. Highlight card with lime pulse
      if (correctionHighlightCard && typeof gsap !== "undefined") {
        gsap.fromTo(correctionHighlightCard, 
          { borderColor: "rgba(197, 244, 103, 0.9)", boxShadow: "0 0 25px rgba(197, 244, 103, 0.35)" }, 
          { borderColor: "rgba(20, 86, 56, 0.12)", boxShadow: "0 14px 40px rgba(20, 86, 56, 0.08)", duration: 1.2 }
        );
      }

      // 3. Animate numbers
      if (rotiQtyElem) {
        rotiQtyElem.textContent = "3 pcs (Whole Wheat)";
        rotiQtyElem.style.color = "var(--color-emerald)";
      }

      if (mealCalsElem && typeof gsap !== "undefined") {
        gsap.fromTo(mealCalsElem, 
          { innerText: 580 }, 
          {
            innerText: 720, 
            duration: 0.9, 
            snap: { innerText: 1 }, 
            ease: "power2.out",
            onUpdate: function() {
              mealCalsElem.innerText = `${Math.ceil(this.targets()[0].innerText)} kcal`;
            }
          }
        );
      }

      if (carbStatElem) carbStatElem.textContent = "78g (+22g Carbs)";
      if (proteinStatElem) proteinStatElem.textContent = "26g (+3g Protein)";

      if (mealStatusBadge) {
        mealStatusBadge.className = "transition-state-badge state-after";
        mealStatusBadge.textContent = "✓ Recalculated & Synced";
      }

      if (triggerBtn) {
        triggerBtn.innerHTML = `
          <span>↺</span> Reset to Original Meal (2 Rotis)
        `;
      }
    } else {
      if (aiCorrectionBubble) aiCorrectionBubble.style.opacity = "0.25";

      if (rotiQtyElem) {
        rotiQtyElem.textContent = "2 pcs (Whole Wheat)";
        rotiQtyElem.style.color = "inherit";
      }

      if (mealCalsElem && typeof gsap !== "undefined") {
        gsap.fromTo(mealCalsElem, 
          { innerText: 720 }, 
          {
            innerText: 580, 
            duration: 0.8, 
            snap: { innerText: 1 }, 
            ease: "power2.out",
            onUpdate: function() {
              mealCalsElem.innerText = `${Math.ceil(this.targets()[0].innerText)} kcal`;
            }
          }
        );
      }

      if (carbStatElem) carbStatElem.textContent = "56g Carbs";
      if (proteinStatElem) proteinStatElem.textContent = "23g Protein";

      if (mealStatusBadge) {
        mealStatusBadge.className = "transition-state-badge state-before";
        mealStatusBadge.textContent = "Original Entry";
      }

      if (triggerBtn) {
        triggerBtn.innerHTML = `
          <span>💬</span> Simulate Correction: "Actually, 3 rotis instead of 2"
        `;
      }
    }
  }

  if (triggerBtn) {
    triggerBtn.addEventListener("click", toggleCorrection);
  }
}

function getCurrentTimeString() {
  const now = new Date();
  let hours = now.getHours();
  let minutes = now.getMinutes();
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12;
  minutes = minutes < 10 ? "0" + minutes : minutes;
  return `${hours}:${minutes} ${ampm}`;
}
