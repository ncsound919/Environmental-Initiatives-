import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  hoverable?: boolean;
  accent?: string; // any CSS color for the top bar / hover border
  accentBar?: boolean;
  className?: string;
}

export function Card({ children, hoverable, accent, accentBar, className = '' }: CardProps) {
  return (
    <div
      className={`card ${hoverable ? 'hoverable' : ''} ${className}`}
      style={
        {
          '--accent': accent ?? undefined,
          borderTop: accentBar ? `3px solid ${accent}` : undefined,
        } as React.CSSProperties
      }
    >
      {children}
    </div>
  );
}
