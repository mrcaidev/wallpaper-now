export class RequestError extends Error {
  public readonly status: number;

  public constructor(status: number, message: string) {
    super(message);
    this.name = "RequestError";
    this.status = status;
  }
}

async function wrappedFetch<T>(input: string, init: RequestInit) {
  const token = localStorage.getItem("token");

  const res = await fetch(import.meta.env.VITE_API_BASE_URL + input, {
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
  get: async <T>(pathname: string, init: RequestInit = {}) => {
    return await wrappedFetch<T>(pathname, { method: "GET", ...init });
  },

  post: async <T>(
    pathname: string,
    data: unknown = {},
    init: RequestInit = {},
  ) => {
    return await wrappedFetch<T>(pathname, {
      method: "POST",
      body: JSON.stringify(data),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  },

  put: async <T>(
    pathname: string,
    data: unknown = {},
    init: RequestInit = {},
  ) => {
    return await wrappedFetch<T>(pathname, {
      method: "PUT",
      body: JSON.stringify(data),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  },

  patch: async <T>(
    pathname: string,
    data: unknown = {},
    init: RequestInit = {},
  ) => {
    return await wrappedFetch<T>(pathname, {
      method: "PATCH",
      body: JSON.stringify(data),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  },

  delete: async <T>(pathname: string, init: RequestInit = {}) => {
    return await wrappedFetch<T>(pathname, { method: "DELETE", ...init });
  },
};
