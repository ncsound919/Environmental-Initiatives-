'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';

export interface BomLine {
  part: string;
  qty: number;
  unitUsd?: number | null;
}

export function BomChart({ bom, color }: { bom: BomLine[]; color: string }) {
  const data = bom
    .map((b) => ({ name: b.part, cost: Number(((b.unitUsd ?? 0) * b.qty).toFixed(2)), qty: b.qty, unit: b.unitUsd ?? 0 }))
    .sort((a, b) => b.cost - a.cost);
  const total = data.reduce((s, d) => s + d.cost, 0);

  if (data.length === 0) return <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>No BOM lines.</p>;

  return (
    <div role="img" aria-label={`Bill of materials extended cost by part, total $${total.toLocaleString()} (list estimates)`}>
      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
        Extended BOM cost (qty × unit) — total <strong>${total.toLocaleString()}</strong> (list estimates)
      </div>
      <ResponsiveContainer width="100%" height={Math.max(140, data.length * 30)}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
          <XAxis type="number" tick={{ fontSize: 10 }} />
          <YAxis type="category" dataKey="name" width={170} tick={{ fontSize: 10 }} />
          <Tooltip
            formatter={(v: number, _n, p) => [`$${v.toLocaleString()}`, `${p?.payload?.qty} × $${p?.payload?.unit}`]}
            contentStyle={{ fontSize: 12 }}
          />
          <Bar dataKey="cost" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={i === 0 ? color : `${color}99`} />
            ))}
            <LabelList
              dataKey="cost"
              position="right"
              formatter={(v: number) => `$${Number(v).toLocaleString()}`}
              style={{ fontSize: 10, fill: '#94a3b8' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
