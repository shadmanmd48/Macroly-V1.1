// Macroly REST API Client with Supabase Bearer Authentication
const RENDER_BACKEND_URL = "https://macroly-v1-1.onrender.com";
const DEFAULT_SUPABASE_URL = "https://xvlyyyjaeseewvuvlwur.supabase.co";
const DEFAULT_SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2bHl5eWphZXNlZXd2dXZsd3VyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkyODU1MDMsImV4cCI6MjEwNDg2MTUwM30.b6VEA57s8IIx-AXXu_gMlp8WBjvp7X0bPJDQ1K8h8Lw";

const isCapacitor = typeof window !== "undefined" && (
  (window.Capacitor && typeof window.Capacitor.isNativePlatform === "function" && window.Capacitor.isNativePlatform()) ||
  window.location.protocol === "capacitor:" ||
  (window.location.hostname === "localhost" && !window.location.port)
);

let detectedApiBase = "";
if (typeof window !== "undefined") {
  const isLocalHost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  if (isLocalHost) {
    if (window.location.port === "8000") {
      detectedApiBase = "http://127.0.0.1:8000";
    } else {
      // When testing on static server (e.g. port 3000), connect to live cloud backend
      detectedApiBase = RENDER_BACKEND_URL;
    }
  } else if (isCapacitor || window.location.protocol === "file:") {
    detectedApiBase = RENDER_BACKEND_URL;
  }
}

const API_BASE = detectedApiBase;

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
    try {
      const res = await fetch(`${API_BASE}/api/config`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.supabase_url && data.supabase_anon_key) {
          return data;
        }
      }
    } catch (err) {
      console.warn("Direct /api/config failed, using fallback config...", err);
    }
    return {
      supabase_url: DEFAULT_SUPABASE_URL,
      supabase_anon_key: DEFAULT_SUPABASE_ANON_KEY
    };
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
