import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Database, Trash2 } from "lucide-react";
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
import { apiClient, type Competitor } from "@/api/client";
import { CompetitorForm } from "@/components/dashboard/CompetitorForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const EMPTY_COMPETITORS: Competitor[] = [];

function buildIndustryData(competitors: Competitor[]) {
  const counts = new Map<string, number>();
  for (const competitor of competitors) {
    counts.set(competitor.industry, (counts.get(competitor.industry) ?? 0) + 1);
  }
  return Array.from(counts.entries()).map(([industry, count]) => ({ industry, count }));
}

export function Dashboard() {
  const queryClient = useQueryClient();
  const competitorsQuery = useQuery({
    queryKey: ["competitors"],
    queryFn: apiClient.listCompetitors,
  });
  const createMutation = useMutation({
    mutationFn: apiClient.createCompetitor,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
  });
  const deleteMutation = useMutation({
    mutationFn: apiClient.deleteCompetitor,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
  });

  const competitors = competitorsQuery.data ?? EMPTY_COMPETITORS;
  const industryData = useMemo(() => buildIndustryData(competitors), [competitors]);
  const enabledCount = competitors.filter((competitor) => competitor.enabled).length;

  return (
    <main className="min-h-screen">
      <section className="border-b bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">Competitive Intelligence</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-normal">Dashboard</h1>
          </div>
          <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4 text-primary" />
            API-backed workspace
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
            <CardContent className="text-sm text-muted-foreground">No analysis reports generated yet.</CardContent>
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

        <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <Card>
            <CardHeader>
              <CardTitle>Latest Competitor Dynamics</CardTitle>
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
                      <div className="min-w-0">
                        <p className="truncate font-medium">{competitor.name}</p>
                        <p className="truncate text-sm text-muted-foreground">
                          {competitor.industry} · {competitor.keywords.join(", ") || "No keywords"}
                        </p>
                      </div>
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
              <CardTitle>Agent Reasoning Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex min-h-44 flex-col items-center justify-center gap-3 rounded-md border border-dashed text-center text-sm text-muted-foreground">
                <Database className="h-5 w-5 text-primary" />
                Analysis workflow starts in the next implementation phase.
              </div>
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
              <CardTitle>Coverage Radar</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              {industryData.length === 0 ? (
                <div className="flex h-full items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
                  Monitoring dimensions will appear after competitors are configured.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={industryData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="industry" />
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
