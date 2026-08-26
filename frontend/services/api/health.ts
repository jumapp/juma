import { config } from "@/lib/config";

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
}

export interface FullHealthResponse extends HealthResponse {
  database: string;
  timestamp: string;
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${config.apiUrl}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

export async function checkFullHealth(): Promise<FullHealthResponse> {
  const response = await fetch(`${config.apiUrl}/health/full`);
  if (!response.ok) {
    throw new Error(`Full health check failed: ${response.status}`);
  }
  return response.json();
}
