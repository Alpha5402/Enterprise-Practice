const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface Competitor {
  id: string;
  name: string;
  industry: string;
  description: string;
  keywords: string[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompetitorCreate {
  name: string;
  industry: string;
  description: string;
  keywords: string[];
  enabled: boolean;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  listCompetitors: () => request<Competitor[]>("/competitors"),
  createCompetitor: (payload: CompetitorCreate) =>
    request<Competitor>("/competitors", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteCompetitor: (id: string) =>
    request<void>(`/competitors/${id}`, {
      method: "DELETE",
    }),
};

