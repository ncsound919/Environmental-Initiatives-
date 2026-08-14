'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { challengesApi, type Challenge } from '@/lib/api';

export default function ChallengesPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([challengesApi.list(), challengesApi.stats()])
      .then(([c, s]) => { setChallenges(c); setStats(s as Record<string, unknown>); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageHeader title="Public Challenges & Dev Bounties" subtitle="Compete, collaborate, and earn rewards while building a greener planet." accent="emerald">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_challenges', 'active_challenges', 'total_prize_pool'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="emerald" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">Active Challenges</h2>
        {loading ? (
          <div className="grid grid-3"><Skeleton height={180} /><Skeleton height={180} /><Skeleton height={180} /></div>
        ) : (
          <div className="grid grid-3">
            {challenges.map((c) => {
              const ch = c as Record<string, unknown>;
              return (
                <Card key={String(ch.id)} hoverable accent="var(--emerald)" accentBar style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <Badge tone="emerald">{String(ch.category ?? 'General')}</Badge>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(ch.difficulty ?? 'Medium')}</span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>{String(ch.title ?? 'Challenge')}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>{String(ch.description ?? '')}</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ color: 'var(--emerald-hover)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>${String(ch.prize_usd ?? 0)} prize</div>
                    <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 1.1rem' }}>Enter Challenge</button>
                  </div>
                  <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                    <span>{String(ch.participants ?? 0)} participants</span>
                    <span>•</span>
                    <span>Ends {String(ch.deadline ?? 'TBD')}</span>
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
