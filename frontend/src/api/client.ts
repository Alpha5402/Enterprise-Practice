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

export interface NewsArticle {
  id: string;
  competitor_id: string;
  source_type: string;
  source_name: string;
  url: string;
  title: string;
  content: string;
  cleaned_content: string;
  published_at: string | null;
  collected_at: string;
  extra_metadata: Record<string, string>;
}

export interface AnalysisReport {
  id: string;
  competitor_id: string;
  competitor: string;
  dimension: "sentiment" | "price" | "product" | "summary";
  risk_level: "low" | "medium" | "high" | "critical";
  summary: string;
  opportunity_points: string[];
  threat_points: string[];
  confidence_score: number;
  source_article_ids: string[];
  created_at: string;
}

export interface SourceConfig {
  id: string;
  competitor_id: string;
  name: string;
  source_url: string;
  crawler: "rss" | "web";
  interval_minutes: number;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface SourceConfigCreate {
  competitor_id: string;
  name: string;
  source_url: string;
  crawler: "rss" | "web";
  interval_minutes: number;
  enabled: boolean;
}

export interface CollectRequest {
  competitor_id: string;
  source_url: string;
  crawler: "rss" | "web";
}

export interface CollectResponse {
  collected_count: number;
  articles: NewsArticle[];
}

export interface IndexCompetitorResponse {
  competitor_id: string;
  metadata_count: number;
}

export interface AnalyzeRequest {
  competitor_id: string;
  query: string;
  context_limit: number;
}

export interface AnalyzeResponse {
  reports: AnalysisReport[];
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
  listArticles: (competitorId?: string) =>
    request<NewsArticle[]>(competitorId ? `/articles?competitor_id=${competitorId}` : "/articles"),
  listReports: (competitorId?: string) =>
    request<AnalysisReport[]>(competitorId ? `/reports?competitor_id=${competitorId}` : "/reports"),
  listSources: (competitorId?: string) =>
    request<SourceConfig[]>(competitorId ? `/sources?competitor_id=${competitorId}` : "/sources"),
  createCompetitor: (payload: CompetitorCreate) =>
    request<Competitor>("/competitors", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteCompetitor: (id: string) =>
    request<void>(`/competitors/${id}`, {
      method: "DELETE",
    }),
  collect: (payload: CollectRequest) =>
    request<CollectResponse>("/collect", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createSource: (payload: SourceConfigCreate) =>
    request<SourceConfig>("/sources", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteSource: (id: string) =>
    request<void>(`/sources/${id}`, {
      method: "DELETE",
    }),
  collectSource: (id: string) =>
    request<CollectResponse>(`/sources/${id}/collect`, {
      method: "POST",
    }),
  indexCompetitor: (competitorId: string) =>
    request<IndexCompetitorResponse>(`/competitors/${competitorId}/index`, {
      method: "POST",
    }),
  analyze: (payload: AnalyzeRequest) =>
    request<AnalyzeResponse>("/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  analyzeStreamUrl: (payload: AnalyzeRequest) => {
    const params = new URLSearchParams({
      competitor_id: payload.competitor_id,
      query: payload.query,
      context_limit: String(payload.context_limit),
    });
    return `${API_BASE_URL}/analyze/stream?${params.toString()}`;
  },
};
