// Thin wrapper around fetch for talking to the backend.
//
// Every request goes to /api/..., which the dev server (and later nginx) forwards
// to FastAPI. Because the browser only sees one origin, the session cookie is
// sent automatically.

export const API_BASE: string = "/api";

/** An error response from the backend, with the message FastAPI put in `detail`. */
export class ApiError extends Error {
  readonly status: number;
  /** Seconds to wait before retrying (from the Retry-After header, e.g. on 429). */
  readonly retryAfter: number | null;

  constructor(status: number, message: string, retryAfter: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (typeof body === "object" && body !== null && "detail" in body) {
      const detail: unknown = (body as { detail: unknown }).detail;
      if (typeof detail === "string") return detail;
    }
  } catch {
    // body was not JSON; fall through to the generic message
  }
  return `Request failed (${response.status})`;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { credentials: "same-origin", ...init });
  } catch {
    throw new ApiError(0, "Could not reach the server. Is the backend running?");
  }

  if (!response.ok) {
    const retryAfterHeader: string | null = response.headers.get("Retry-After");
    const retryAfter: number | null = retryAfterHeader !== null ? Number(retryAfterHeader) : null;
    throw new ApiError(
      response.status,
      await readErrorMessage(response),
      Number.isFinite(retryAfter) ? retryAfter : null,
    );
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
