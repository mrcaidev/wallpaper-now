export class RequestError extends Error {
  public readonly status: number;

  public constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function wrappedFetch<T>(url: string, init: RequestInit) {
  const token = localStorage.getItem("token");

  const res = await fetch(import.meta.env.VITE_API_BASE_URL + url, {
    ...init,
    headers: {
      Authorization: token ? `Bearer ${token}` : "",
      ...init.headers,
    },
  });

  if (res.status === 204) {
    return undefined as T;
  }

  const json = await res.json();

  if (!res.ok) {
    throw new RequestError(res.status, json.error);
  }

  return json as T;
}

export const request = {
  get: async <T>(url: string, init: RequestInit = {}) => {
    return await wrappedFetch<T>(url, { method: "GET", ...init });
  },

  post: async <T>(url: string, data: unknown = {}, init: RequestInit = {}) => {
    return await wrappedFetch<T>(url, {
      method: "POST",
      body: JSON.stringify(data),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  },

  put: async <T>(url: string, data: unknown = {}, init: RequestInit = {}) => {
    return await wrappedFetch<T>(url, {
      method: "PUT",
      body: JSON.stringify(data),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  },

  patch: async <T>(url: string, data: unknown = {}, init: RequestInit = {}) => {
    return await wrappedFetch<T>(url, {
      method: "PATCH",
      body: JSON.stringify(data),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  },

  delete: async <T>(url: string, init: RequestInit = {}) => {
    return await wrappedFetch<T>(url, { method: "DELETE", ...init });
  },
};
