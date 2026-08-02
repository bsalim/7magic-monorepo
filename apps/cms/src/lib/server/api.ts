import { env } from '$env/dynamic/public';

const fallbackApiBaseUrl = 'http://127.0.0.1:8003';

export class ApiRequestError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

type ServerApiRequest = RequestInit & {
  token?: string | null;
};

// Server-only module ($lib/server is never bundled for the browser), so this
// always wants the internal loopback URL -- Node cannot resolve the
// *.localhost host that Caddy serves to the browser.
export function getApiBaseUrl(): string {
  return env.PUBLIC_API_INTERNAL_URL || env.PUBLIC_API_BASE_URL || fallbackApiBaseUrl;
}

export async function apiFetch<T>(path: string, init: ServerApiRequest = {}): Promise<T> {
  const { token, ...requestInit } = init;
  const headers = new Headers(requestInit.headers);
  headers.set('Accept', 'application/json');

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...requestInit,
    headers
  });

  if (!response.ok) {
    throw await toApiRequestError(response);
  }

  return response.json() as Promise<T>;
}

async function toApiRequestError(response: Response): Promise<ApiRequestError> {
  try {
    const payload = (await response.json()) as {
      error?: { code?: string; message?: string };
    };
    return new ApiRequestError(
      response.status,
      payload.error?.code ?? 'api_error',
      payload.error?.message ?? `API request failed: ${response.status}`
    );
  } catch {
    return new ApiRequestError(response.status, 'api_error', `API request failed: ${response.status}`);
  }
}
