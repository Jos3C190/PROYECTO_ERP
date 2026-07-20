/**
 * Centralised API client. Phase 0: thin wrapper around fetch with typed responses
 * and a single base URL. Auth/refresh interceptor and TanStack Query wiring
 * arrive in Phase 1.
 */
import { browser } from '$app/environment';
import { PUBLIC_API_URL } from '$env/static/public';

export const API_BASE_URL = PUBLIC_API_URL ?? 'http://localhost:8000';

export type ApiError = {
  code: string;
  message: string;
  status: number;
};

export class HttpError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
    this.name = 'HttpError';
  }
}

async function parseError(res: Response): Promise<HttpError> {
  let code = 'http_error';
  let message = `Request failed with status ${res.status}`;
  try {
    const body = (await res.json()) as { code?: string; message?: string };
    if (body?.code) code = body.code;
    if (body?.message) message = body.message;
  } catch {
    // keep defaults
  }
  return new HttpError(code, message, res.status);
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!browser && !path.startsWith('http')) {
    // Server-side calls in SvelteKit should use absolute URLs.
    throw new Error('apiFetch must receive an absolute URL when called on the server.');
  }
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...(init.headers ?? {})
    }
  });
  if (!res.ok) {
    throw await parseError(res);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export interface HealthReport {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  components: { name: string; status: string; detail?: string }[];
}

export const api = {
  health: {
    live: () => apiFetch<HealthReport>('/health/live'),
    ready: () => apiFetch<HealthReport>('/health/ready')
  }
};