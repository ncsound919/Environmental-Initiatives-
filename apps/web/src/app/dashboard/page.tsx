'use client';

import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { mockTelemetryData, systemMetrics, projects } from '@/lib/data';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart,
} from 'recharts';

export default function Dashboard() {
  return (
    <>
      <PageHeader title="System Dashboard" subtitle="Demo dashboard — illustrative telemetry, not live device feeds." accent="cyan">
        <StatBand>
          <KpiCard value={`${systemMetrics.totalPowerGeneration} kW`} label="Power (demo)" accent="cyan" />
          <KpiCard value={`${systemMetrics.waterProduction} L/hr`} label="Water (demo)" accent="cyan" />
          <KpiCard value={`${systemMetrics.carbonOffset} t/day`} label="Carbon Offset (demo)" accent="cyan" />
          <KpiCard value={`${systemMetrics.activeDevices}`} label="Devices (demo)" accent="cyan" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <div className="grid grid-2" style={{ marginBottom: '1.5rem' }}>
          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '0.75rem' }}>☀️ Solar Generation (W/m²)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={mockTelemetryData.solar}>
                <defs>
                  <linearGradient id="gSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#eab308" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#eab308" strokeWidth={2} fill="url(#gSolar)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '0.75rem' }}>💧 Hydro Power Output (kW)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mockTelemetryData.hydro}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div className="grid grid-2" style={{ marginBottom: '1.5rem' }}>
          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '0.75rem' }}>🌊 AWG Water Production (L/hr)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={mockTelemetryData.water}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#14b8a6" strokeWidth={2} dot={{ fill: '#14b8a6', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '1rem' }}>🔄 Dispatcher Status</h3>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {[
                ['System Health', 'Operational', 'success'],
                ['Active Initiatives', '12', 'text'],
                ['Pending Commands', '3', 'text'],
                ['Cross-Project Synergies', 'Active', 'success'],
              ].map(([label, value, kind], i) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem 0', borderBottom: i < 3 ? '1px solid var(--border)' : 'none' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                  <span style={{ fontWeight: 700, color: kind === 'success' ? 'var(--success)' : 'var(--text)' }}>{value}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card style={{ padding: '1.25rem' }}>
          <h3 style={{ fontWeight: 700, marginBottom: '1rem' }}>📊 Project Status Overview</h3>
          <table className="data-table">
            <thead>
              <tr><th>Project</th><th>Name</th><th>Type</th><th>Readiness</th><th>Status</th></tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id}>
                  <td><span>{project.icon}</span> {project.id}</td>
                  <td style={{ fontWeight: 500 }}>{project.name}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{project.type}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="progress-track" style={{ width: 80 }}>
                        <div className="progress-fill" style={{ width: `${project.readiness}%` }} data-empty={project.readiness === 0 ? '' : undefined} />
                      </div>
                      <span style={{ fontSize: '0.8rem' }}>{project.readiness}%</span>
                    </div>
                  </td>
                  <td>
                    <Badge tone={project.readiness > 0 ? 'emerald' : 'dim'}>
                      {project.readiness > 0 ? 'Active' : 'Reserved'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </>
  );
}
