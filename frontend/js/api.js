// Macroly REST API Client with Supabase Bearer Authentication
const API_BASE = "";

const api = {
  authToken: localStorage.getItem("macroly_auth_token") || "",
  onUnauthorizedCallback: null,

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
    const res = await fetch(`${API_BASE}/api/config`);
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
  }
};
