'use client';

import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
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
} from 'recharts';

export default function Dashboard() {
  return (
    <>
      <Header />
      <main className="section">
        <div className="container">
          <h1 className="section-title">System Dashboard</h1>
          <p className="section-subtitle">Real-time monitoring of the ECOS ecosystem</p>

          {/* Key Metrics */}
          <div className="dashboard" style={{ marginBottom: '2rem' }}>
            <div className="dashboard-card">
              <div className="dashboard-card-title">Total Power Generation</div>
              <div className="dashboard-card-value">{systemMetrics.totalPowerGeneration} kW</div>
              <div className="dashboard-card-trend trend-up">↑ 12% from yesterday</div>
            </div>
            <div className="dashboard-card">
              <div className="dashboard-card-title">Water Production</div>
              <div className="dashboard-card-value">{systemMetrics.waterProduction} L/hr</div>
              <div className="dashboard-card-trend trend-up">↑ 8% from yesterday</div>
            </div>
            <div className="dashboard-card">
              <div className="dashboard-card-title">Carbon Offset</div>
              <div className="dashboard-card-value">{systemMetrics.carbonOffset} tons/day</div>
              <div className="dashboard-card-trend trend-up">↑ 5% from yesterday</div>
            </div>
            <div className="dashboard-card">
              <div className="dashboard-card-title">Active Devices</div>
              <div className="dashboard-card-value">{systemMetrics.activeDevices}</div>
              <div className="dashboard-card-trend">System Uptime: {systemMetrics.systemUptime}%</div>
            </div>
          </div>

          {/* Charts */}
          <div className="dashboard" style={{ marginBottom: '2rem' }}>
            <div className="chart-container">
              <h3 className="chart-title">☀️ Solar Generation (W/m²)</h3>
              <ResponsiveContainer width="100%" height="85%">
                <LineChart data={mockTelemetryData.solar}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="time" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#eab308" 
                    strokeWidth={2}
                    dot={{ fill: '#eab308', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <h3 className="chart-title">💧 Hydro Power Output (kW)</h3>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={mockTelemetryData.hydro}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="time" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="dashboard" style={{ marginBottom: '2rem' }}>
            <div className="chart-container">
              <h3 className="chart-title">🌊 AWG Water Production (L/hr)</h3>
              <ResponsiveContainer width="100%" height="85%">
                <LineChart data={mockTelemetryData.water}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="time" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#06b6d4" 
                    strokeWidth={2}
                    dot={{ fill: '#06b6d4', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="dashboard-card">
              <h3 className="chart-title">🔄 Dispatcher Status</h3>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid #e5e7eb' }}>
                  <span>System Health</span>
                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>Operational</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid #e5e7eb' }}>
                  <span>Active Projects</span>
                  <span style={{ fontWeight: 'bold' }}>12</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid #e5e7eb' }}>
                  <span>Pending Commands</span>
                  <span style={{ fontWeight: 'bold' }}>3</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0' }}>
                  <span>Cross-Project Synergies</span>
                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>Active</span>
                </div>
              </div>
            </div>
          </div>

          {/* Project Status Table */}
          <div className="dashboard-card" style={{ gridColumn: 'span 2' }}>
            <h3 className="chart-title">📊 Project Status Overview</h3>
            <table className="metrics-table" style={{ marginTop: '1rem' }}>
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Readiness</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {projects.map(project => (
                  <tr key={project.id}>
                    <td>
                      <span>{project.icon}</span> {project.id}
                    </td>
                    <td style={{ fontWeight: '500' }}>{project.name}</td>
                    <td style={{ color: '#6b7280' }}>{project.type}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ 
                          width: '60px', 
                          height: '8px', 
                          background: '#e5e7eb', 
                          borderRadius: '4px',
                          overflow: 'hidden'
                        }}>
                          <div style={{ 
                            width: `${project.readiness}%`, 
                            height: '100%', 
                            background: project.readiness > 0 ? '#10b981' : '#6b7280',
                            borderRadius: '4px'
                          }} />
                        </div>
                        <span style={{ fontSize: '0.875rem' }}>{project.readiness}%</span>
                      </div>
                    </td>
                    <td>
                      <span className={`project-badge ${project.readiness > 0 ? 'badge-active' : 'badge-reserved'}`}>
                        {project.readiness > 0 ? 'Active' : 'Reserved'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
