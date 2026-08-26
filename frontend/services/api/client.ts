import { config } from "@/lib/config";
import { getCurrentSession } from "@/services/auth/store";
import { getAuthHeaders } from "@/services/auth/headers";

export class ApiError extends Error {
  status: number;
  details?: any;

  constructor(message: string, status: number, details?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: any;
  params?: Record<string, any>;
  timeoutMs?: number;
}

function normalizeUrl(endpoint: string, params?: Record<string, any>): string {
  let path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

  // FastAPI route endpoints are registered with trailing slash on root collections
  // e.g. /masjids/ instead of /masjids
  const collectionRoots = ["/masjids", "/schedules", "/programs", "/people", "/sync"];
  if (collectionRoots.includes(path)) {
    path = `${path}/`;
  }

  let fullUrl = `${config.apiUrl}${config.apiPrefix}${path}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((v) => searchParams.append(key, String(v)));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });
    const qs = searchParams.toString();
    if (qs) {
      fullUrl += `?${qs}`;
    }
  }

  return fullUrl;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    method = "GET",
    body,
    params,
    headers: customHeaders = {},
    timeoutMs = config.requestTimeoutMs,
    ...restOptions
  } = options;

  const url = normalizeUrl(endpoint, params);

  const session = getCurrentSession();
  const authHeaders = getAuthHeaders(session);

  const isMutating = ["POST", "PUT", "PATCH", "DELETE"].includes(
    method.toUpperCase()
  );

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...authHeaders,
    ...(customHeaders as Record<string, string>),
  };

  if (isMutating) {
    // Generate UUID request ID for audit tracking
    headers["X-Request-ID"] = `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  let requestBody: string | undefined;
  if (body !== undefined && body !== null) {
    headers["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: requestBody,
      signal: controller.signal,
      ...restOptions,
    });

    clearTimeout(timeoutId);

    if (response.status === 204) {
      return {} as T;
    }

    let responseData: any;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      responseData = await response.json();
    } else {
      const text = await response.text();
      try {
        responseData = JSON.parse(text);
      } catch {
        responseData = text;
      }
    }

    if (!response.ok) {
      const message =
        responseData?.detail ||
        responseData?.message ||
        `Request failed with status ${response.status}`;
      throw new ApiError(message, response.status, responseData);
    }

    return responseData as T;
  } catch (error: any) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error.name === "AbortError") {
      throw new ApiError("Request timed out", 408);
    }

    throw new ApiError(
      error.message || "Network request failed",
      0,
      error
    );
  }
}
