'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts';
import { initiativeSpecs } from '@/lib/initiatives';

export function PortfolioReadiness() {
  const data = Object.values(initiativeSpecs)
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((s) => ({
      name: s.name,
      community: s.hardware.individual.status === 'verified' ? 1 : 0,
      enterprise: s.hardware.enterprise.status === 'verified' ? 1 : 0,
      gaps: s.derived.gapCount,
    }));

  return (
    <div role="img" aria-label="Hardware spec readiness per initiative: community and enterprise tiers verified">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ left: -20, right: 8, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
          <XAxis dataKey="name" interval={0} angle={-35} textAnchor="end" height={70} tick={{ fontSize: 9 }} />
          <YAxis allowDecimals={false} domain={[0, 2]} tick={{ fontSize: 10 }} />
          <Tooltip
            contentStyle={{ fontSize: 12 }}
            formatter={(v: number, n) => [v ? 'verified' : 'draft', n]}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="community" name="Community tier" stackId="a" fill="#22d3ee" />
          <Bar dataKey="enterprise" name="Enterprise tier" stackId="a" fill="#f59e0b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.3rem' }}>
        Hardware <strong>spec readiness</strong> from each IDS (2 = both tiers verified). This is not physical or founding
        readiness — every initiative is still 0/3 on pilot / LOI / unit economics.
      </p>
    </div>
  );
}
