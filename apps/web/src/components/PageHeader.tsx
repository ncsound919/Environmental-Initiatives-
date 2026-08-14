import { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  accent?: 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal';
  children?: ReactNode; // stat band etc.
}

const GRADIENTS: Record<string, [string, string]> = {
  emerald: ['#064e3b', '#0c4a6e'],
  cyan: ['#164e63', '#0c4a6e'],
  violet: ['#312e81', '#4c1d95'],
  amber: ['#713f12', '#7c2d12'],
  rose: ['#881337', '#4c0519'],
  blue: ['#1e3a8a', '#164e63'],
  teal: ['#134e4a', '#164e63'],
};

export function PageHeader({ title, subtitle, accent = 'emerald', children }: PageHeaderProps) {
  const [from, to] = GRADIENTS[accent] ?? GRADIENTS.emerald;
  return (
    <section className="page-hero" style={{ '--hero-from': from, '--hero-to': to } as React.CSSProperties}>
      <div className="page-container">
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
        {children}
      </div>
    </section>
  );
}
