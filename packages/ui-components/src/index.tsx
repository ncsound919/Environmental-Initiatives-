/**
 * ECOS Shared UI Components
 * Reusable React components for dashboards across all 13 projects
 */

import React from 'react';

// ============================================
// METRIC CARD
// ============================================

export interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  trend,
  trendValue,
}) => {
  const trendColor = trend === 'up' ? '#10b981' : trend === 'down' ? '#ef4444' : '#6b7280';

  return (
    <div style={{ padding: '1rem', border: '1px solid #e5e7eb', borderRadius: '0.5rem' }}>
      <h3 style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.5rem 0' }}>{title}</h3>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.25rem' }}>
        <span style={{ fontSize: '1.875rem', fontWeight: 'bold' }}>{value}</span>
        {unit && <span style={{ fontSize: '1rem', color: '#6b7280' }}>{unit}</span>}
      </div>
      {trend && trendValue && (
        <div style={{ fontSize: '0.875rem', color: trendColor, marginTop: '0.25rem' }}>
          {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
        </div>
      )}
    </div>
  );
};

// ============================================
// STATUS BADGE
// ============================================

export interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'warning' | 'error';
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  const colors = {
    active: { bg: '#10b981', text: '#ffffff' },
    inactive: { bg: '#6b7280', text: '#ffffff' },
    warning: { bg: '#f59e0b', text: '#ffffff' },
    error: { bg: '#ef4444', text: '#ffffff' },
  };

  const color = colors[status];

  return (
    <span
      style={{
        padding: '0.25rem 0.75rem',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 'bold',
        backgroundColor: color.bg,
        color: color.text,
      }}
    >
      {label || status.toUpperCase()}
    </span>
  );
};

// ============================================
// DATA TABLE
// ============================================

export interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
}

export interface DataTableProps {
  columns: Column[];
  data: any[];
  emptyMessage?: string;
}

export const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  emptyMessage = 'No data available',
}) => {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            {columns.map((col) => (
              <th
                key={col.key}
                style={{
                  padding: '0.75rem',
                  textAlign: 'left',
                  fontSize: '0.875rem',
                  fontWeight: 'bold',
                  color: '#374151',
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #e5e7eb' }}>
                {columns.map((col) => (
                  <td key={col.key} style={{ padding: '0.75rem', fontSize: '0.875rem' }}>
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

// ============================================
// PROJECT SELECTOR
// ============================================

export interface Project {
  code: string;
  name: string;
  status: 'active' | 'inactive';
}

export interface ProjectSelectorProps {
  projects: Project[];
  selectedProject: string;
  onSelect: (projectCode: string) => void;
}

export const ProjectSelector: React.FC<ProjectSelectorProps> = ({
  projects,
  selectedProject,
  onSelect,
}) => {
  return (
    <select
      value={selectedProject}
      onChange={(e) => onSelect(e.target.value)}
      style={{
        padding: '0.5rem 1rem',
        border: '1px solid #e5e7eb',
        borderRadius: '0.375rem',
        fontSize: '0.875rem',
        backgroundColor: '#ffffff',
      }}
    >
      {projects.map((project) => (
        <option key={project.code} value={project.code}>
          {project.name} ({project.code})
        </option>
      ))}
    </select>
  );
};

// ============================================
// EXPORTS
// ============================================

export default {
  MetricCard,
  StatusBadge,
  DataTable,
  ProjectSelector,
};
