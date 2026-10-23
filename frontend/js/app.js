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

  // Avatar and user profile references
  const headerAvatarImg = document.getElementById("headerAvatarImg");
  const profileAvatarImg = document.getElementById("profileAvatarImg");
  const profileAvatarRing = document.getElementById("profileAvatarRing");
  const editAvatarBtn = document.getElementById("editAvatarBtn");
  const avatarFileInput = document.getElementById("avatarFileInput");

  let currentEditingMeal = null;
  let activeScreen = "dashboard";
  let supabaseClient = null;
  let authMode = "signin";
  let currentUserProfile = null;
  let latestDashboardData = null;

  // Chat auto-scrolling helper
  function scrollChatToBottom(smooth = true) {
    const screenContent = document.querySelector(".screen-content");
    if (screenContent) {
      if (smooth) {
        screenContent.scrollTo({ top: screenContent.scrollHeight, behavior: "smooth" });
      } else {
        screenContent.scrollTop = screenContent.scrollHeight;
      }
    }
    if (chatMessagesContainer) {
      if (smooth) {
        chatMessagesContainer.scrollTo({ top: chatMessagesContainer.scrollHeight, behavior: "smooth" });
      } else {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
      }
    }
  }

  const headerBackBtn = document.getElementById("headerBackBtn");
  const headerBrandSection = document.getElementById("headerBrandSection");

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
      if (headerBackBtn) headerBackBtn.style.display = "none";
    } else if (screen === "chat") {
      chatView.classList.add("active");
      currentScreenTitle.textContent = "Ai Nutrition Logger";
      chatStickyBar.style.display = "flex";
      if (headerBackBtn) headerBackBtn.style.display = "flex";
      setTimeout(() => {
        scrollChatToBottom(false);
      }, 40);
    } else if (screen === "stats") {
      statsView.classList.add("active");
      currentScreenTitle.textContent = "Weekly Trends";
      navStatsBtn.classList.add("active");
      chatStickyBar.style.display = "none";
      if (headerBackBtn) headerBackBtn.style.display = "flex";
      renderCalendar();
      renderSelectedDayInfo(selectedCalDate);
      renderWeeklyStreakBars();
    } else if (screen === "profile") {
      if (profileView) profileView.classList.add("active");
      currentScreenTitle.textContent = "My Profile";
      navProfileBtn.classList.add("active");
      chatStickyBar.style.display = "none";
      if (headerBackBtn) headerBackBtn.style.display = "flex";
    }
  }

  navHomeBtn.addEventListener("click", () => switchScreen("dashboard"));
  navPlusBtn.addEventListener("click", () => switchScreen("chat"));
  navStatsBtn.addEventListener("click", () => switchScreen("stats"));
  navProfileBtn.addEventListener("click", () => switchScreen("profile"));
  if (avatarBtn) avatarBtn.addEventListener("click", () => switchScreen("profile"));
  if (headerBackBtn) headerBackBtn.addEventListener("click", () => switchScreen("dashboard"));
  if (headerBrandSection) {
    headerBrandSection.addEventListener("click", (e) => {
      if (e.target !== headerBackBtn && !headerBackBtn.contains(e.target)) {
        switchScreen("dashboard");
      }
    });
  }
  viewAllLink.addEventListener("click", () => switchScreen("chat"));

  // Profile Interactive Controls & Theme Toggle
  const themeToggleSwitch = document.getElementById("themeToggleSwitch");
  const prefAppearanceRow = document.getElementById("prefAppearanceRow");
  const aiVoiceSwitch = document.getElementById("aiVoiceSwitch");
  const logoutBtn = document.getElementById("logoutBtn");
  const editProfileBtn = document.getElementById("editProfileBtn");
  const appearanceSubLabel = document.getElementById("appearanceSubLabel");

  function applyTheme(isDark, save = true) {
    const slider = themeToggleSwitch ? themeToggleSwitch.querySelector(".clay-toggle-slider") : null;
    if (isDark) {
      document.documentElement.setAttribute("data-theme", "dark");
      document.body.classList.add("dark-theme");
      if (themeToggleSwitch) {
        themeToggleSwitch.classList.add("dark-active");
        themeToggleSwitch.style.background = "#10b981";
      }
      if (slider) slider.style.transform = "translateX(20px)";
      if (appearanceSubLabel) appearanceSubLabel.textContent = "Soft Dark Mode (Active)";
    } else {
      document.documentElement.setAttribute("data-theme", "light");
      document.body.classList.remove("dark-theme");
      if (themeToggleSwitch) {
        themeToggleSwitch.classList.remove("dark-active");
        themeToggleSwitch.style.background = "#e2e8f0";
      }
      if (slider) slider.style.transform = "translateX(0px)";
      if (appearanceSubLabel) appearanceSubLabel.textContent = "Soft Clay Light Mode";
    }
    if (save) {
      localStorage.setItem("macroly_theme_manual", isDark ? "dark" : "light");
    }
  }

  // Default appearance is light mode only when someone opens the app
  let isCurrentDark = false;
  const manualTheme = localStorage.getItem("macroly_theme_manual");
  if (manualTheme === "dark") {
    isCurrentDark = true;
  }
  // Clear legacy auto-saved theme
  localStorage.removeItem("macroly_theme");
  applyTheme(isCurrentDark, false);

  function toggleTheme() {
    isCurrentDark = !isCurrentDark;
    applyTheme(isCurrentDark, true);
  }

  if (themeToggleSwitch) {
    themeToggleSwitch.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleTheme();
    });
  }
  if (prefAppearanceRow) {
    prefAppearanceRow.addEventListener("click", () => {
      toggleTheme();
    });
  }

  // Profile Picture Upload
  if (profileAvatarRing && avatarFileInput) {
    profileAvatarRing.addEventListener("click", () => avatarFileInput.click());
  }
  if (editAvatarBtn && avatarFileInput) {
    editAvatarBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      avatarFileInput.click();
    });
  }

  if (avatarFileInput) {
    avatarFileInput.addEventListener("change", async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file.");
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        alert("Image must be smaller than 5MB.");
        return;
      }

      const reader = new FileReader();
      reader.onload = async (evt) => {
        const dataUrl = evt.target.result;
        if (profileAvatarImg) profileAvatarImg.src = dataUrl;
        if (headerAvatarImg) headerAvatarImg.src = dataUrl;

        try {
          await api.updateAvatar(dataUrl);
          if (currentUserProfile) currentUserProfile.avatar_url = dataUrl;
        } catch (err) {
          console.error("Failed to save avatar:", err);
          alert("Failed to save avatar: " + err.message);
        }
      };
      reader.readAsDataURL(file);
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
    editProfileBtn.addEventListener("click", () => openVitalsModal());
  }
  const editVitalsBtn = document.getElementById("editVitalsBtn");
  if (editVitalsBtn) {
    editVitalsBtn.addEventListener("click", () => openVitalsModal());
  }
  const vitalsWeightSubcard = document.getElementById("vitalsWeightSubcard");
  if (vitalsWeightSubcard) {
    vitalsWeightSubcard.addEventListener("click", () => openVitalsModal());
  }
  const vitalsHeightSubcard = document.getElementById("vitalsHeightSubcard");
  if (vitalsHeightSubcard) {
    vitalsHeightSubcard.addEventListener("click", () => openVitalsModal());
  }

  if (resetDataBtn) {
    resetDataBtn.addEventListener("click", async () => {
      if (confirm("Reset today's meals and vitals?")) {
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
    latestDashboardData = data;

    // Calories
    calsConsumedVal.textContent = data.calories_consumed.toLocaleString();
    calsTargetVal.textContent = data.calorie_target.toLocaleString();
    calsLeftPill.textContent = `${data.calories_left.toLocaleString()} kcal left`;

    const calCircumference = 402;
    const targetCals = Math.max(1, data.calorie_target);
    const calPct = Math.min(1, data.calories_consumed / targetCals);
    calorieArc.style.strokeDashoffset = calCircumference - (calCircumference * calPct);

    // Protein
    pVal.textContent = Math.round(data.protein_consumed);
    pTarget.textContent = Math.round(data.protein_target);
    const targetProtein = Math.max(1, data.protein_target);
    const pPercent = Math.round((data.protein_consumed / targetProtein) * 100);
    pPct.textContent = `${pPercent}%`;
    const miniCircumference = 100.5;
    proteinRing.style.strokeDashoffset = miniCircumference - (miniCircumference * Math.min(1, data.protein_consumed / targetProtein));

    // Carbs
    cVal.textContent = Math.round(data.carbs_consumed);
    cTarget.textContent = Math.round(data.carbs_target);
    const targetCarbs = Math.max(1, data.carbs_target);
    const cPercent = Math.round((data.carbs_consumed / targetCarbs) * 100);
    cPct.textContent = `${cPercent}%`;
    carbsRing.style.strokeDashoffset = miniCircumference - (miniCircumference * Math.min(1, data.carbs_consumed / targetCarbs));

    // Fats
    fVal.textContent = Math.round(data.fats_consumed);
    fTarget.textContent = Math.round(data.fats_target);
    const targetFats = Math.max(1, data.fats_target);
    const fPercent = Math.round((data.fats_consumed / targetFats) * 100);
    fPct.textContent = `${fPercent}%`;
    fatsRing.style.strokeDashoffset = miniCircumference - (miniCircumference * Math.min(1, data.fats_consumed / targetFats));

    // Vitals
    workoutKcalVal.innerHTML = `${data.vitals.workout_kcal} <span class="vital-sub-val">kcal</span>`;
    workoutMinsVal.textContent = `(${data.vitals.workout_mins}m)`;
    hydrationVal.innerHTML = `${data.vitals.hydration_liters} <span class="vital-sub-val">/ ${data.vitals.hydration_target} L</span>`;
    weightVal.innerHTML = `${data.vitals.weight_kg} <span class="vital-sub-val">kg</span>`;

    const profileWeight = document.getElementById("profileWeightVal");
    const profileHeight = document.getElementById("profileHeightVal");
    const profileGoalWeight = document.getElementById("profileGoalWeightVal");
    const profileBmi = document.getElementById("profileBmiVal");

    if (data.vitals) {
      const w = parseFloat(data.vitals.weight_kg) || 64.2;
      const h = parseFloat(data.vitals.height_cm) || 172.0;
      const gw = parseFloat(data.vitals.target_weight_kg) || 62.0;
      const hM = h / 100;
      const bmiVal = (hM > 0) ? (w / (hM * hM)) : 21.7;

      if (profileWeight) profileWeight.textContent = w.toFixed(1);
      if (profileHeight) profileHeight.textContent = Math.round(h);
      if (profileGoalWeight) profileGoalWeight.textContent = `Goal: ${gw.toFixed(1)}`;
      if (profileBmi) profileBmi.textContent = `BMI ${bmiVal.toFixed(1)}`;
    }

    const profileSavedMeals = document.getElementById("profileSavedMealsCount");
    if (profileSavedMeals && data.meals) {
      profileSavedMeals.textContent = `${data.meals.length} custom meals logged`;
    }

    // Sync Goals Summary Card in Profile View
    const profCal = document.getElementById("profileGoalCalVal");
    const profP = document.getElementById("profileGoalProteinVal");
    const profC = document.getElementById("profileGoalCarbVal");
    const profF = document.getElementById("profileGoalFatVal");
    if (profCal) profCal.innerHTML = `${Math.round(data.calorie_target || 2000).toLocaleString()} <small>kcal</small>`;
    if (profP) profP.innerHTML = `${Math.round(data.protein_target || 130)} <small>g</small>`;
    if (profC) profC.innerHTML = `${Math.round(data.carbs_target || 220)} <small>g</small>`;
    if (profF) profF.innerHTML = `${Math.round(data.fats_target || 65)} <small>g</small>`;

    if (userGreeting && data.greeting) {
      userGreeting.innerHTML = data.greeting.replace(", ", ",<br>");
    }
    const dateSubtitle = document.getElementById("dateSubtitle");
    if (dateSubtitle) {
      try {
        const istFormatter = new Intl.DateTimeFormat("en-US", {
          timeZone: "Asia/Kolkata",
          weekday: "long",
          month: "short",
          day: "numeric"
        });
        dateSubtitle.textContent = istFormatter.format(new Date()).toUpperCase();
      } catch (e) {}
    }
    if (profileDisplayName && data.user_name) {
      profileDisplayName.textContent = data.user_name;
    }
    if (currentUserProfile && currentUserProfile.avatar_url) {
      if (profileAvatarImg) profileAvatarImg.src = currentUserProfile.avatar_url;
      if (headerAvatarImg) headerAvatarImg.src = currentUserProfile.avatar_url;
    }
    if (activeScreen === "stats") {
      renderSelectedDayInfo(selectedCalDate);
      renderWeeklyStreakBars();
    }

    // Meals List
    mealsCountPill.textContent = `${data.meals.length} meals`;
    mealsListContainer.innerHTML = "";

    if (!data.meals || data.meals.length === 0) {
      mealsListContainer.innerHTML = `
        <div style="text-align: center; padding: 24px 16px; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-card); margin: 6px 0;">
          <div style="font-size: 26px; margin-bottom: 6px;">🥗</div>
          <div style="font-weight: 700; color: var(--text-main); font-size: 13.5px; margin-bottom: 4px;">No meals logged yet today</div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.4;">Type or speak into AI Quick Log to record your breakfast, lunch, or snack!</div>
        </div>
      `;
      return;
    }

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
            <div class="meal-time-tag">${meal.meal_type}${meal.subtitle ? ` • ${meal.subtitle.replace(new RegExp('^' + meal.meal_type + '\\s*(?:•\\s*)?', 'i'), '').trim()}` : ""}</div>
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
            <button class="meal-action-btn delete-meal-trigger" data-id="${meal.id}" title="Delete meal">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
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

      const deleteBtn = card.querySelector(".delete-meal-trigger");
      if (deleteBtn) {
        deleteBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (confirm(`Remove "${meal.title}" from today's log?`)) {
            try {
              await api.deleteMeal(meal.id);
              await refreshDashboard();
            } catch (err) {
              alert("Failed to delete meal: " + err.message);
            }
          }
        });
      }

      mealsListContainer.appendChild(card);
    });
  }

  // Goals Management Modal Handlers
  const editGoalsBtn = document.getElementById("editGoalsBtn");
  const goalsModal = document.getElementById("goalsModal");
  const goalsModalCloseBtn = document.getElementById("goalsModalCloseBtn");
  const modalSaveGoalsBtn = document.getElementById("modalSaveGoalsBtn");
  const modalGoalCalories = document.getElementById("modalGoalCalories");
  const modalGoalProtein = document.getElementById("modalGoalProtein");
  const modalGoalCarbs = document.getElementById("modalGoalCarbs");
  const modalGoalFats = document.getElementById("modalGoalFats");

  if (editGoalsBtn && goalsModal) {
    editGoalsBtn.addEventListener("click", () => {
      const cal = currentUserProfile ? currentUserProfile.calorie_goal : (latestDashboardData ? latestDashboardData.calorie_target : 2000);
      const p = currentUserProfile ? currentUserProfile.protein_goal : (latestDashboardData ? latestDashboardData.protein_target : 130);
      const c = currentUserProfile ? currentUserProfile.carb_goal : (latestDashboardData ? latestDashboardData.carbs_target : 220);
      const f = currentUserProfile ? currentUserProfile.fat_goal : (latestDashboardData ? latestDashboardData.fats_target : 65);

      if (modalGoalCalories) modalGoalCalories.value = Math.round(cal);
      if (modalGoalProtein) modalGoalProtein.value = Math.round(p);
      if (modalGoalCarbs) modalGoalCarbs.value = Math.round(c);
      if (modalGoalFats) modalGoalFats.value = Math.round(f);

      goalsModal.classList.add("open");
    });
  }

  function closeGoalsModal() {
    if (goalsModal) goalsModal.classList.remove("open");
  }

  if (goalsModalCloseBtn) {
    goalsModalCloseBtn.addEventListener("click", closeGoalsModal);
  }
  if (goalsModal) {
    goalsModal.addEventListener("click", (e) => {
      if (e.target === goalsModal) closeGoalsModal();
    });
  }

  if (modalSaveGoalsBtn) {
    modalSaveGoalsBtn.addEventListener("click", async () => {
      const cal = parseInt(modalGoalCalories.value) || 2000;
      const p = parseFloat(modalGoalProtein.value) || 130;
      const c = parseFloat(modalGoalCarbs.value) || 220;
      const f = parseFloat(modalGoalFats.value) || 65;

      modalSaveGoalsBtn.disabled = true;
      modalSaveGoalsBtn.textContent = "Saving Targets...";

      try {
        const res = await api.updateGoals({
          calorie_goal: cal,
          protein_goal: p,
          carb_goal: c,
          fat_goal: f
        });
        if (res.user) currentUserProfile = res.user;
        closeGoalsModal();
        if (res.dashboard) {
          renderDashboardData(res.dashboard);
        } else {
          await refreshDashboard();
        }
      } catch (err) {
        alert("Failed to update goals: " + err.message);
      } finally {
        modalSaveGoalsBtn.disabled = false;
        modalSaveGoalsBtn.textContent = "Save Nutrition Targets";
      }
    });
  }

  // ================= USER VITALS (HEIGHT & WEIGHT) MODAL =================
  const vitalsModal = document.getElementById("vitalsModal");
  const vitalsModalCloseBtn = document.getElementById("vitalsModalCloseBtn");
  const modalSaveVitalsBtn = document.getElementById("modalSaveVitalsBtn");
  const modalVitalsHeight = document.getElementById("modalVitalsHeight");
  const modalVitalsWeight = document.getElementById("modalVitalsWeight");
  const modalVitalsTargetWeight = document.getElementById("modalVitalsTargetWeight");
  const modalLiveBmi = document.getElementById("modalLiveBmi");

  function updateLiveBmi() {
    const h = parseFloat(modalVitalsHeight ? modalVitalsHeight.value : 172) || 172;
    const w = parseFloat(modalVitalsWeight ? modalVitalsWeight.value : 64) || 64;
    const hM = h / 100;
    const bmi = (hM > 0) ? (w / (hM * hM)) : 21.7;
    let cat = "Normal";
    if (bmi < 18.5) cat = "Underweight";
    else if (bmi >= 25 && bmi < 30) cat = "Overweight";
    else if (bmi >= 30) cat = "Obese";
    if (modalLiveBmi) modalLiveBmi.textContent = `${bmi.toFixed(1)} (${cat})`;
  }

  function openVitalsModal() {
    if (!vitalsModal) return;
    const v = (latestDashboardData && latestDashboardData.vitals) ? latestDashboardData.vitals : {};
    const curH = v.height_cm || (currentUserProfile && currentUserProfile.height_cm) || 172.0;
    const curW = v.weight_kg || (currentUserProfile && currentUserProfile.weight_kg) || 64.2;
    const curGoalW = v.target_weight_kg || (currentUserProfile && currentUserProfile.target_weight_kg) || 62.0;

    if (modalVitalsHeight) modalVitalsHeight.value = curH;
    if (modalVitalsWeight) modalVitalsWeight.value = curW;
    if (modalVitalsTargetWeight) modalVitalsTargetWeight.value = curGoalW;
    updateLiveBmi();

    vitalsModal.classList.add("open");
  }

  function closeVitalsModal() {
    if (vitalsModal) vitalsModal.classList.remove("open");
  }

  if (vitalsModalCloseBtn) {
    vitalsModalCloseBtn.addEventListener("click", closeVitalsModal);
  }
  if (vitalsModal) {
    vitalsModal.addEventListener("click", (e) => {
      if (e.target === vitalsModal) closeVitalsModal();
    });
  }
  if (modalVitalsHeight) modalVitalsHeight.addEventListener("input", updateLiveBmi);
  if (modalVitalsWeight) modalVitalsWeight.addEventListener("input", updateLiveBmi);

  if (modalSaveVitalsBtn) {
    modalSaveVitalsBtn.addEventListener("click", async () => {
      const h = parseFloat(modalVitalsHeight.value) || 172.0;
      const w = parseFloat(modalVitalsWeight.value) || 64.2;
      const targetW = parseFloat(modalVitalsTargetWeight.value) || 62.0;

      modalSaveVitalsBtn.disabled = true;
      modalSaveVitalsBtn.textContent = "Saving Vitals...";

      try {
        const res = await api.updateVitals({
          height_cm: h,
          weight_kg: w,
          target_weight_kg: targetW
        });
        closeVitalsModal();
        if (res.dashboard) {
          renderDashboardData(res.dashboard);
        } else {
          await refreshDashboard();
        }
      } catch (err) {
        alert("Failed to update vitals: " + err.message);
      } finally {
        modalSaveVitalsBtn.disabled = false;
        modalSaveVitalsBtn.textContent = "Save Body Vitals";
      }
    });
  }

  // ================= DAY TRANSITION (IST 12:00 AM ROLLOVER) =================
  const dayTransitionModal = document.getElementById("dayTransitionModal");
  const dayTransitionCloseBtn = document.getElementById("dayTransitionCloseBtn");
  const startNewDayBtn = document.getElementById("startNewDayBtn");
  const transitionYesterdayDate = document.getElementById("transitionYesterdayDate");
  const transitionYesterdayCals = document.getElementById("transitionYesterdayCals");
  const transitionYesterdayMeals = document.getElementById("transitionYesterdayMeals");
  const transitionYesterdayProtein = document.getElementById("transitionYesterdayProtein");
  const transitionYesterdayCarbs = document.getElementById("transitionYesterdayCarbs");
  const transitionYesterdayFats = document.getElementById("transitionYesterdayFats");

  async function checkDayTransition() {
    if (!api.getAuthToken()) return;
    try {
      const status = await api.getDayStatus();
      if (status && status.show_transition && status.yesterday_summary) {
        const s = status.yesterday_summary;
        if (transitionYesterdayDate) transitionYesterdayDate.textContent = s.date || "Yesterday";
        if (transitionYesterdayCals) transitionYesterdayCals.innerHTML = `${Math.round(s.calories || 0)} <small>kcal</small>`;
        if (transitionYesterdayMeals) transitionYesterdayMeals.innerHTML = `${s.meals_count || 0} <small>meals</small>`;
        if (transitionYesterdayProtein) transitionYesterdayProtein.innerHTML = `${Math.round(s.protein || 0)} <small>g</small>`;
        if (transitionYesterdayCarbs) transitionYesterdayCarbs.innerHTML = `${Math.round(s.carbs || 0)} <small>g</small>`;
        if (transitionYesterdayFats) transitionYesterdayFats.innerHTML = `${Math.round(s.fats || 0)} <small>g</small>`;

        if (dayTransitionModal) dayTransitionModal.classList.add("open");
      }
    } catch (e) {
      console.warn("Day status check error:", e);
    }
  }

  function closeDayTransitionModal() {
    if (dayTransitionModal) dayTransitionModal.classList.remove("open");
  }

  if (dayTransitionCloseBtn) {
    dayTransitionCloseBtn.addEventListener("click", closeDayTransitionModal);
  }
  if (dayTransitionModal) {
    dayTransitionModal.addEventListener("click", (e) => {
      if (e.target === dayTransitionModal) closeDayTransitionModal();
    });
  }

  if (startNewDayBtn) {
    startNewDayBtn.addEventListener("click", async () => {
      startNewDayBtn.disabled = true;
      startNewDayBtn.textContent = "Starting New Day...";
      try {
        await api.startNewDay();
        closeDayTransitionModal();
        await refreshDashboard();
      } catch (err) {
        alert("Failed to start new day: " + err.message);
      } finally {
        startNewDayBtn.disabled = false;
        startNewDayBtn.innerHTML = `<span>🌅</span><span>Start New Day (Reset Today's Values)</span>`;
      }
    });
  }

  // Check transition on window focus & visibility
  window.addEventListener("focus", checkDayTransition);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") checkDayTransition();
  });

  // ================= DAILY NUTRITION HISTORY MODAL =================
  const historyModal = document.getElementById("historyModal");
  const historyModalCloseBtn = document.getElementById("historyModalCloseBtn");
  const viewHistoryBtn = document.getElementById("viewHistoryBtn");
  const historyCardRow = document.getElementById("historyCardRow");
  const historyModalList = document.getElementById("historyModalList");

  async function openHistoryModal() {
    if (!historyModal) return;
    historyModal.classList.add("open");
    if (historyModalList) {
      historyModalList.innerHTML = `<div class="history-empty-placeholder">Loading nutrition history...</div>`;
    }

    try {
      const history = await api.getUserHistory();
      if (!historyModalList) return;

      if (!history || history.length === 0) {
        historyModalList.innerHTML = `
          <div class="history-empty-placeholder">
            <div style="font-size:26px; margin-bottom:6px;">📅</div>
            <b>No daily records yet</b><br>
            Every midnight (IST), your active meals and macros will be summarized and archived here automatically!
          </div>
        `;
        return;
      }

      historyModalList.innerHTML = history.map(item => `
        <div class="history-day-card">
          <div class="history-day-header">
            <span class="history-date-badge">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
              ${item.date_str}
            </span>
            <span class="history-cals-badge">${Math.round(item.calories)} kcal</span>
          </div>
          <div class="history-macro-pills-row">
            <span class="history-macro-chip">
              <span class="dot-indicator dot-protein"></span>
              Protein: <b>${Math.round(item.protein)}g</b>
            </span>
            <span class="history-macro-chip">
              <span class="dot-indicator dot-carbs"></span>
              Carbs: <b>${Math.round(item.carbs)}g</b>
            </span>
            <span class="history-macro-chip">
              <span class="dot-indicator dot-fats"></span>
              Fats: <b>${Math.round(item.fats)}g</b>
            </span>
            <span class="history-macro-chip" style="color:var(--text-muted);">
              ${item.meals_count} meals
            </span>
          </div>
        </div>
      `).join("");
    } catch (err) {
      if (historyModalList) {
        historyModalList.innerHTML = `<div class="history-empty-placeholder" style="color:#ef4444;">Failed to load history: ${err.message}</div>`;
      }
    }
  }

  function closeHistoryModal() {
    if (historyModal) historyModal.classList.remove("open");
  }

  if (viewHistoryBtn) viewHistoryBtn.addEventListener("click", openHistoryModal);
  if (historyCardRow) historyCardRow.addEventListener("click", openHistoryModal);
  if (historyModalCloseBtn) historyModalCloseBtn.addEventListener("click", closeHistoryModal);
  if (historyModal) {
    historyModal.addEventListener("click", (e) => {
      if (e.target === historyModal) closeHistoryModal();
    });
  }

  // ================= CALENDAR & WEEKLY STATS =================
  let currentCalDate = new Date();
  let selectedCalDate = new Date();

  const calPrevMonthBtn = document.getElementById("calPrevMonthBtn");
  const calNextMonthBtn = document.getElementById("calNextMonthBtn");
  const calendarTodayBtn = document.getElementById("calendarTodayBtn");
  const calCurrentMonthTitle = document.getElementById("calCurrentMonthTitle");
  const calendarDaysGrid = document.getElementById("calendarDaysGrid");
  const statsSubDate = document.getElementById("statsSubDate");

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  function renderCalendar() {
    if (!calendarDaysGrid || !calCurrentMonthTitle) return;

    const year = currentCalDate.getFullYear();
    const month = currentCalDate.getMonth();

    calCurrentMonthTitle.textContent = `${monthNames[month]} ${year}`;
    if (statsSubDate) {
      statsSubDate.textContent = `${monthNames[month].toUpperCase()} ${year} • CONSISTENCY TRACKER`;
    }

    calendarDaysGrid.innerHTML = "";

    const firstDayIndex = new Date(year, month, 1).getDay(); // 0 is Sunday
    const lastDayDate = new Date(year, month + 1, 0).getDate();
    const prevLastDayDate = new Date(year, month, 0).getDate();

    const today = new Date();
    const isThisMonth = today.getFullYear() === year && today.getMonth() === month;

    // Previous month trailing days
    for (let x = firstDayIndex; x > 0; x--) {
      const dayNum = prevLastDayDate - x + 1;
      const cell = document.createElement("div");
      cell.className = "cal-day-cell other-month";
      cell.textContent = dayNum;
      calendarDaysGrid.appendChild(cell);
    }

    // Active month days
    for (let i = 1; i <= lastDayDate; i++) {
      const cell = document.createElement("div");
      cell.className = "cal-day-cell";
      cell.textContent = i;

      const isToday = isThisMonth && today.getDate() === i;
      if (isToday) cell.classList.add("today");

      const isSelected = selectedCalDate.getFullYear() === year &&
                         selectedCalDate.getMonth() === month &&
                         selectedCalDate.getDate() === i;
      if (isSelected) cell.classList.add("selected");

      // Visual indicator dot
      const dot = document.createElement("span");
      dot.className = "cal-day-dot";
      if (i <= (isThisMonth ? today.getDate() : lastDayDate)) {
        if (i % 7 !== 0) {
          dot.classList.add("dot-complete");
        } else {
          dot.classList.add("dot-partial");
        }
        cell.appendChild(dot);
      }

      cell.addEventListener("click", () => {
        selectedCalDate = new Date(year, month, i);
        renderCalendar();
        renderSelectedDayInfo(selectedCalDate);
      });

      calendarDaysGrid.appendChild(cell);
    }

    // Next month filler days
    const totalCells = firstDayIndex + lastDayDate;
    const remaining = (7 - (totalCells % 7)) % 7;
    for (let j = 1; j <= remaining; j++) {
      const cell = document.createElement("div");
      cell.className = "cal-day-cell other-month";
      cell.textContent = j;
      calendarDaysGrid.appendChild(cell);
    }
  }

  function renderSelectedDayInfo(date) {
    const titleEl = document.getElementById("selectedDayTitle");
    const pillEl = document.getElementById("selectedDayCalsPill");
    const progEl = document.getElementById("selectedDayProgFill");
    const pEl = document.getElementById("selDayP");
    const cEl = document.getElementById("selDayC");
    const fEl = document.getElementById("selDayF");
    const mealsListEl = document.getElementById("selectedDayMealsList");

    if (!titleEl) return;

    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();
    const dateFormatted = `${monthNames[date.getMonth()]} ${date.getDate()}`;
    titleEl.textContent = isToday ? `Today, ${dateFormatted}` : dateFormatted;

    const userTarget = currentUserProfile ? currentUserProfile.calorie_goal : 2200;
    const pTarget = currentUserProfile ? currentUserProfile.protein_goal : 140;
    const cTarget = currentUserProfile ? currentUserProfile.carb_goal : 220;
    const fTarget = currentUserProfile ? currentUserProfile.fat_goal : 65;

    if (isToday && latestDashboardData) {
      const consumed = Math.round(latestDashboardData.calories_consumed || 0);
      const pct = Math.min(100, Math.round((consumed / userTarget) * 100));
      if (pillEl) pillEl.textContent = `${consumed} / ${userTarget} kcal`;
      if (progEl) progEl.style.width = `${pct}%`;
      if (pEl) pEl.textContent = `${Math.round(latestDashboardData.protein_consumed || 0)}g P`;
      if (cEl) cEl.textContent = `${Math.round(latestDashboardData.carbs_consumed || 0)}g C`;
      if (fEl) fEl.textContent = `${Math.round(latestDashboardData.fats_consumed || 0)}g F`;

      if (mealsListEl) {
        if (latestDashboardData.meals && latestDashboardData.meals.length > 0) {
          mealsListEl.innerHTML = latestDashboardData.meals.map(m => `
            <div class="selected-meal-preview-item">
              <span class="selected-meal-name">${m.food_name || m.title}</span>
              <span class="selected-meal-cals">${m.calories || m.total_calories} kcal</span>
            </div>
          `).join("");
        } else {
          mealsListEl.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:8px;">No meals logged today yet.</div>`;
        }
      }
    } else {
      const isPast = date < today;
      if (isPast) {
        const estCal = Math.round(userTarget * 0.92);
        if (pillEl) pillEl.textContent = `${estCal} / ${userTarget} kcal`;
        if (progEl) progEl.style.width = `92%`;
        if (pEl) pEl.textContent = `${Math.round(pTarget * 0.95)}g P`;
        if (cEl) cEl.textContent = `${Math.round(cTarget * 0.9)}g C`;
        if (fEl) fEl.textContent = `${Math.round(fTarget * 0.88)}g F`;
        if (mealsListEl) {
          mealsListEl.innerHTML = `
            <div class="selected-meal-preview-item">
              <span class="selected-meal-name">Avocado Sourdough & Eggs</span>
              <span class="selected-meal-cals">420 kcal</span>
            </div>
            <div class="selected-meal-preview-item">
              <span class="selected-meal-name">Quinoa Chicken Bowl</span>
              <span class="selected-meal-cals">580 kcal</span>
            </div>
          `;
        }
      } else {
        if (pillEl) pillEl.textContent = `0 / ${userTarget} kcal`;
        if (progEl) progEl.style.width = `0%`;
        if (pEl) pEl.textContent = `0g P`;
        if (cEl) cEl.textContent = `0g C`;
        if (fEl) fEl.textContent = `0g F`;
        if (mealsListEl) {
          mealsListEl.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:8px;">Upcoming date • No logs yet</div>`;
        }
      }
    }
  }

  function renderWeeklyStreakBars() {
    const container = document.getElementById("weeklyBarsContainer");
    if (!container) return;

    const daysShort = ["M", "T", "W", "T", "F", "S", "S"];
    const heights = [75, 90, 82, 95, 70, 65, 80];
    const todayDay = (new Date().getDay() + 6) % 7; // Monday = 0

    container.innerHTML = daysShort.map((day, idx) => {
      const isToday = idx === todayDay;
      const h = heights[idx];
      return `
        <div class="weekly-bar-col">
          <div class="weekly-bar-fill ${isToday ? 'active' : ''}" style="height: ${h}%;"></div>
          <span class="weekly-bar-day ${isToday ? 'today-day' : ''}">${day}</span>
        </div>
      `;
    }).join("");
  }

  if (calPrevMonthBtn) {
    calPrevMonthBtn.addEventListener("click", () => {
      currentCalDate.setMonth(currentCalDate.getMonth() - 1);
      renderCalendar();
    });
  }
  if (calNextMonthBtn) {
    calNextMonthBtn.addEventListener("click", () => {
      currentCalDate.setMonth(currentCalDate.getMonth() + 1);
      renderCalendar();
    });
  }
  if (calendarTodayBtn) {
    calendarTodayBtn.addEventListener("click", () => {
      currentCalDate = new Date();
      selectedCalDate = new Date();
      renderCalendar();
      renderSelectedDayInfo(selectedCalDate);
    });
  }

  // Initial Mockup 1 Chat Seed
  function initMockupChatSeed() {
    chatMessagesContainer.innerHTML = "";

    const isElena = currentUserProfile && (
      currentUserProfile.id === "86759b8f-d1fd-4f9a-9e3d-a93bf143c10b" || 
      currentUserProfile.id.includes("elena") || 
      currentUserProfile.id === "Elena" || 
      (currentUserProfile.email && currentUserProfile.email.toLowerCase().includes("elena"))
    );

    if (!isElena) {
      const firstName = (currentUserProfile && currentUserProfile.display_name) ? currentUserProfile.display_name.split(" ")[0] : "there";
      const welcomeHtml = `
        <div class="chat-response-ai">
          <div class="ai-message-sender-tag">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
            Macroly AI • Just now
          </div>
          <div class="ai-dialogue-text">
            Hi ${firstName}! 👋 Welcome to Macroly. Tell me or speak what you ate today (e.g. <i>"2 boiled eggs and avocado sourdough"</i>), and I will calculate your calories and nutrition goals immediately!
          </div>
        </div>
      `;
      chatMessagesContainer.insertAdjacentHTML("beforeend", welcomeHtml);
      scrollChatToBottom(false);
      return;
    }

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

    scrollChatToBottom(false);
  }

  function showAiLoadingBubble() {
    const bubble = document.createElement("div");
    bubble.className = "chat-loading-bubble";
    bubble.id = "chatAiLoadingBubble";
    bubble.innerHTML = `
      <div class="loading-avatar-pulsar">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="8"/>
          <path d="M12 8v8"/>
          <path d="M8 12h8"/>
        </svg>
      </div>
      <div class="loading-text-col">
        <div class="loading-title-msg">
          Analyzing & Calculating Macros
        </div>
        <div class="loading-sub-pulse">
          Macroly Intelligence Engine is thinking...
        </div>
        <div class="loading-wave-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    chatMessagesContainer.appendChild(bubble);
    scrollChatToBottom(true);
    return bubble;
  }

  function hideAiLoadingBubble() {
    const bubble = document.getElementById("chatAiLoadingBubble");
    if (bubble) bubble.remove();
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
    scrollChatToBottom(true);
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
          <div class="chat-meal-heading">${m.title || m.food_name || "Custom Meal"}</div>
          <div class="chat-meal-badges-line">
            <span class="tag-meal-type">${m.meal_type}</span>
            ${m.subtitle ? `<span class="tag-meal-subtitle">• ${m.subtitle.replace(new RegExp('^' + m.meal_type + '\\s*(?:•\\s*)?', 'i'), '').trim()}</span>` : ""}
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

    if (msg.meal_prompt) {
      const options = msg.options && msg.options.length ? msg.options : ["Breakfast", "Lunch", "Snacks", "Cheat Meal", "Dinner"];
      innerHtml += `
        <div class="meal-prompt-container">
          <div class="meal-prompt-label">Select Meal Category:</div>
          <div class="meal-prompt-buttons-row">
            ${options.map(opt => {
              let emoji = "🍽️";
              if (opt.toLowerCase().includes("breakfast")) emoji = "🍳";
              else if (opt.toLowerCase().includes("lunch")) emoji = "🍛";
              else if (opt.toLowerCase().includes("snack")) emoji = "🍎";
              else if (opt.toLowerCase().includes("cheat")) emoji = "🍕";
              else if (opt.toLowerCase().includes("dinner")) emoji = "🍲";
              return `<button type="button" class="meal-prompt-btn" data-meal="${opt}">${emoji} ${opt}</button>`;
            }).join("")}
          </div>
        </div>
      `;
    }

    if (msg.deleted_meal_id || msg.type === "meal_deleted") {
      innerHtml += `
        <div style="margin-top: 8px; display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; color: #dc2626; font-size: 12px; font-weight: 700;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          Meal removed directly from logging area
        </div>
      `;
    }

    aiWrap.innerHTML = innerHtml;
    chatMessagesContainer.appendChild(aiWrap);

    // Wire category prompt buttons
    aiWrap.querySelectorAll(".meal-prompt-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const mealChoice = btn.getAttribute("data-meal");
        if (mealChoice) {
          handleSendMessage(mealChoice);
        }
      });
    });

    if (msg.meal_data) {
      const editBtn = document.getElementById(`edit_${msg.meal_data.id}`);
      if (editBtn) {
        editBtn.addEventListener("click", () => openOverrideModal(msg.meal_data));
      }
    }

    scrollChatToBottom(true);
  }

  // Handle Sending Messages
  async function handleSendMessage(rawText) {
    const text = (rawText || chatTextInput.value).trim();
    if (!text) return;

    chatTextInput.value = "";
    dashboardQuickInput.value = "";

    // Show on chat screen
    appendUserBubble(text);
    scrollChatToBottom(true);

    showAiLoadingBubble();

    // Call API
    try {
      const aiResponse = await api.sendChatMessage(text);
      hideAiLoadingBubble();
      const messageToRender = aiResponse.message || aiResponse;
      appendAIMessage(messageToRender);
      scrollChatToBottom(true);
      if (aiResponse.suggestions && aiResponse.suggestions.length) {
        updateSuggestionChips(aiResponse.suggestions);
      }
      if (aiResponse.dashboard) {
        renderDashboardData(aiResponse.dashboard);
      } else {
        await refreshDashboard();
      }
    } catch (e) {
      console.error("Chat message error:", e);
      hideAiLoadingBubble();
      const errorMsg = (e && e.message && (e.message.includes("Failed to fetch") || e.message.includes("NetworkError")))
        ? "Unable to connect to Macroly backend server. Please check your connection or ensure the server is running."
        : "Sorry, I had trouble processing that. Please try again!";
      appendAIMessage({
        text: errorMsg,
        sender: "ai"
      });
      scrollChatToBottom(true);
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

  // Dynamic Suggestion Chips
  function updateSuggestionChips(suggestions) {
    const chipsScroll = document.querySelector(".quick-chips-scroll");
    if (!chipsScroll || !suggestions || !suggestions.length) return;
    chipsScroll.innerHTML = suggestions.map(s => 
      `<button class="suggestion-chip" data-text="${s}">${s}</button>`
    ).join("");
    wireSuggestionChips();
  }

  function wireSuggestionChips() {
    document.querySelectorAll(".suggestion-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const text = chip.dataset.text || chip.textContent;
        handleSendMessage(text);
      });
    });
  }
  wireSuggestionChips();

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
      // Parallelize profile & dashboard requests for instant screen load
      const [profile, dashboard] = await Promise.all([
        api.getUserProfile(),
        api.getDashboard()
      ]);

      currentUserProfile = profile;
      latestDashboardData = dashboard;

      if (profileDisplayName) profileDisplayName.textContent = profile.display_name;
      if (profileEmail) profileEmail.textContent = profile.email;
      if (userGreeting && profile.display_name) {
        userGreeting.textContent = `Welcome back, ${profile.display_name.split(" ")[0]}!`;
      }
      if (profile.avatar_url) {
        if (headerAvatarImg) headerAvatarImg.src = profile.avatar_url;
        if (profileAvatarImg) profileAvatarImg.src = profile.avatar_url;
      }

      // Check onboarding status
      if (!profile.is_onboarded) {
        if (onboardingOverlay) onboardingOverlay.classList.remove("hidden");
      } else {
        if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
      }

      renderDashboardData(dashboard);
      initMockupChatSeed();
      switchScreen("dashboard");
      await checkDayTransition();
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

  // Quick Demo Account Shortcut (Instant Access)
  if (demoAccountBtn) {
    demoAccountBtn.style.display = "flex";
    demoAccountBtn.addEventListener("click", async () => {
      await handleAuthSuccess("elena-demo-token");
    });
  }

  // Secret admin unlock: 3 taps on auth modal logo reveals demo button
  const authBrandLogoBadge = document.getElementById("authBrandLogoBadge");
  if (authBrandLogoBadge && demoAccountBtn) {
    let logoTaps = 0;
    authBrandLogoBadge.addEventListener("click", () => {
      logoTaps++;
      if (logoTaps >= 3) {
        demoAccountBtn.style.display = demoAccountBtn.style.display === "none" ? "flex" : "none";
        logoTaps = 0;
      }
    });
  }

  // Onboarding Goal Handlers
  if (onboardSaveBtn) {
    onboardSaveBtn.addEventListener("click", async () => {
      const cal = parseInt(onboardCalories.value) || 2000;
      const p = parseFloat(onboardProtein.value) || 130;
      const c = parseFloat(onboardCarbs.value) || 220;
      const f = parseFloat(onboardFats.value) || 65;

      onboardSaveBtn.disabled = true;
      onboardSaveBtn.textContent = "Saving Goals...";

      try {
        const res = await api.updateGoals({ calorie_goal: cal, protein_goal: p, carb_goal: c, fat_goal: f });
        if (res.user) currentUserProfile = res.user;
        if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
        if (res.dashboard) {
          renderDashboardData(res.dashboard);
        } else {
          await refreshDashboard();
        }
      } catch (err) {
        alert("Failed to save goals: " + err.message);
      } finally {
        onboardSaveBtn.disabled = false;
        onboardSaveBtn.textContent = "Save Daily Goals";
      }
    });
  }

  if (onboardSkipBtn) {
    onboardSkipBtn.addEventListener("click", async () => {
      try {
        const res = await api.updateGoals({ calorie_goal: 2000, protein_goal: 130, carb_goal: 220, fat_goal: 65 });
        if (res.user) currentUserProfile = res.user;
        if (onboardingOverlay) onboardingOverlay.classList.add("hidden");
        if (res.dashboard) {
          renderDashboardData(res.dashboard);
        } else {
          await refreshDashboard();
        }
      } catch (err) {
        alert("Failed to set default goals: " + err.message);
      }
    });
  }

  // APK Notice Popup Logic
  const apkNoticeToast = document.getElementById("apkNoticeToast");
  const apkToastClose = document.getElementById("apkToastClose");
  const apkInfoRow = document.getElementById("apkInfoRow");

  let apkToastTimer = null;

  function showApkNotice(customMsg) {
    if (!apkNoticeToast) return;
    if (customMsg) {
      const descEl = apkNoticeToast.querySelector(".apk-toast-desc");
      if (descEl) descEl.textContent = customMsg;
    }
    apkNoticeToast.classList.add("show");

    if (apkToastTimer) clearTimeout(apkToastTimer);
    apkToastTimer = setTimeout(() => {
      apkNoticeToast.classList.remove("show");
    }, 6500);
  }

  function hideApkNotice() {
    if (!apkNoticeToast) return;
    apkNoticeToast.classList.remove("show");
    if (apkToastTimer) clearTimeout(apkToastTimer);
  }

  if (apkToastClose) {
    apkToastClose.addEventListener("click", (e) => {
      e.stopPropagation();
      hideApkNotice();
    });
  }

  if (apkInfoRow) {
    apkInfoRow.addEventListener("click", () => {
      showApkNotice("APK update will be given soon! Stay tuned.");
    });
  }

  if (apkNoticeToast) {
    apkNoticeToast.addEventListener("mouseenter", () => {
      if (apkToastTimer) clearTimeout(apkToastTimer);
    });
    apkNoticeToast.addEventListener("mouseleave", () => {
      if (apkNoticeToast.classList.contains("show")) {
        apkToastTimer = setTimeout(hideApkNotice, 3500);
      }
    });
  }

  // Expose globally for interactive calls
  window.showApkUpdateNotice = showApkNotice;

  // Automatically trigger popup notice on load
  setTimeout(() => {
    showApkNotice("APK update will be given soon!");
  }, 1200);

  // Initial Boot with Supabase Authentication
  initAuth();
});

