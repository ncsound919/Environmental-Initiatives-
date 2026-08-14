import { ReactNode } from 'react';

type Tone = 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal' | 'dim';

export function Badge({ tone = 'dim', children, style }: { tone?: Tone; children: ReactNode; style?: React.CSSProperties }) {
  return <span className={`badge badge-${tone}`} style={style}>{children}</span>;
}
