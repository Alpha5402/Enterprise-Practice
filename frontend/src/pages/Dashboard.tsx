import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Database, FileText, Play, RadarIcon, Search, Trash2 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { apiClient, type Competitor, type AnalysisReport } from "@/api/client";
import { CompetitorForm } from "@/components/dashboard/CompetitorForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const EMPTY_COMPETITORS: Competitor[] = [];
const EMPTY_REPORTS: AnalysisReport[] = [];

function buildIndustryData(competitors: Competitor[]) {
  const counts = new Map<string, number>();
  for (const competitor of competitors) {
    counts.set(competitor.industry, (counts.get(competitor.industry) ?? 0) + 1);
  }
  return Array.from(counts.entries()).map(([industry, count]) => ({ industry, count }));
}

function buildRiskData(reports: AnalysisReport[]) {
  const levels = ["low", "medium", "high", "critical"];
  return levels.map((level) => ({
    level,
    count: reports.filter((report) => report.risk_level === level).length,
  }));
}

export function Dashboard() {
  const queryClient = useQueryClient();
  const [selectedCompetitorId, setSelectedCompetitorId] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [crawler, setCrawler] = useState<"rss" | "web">("rss");
  const [query, setQuery] = useState("latest competitive signals");
  const [statusMessage, setStatusMessage] = useState("");

  const competitorsQuery = useQuery({
    queryKey: ["competitors"],
    queryFn: apiClient.listCompetitors,
  });
  const reportsQuery = useQuery({
    queryKey: ["reports", selectedCompetitorId],
    queryFn: () => apiClient.listReports(selectedCompetitorId || undefined),
  });
  const articlesQuery = useQuery({
    queryKey: ["articles", selectedCompetitorId],
    queryFn: () => apiClient.listArticles(selectedCompetitorId || undefined),
  });

  const competitors = competitorsQuery.data ?? EMPTY_COMPETITORS;
  const reports = reportsQuery.data ?? EMPTY_REPORTS;
  const selectedCompetitor = competitors.find((competitor) => competitor.id === selectedCompetitorId);
  const industryData = useMemo(() => buildIndustryData(competitors), [competitors]);
  const riskData = useMemo(() => buildRiskData(reports), [reports]);
  const enabledCount = competitors.filter((competitor) => competitor.enabled).length;

  const createMutation = useMutation({
    mutationFn: apiClient.createCompetitor,
    onSuccess: (competitor) => {
      setSelectedCompetitorId(competitor.id);
      setStatusMessage("Competitor created.");
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
    },
  });
  const deleteMutation = useMutation({
    mutationFn: apiClient.deleteCompetitor,
    onSuccess: () => {
      setSelectedCompetitorId("");
      setStatusMessage("Competitor deleted.");
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    },
  });
  const collectMutation = useMutation({
    mutationFn: apiClient.collect,
    onSuccess: (response) => {
      setStatusMessage(`Collected ${response.collected_count} article(s).`);
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });
  const indexMutation = useMutation({
    mutationFn: apiClient.indexCompetitor,
    onSuccess: (response) => {
      setStatusMessage(`Indexed ${response.metadata_count} chunk(s).`);
    },
    onError: (error) => setStatusMessage(error.message),
  });
  const analyzeMutation = useMutation({
    mutationFn: apiClient.analyze,
    onSuccess: (response) => {
      setStatusMessage(`Generated ${response.reports.length} report(s).`);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });

  function handleCollect(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompetitorId || !sourceUrl) {
      setStatusMessage("Select a competitor and enter a source URL.");
      return;
    }
    collectMutation.mutate({
      competitor_id: selectedCompetitorId,
      source_url: sourceUrl,
      crawler,
    });
  }

  function handleAnalyze() {
    if (!selectedCompetitorId) {
      setStatusMessage("Select a competitor first.");
      return;
    }
    analyzeMutation.mutate({
      competitor_id: selectedCompetitorId,
      query,
      context_limit: 5,
    });
  }

  return (
    <main className="min-h-screen">
      <section className="border-b bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">Competitive Intelligence</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-normal">Operations Dashboard</h1>
          </div>
          <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4 text-primary" />
            RAG and Agent workflow ready
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-6 py-6">
        <div className="grid gap-5 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Monitored Competitors</CardTitle>
            </CardHeader>
            <CardContent className="text-3xl font-semibold">{competitors.length}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Enabled Sources</CardTitle>
            </CardHeader>
            <CardContent className="text-3xl font-semibold">{enabledCount}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Risk Reports</CardTitle>
            </CardHeader>
            <CardContent className="text-3xl font-semibold">{reports.length}</CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Competitor Management</CardTitle>
          </CardHeader>
          <CardContent>
            <CompetitorForm
              isSubmitting={createMutation.isPending}
              onSubmit={(payload) => createMutation.mutate(payload)}
            />
          </CardContent>
        </Card>

        <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
          <Card>
            <CardHeader>
              <CardTitle>Competitors</CardTitle>
            </CardHeader>
            <CardContent>
              {competitors.length === 0 ? (
                <div className="flex min-h-44 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
                  Add a competitor to begin tracking public signals.
                </div>
              ) : (
                <div className="divide-y">
                  {competitors.map((competitor) => (
                    <div key={competitor.id} className="flex items-center justify-between gap-3 py-3">
                      <button
                        className="min-w-0 flex-1 text-left"
                        onClick={() => setSelectedCompetitorId(competitor.id)}
                        type="button"
                      >
                        <p className="truncate font-medium">{competitor.name}</p>
                        <p className="truncate text-sm text-muted-foreground">
                          {competitor.industry} · {competitor.keywords.join(", ") || "No keywords"}
                        </p>
                      </button>
                      <Button
                        aria-label={`Delete ${competitor.name}`}
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteMutation.mutate(competitor.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Collection And Analysis</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              <select
                className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={selectedCompetitorId}
                onChange={(event) => setSelectedCompetitorId(event.target.value)}
              >
                <option value="">Select competitor</option>
                {competitors.map((competitor) => (
                  <option key={competitor.id} value={competitor.id}>
                    {competitor.name}
                  </option>
                ))}
              </select>

              <form className="grid gap-3 md:grid-cols-[120px_1fr_auto]" onSubmit={handleCollect}>
                <select
                  className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                  value={crawler}
                  onChange={(event) => setCrawler(event.target.value as "rss" | "web")}
                >
                  <option value="rss">RSS</option>
                  <option value="web">Web</option>
                </select>
                <Input
                  placeholder="https://example.com/feed.xml"
                  value={sourceUrl}
                  onChange={(event) => setSourceUrl(event.target.value)}
                />
                <Button type="submit" disabled={collectMutation.isPending}>
                  <Search className="h-4 w-4" />
                  Collect
                </Button>
              </form>

              <div className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
                <Input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="latest competitive signals"
                />
                <Button
                  variant="outline"
                  disabled={!selectedCompetitorId || indexMutation.isPending}
                  onClick={() => indexMutation.mutate(selectedCompetitorId)}
                >
                  <Database className="h-4 w-4" />
                  Index
                </Button>
                <Button disabled={!selectedCompetitorId || analyzeMutation.isPending} onClick={handleAnalyze}>
                  <Play className="h-4 w-4" />
                  Analyze
                </Button>
              </div>

              <div className="rounded-md border bg-muted px-3 py-2 text-sm text-muted-foreground">
                {selectedCompetitor ? `Selected: ${selectedCompetitor.name}` : "No competitor selected"}
                {statusMessage ? ` · ${statusMessage}` : ""}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
          <Card>
            <CardHeader>
              <CardTitle>Collected Articles</CardTitle>
            </CardHeader>
            <CardContent>
              {(articlesQuery.data ?? []).length === 0 ? (
                <div className="flex min-h-40 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
                  No collected articles yet.
                </div>
              ) : (
                <div className="divide-y">
                  {(articlesQuery.data ?? []).slice(0, 6).map((article) => (
                    <div key={article.id} className="py-3">
                      <p className="truncate font-medium">{article.title}</p>
                      <p className="truncate text-sm text-muted-foreground">
                        {article.source_type} · {article.source_name}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Agent Reports</CardTitle>
            </CardHeader>
            <CardContent>
              {reports.length === 0 ? (
                <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-md border border-dashed text-center text-sm text-muted-foreground">
                  <FileText className="h-5 w-5 text-primary" />
                  Run analysis after collecting and indexing articles.
                </div>
              ) : (
                <div className="divide-y">
                  {reports.slice(0, 6).map((report) => (
                    <div key={report.id} className="py-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-medium capitalize">{report.dimension}</p>
                        <span className="rounded-md border px-2 py-1 text-xs uppercase text-muted-foreground">
                          {report.risk_level}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-muted-foreground">{report.summary}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Industry Trend</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              {industryData.length === 0 ? (
                <div className="flex h-full items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
                  No competitor data available.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={industryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="industry" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Risk Radar</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              {reports.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center gap-3 rounded-md border border-dashed text-sm text-muted-foreground">
                  <RadarIcon className="h-5 w-5 text-primary" />
                  Risk distribution appears after analysis.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={riskData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="level" />
                    <Radar dataKey="count" fill="hsl(var(--accent))" fillOpacity={0.35} stroke="hsl(var(--accent))" />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>

        {competitorsQuery.isError ? (
          <p className="text-sm text-destructive">Unable to load competitors. Check backend connectivity.</p>
        ) : null}
      </section>
    </main>
  );
}
