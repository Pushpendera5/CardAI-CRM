(function () {
  const DEFAULT_API_BASE_URL = window.location.origin + "/api/v1";
  const storedApiBaseUrl = localStorage.getItem("cardaiApiBaseUrl");
  const PAGE_ROUTES = {
    "../login_cardai_crm/code.html": "/login",
    "login_cardai_crm/code.html": "/login",
    "../dashboard_cardai_crm/code.html": "/dashboard",
    "dashboard_cardai_crm/code.html": "/dashboard",
    "../contacts_cardai_crm/code.html": "/contacts",
    "contacts_cardai_crm/code.html": "/contacts",
    "../scan_card_cardai_crm/code.html": "/scan",
    "scan_card_cardai_crm/code.html": "/scan",
    "../companies_cardai_crm/code.html": "/companies",
    "companies_cardai_crm/code.html": "/companies",
    "../reports_cardai_crm/code.html": "/reports",
    "reports_cardai_crm/code.html": "/reports",
  };

  function normalizeApiBaseUrl(value) {
    if (!value) return null;
    try {
      const parsed = new URL(value, window.location.origin);
      return parsed.origin === window.location.origin ? parsed.origin + parsed.pathname.replace(/\/$/, "") : null;
    } catch {
      return null;
    }
  }

  const API_BASE_URL = normalizeApiBaseUrl(storedApiBaseUrl) || DEFAULT_API_BASE_URL;
  let refreshPromise = null;

  if (storedApiBaseUrl !== API_BASE_URL) {
    localStorage.setItem("cardaiApiBaseUrl", API_BASE_URL);
  }

  function resolvePagePath(path) {
    return PAGE_ROUTES[path] || path;
  }

  function getToken() {
    return localStorage.getItem("cardaiAccessToken");
  }

  function getRefreshToken() {
    return localStorage.getItem("cardaiRefreshToken");
  }

  function setTokens(tokens) {
    localStorage.setItem("cardaiAccessToken", tokens.access_token);
    localStorage.setItem("cardaiRefreshToken", tokens.refresh_token);
  }

  function clearTokens() {
    localStorage.removeItem("cardaiAccessToken");
    localStorage.removeItem("cardaiRefreshToken");
  }

  async function parseResponse(response) {
    if (response.status === 204 || response.headers.get("content-length") === "0") {
      return null;
    }
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    return response.blob();
  }

  function authHeaders(options = {}) {
    const headers = new Headers(options.headers || {});
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    return headers;
  }

  async function refreshTokens() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      throw new Error("Session expired. Please login again.");
    }
    if (!refreshPromise) {
      refreshPromise = fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
        .then(async (response) => {
          const payload = await parseResponse(response);
          if (!response.ok || !payload?.data) {
            clearTokens();
            throw new Error(payload?.message || "Session expired. Please login again.");
          }
          setTokens(payload.data);
          return payload.data;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }
    return refreshPromise;
  }

  async function request(path, options = {}, retryOnAuth = true) {
    const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers: authHeaders(options) });
    const payload = await parseResponse(response);

    if (response.status === 401 && retryOnAuth && getRefreshToken()) {
      try {
        await refreshTokens();
      } catch (error) {
        throw error;
      }
      return request(path, options, false);
    }

    if (!response.ok) {
      const message = payload && payload.message ? payload.message : "Request failed";
      throw new Error(message);
    }
    return payload;
  }

  async function download(path, filename) {
    const payload = await request(path, { method: "GET" });
    if (!(payload instanceof Blob)) {
      throw new Error("Download failed");
    }
    const url = URL.createObjectURL(payload);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function requireAuth() {
    if (!getToken()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  }

  function page(path) {
    window.location.href = resolvePagePath(path);
  }

  window.CardAI = {
    API_BASE_URL,
    getToken,
    setTokens,
    clearTokens,
    requireAuth,
    page,
    request,
    auth: {
      login: (email, password) => request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
      me: () => request("/auth/me"),
      refresh: () => refreshTokens(),
      logout: async () => {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          try {
            await request("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) }, false);
          } catch {
            // Ignore logout network/auth errors and clear local session anyway.
          }
        }
        clearTokens();
      },
      updateProfile: (payload) => request("/auth/me", { method: "PATCH", body: JSON.stringify(payload) }),
    },
    contacts: {
      list: (params = {}) => request(`/contacts?${new URLSearchParams(params).toString()}`),
      create: (payload) => request("/contacts", { method: "POST", body: JSON.stringify(payload) }),
      get: (contactId) => request(`/contacts/${contactId}`),
      update: (contactId, payload) => request(`/contacts/${contactId}`, { method: "PUT", body: JSON.stringify(payload) }),
      remove: (contactId) => request(`/contacts/${contactId}`, { method: "DELETE" }),
    },
    companies: {
      list: (params = {}) => request(`/companies?${new URLSearchParams(params).toString()}`),
      create: (payload) => request("/companies", { method: "POST", body: JSON.stringify(payload) }),
      get: (id) => request(`/companies/${id}`),
      update: (id, payload) => request(`/companies/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
      remove: (id) => request(`/companies/${id}`, { method: "DELETE" }),
    },
    reports: {
      overview: () => request("/reports/overview"),
      companies: () => request("/reports/companies"),
      recentScans: (limit = 8) => request(`/reports/recent-scans?limit=${limit}`),
      processingStatus: () => request("/reports/processing-status"),
      insights: () => request("/reports/insights"),
      dashboard: () => request("/reports/dashboard"),
    },
    cards: {
      scan: (file) => {
        const formData = new FormData();
        formData.append("image", file);
        return request("/cards/scan", { method: "POST", body: formData });
      },
    },
    exports: {
      downloadCsv: (params = {}) => download(`/exports/contacts.csv?${new URLSearchParams(params).toString()}`, "contacts.csv"),
      downloadXlsx: (params = {}) => download(`/exports/contacts.xlsx?${new URLSearchParams(params).toString()}`, "contacts.xlsx"),
      downloadPdf: () => download("/exports/contacts.pdf", "contacts.pdf"),
    },
    admin: {
      listUsers: (params = {}) => request(`/admin/users?${new URLSearchParams(params).toString()}`),
      createUser: (payload) => request("/admin/users", { method: "POST", body: JSON.stringify(payload) }),
      changeRole: (userId, role) => request(`/admin/users/${userId}/role?role=${encodeURIComponent(role)}`, { method: "PATCH" }),
      toggleStatus: (userId, isActive) => request(`/admin/users/${userId}/status?is_active=${isActive}`, { method: "PATCH" }),
      deleteUser: (userId) => request(`/admin/users/${userId}`, { method: "DELETE" }),
    },
  };
})();

