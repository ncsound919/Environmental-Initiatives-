import { ReactNode } from 'react';

type Tone = 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal' | 'dim';

export function Badge({ tone = 'dim', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
