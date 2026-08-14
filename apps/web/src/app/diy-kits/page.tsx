'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { diyKitsApi, type DiyKit } from '@/lib/api';

export default function DiyKitsPage() {
  const [kits, setKits] = useState<DiyKit[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    Promise.all([diyKitsApi.list(), diyKitsApi.stats()])
      .then(([k, s]) => { setKits(k); setStats(s as Record<string, unknown>); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageHeader title="DIY Hardware Kits" subtitle="Build real environmental monitoring & energy hardware. Full BOM, firmware, community builds." accent="teal">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_kits', 'total_revenue_usd', 'community_builds'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="teal" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        {loading ? (
          <div className="grid grid-3"><Skeleton height={200} /><Skeleton height={200} /><Skeleton height={200} /></div>
        ) : (
          <div className="grid grid-3">
            {kits.map((kit) => {
              const k = kit as Record<string, unknown>;
              const bom = (k.bom as Array<Record<string, unknown>>) ?? [];
              const isOpen = selected?.id === k.id;
              return (
                <Card key={String(k.id)} hoverable accent="var(--teal)" accentBar style={{ padding: '1.5rem', cursor: 'pointer' }} className="" >
                  <div onClick={() => setSelected(isOpen ? null : k)}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <Badge tone="teal">{String(k.category ?? 'Hardware')}</Badge>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(k.difficulty ?? 'Intermediate')}</span>
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>{String(k.title ?? 'Kit')}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>{String(k.description ?? '')}</p>
                  </div>

                  {isOpen && (
                    <div style={{ marginBottom: '1rem', background: 'var(--panel-raised)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--teal)', marginBottom: '0.5rem' }}>Bill of Materials</div>
                      <ul style={{ listStyle: 'none' }}>
                        {bom.map((part, i) => (
                          <li key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', padding: '0.2rem 0' }}>
                            <span>{String(part.component ?? '')}</span>
                            <span style={{ color: 'var(--text-dim)' }}>${String(part.unit_cost_usd ?? 0)} x{String(part.qty ?? 1)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ color: 'var(--teal)', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '1.1rem' }}>${String(k.price_usd ?? 0)}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(k.units_sold ?? 0)} sold &bull; {String(k.community_builds ?? 0)} community builds</div>
                    </div>
                    <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 1.1rem', background: 'var(--teal)', borderColor: 'var(--teal)', color: '#042f2e' }}>Order Kit</button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
