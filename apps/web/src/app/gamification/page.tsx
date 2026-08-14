'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { gamificationApi } from '@/lib/api';

const LEVEL_TONES = ['emerald', 'cyan', 'violet', 'amber', 'rose', 'blue', 'teal', 'amber', 'rose'] as const;

export default function GamificationPage() {
  const [leaderboard, setLeaderboard] = useState<Record<string, unknown>[]>([]);
  const [levels, setLevels] = useState<Record<string, unknown>[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      gamificationApi.leaderboard(),
      gamificationApi.levels(),
      gamificationApi.stats(),
    ])
      .then(([lb, lv, s]) => {
        setLeaderboard(lb as Record<string, unknown>[]);
        setLevels(lv as Record<string, unknown>[]);
        setStats(s as Record<string, unknown>);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const rankColor = (i: number) => (i === 0 ? 'var(--amber)' : i === 1 ? 'var(--text-muted)' : i === 2 ? '#fb923c' : 'var(--text-dim)');

  return (
    <>
      <PageHeader title="Gamification & XP System" subtitle="Earn XP, level up, complete quests, collect badges. Make saving the planet fun." accent="amber">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_users', 'total_xp_awarded', 'total_quests'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="amber" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <div className="grid grid-2" style={{ alignItems: 'start' }}>
          <section>
            <h2 className="section-heading">Global Leaderboard</h2>
            {loading ? (
              <Skeleton height={300} />
            ) : (
              <Card style={{ overflow: 'hidden' }}>
                {leaderboard.slice(0, 10).map((entry, i) => (
                  <div key={String(entry.user_id ?? i)} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.9rem 1.2rem', borderBottom: i < 9 ? '1px solid var(--border)' : 'none', background: i < 3 ? 'rgba(251,191,36,0.07)' : undefined }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, width: '1.6rem', textAlign: 'center', color: rankColor(i) }}>{i + 1}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600 }}>{String(entry.user_id ?? 'User')}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Level {String(entry.level ?? 1)} &bull; {String(entry.title ?? 'Eco Starter')}</div>
                    </div>
                    <div style={{ color: 'var(--amber)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{String(entry.total_xp ?? 0)} XP</div>
                  </div>
                ))}
              </Card>
            )}
          </section>

          <section>
            <h2 className="section-heading">XP Levels</h2>
            {loading ? (
              <Skeleton height={300} />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {levels.map((lv) => {
                  const lvl = lv as Record<string, unknown>;
                  const idx = (Number(lvl.level ?? 1) - 1) % LEVEL_TONES.length;
                  const tone = LEVEL_TONES[idx];
                  return (
                    <Card key={String(lvl.level)} style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <Badge tone={tone} style={{ fontSize: '0.9rem' }}>{String(lvl.level)}</Badge>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600 }}>{String(lvl.title ?? 'Level')}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(lvl.xp_required ?? 0)} XP required</div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      </div>
    </>
  );
}
