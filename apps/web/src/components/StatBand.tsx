import { ReactNode } from 'react';

export function StatBand({ children }: { children: ReactNode }) {
  return <div className="stat-band">{children}</div>;
}
