'use client';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const PALETTE = ['#22d3ee', '#a78bfa', '#fbbf24', '#34d399'];

function seeded(seed: string, i: number): number {
  let h = 0;
  for (let k = 0; k < seed.length; k++) h = (h * 31 + seed.charCodeAt(k)) % 997;
  return Number((50 + 45 * Math.sin((i + h) / 3.2)).toFixed(1));
}

export function TelemetryChart({ sensors }: { sensors: string[] }) {
  const channels = sensors.slice(0, 4);
  if (channels.length === 0) {
    return <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>No telemetry channels declared.</p>;
  }
  const data = Array.from({ length: 24 }, (_, i) => {
    const row: Record<string, number | string> = { t: `${i}h` };
    channels.forEach((c) => {
      row[c] = seeded(c, i);
    });
    return row;
  });

  return (
    <div role="img" aria-label={`Illustrative telemetry over 24 hours for channels: ${channels.join(', ')}`}>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ left: -18, right: 8, top: 4 }}>
          <defs>
            {channels.map((c, i) => (
              <linearGradient key={c} id={`g-${c}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0.35} />
                <stop offset="95%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
          <XAxis dataKey="t" tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} />
          {channels.map((c, i) => (
            <Area
              key={c}
              type="monotone"
              dataKey={c}
              stroke={PALETTE[i % PALETTE.length]}
              fill={`url(#g-${c})`}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
      <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>
        Channel names come from the IDS. <strong>Series are illustrative</strong> — shaped from the sensor name, not live device data.
      </p>
    </div>
  );
}
