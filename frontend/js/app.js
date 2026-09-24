// Macroly Application Logic & Real-Time Sync
document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const dashboardView = document.getElementById("dashboardView");
  const chatView = document.getElementById("chatView");
  const statsView = document.getElementById("statsView");
  const profileView = document.getElementById("profileView");
  const currentScreenTitle = document.getElementById("currentScreenTitle");
  const chatStickyBar = document.getElementById("chatStickyBar");
  const avatarBtn = document.getElementById("avatarBtn");
  const resetDataBtn = document.getElementById("resetDataBtn");

  // Nav buttons
  const navHomeBtn = document.getElementById("navHomeBtn");
  const navPlusBtn = document.getElementById("navPlusBtn");
  const navStatsBtn = document.getElementById("navStatsBtn");
  const navProfileBtn = document.getElementById("navProfileBtn");
  const viewAllLink = document.getElementById("viewAllLink");

  // Dashboard elements
  const calorieArc = document.getElementById("calorieArc");
  const calsConsumedVal = document.getElementById("calsConsumedVal");
  const calsTargetVal = document.getElementById("calsTargetVal");
  const calsLeftPill = document.getElementById("calsLeftPill");
  const proteinRing = document.getElementById("proteinRing");
  const carbsRing = document.getElementById("carbsRing");
  const fatsRing = document.getElementById("fatsRing");
  const pVal = document.getElementById("pVal");
  const pTarget = document.getElementById("pTarget");
  const pPct = document.getElementById("pPct");
  const cVal = document.getElementById("cVal");
  const cTarget = document.getElementById("cTarget");
  const cPct = document.getElementById("cPct");
  const fVal = document.getElementById("fVal");
  const fTarget = document.getElementById("fTarget");
  const fPct = document.getElementById("fPct");
  const mealsListContainer = document.getElementById("mealsListContainer");
  const mealsCountPill = document.getElementById("mealsCountPill");
  const workoutKcalVal = document.getElementById("workoutKcalVal");
  const workoutMinsVal = document.getElementById("workoutMinsVal");
  const hydrationVal = document.getElementById("hydrationVal");
  const hydrationCard = document.getElementById("hydrationCard");
  const weightVal = document.getElementById("weightVal");

  // Quick inputs
  const dashboardQuickInput = document.getElementById("dashboardQuickInput");
  const dashboardSendBtn = document.getElementById("dashboardSendBtn");
  const dashboardMicBtn = document.getElementById("dashboardMicBtn");

  // Chat elements
  const chatMessagesContainer = document.getElementById("chatMessagesContainer");
  const chatTextInput = document.getElementById("chatTextInput");
  const chatSendBtn = document.getElementById("chatSendBtn");
  const chatMicBtn = document.getElementById("chatMicBtn");

  // Modal elements
  const overrideModal = document.getElementById("overrideModal");
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const modalItemsList = document.getElementById("modalItemsList");
  const modalSaveBtn = document.getElementById("modalSaveBtn");

  // Auth & Onboarding DOM elements
  const authOverlay = document.getElementById("authOverlay");
  const tabSignIn = document.getElementById("tabSignIn");
  const tabSignUp = document.getElementById("tabSignUp");
  const authErrorBanner = document.getElementById("authErrorBanner");
  const authEmailForm = document.getElementById("authEmailForm");
  const authEmailInput = document.getElementById("authEmailInput");
  const authPasswordInput = document.getElementById("authPasswordInput");
  const authSubmitBtn = document.getElementById("authSubmitBtn");
  const googleSignInBtn = document.getElementById("googleSignInBtn");
  const demoAccountBtn = document.getElementById("demoAccountBtn");

  const onboardingOverlay = document.getElementById("onboardingOverlay");
  const onboardCalories = document.getElementById("onboardCalories");
  const onboardProtein = document.getElementById("onboardProtein");
  const onboardCarbs = document.getElementById("onboardCarbs");
  const onboardFats = document.getElementById("onboardFats");
  const onboardSkipBtn = document.getElementById("onboardSkipBtn");
  const onboardSaveBtn = document.getElementById("onboardSaveBtn");

  const profileDisplayName = document.getElementById("profileDisplayName");
  const profileEmail = document.getElementById("profileEmail");
  const userGreeting = document.getElementById("userGreeting");

  let currentEditingMeal = null;
  let activeScreen = "dashboard";
  let supabaseClient = null;
  let authMode = "signin";

  // Navigation Logic
  function switchScreen(screen) {
    activeScreen = screen;
    dashboardView.classList.remove("active");
    chatView.classList.remove("active");
    statsView.classList.remove("active");
    if (profileView) profileView.classList.remove("active");

    navHomeBtn.classList.remove("active");
    navStatsBtn.classList.remove("active");
    navProfileBtn.classList.remove("active");

    if (screen === "dashboard") {
      dashboardView.classList.add("active");
      currentScreenTitle.textContent = "Dashboard";
      navHomeBtn.classList.add("active");
      chatStickyBar.style.display = "none";
    } else if (screen === "chat") {
      chatView.classList.add("active");
      currentScreenTitle.textContent = "Ai Nutrition Logger";
      chatStickyBar.style.display = "flex";
      setTimeout(() => {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
      }, 50);
    } else if (screen === "stats") {
      statsView.classList.add("active");
      currentScreenTitle.textContent = "Weekly Trends";
      navStatsBtn.classList.add("active");
      chatStickyBar.style.display = "none";
    } else if (screen === "profile") {
      if (profileView) profileView.classList.add("active");
      currentScreenTitle.textContent = "Ai Nutrition Logger";
      navProfileBtn.classList.add("active");
      chatStickyBar.style.display = "none";
    }
  }

  navHomeBtn.addEventListener("click", () => switchScreen("dashboard"));
  navPlusBtn.addEventListener("click", () => switchScreen("chat"));
  navStatsBtn.addEventListener("click", () => switchScreen("stats"));
  navProfileBtn.addEventListener("click", () => switchScreen("profile"));
  if (avatarBtn) avatarBtn.addEventListener("click", () => switchScreen("profile"));
  viewAllLink.addEventListener("click", () => switchScreen("chat"));

  // Profile Interactive Controls
  const themeToggleSwitch = document.getElementById("themeToggleSwitch");
  const aiVoiceSwitch = document.getElementById("aiVoiceSwitch");
  const logoutBtn = document.getElementById("logoutBtn");
  const editProfileBtn = document.getElementById("editProfileBtn");
  const appearanceSubLabel = document.getElementById("appearanceSubLabel");

  if (themeToggleSwitch) {
    let isDark = false;
    themeToggleSwitch.addEventListener("click", () => {
      isDark = !isDark;
      const slider = themeToggleSwitch.querySelector(".clay-toggle-slider");
      if (isDark) {
        themeToggleSwitch.style.background = "#10b981";
        if (slider) slider.style.transform = "translateX(18px)";
        if (appearanceSubLabel) appearanceSubLabel.textContent = "Soft Dark Mode";
      } else {
        themeToggleSwitch.style.background = "#f1f5f9";
        if (slider) slider.style.transform = "translateX(0px)";
        if (appearanceSubLabel) appearanceSubLabel.textContent = "Soft Clay Light Mode";
      }
    });
  }

  if (aiVoiceSwitch) {
    let isVoiceActive = true;
    aiVoiceSwitch.addEventListener("click", () => {
      isVoiceActive = !isVoiceActive;
      if (isVoiceActive) {
        aiVoiceSwitch.style.background = "#10b981";
        aiVoiceSwitch.style.justifyContent = "flex-end";
        const meta = document.querySelector("#prefAiRow .clay-item-meta");
        if (meta) {
          meta.textContent = "Auto-breakdown enabled";
          meta.className = "clay-item-meta text-emerald";
        }
      } else {
        aiVoiceSwitch.style.background = "#cbd5e1";
        aiVoiceSwitch.style.justifyContent = "flex-start";
        const meta = document.querySelector("#prefAiRow .clay-item-meta");
        if (meta) {
          meta.textContent = "Auto-breakdown disabled";
          meta.className = "clay-item-meta";
        }
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        if (supabaseClient) {
          await supabaseClient.auth.signOut();
        }
      } catch (e) {
        console.error("Logout error:", e);
      }
      api.setAuthToken("");
      showAuthOverlay();
    });
  }

  if (editProfileBtn) {
    editProfileBtn.addEventListener("click", () => {
      const newWeight = prompt("Update current weight (kg):", "64.2");
      if (newWeight && !isNaN(parseFloat(newWeight))) {
        const pw = document.getElementById("profileWeightVal");
        if (pw) pw.textContent = parseFloat(newWeight).toFixed(1);
        if (weightVal) weightVal.innerHTML = `${parseFloat(newWeight).toFixed(1)} <span class="vital-sub-val">kg</span>`;
      }
    });
  }

  if (resetDataBtn) {
    resetDataBtn.addEventListener("click", async () => {
      if (confirm("Reset today's meals to Elena's baseline demo meals?")) {
        try {
          await api.resetData();
          await refreshDashboard();
          switchScreen("dashboard");
        } catch (e) {
          alert("Error resetting meals: " + e.message);
        }
      }
    });
  }

  // Render Dashboard
  async function refreshDashboard() {
    try {
      const data = await api.getDashboard();
      renderDashboardData(data);
    } catch (e) {
      console.error("Dashboard refresh error:", e);
    }
  }

  function renderDashboardData(data) {
    // Calories
    calsConsumedVal.textContent = data.calories_consumed.toLocaleString();
    calsTargetVal.textContent = data.calorie_target.toLocaleString();
    calsLeftPill.textContent = `${data.calories_left.toLocaleString()} kcal left`;

    const calCircumference = 402;
    const calPct = Math.min(1, data.calories_consumed / data.calorie_target);
    calorieArc.style.strokeDashoffset = calCircumference - (calCircumference * calPct);

    // Protein
    pVal.textContent = Math.round(data.protein_consumed);
    pTarget.textContent = Math.round(data.protein_target);
    const pPercent = Math.round((data.protein_consumed / data.protein_target) * 100);
    pPct.textContent = `${pPercent}%`;
    const miniCircumference = 100.5;
    proteinRing.style.strokeDashoffset = miniCircumference - (miniCircumference * Math.min(1, data.protein_consumed / data.protein_target));

    // Carbs
    cVal.textContent = Math.round(data.carbs_consumed);
    cTarget.textContent = Math.round(data.carbs_target);
    const cPercent = Math.round((data.carbs_consumed / data.carbs_target) * 100);
    cPct.textContent = `${cPercent}%`;
    carbsRing.style.strokeDashoffset = miniCircumference - (miniCircumference * Math.min(1, data.carbs_consumed / data.carbs_target));

    // Fats
    fVal.textContent = Math.round(data.fats_consumed);
    fTarget.textContent = Math.round(data.fats_target);
    const fPercent = Math.round((data.fats_consumed / data.fats_target) * 100);
    fPct.textContent = `${fPercent}%`;
    fatsRing.style.strokeDashoffset = miniCircumference - (miniCircumference * Math.min(1, data.fats_consumed / data.fats_target));

    // Vitals
    workoutKcalVal.innerHTML = `${data.vitals.workout_kcal} <span class="vital-sub-val">kcal</span>`;
    workoutMinsVal.textContent = `(${data.vitals.workout_mins}m)`;
    hydrationVal.innerHTML = `${data.vitals.hydration_liters} <span class="vital-sub-val">/ ${data.vitals.hydration_target} L</span>`;
    weightVal.innerHTML = `${data.vitals.weight_kg} <span class="vital-sub-val">kg</span>`;

    const profileWeight = document.getElementById("profileWeightVal");
    if (profileWeight && data.vitals && data.vitals.weight_kg) {
      profileWeight.textContent = data.vitals.weight_kg;
    }
    const profileSavedMeals = document.getElementById("profileSavedMealsCount");
    if (profileSavedMeals && data.meals) {
      profileSavedMeals.textContent = `${data.meals.length} custom meals logged`;
    }

    if (userGreeting && data.greeting) {
      userGreeting.innerHTML = data.greeting.replace(", ", ",<br>");
    }
    if (profileDisplayName && data.user_name) {
      profileDisplayName.textContent = data.user_name;
    }

    // Meals List
    mealsCountPill.textContent = `${data.meals.length} meals`;
    mealsListContainer.innerHTML = "";

    data.meals.forEach(meal => {
      const card = document.createElement("div");
      card.className = "meal-item-card";

      const defaultThumb = meal.image_url || "/static/assets/quinoa_bowl.jpg";
      const thumbSrc = meal.meal_type.toLowerCase().includes("breakfast") 
        ? "/static/assets/avocado_toast.jpg"
        : meal.meal_type.toLowerCase().includes("snack")
        ? "/static/assets/greek_yogurt.jpg"
        : "/static/assets/quinoa_bowl.jpg";

      card.innerHTML = `
        <div class="meal-card-top">
          <div class="meal-card-thumb">
            <img src="${thumbSrc}" alt="${meal.title}" onerror="this.src='/static/assets/quinoa_bowl.jpg'">
          </div>
          <div class="meal-card-details">
            <div class="meal-time-tag">${meal.subtitle || meal.meal_type}</div>
            <div class="meal-item-name">${meal.title}</div>
            <div class="meal-item-cals">${meal.total_calories} kcal</div>
          </div>
          <div class="meal-item-actions">
            <button class="meal-action-btn edit-meal-trigger" data-id="${meal.id}" title="Edit / Adjust">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="21" x2="4" y2="14"/>
                <line x1="4" y1="10" x2="4" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12" y2="3"/>
                <line x1="20" y1="21" x2="20" y2="16"/>
                <line x1="20" y1="12" x2="20" y2="3"/>
                <line x1="1" y1="14" x2="7" y2="14"/>
                <line x1="9" y1="8" x2="15" y2="8"/>
                <line x1="17" y1="16" x2="23" y2="16"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="meal-card-macros-bar">
          <div class="macro-pill-indicator">
            <span class="dot-indicator dot-protein"></span>
            <span>Protein: <b>${Math.round(meal.protein)}g</b></span>
          </div>
          <div class="macro-pill-indicator">
            <span class="dot-indicator dot-carbs"></span>
            <span>Carbs: <b>${Math.round(meal.carbs)}g</b></span>
          </div>
          <div class="macro-pill-indicator">
            <span class="dot-indicator dot-fats"></span>
            <span>Fats: <b>${Math.round(meal.fats)}g</b></span>
          </div>
        </div>
      `;

      card.querySelector(".edit-meal-trigger").addEventListener("click", () => {
        openOverrideModal(meal);
      });

      mealsListContainer.appendChild(card);
    });
  }

  // Initial Mockup 1 Chat Seed
  function initMockupChatSeed() {
    chatMessagesContainer.innerHTML = "";

    // 1. User original message
    appendUserBubble("Had 2 whole wheat rotis with a bowl of chicken curry and cucumber salad for dinner", "8:14 PM");

    // 2. AI original parsed meal card
    const mealCardHtml = `
      <div class="chat-response-ai">
        <div class="ai-message-sender-tag">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
          Macroly AI • 8:14 PM
        </div>
        <div class="ai-dialogue-text">Logged that for you! Here is the nutritional breakdown:</div>
        <div class="chat-meal-card">
          <div class="chat-meal-card-top">
            <span class="chat-meal-food-icon">🍛</span>
            <button class="chat-card-edit-btn" id="seedEditBtn">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Edit
            </button>
          </div>
          <div class="chat-meal-heading">Chicken Curry & 2 Rotis</div>
          <div class="chat-meal-badges-line">
            <span class="tag-meal-type">Dinner</span>
            <span class="tag-meal-subtitle">• Cucumber Salad</span>
          </div>
          <div class="chat-meal-cals-big">
            540 <span>kcal</span>
          </div>
          <div class="chat-meal-macros-row">
            <div class="macro-capsule-item">
              <div class="macro-capsule-label"><span class="dot-indicator dot-protein"></span>Protein</div>
              <div class="macro-capsule-val">38g</div>
            </div>
            <div class="macro-capsule-item">
              <div class="macro-capsule-label"><span class="dot-indicator dot-carbs"></span>Carbs</div>
              <div class="macro-capsule-val">52g</div>
            </div>
            <div class="macro-capsule-item">
              <div class="macro-capsule-label"><span class="dot-indicator dot-fats"></span>Fats</div>
              <div class="macro-capsule-val">14g</div>
            </div>
          </div>
          <div class="itemized-breakdown-list">
            <div class="breakdown-row">
              <span class="breakdown-item-name">2x Whole Wheat Roti</span>
              <span class="breakdown-item-cals">220 kcal</span>
            </div>
            <div class="breakdown-row">
              <span class="breakdown-item-name">1x Chicken Curry Bowl</span>
              <span class="breakdown-item-cals">280 kcal</span>
            </div>
            <div class="breakdown-row">
              <span class="breakdown-item-name">1x Cucumber Salad</span>
              <span class="breakdown-item-cals">40 kcal</span>
            </div>
          </div>
        </div>
      </div>
    `;
    chatMessagesContainer.insertAdjacentHTML("beforeend", mealCardHtml);

    // 3. User contextual correction message
    appendUserBubble("Make that 3 rotis actually!", "8:15 PM");

    // 4. AI recalculated response card
    const recalcHtml = `
      <div class="chat-response-ai">
        <div class="ai-message-sender-tag">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          Macroly AI • Just now
        </div>
        <div class="ai-dialogue-text" style="display:flex; align-items:center; gap:6px;">
          <span style="display:inline-block;width:6px;height:6px;background:var(--primary);border-radius:50%;"></span>
          Updated dinner! Added 1 extra roti (+110 kcal).
        </div>
        <div class="recalc-update-card">
          <div class="recalc-header-row">
            <div class="recalc-title-group">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
              <span>Dinner Total Recalculated</span>
            </div>
            <span class="recalc-badge-pill">Updated</span>
          </div>
          <div class="recalc-calories-display">
            <span class="recalc-big-cals">650</span>
            <span class="recalc-unit">kcal</span>
            <span class="recalc-delta-badge">(+110 kcal)</span>
          </div>
          <div class="recalc-macros-strip">
            <div class="macro-pill-indicator">
              <span class="dot-indicator dot-protein"></span>
              <span>Protein: <b>41g</b></span>
            </div>
            <div class="macro-pill-indicator">
              <span class="dot-indicator dot-carbs"></span>
              <span>Carbs: <b>74g</b></span>
            </div>
            <div class="macro-pill-indicator">
              <span class="dot-indicator dot-fats"></span>
              <span>Fats: <b>16g</b></span>
            </div>
          </div>
          <div class="recalc-footer-sync">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span>Synchronized with Dashboard Entry #1084</span>
          </div>
        </div>
      </div>
    `;
    chatMessagesContainer.insertAdjacentHTML("beforeend", recalcHtml);

    const editBtn = document.getElementById("seedEditBtn");
    if (editBtn) {
      editBtn.addEventListener("click", () => {
        openOverrideModal({
          id: "meal_1084",
          title: "Chicken Curry & 3 Rotis",
          meal_type: "Dinner",
          items: [
            { name: "Whole Wheat Roti", quantity: 3, unit: "roti", calories: 330, protein: 9, carbs: 66, fats: 3 },
            { name: "Chicken Curry Bowl", quantity: 1, unit: "bowl", calories: 280, protein: 32, carbs: 8, fats: 12 },
            { name: "Cucumber Salad", quantity: 1, unit: "bowl", calories: 40, protein: 0.5, carbs: 4, fats: 0.5 }
          ]
        });
      });
    }
  }

  function appendUserBubble(text, timeStr) {
    const time = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble-user";
    bubble.innerHTML = `
      <div class="bubble-user-content">${text}</div>
      <div class="chat-timestamp">${time}</div>
    `;
    chatMessagesContainer.appendChild(bubble);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }

  function appendAIMessage(msg) {
    const aiWrap = document.createElement("div");
    aiWrap.className = "chat-response-ai";

    let innerHtml = `
      <div class="ai-message-sender-tag">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        Macroly AI • Just now
      </div>
      <div class="ai-dialogue-text">${msg.text}</div>
    `;

    if (msg.is_update && msg.meal_data) {
      const m = msg.meal_data;
      const sign = (msg.delta_kcal >= 0) ? "+" : "";
      innerHtml += `
        <div class="recalc-update-card">
          <div class="recalc-header-row">
            <div class="recalc-title-group">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
              <span>${m.meal_type} Total Recalculated</span>
            </div>
            <span class="recalc-badge-pill">Updated</span>
          </div>
          <div class="recalc-calories-display">
            <span class="recalc-big-cals">${m.total_calories}</span>
            <span class="recalc-unit">kcal</span>
            ${msg.delta_kcal ? `<span class="recalc-delta-badge">(${sign}${msg.delta_kcal} kcal)</span>` : ""}
          </div>
          <div class="recalc-macros-strip">
            <div class="macro-pill-indicator">
              <span class="dot-indicator dot-protein"></span>
              <span>Protein: <b>${Math.round(m.protein)}g</b></span>
            </div>
            <div class="macro-pill-indicator">
              <span class="dot-indicator dot-carbs"></span>
              <span>Carbs: <b>${Math.round(m.carbs)}g</b></span>
            </div>
            <div class="macro-pill-indicator">
              <span class="dot-indicator dot-fats"></span>
              <span>Fats: <b>${Math.round(m.fats)}g</b></span>
            </div>
          </div>
          <div class="recalc-footer-sync">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span>Synchronized with Dashboard Entry #${m.entry_number || 1084}</span>
          </div>
        </div>
      `;
    } else if (msg.meal_data) {
      const m = msg.meal_data;
      const breakdownRows = (m.items || []).map(it => `
        <div class="breakdown-row">
          <span class="breakdown-item-name">${it.quantity}x ${it.name}</span>
          <span class="breakdown-item-cals">${it.calories} kcal</span>
        </div>
      `).join("");

      innerHtml += `
        <div class="chat-meal-card">
          <div class="chat-meal-card-top">
            <span class="chat-meal-food-icon">🍽️</span>
            <button class="chat-card-edit-btn" id="edit_${m.id}">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Edit
            </button>
          </div>
          <div class="chat-meal-heading">${m.title}</div>
          <div class="chat-meal-badges-line">
            <span class="tag-meal-type">${m.meal_type}</span>
            ${m.subtitle ? `<span class="tag-meal-subtitle">• ${m.subtitle}</span>` : ""}
          </div>
          <div class="chat-meal-cals-big">
            ${m.total_calories} <span>kcal</span>
          </div>
          <div class="chat-meal-macros-row">
            <div class="macro-capsule-item">
              <div class="macro-capsule-label"><span class="dot-indicator dot-protein"></span>Protein</div>
              <div class="macro-capsule-val">${Math.round(m.protein)}g</div>
            </div>
            <div class="macro-capsule-item">
              <div class="macro-capsule-label"><span class="dot-indicator dot-carbs"></span>Carbs</div>
              <div class="macro-capsule-val">${Math.round(m.carbs)}g</div>
            </div>
            <div class="macro-capsule-item">
              <div class="macro-capsule-label"><span class="dot-indicator dot-fats"></span>Fats</div>
              <div class="macro-capsule-val">${Math.round(m.fats)}g</div>
            </div>
          </div>
          <div class="itemized-breakdown-list">
            ${breakdownRows}
          </div>
        </div>
      `;
    }

    aiWrap.innerHTML = innerHtml;
    chatMessagesContainer.appendChild(aiWrap);

    if (msg.meal_data) {
      const editBtn = document.getElementById(`edit_${msg.meal_data.id}`);
      if (editBtn) {
        editBtn.addEventListener("click", () => openOverrideModal(msg.meal_data));
      }
    }

    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }

  // Handle Sending Messages
  async function handleSendMessage(rawText) {
    const text = (rawText || chatTextInput.value).trim();
    if (!text) return;

    chatTextInput.value = "";
    dashboardQuickInput.value = "";

    // Show on chat screen
    appendUserBubble(text);

    // Call API
    try {
      const aiResponse = await api.sendChatMessage(text);
      appendAIMessage(aiResponse);
      await refreshDashboard();
    } catch (e) {
      console.error(e);
      appendAIMessage({
        text: "Sorry, I had trouble processing that. Please try again!",
        sender: "ai"
      });
    }
  }

  chatSendBtn.addEventListener("click", () => handleSendMessage());
  chatTextInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSendMessage();
  });

  // Dashboard quick log input
  dashboardSendBtn.addEventListener("click", () => {
    const val = dashboardQuickInput.value.trim();
    if (val) {
      switchScreen("chat");
      handleSendMessage(val);
    }
  });

  dashboardQuickInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const val = dashboardQuickInput.value.trim();
      if (val) {
        switchScreen("chat");
        handleSendMessage(val);
      }
    }
  });

  // Quick suggestion chips
  document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const text = chip.dataset.text || chip.textContent;
      handleSendMessage(text);
    });
  });

  // Speech Recognition Integration
  function setupSpeech(micBtn, inputTarget) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      micBtn.addEventListener("click", () => {
        alert("Speech-to-text is available on Chrome, Edge, and Safari with microphone permissions enabled.");
      });
      return;
    }

    const recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    let isListening = false;

    recognition.onstart = () => {
      isListening = true;
      micBtn.classList.add("voice-pulsing");
      inputTarget.placeholder = "Listening... speak now";
    };

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      inputTarget.value = transcript;
    };

    recognition.onend = () => {
      isListening = false;
      micBtn.classList.remove("voice-pulsing");
      inputTarget.placeholder = (inputTarget === dashboardQuickInput)
        ? "e.g., '1 glass iced latte with oat milk'..."
        : "Tell Macroly what you had...";
      if (inputTarget.value.trim()) {
        if (inputTarget === dashboardQuickInput) {
          switchScreen("chat");
        }
        handleSendMessage(inputTarget.value);
      }
    };

    recognition.onerror = () => {
      isListening = false;
      micBtn.classList.remove("voice-pulsing");
    };

    micBtn.addEventListener("click", () => {
      if (!isListening) {
        recognition.start();
      } else {
        recognition.stop();
      }
    });
  }

  setupSpeech(chatMicBtn, chatTextInput);
  setupSpeech(dashboardMicBtn, dashboardQuickInput);

  // Manual Override Modal Logic
  function openOverrideModal(meal) {
    currentEditingMeal = JSON.parse(JSON.stringify(meal));
    modalMealTitle.textContent = `Adjust: ${meal.title}`;
    modalItemsList.innerHTML = "";

    (currentEditingMeal.items || []).forEach((item, index) => {
      const row = document.createElement("div");
      row.className = "edit-item-row";
      row.innerHTML = `
        <div class="edit-item-info">
          <span class="edit-item-name">${item.name}</span>
          <span class="edit-item-unit-cal" id="itemCal_${index}">${item.calories} kcal (${item.protein}g P, ${item.carbs}g C, ${item.fats}g F)</span>
        </div>
        <div class="edit-qty-stepper">
          <button class="stepper-btn" data-action="minus" data-idx="${index}">-</button>
          <span class="stepper-val" id="qtyVal_${index}">${item.quantity}</span>
          <button class="stepper-btn" data-action="plus" data-idx="${index}">+</button>
        </div>
      `;
      modalItemsList.appendChild(row);
    });

    modalItemsList.querySelectorAll(".stepper-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const idx = parseInt(btn.dataset.idx);
        const action = btn.dataset.action;
        const targetItem = currentEditingMeal.items[idx];
        const unitCal = targetItem.calories / (targetItem.quantity || 1);
        const unitP = targetItem.protein / (targetItem.quantity || 1);
        const unitC = targetItem.carbs / (targetItem.quantity || 1);
        const unitF = targetItem.fats / (targetItem.quantity || 1);

        if (action === "plus") {
          targetItem.quantity += 1;
        } else if (action === "minus") {
          if (targetItem.quantity > 1) {
            targetItem.quantity -= 1;
          }
        }

        targetItem.calories = Math.round(unitCal * targetItem.quantity);
        targetItem.protein = Math.round(unitP * targetItem.quantity * 10) / 10;
        targetItem.carbs = Math.round(unitC * targetItem.quantity * 10) / 10;
        targetItem.fats = Math.round(unitF * targetItem.quantity * 10) / 10;

        document.getElementById(`qtyVal_${idx}`).textContent = targetItem.quantity;
        document.getElementById(`itemCal_${idx}`).textContent = `${targetItem.calories} kcal (${targetItem.protein}g P, ${targetItem.carbs}g C, ${targetItem.fats}g F)`;
      });
    });

    overrideModal.classList.add("open");
  }

  function closeOverrideModal() {
    overrideModal.classList.remove("open");
    currentEditingMeal = null;
  }

  modalCloseBtn.addEventListener("click", closeOverrideModal);
  overrideModal.addEventListener("click", (e) => {
    if (e.target === overrideModal) closeOverrideModal();
  });

  modalSaveBtn.addEventListener("click", async () => {
    if (!currentEditingMeal) return;
    try {
      await api.overrideMeal({
        meal_id: currentEditingMeal.id,
        items: currentEditingMeal.items
      });
      closeOverrideModal();
      await refreshDashboard();
      appendAIMessage({
        text: `Manually adjusted portions for ${currentEditingMeal.title}. Daily totals and dashboard rings updated!`,
        sender: "ai",
        is_update: false
      });
    } catch (err) {
      console.error(err);
      alert("Error updating meal: " + err.message);
    }
  });

  // Hydration card tap adds 250ml
  hydrationCard.addEventListener("click", async () => {
    try {
      const data = await api.getDashboard();
      data.vitals.hydration_liters = Math.round((data.vitals.hydration_liters + 0.25) * 100) / 100;
      hydrationVal.innerHTML = `${data.vitals.hydration_liters} <span class="vital-sub-val">/ 3.0 L</span>`;
    } catch (e) {
      console.error(e);
    }
  });

  // =========================================================================
  // SUPABASE AUTHENTICATION & ONBOARDING CONTROLLER
  // =========================================================================

  function showAuthOverlay() {
    if (authOverlay) authOverlay.classList.remove("hidden");
    if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
  }

  function hideAuthOverlay() {
    if (authOverlay) authOverlay.classList.add("hidden");
  }

  function showAuthError(msg) {
    if (authErrorBanner) {
      authErrorBanner.textContent = msg;
      authErrorBanner.style.display = "block";
    }
  }

  function clearAuthError() {
    if (authErrorBanner) {
      authErrorBanner.textContent = "";
      authErrorBanner.style.display = "none";
    }
  }

  async function handleAuthSuccess(token) {
    api.setAuthToken(token);
    hideAuthOverlay();
    clearAuthError();

    try {
      const profile = await api.getUserProfile();
      if (profileDisplayName) profileDisplayName.textContent = profile.display_name;
      if (profileEmail) profileEmail.textContent = profile.email;

      // Check onboarding status
      if (!profile.is_onboarded) {
        if (onboardingOverlay) onboardingOverlay.classList.remove("hidden");
      } else {
        if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
      }

      await refreshDashboard();
      initMockupChatSeed();
      switchScreen("dashboard");
    } catch (e) {
      console.error("Post-auth profile fetch failed:", e);
      showAuthOverlay();
    }
  }

  async function initAuth() {
    api.onUnauthorized(() => {
      showAuthOverlay();
    });

    try {
      const config = await api.getConfig();
      if (window.supabase && config.supabase_url && config.supabase_anon_key) {
        supabaseClient = window.supabase.createClient(config.supabase_url, config.supabase_anon_key);

        // Check active session on page load (e.g. after redirect or persisted session)
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session && session.access_token) {
          await handleAuthSuccess(session.access_token);
          return;
        }

        // Subscribe to auth state updates (e.g. after Google OAuth redirect)
        supabaseClient.auth.onAuthStateChange(async (event, session) => {
          if (session && session.access_token) {
            await handleAuthSuccess(session.access_token);
          } else if (!api.getAuthToken()) {
            showAuthOverlay();
          }
        });
      }
    } catch (e) {
      console.warn("Supabase init error:", e);
    }

    // Check existing stored token (e.g. demo account)
    const existingToken = api.getAuthToken();
    if (existingToken) {
      try {
        await handleAuthSuccess(existingToken);
        return;
      } catch (e) {
        api.setAuthToken("");
      }
    }

    // If no active session, present the auth screen
    showAuthOverlay();
  }

  // Auth Mode Tabs Switcher
  if (tabSignIn && tabSignUp) {
    tabSignIn.addEventListener("click", () => {
      authMode = "signin";
      tabSignIn.classList.add("active");
      tabSignUp.classList.remove("active");
      if (authSubmitBtn) authSubmitBtn.textContent = "Sign In";
      clearAuthError();
    });
    tabSignUp.addEventListener("click", () => {
      authMode = "signup";
      tabSignUp.classList.add("active");
      tabSignIn.classList.remove("active");
      if (authSubmitBtn) authSubmitBtn.textContent = "Create Account";
      clearAuthError();
    });
  }

  // Email/Password Form Submit
  if (authEmailForm) {
    authEmailForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearAuthError();
      const email = authEmailInput.value.trim();
      const password = authPasswordInput.value;
      if (!email || !password) return;

      if (!supabaseClient) {
        showAuthError("Supabase client is not available. Please verify network or config.");
        return;
      }

      authSubmitBtn.disabled = true;
      const originalText = authSubmitBtn.textContent;
      authSubmitBtn.textContent = "Please wait...";

      try {
        if (authMode === "signin") {
          const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
          if (error) throw error;
          if (data && data.session) {
            await handleAuthSuccess(data.session.access_token);
          }
        } else {
          const { data, error } = await supabaseClient.auth.signUp({
            email,
            password,
            options: { data: { name: email.split("@")[0] } }
          });
          if (error) throw error;
          if (data && data.session) {
            await handleAuthSuccess(data.session.access_token);
          } else {
            showAuthError("Account created! Please check your email inbox to confirm your address, then sign in.");
          }
        }
      } catch (err) {
        showAuthError(err.message || "Authentication failed.");
      } finally {
        authSubmitBtn.disabled = false;
        authSubmitBtn.textContent = originalText;
      }
    });
  }

  // Google OAuth Sign-In
  if (googleSignInBtn) {
    googleSignInBtn.addEventListener("click", async () => {
      if (!supabaseClient) {
        showAuthError("Supabase client is not available.");
        return;
      }
      try {
        const { error } = await supabaseClient.auth.signInWithOAuth({
          provider: "google",
          options: {
            redirectTo: window.location.origin
          }
        });
        if (error) throw error;
      } catch (err) {
        showAuthError(err.message || "Google sign-in failed.");
      }
    });
  }

  // Demo Elena Account Shortcut
  if (demoAccountBtn) {
    demoAccountBtn.addEventListener("click", async () => {
      await handleAuthSuccess("elena-demo-token");
    });
  }

  // Onboarding Goal Handlers
  if (onboardSaveBtn) {
    onboardSaveBtn.addEventListener("click", async () => {
      const cal = parseInt(onboardCalories.value) || 2000;
      const p = parseFloat(onboardProtein.value) || 130;
      const c = parseFloat(onboardCarbs.value) || 220;
      const f = parseFloat(onboardFats.value) || 65;

      try {
        await api.updateGoals({ calorie_goal: cal, protein_goal: p, carb_goal: c, fat_goal: f });
        if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
        await refreshDashboard();
      } catch (err) {
        alert("Failed to save goals: " + err.message);
      }
    });
  }

  if (onboardSkipBtn) {
    onboardSkipBtn.addEventListener("click", async () => {
      try {
        await api.updateGoals({ calorie_goal: 2000, protein_goal: 130, carb_goal: 220, fat_goal: 65 });
        if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
        await refreshDashboard();
      } catch (err) {
        alert("Failed to set default goals: " + err.message);
      }
    });
  }

  // Initial Boot with Supabase Authentication
  initAuth();
});

