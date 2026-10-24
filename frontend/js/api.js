// Macroly REST API Client with Supabase Bearer Authentication
const RENDER_BACKEND_URL = "https://macroly-v1-1.onrender.com";

const isCapacitor = typeof window !== "undefined" && (
  (window.Capacitor && typeof window.Capacitor.isNativePlatform === "function" && window.Capacitor.isNativePlatform()) ||
  window.location.protocol === "capacitor:" ||
  (window.location.hostname === "localhost" && !window.location.port)
);

const isLocalMachine = typeof window !== "undefined" && 
  (window.location.hostname === "127.0.0.1" || 
   (window.location.hostname === "localhost" && window.location.port && window.location.port !== "8000") ||
   window.location.protocol === "file:");

const API_BASE = isCapacitor
  ? RENDER_BACKEND_URL
  : (isLocalMachine ? "http://127.0.0.1:8000" : "");

const api = {
  authToken: localStorage.getItem("macroly_auth_token") || "",
  onUnauthorizedCallback: null,

  getBaseUrl() {
    return API_BASE;
  },

  isNativeApp() {
    return isCapacitor;
  },

  setAuthToken(token) {
    this.authToken = token || "";
    if (token) {
      localStorage.setItem("macroly_auth_token", token);
    } else {
      localStorage.removeItem("macroly_auth_token");
    }
  },

  getAuthToken() {
    return this.authToken;
  },

  onUnauthorized(cb) {
    this.onUnauthorizedCallback = cb;
  },

  async pingHealth(timeoutMs = 10000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(`${API_BASE}/api/health`, {
        signal: controller.signal,
        headers: { "Cache-Control": "no-cache" }
      });
      clearTimeout(timer);
      return res.ok;
    } catch (e) {
      clearTimeout(timer);
      return false;
    }
  },

  async wakeUpServer({ onSlowNotice, onProgress, maxSeconds = 90 } = {}) {
    const startTime = Date.now();
    let attempt = 0;

    const slowTimer = setTimeout(() => {
      if (typeof onSlowNotice === "function") {
        onSlowNotice();
      }
    }, 2200);

    while ((Date.now() - startTime) < maxSeconds * 1000) {
      attempt++;
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      if (typeof onProgress === "function") {
        onProgress({ attempt, elapsed });
      }

      const isHealthy = await this.pingHealth(9000);
      if (isHealthy) {
        clearTimeout(slowTimer);
        return true;
      }

      await new Promise(r => setTimeout(r, 2500));
    }

    clearTimeout(slowTimer);
    return false;
  },

  _getHeaders(includeJson = true) {
    const headers = {};
    if (includeJson) {
      headers["Content-Type"] = "application/json";
    }
    if (this.authToken) {
      headers["Authorization"] = `Bearer ${this.authToken}`;
    }
    return headers;
  },

  async _handleResponse(res, errorMessage = "Request failed") {
    if (res.status === 401) {
      this.setAuthToken("");
      if (this.onUnauthorizedCallback) {
        this.onUnauthorizedCallback();
      }
      throw new Error("Authentication session expired or invalid. Please sign in.");
    }
    if (!res.ok) {
      let detail = errorMessage;
      try {
        const errJson = await res.json();
        if (errJson && errJson.detail) detail = errJson.detail;
      } catch (e) {}
      throw new Error(detail);
    }
    return await res.json();
  },

  async getConfig() {
    let res;
    try {
      res = await fetch(`${API_BASE}/api/config`);
    } catch (err) {
      console.warn("Direct /api/config failed, checking server wake-up status...", err);
      const isAwake = await this.wakeUpServer();
      if (!isAwake) {
        throw new Error("Cloud server could not be reached. Please check your internet connection.");
      }
      res = await fetch(`${API_BASE}/api/config`);
    }
    return await this._handleResponse(res, "Failed to fetch Supabase config");
  },

  async getUserProfile() {
    const res = await fetch(`${API_BASE}/api/user/profile`, {
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to fetch user profile");
  },

  async updateGoals(goals) {
    const res = await fetch(`${API_BASE}/api/user/goals`, {
      method: "POST",
      headers: this._getHeaders(true),
      body: JSON.stringify(goals)
    });
    return await this._handleResponse(res, "Failed to update nutrition goals");
  },

  async updateAvatar(avatarUrl) {
    const res = await fetch(`${API_BASE}/api/user/avatar`, {
      method: "POST",
      headers: this._getHeaders(true),
      body: JSON.stringify({ avatar_url: avatarUrl })
    });
    return await this._handleResponse(res, "Failed to update profile picture");
  },

  async getDashboard() {
    const res = await fetch(`${API_BASE}/api/dashboard`, {
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to fetch dashboard");
  },

  async sendChatMessage(message) {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: this._getHeaders(true),
      body: JSON.stringify({ message })
    });
    return await this._handleResponse(res, "Failed to send chat message");
  },

  async getChatHistory() {
    const res = await fetch(`${API_BASE}/api/chat/history`, {
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to fetch chat history");
  },

  async overrideMeal(payload) {
    const res = await fetch(`${API_BASE}/api/meal/override`, {
      method: "POST",
      headers: this._getHeaders(true),
      body: JSON.stringify(payload)
    });
    return await this._handleResponse(res, "Failed to update meal");
  },

  async deleteMeal(mealId) {
    const res = await fetch(`${API_BASE}/api/meal/${mealId}`, {
      method: "DELETE",
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to delete meal");
  },

  async resetData() {
    const res = await fetch(`${API_BASE}/api/reset`, {
      method: "POST",
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to reset data");
  },

  async updateVitals(vitals) {
    const res = await fetch(`${API_BASE}/api/user/vitals`, {
      method: "POST",
      headers: this._getHeaders(true),
      body: JSON.stringify(vitals)
    });
    return await this._handleResponse(res, "Failed to update height and weight");
  },

  async getDayStatus() {
    const res = await fetch(`${API_BASE}/api/user/day-status`, {
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to check day status");
  },

  async startNewDay() {
    const res = await fetch(`${API_BASE}/api/user/start-new-day`, {
      method: "POST",
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to start new day");
  },

  async getUserHistory() {
    const res = await fetch(`${API_BASE}/api/user/history`, {
      headers: this._getHeaders(false)
    });
    return await this._handleResponse(res, "Failed to fetch nutrition history");
  }
};
