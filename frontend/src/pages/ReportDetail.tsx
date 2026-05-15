import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, FileText } from "lucide-react";
import { apiClient, type AnalysisReport } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const riskLabel = { low: "低", medium: "中", high: "高", critical: "严重" };
const dimensionLabel = { sentiment: "舆情", price: "价格", product: "产品", summary: "汇总" };

export function ReportDetail({ reportId }: { reportId: string }) {
  const reportQuery = useQuery({
    queryKey: ["report", reportId],
    queryFn: () => apiClient.getReport(reportId),
  });

  return (
    <main className="min-h-screen">
      <section className="border-b bg-card">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-6 py-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">Agent 报告</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-normal">报告详情</h1>
          </div>
          <Button asChild variant="outline">
            <a href="/">
              <ArrowLeft className="h-4 w-4" />
              返回工作台
            </a>
          </Button>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-5 px-6 py-6">
        {reportQuery.isLoading ? <EmptyState text="正在加载报告..." /> : null}
        {reportQuery.isError ? <EmptyState text={reportQuery.error.message || "报告加载失败。"} /> : null}
        {reportQuery.data ? <ReportBody report={reportQuery.data} /> : null}
      </section>
    </main>
  );
}

function ReportBody({ report }: { report: AnalysisReport }) {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{report.competitor} · {dimensionLabel[report.dimension]}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 text-sm leading-6">
          <p className="text-base">{report.summary}</p>
          <div className="grid gap-3 md:grid-cols-3">
            <Metric label="风险等级" value={riskLabel[report.risk_level]} />
            <Metric label="置信度" value={`${(report.confidence_score * 100).toFixed(0)}%`} />
            <Metric label="生成时间" value={new Date(report.created_at).toLocaleString()} />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <DetailList title="机会点" items={report.opportunity_points} />
        <DetailList title="威胁点" items={report.threat_points} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>证据来源</CardTitle>
        </CardHeader>
        <CardContent>
          {report.source_article_ids.length === 0 ? (
            <EmptyState text="暂无来源文章 ID。" icon={<FileText className="h-5 w-5 text-primary" />} />
          ) : (
            <div className="grid gap-2 text-sm text-muted-foreground">
              {report.source_article_ids.map((id) => (
                <code key={id} className="rounded-md border bg-muted px-3 py-2">{id}</code>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-muted px-3 py-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-medium">{value}</p>
    </div>
  );
}

function DetailList({ title, items }: { title: string; items: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="grid gap-2 text-sm text-muted-foreground">
          {items.length === 0 ? <li>暂无</li> : items.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </CardContent>
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
