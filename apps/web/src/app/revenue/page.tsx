'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Skeleton } from '@/components/Skeleton';
import {
  challengesApi,
  membershipApi,
  marketplaceApi,
  gamificationApi,
  diyKitsApi,
} from '@/lib/api';

type StatCard = { label: string; value: string; accent: string; href: string; icon: string };

const ACCENTS: Record<string, string> = {
  'Challenge Prize Pool': 'emerald',
  'Membership MRR': 'violet',
  'Marketplace GMV': 'blue',
  'XP Awarded': 'amber',
  'Kit Revenue': 'teal',
};

export default function RevenueDashboard() {
  const [cards, setCards] = useState<StatCard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      challengesApi.stats(),
      membershipApi.revenue(),
      marketplaceApi.stats(),
      gamificationApi.stats(),
      diyKitsApi.stats(),
    ]).then((results) => {
      const get = (r: PromiseSettledResult<unknown>, key: string): string => {
        if (r.status === 'fulfilled') {
          const val = (r.value as Record<string, unknown>)[key];
          return String(val ?? '—');
        }
        return '—';
      };
      const raw = [
        { label: 'Challenge Prize Pool', value: `$${get(results[0], 'total_prize_pool')}`, href: '/challenges', icon: '🏆' },
        { label: 'Membership MRR', value: `$${get(results[1], 'monthly_recurring_revenue')}`, href: '/membership', icon: '👑' },
        { label: 'Marketplace GMV', value: `$${get(results[2], 'total_gmv_usd')}`, href: '/marketplace', icon: '🛒' },
        { label: 'XP Awarded', value: get(results[3], 'total_xp_awarded'), href: '/gamification', icon: '⭐' },
        { label: 'Kit Revenue', value: `$${get(results[4], 'total_revenue_usd')}`, href: '/diy-kits', icon: '🔧' },
      ];
      setCards(raw.map((c) => ({ ...c, accent: ACCENTS[c.label] ?? 'emerald' })));
    }).finally(() => setLoading(false));
  }, []);

  const modules = [
    { name: 'Public Challenges', desc: 'Bounties, submissions, leaderboards', href: '/challenges', icon: '🏆' },
    { name: 'Membership', desc: '4 tiers: Free / Pro / EcoChampion / PlanetGuardian', href: '/membership', icon: '👑' },
    { name: 'Marketplace', desc: 'Green goods, IP licenses, digital products', href: '/marketplace', icon: '🛒' },
    { name: 'Gamification', desc: 'XP, 9 levels, quests, badges, leaderboard', href: '/gamification', icon: '⭐' },
    { name: 'DIY Kits', desc: '5 hardware kits with full BOM & firmware', href: '/diy-kits', icon: '🔧' },
  ];

  return (
    <>
      <PageHeader title="Revenue Dashboard" subtitle="Reference implementation — metrics come from the demo API. Storage is in-memory and is not connected to live transactions." accent="emerald">
        <StatBand>
          {loading
            ? [1, 2, 3, 4, 5].map((i) => <Skeleton key={i} height={90} />)
            : cards.map((c) => (
                <KpiCard key={c.label} value={c.value} label={c.label} accent={c.accent as 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal'} icon={c.icon} />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">Revenue Modules</h2>
        <p className="section-sub">Each module is a working reference implementation wired to the demo API (no auth, no persistent storage yet).</p>
        <div className="grid grid-3">
          {modules.map((m) => (
            <Link key={m.href} href={m.href}>
              <Card hoverable style={{ padding: '1.5rem', height: '100%' }}>
                <div style={{ fontSize: '1.6rem', marginBottom: '0.5rem' }}>{m.icon}</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.3rem' }}>{m.name}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{m.desc}</p>
                <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>View module &rarr;</div>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
