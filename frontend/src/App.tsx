import { Dashboard } from "@/pages/Dashboard";
import { ReportDetail } from "@/pages/ReportDetail";

export function getReportIdFromPath(pathname: string) {
  const match = pathname.match(/^\/reports\/([^/]+)$/);
  return match?.[1] ?? null;
}

export default function App() {
  const reportId = getReportIdFromPath(window.location.pathname);
  if (reportId) {
    return <ReportDetail reportId={reportId} />;
  }
  return <Dashboard />;
}
