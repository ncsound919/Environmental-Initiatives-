interface KpiCardProps {
  value: string;
  label: string;
  accent?: 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue';
  trend?: { dir: 'up' | 'down' | 'flat'; text: string };
}

export function KpiCard({ value, label, accent = 'emerald', trend }: KpiCardProps) {
  return (
    <div className="kpi-card" data-accent={accent}>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
      {trend && (
        <div className={`kpi-trend ${trend.dir === 'up' ? 'up' : trend.dir === 'down' ? 'down' : 'flat'}`}>
          {trend.dir === 'up' ? '▲' : trend.dir === 'down' ? '▼' : '•'} {trend.text}
        </div>
      )}
    </div>
  );
}
