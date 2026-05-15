import { FormEvent, useMemo, useState } from "react";
import type React from "react";
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
import { apiClient, type AnalysisReport, type Competitor } from "@/api/client";
import { CompetitorForm } from "@/components/dashboard/CompetitorForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const EMPTY_COMPETITORS: Competitor[] = [];
const EMPTY_REPORTS: AnalysisReport[] = [];
const riskLabel = { low: "低", medium: "中", high: "高", critical: "严重" };
const dimensionLabel = { sentiment: "舆情", price: "价格", product: "产品", summary: "汇总" };

function buildIndustryData(competitors: Competitor[]) {
  const counts = new Map<string, number>();
  for (const competitor of competitors) {
    counts.set(competitor.industry, (counts.get(competitor.industry) ?? 0) + 1);
  }
  return Array.from(counts.entries()).map(([industry, count]) => ({ industry, count }));
}

function buildRiskData(reports: AnalysisReport[]) {
  return (["low", "medium", "high", "critical"] as const).map((level) => ({
    level: riskLabel[level],
    count: reports.filter((report) => report.risk_level === level).length,
  }));
}

export function Dashboard() {
  const queryClient = useQueryClient();
  const [selectedCompetitorId, setSelectedCompetitorId] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceName, setSourceName] = useState("");
  const [crawler, setCrawler] = useState<"rss" | "web">("rss");
  const [query, setQuery] = useState("最新竞品动态");
  const [statusMessage, setStatusMessage] = useState("");
  const [streamMessage, setStreamMessage] = useState("");
  const [selectedReport, setSelectedReport] = useState<AnalysisReport | null>(null);

  const competitorsQuery = useQuery({ queryKey: ["competitors"], queryFn: apiClient.listCompetitors });
  const reportsQuery = useQuery({
    queryKey: ["reports", selectedCompetitorId],
    queryFn: () => apiClient.listReports(selectedCompetitorId || undefined),
  });
  const articlesQuery = useQuery({
    queryKey: ["articles", selectedCompetitorId],
    queryFn: () => apiClient.listArticles(selectedCompetitorId || undefined),
  });
  const sourcesQuery = useQuery({
    queryKey: ["sources", selectedCompetitorId],
    queryFn: () => apiClient.listSources(selectedCompetitorId || undefined),
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
      setStatusMessage("竞品已添加。");
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
    },
  });
  const deleteMutation = useMutation({
    mutationFn: apiClient.deleteCompetitor,
    onSuccess: () => {
      setSelectedCompetitorId("");
      setSelectedReport(null);
      setStatusMessage("竞品已删除。");
      queryClient.invalidateQueries();
    },
  });
  const collectMutation = useMutation({
    mutationFn: apiClient.collect,
    onSuccess: (response) => {
      setStatusMessage(`已采集 ${response.collected_count} 篇文章。`);
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });
  const createSourceMutation = useMutation({
    mutationFn: apiClient.createSource,
    onSuccess: () => {
      setStatusMessage("数据源已保存。");
      setSourceName("");
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });
  const deleteSourceMutation = useMutation({
    mutationFn: apiClient.deleteSource,
    onSuccess: () => {
      setStatusMessage("数据源已删除。");
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
  const collectSourceMutation = useMutation({
    mutationFn: apiClient.collectSource,
    onSuccess: (response) => {
      setStatusMessage(`已从保存的数据源采集 ${response.collected_count} 篇文章。`);
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });
  const indexMutation = useMutation({
    mutationFn: apiClient.indexCompetitor,
    onSuccess: (response) => setStatusMessage(`已索引 ${response.metadata_count} 个文本块。`),
    onError: (error) => setStatusMessage(error.message),
  });
  const analyzeMutation = useMutation({
    mutationFn: apiClient.analyze,
    onSuccess: (response) => {
      setStatusMessage(`已生成 ${response.reports.length} 份报告。`);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });

  function handleCollect(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompetitorId || !sourceUrl) {
      setStatusMessage("请先选择竞品并输入来源 URL。");
      return;
    }
    collectMutation.mutate({ competitor_id: selectedCompetitorId, source_url: sourceUrl, crawler });
  }

  function handleSaveSource() {
    if (!selectedCompetitorId || !sourceUrl) {
      setStatusMessage("请先选择竞品并输入来源 URL。");
      return;
    }
    createSourceMutation.mutate({
      competitor_id: selectedCompetitorId,
      name: sourceName || sourceUrl,
      source_url: sourceUrl,
      crawler,
      interval_minutes: 1440,
      enabled: true,
    });
  }

  function handleAnalyze() {
    if (!selectedCompetitorId) {
      setStatusMessage("请先选择竞品。");
      return;
    }
    analyzeMutation.mutate({ competitor_id: selectedCompetitorId, query, context_limit: 5 });
  }

  function handleStreamAnalyze() {
    if (!selectedCompetitorId) {
      setStatusMessage("请先选择竞品。");
      return;
    }
    setStreamMessage("正在建立分析流...");
    const source = new EventSource(
      apiClient.analyzeStreamUrl({ competitor_id: selectedCompetitorId, query, context_limit: 5 }),
    );
    source.addEventListener("started", () => setStreamMessage("分析已开始"));
    source.addEventListener("retrieving", () => setStreamMessage("正在检索 RAG 上下文"));
    source.addEventListener("completed", () => {
      setStreamMessage("分析完成，正在刷新报告");
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      source.close();
    });
    source.addEventListener("error", (event) => {
      setStreamMessage("分析流异常或已结束");
      source.close();
      console.error(event);
    });
  }

  return (
    <main className="min-h-screen">
      <section className="border-b bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">竞品情报系统</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-normal">运营工作台</h1>
          </div>
          <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4 text-primary" />
            RAG 与 Agent 工作流已接入
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-6 py-6">
        <div className="grid gap-5 md:grid-cols-3">
          <MetricCard title="监控竞品" value={competitors.length} />
          <MetricCard title="启用竞品" value={enabledCount} />
          <MetricCard title="分析报告" value={reports.length} />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>竞品管理</CardTitle>
          </CardHeader>
          <CardContent>
            <CompetitorForm
              isSubmitting={createMutation.isPending}
              onSubmit={(payload) => createMutation.mutate(payload)}
            />
          </CardContent>
        </Card>

        <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
          <Card>
            <CardHeader>
              <CardTitle>竞品列表</CardTitle>
            </CardHeader>
            <CardContent>
              {competitors.length === 0 ? (
                <EmptyState text="先添加一个竞品，再开始采集公开信号。" />
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
                          {competitor.industry} · {competitor.keywords.join(", ") || "暂无关键词"}
                        </p>
                      </button>
                      <Button
                        aria-label={`删除 ${competitor.name}`}
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
              <CardTitle>采集、索引与分析</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              <select
                className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={selectedCompetitorId}
                onChange={(event) => setSelectedCompetitorId(event.target.value)}
              >
                <option value="">选择竞品</option>
                {competitors.map((competitor) => (
                  <option key={competitor.id} value={competitor.id}>
                    {competitor.name}
                  </option>
                ))}
              </select>

              <form className="grid gap-3 md:grid-cols-[110px_1fr_1fr_auto]" onSubmit={handleCollect}>
                <select
                  className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                  value={crawler}
                  onChange={(event) => setCrawler(event.target.value as "rss" | "web")}
                >
                  <option value="rss">RSS</option>
                  <option value="web">网页</option>
                </select>
                <Input placeholder="数据源名称" value={sourceName} onChange={(event) => setSourceName(event.target.value)} />
                <Input placeholder="https://example.com/feed.xml" value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} />
                <Button type="submit" disabled={collectMutation.isPending}>
                  <Search className="h-4 w-4" />
                  采集
                </Button>
              </form>

              <div className="grid gap-3 md:grid-cols-[1fr_auto_auto_auto_auto]">
                <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="最新竞品动态" />
                <Button variant="outline" disabled={!selectedCompetitorId} onClick={handleSaveSource}>
                  保存源
                </Button>
                <Button variant="outline" disabled={!selectedCompetitorId} onClick={() => indexMutation.mutate(selectedCompetitorId)}>
                  <Database className="h-4 w-4" />
                  索引
                </Button>
                <Button disabled={!selectedCompetitorId || analyzeMutation.isPending} onClick={handleAnalyze}>
                  <Play className="h-4 w-4" />
                  分析
                </Button>
                <Button variant="outline" disabled={!selectedCompetitorId} onClick={handleStreamAnalyze}>
                  流式
                </Button>
              </div>

              <div className="rounded-md border bg-muted px-3 py-2 text-sm text-muted-foreground">
                {selectedCompetitor ? `当前竞品：${selectedCompetitor.name}` : "尚未选择竞品"}
                {statusMessage ? ` · ${statusMessage}` : ""}
                {streamMessage ? ` · ${streamMessage}` : ""}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>保存的数据源</CardTitle>
            </CardHeader>
            <CardContent>
              {(sourcesQuery.data ?? []).length === 0 ? (
                <EmptyState text="暂无保存的数据源。" />
              ) : (
                <div className="divide-y">
                  {(sourcesQuery.data ?? []).map((source) => (
                    <div key={source.id} className="grid gap-2 py-3">
                      <p className="truncate font-medium">{source.name}</p>
                      <p className="truncate text-sm text-muted-foreground">
                        {source.crawler === "rss" ? "RSS" : "网页"} · 每 {source.interval_minutes} 分钟
                      </p>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => collectSourceMutation.mutate(source.id)}>
                          立即采集
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => deleteSourceMutation.mutate(source.id)}>
                          删除
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>已采集文章</CardTitle>
            </CardHeader>
            <CardContent>
              {(articlesQuery.data ?? []).length === 0 ? (
                <EmptyState text="暂无采集文章。" />
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
              <CardTitle>Agent 报告</CardTitle>
            </CardHeader>
            <CardContent>
              {reports.length === 0 ? (
                <EmptyState icon={<FileText className="h-5 w-5 text-primary" />} text="采集并索引后运行分析。" />
              ) : (
                <div className="divide-y">
                  {reports.slice(0, 6).map((report) => (
                    <button key={report.id} className="w-full py-3 text-left" onClick={() => setSelectedReport(report)}>
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-medium">{dimensionLabel[report.dimension]}</p>
                        <span className="rounded-md border px-2 py-1 text-xs text-muted-foreground">
                          {riskLabel[report.risk_level]}
                        </span>
                      </div>
                      <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{report.summary}</p>
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {selectedReport ? (
          <Card>
            <CardHeader>
              <CardTitle>报告详情 · {dimensionLabel[selectedReport.dimension]}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 text-sm">
              <p>{selectedReport.summary}</p>
              <DetailList title="机会点" items={selectedReport.opportunity_points} />
              <DetailList title="威胁点" items={selectedReport.threat_points} />
              <p className="text-muted-foreground">
                风险等级：{riskLabel[selectedReport.risk_level]} · 置信度：
                {(selectedReport.confidence_score * 100).toFixed(0)}%
              </p>
            </CardContent>
          </Card>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-2">
          <ChartCard title="行业分布" empty={industryData.length === 0}>
            <BarChart data={industryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="industry" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ChartCard>
          <ChartCard title="风险雷达" empty={reports.length === 0} icon={<RadarIcon className="h-5 w-5 text-primary" />}>
            <RadarChart data={riskData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="level" />
              <Radar dataKey="count" fill="hsl(var(--accent))" fillOpacity={0.35} stroke="hsl(var(--accent))" />
              <Tooltip />
            </RadarChart>
          </ChartCard>
        </div>
      </section>
    </main>
  );
}

function MetricCard({ title, value }: { title: string; value: number }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="text-3xl font-semibold">{value}</CardContent>
    </Card>
  );
}

function EmptyState({ text, icon }: { text: string; icon?: React.ReactNode }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-md border border-dashed text-center text-sm text-muted-foreground">
      {icon}
      {text}
    </div>
  );
}

function DetailList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <p className="font-medium">{title}</p>
      <ul className="mt-2 grid gap-1 text-muted-foreground">
        {items.length === 0 ? <li>暂无</li> : items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}

function ChartCard({
  title,
  empty,
  icon,
  children,
}: { title: string; empty: boolean; icon?: React.ReactNode; children: React.ReactElement }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className={empty ? undefined : "h-72"}>
        {empty ? (
          <EmptyState text="暂无可视化数据。" icon={icon} />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {children}
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
