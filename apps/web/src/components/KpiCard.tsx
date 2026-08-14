interface KpiCardProps {
  value: string;
  label: string;
  accent?: 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal';
  icon?: string;
  trend?: { dir: 'up' | 'down' | 'flat'; text: string };
}

export function KpiCard({ value, label, accent = 'emerald', icon, trend }: KpiCardProps) {
  return (
    <div className="kpi-card" data-accent={accent}>
      {icon && <div style={{ fontSize: '1.4rem', marginBottom: '0.3rem' }}>{icon}</div>}
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
