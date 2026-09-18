export function TopologyDiagram({
  id,
  sensors,
  actuators,
  telemetryTopic,
  controlTopic,
  color,
}: {
  id: string;
  sensors: string[];
  actuators: string[];
  telemetryTopic?: string;
  controlTopic?: string;
  color: string;
}) {
  const W = 680;
  const H = 300;
  const cx = W / 2;
  const cy = 140;
  const yAt = (i: number, n: number) => (n <= 1 ? cy : 36 + ((H - 96) * i) / (n - 1));

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxHeight: 300, display: 'block' }}>
        {/* edges + sensor nodes (left) */}
        {sensors.map((s, i) => {
          const y = yAt(i, sensors.length);
          return (
            <g key={`s-${s}`}>
              <line x1={150} y1={y} x2={cx - 92} y2={cy} stroke={color} strokeOpacity={0.35} strokeWidth={1.5} />
              <circle r="3" fill={color}>
                <animateMotion dur="2.4s" repeatCount="indefinite" path={`M150 ${y} L${cx - 92} ${cy}`} />
              </circle>
              <circle cx={82} cy={y} r={15} fill={color} fillOpacity={0.16} stroke={color} strokeOpacity={0.5} />
              <text x={82} y={y + 4} textAnchor="middle" fontSize={10} fill="#22d3ee">
                {s.slice(0, 3)}
              </text>
              <text x={102} y={y - 20} fontSize={10} fill="#94a3b8">
                {s}
              </text>
            </g>
          );
        })}
        {/* edges + actuator nodes (right) */}
        {actuators.map((a, i) => {
          const y = yAt(i, actuators.length);
          return (
            <g key={`a-${a}`}>
              <line x1={cx + 92} y1={cy} x2={W - 150} y2={y} stroke="#f59e0b" strokeOpacity={0.35} strokeWidth={1.5} />
              <circle r="3" fill="#f59e0b">
                <animateMotion dur="2.4s" repeatCount="indefinite" path={`M${cx + 92} ${cy} L${W - 150} ${y}`} />
              </circle>
              <rect x={W - 98} y={y - 14} width={30} height={28} rx={5} fill="#f59e0b" fillOpacity={0.16} stroke="#f59e0b" strokeOpacity={0.5} />
              <text x={W - 83} y={y + 4} textAnchor="middle" fontSize={10} fill="#fbbf24">
                {a.slice(0, 3)}
              </text>
              <text x={W - 112} y={y - 20} fontSize={10} fill="#94a3b8" textAnchor="end">
                {a}
              </text>
            </g>
          );
        })}
        {/* central device */}
        <rect x={cx - 88} y={cy - 40} width={176} height={80} rx={10} fill="#0b1220" stroke={color} strokeWidth={1.5} />
        <text x={cx} y={cy - 6} textAnchor="middle" fontSize={13} fill="#e2e8f0" fontWeight={700}>
          {id} device
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" fontSize={10} fill="#64748b">
          {telemetryTopic}
        </text>
        <text x={cx} y={cy + 30} textAnchor="middle" fontSize={10} fill="#64748b">
          {controlTopic}
        </text>
        <text x={24} y={20} fontSize={10} fill="#22d3ee">
          SENSORS →
        </text>
        <text x={W - 24} y={20} fontSize={10} fill="#fbbf24" textAnchor="end">
          ← ACTUATORS
        </text>
      </svg>
      <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.4rem' }}>
        Interface topology derived from the IDS and <code>config/hardware-manifests.json</code>.
      </p>
    </div>
  );
}
