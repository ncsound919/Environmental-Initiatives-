'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  challengesApi,
  membershipApi,
  marketplaceApi,
  gamificationApi,
  diyKitsApi,
} from '@/lib/api';

type StatCard = {
  label: string;
  value: string;
  color: string;
  href: string;
  icon: string;
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

      setCards([
        {
          label: 'Challenge Prize Pool',
          value: `$${get(results[0], 'total_prize_pool')}`,
          color: 'from-green-700 to-emerald-500',
          href: '/challenges',
          icon: '🏆',
        },
        {
          label: 'Membership MRR',
          value: `$${get(results[1], 'monthly_recurring_revenue')}`,
          color: 'from-purple-700 to-violet-500',
          href: '/membership',
          icon: '👑',
        },
        {
          label: 'Marketplace GMV',
          value: `$${get(results[2], 'total_gmv_usd')}`,
          color: 'from-blue-700 to-cyan-500',
          href: '/marketplace',
          icon: '🛒',
        },
        {
          label: 'XP Awarded',
          value: get(results[3], 'total_xp_awarded'),
          color: 'from-yellow-700 to-orange-500',
          href: '/gamification',
          icon: '⭐',
        },
        {
          label: 'Kit Revenue',
          value: `$${get(results[4], 'total_revenue_usd')}`,
          color: 'from-emerald-700 to-teal-500',
          href: '/diy-kits',
          icon: '🔧',
        },
      ]);
    }).finally(() => setLoading(false));
  }, []);

  const modules = [
    { name: 'Public Challenges', desc: 'Bounties, submissions, leaderboards', href: '/challenges', color: 'green' },
    { name: 'Membership', desc: '4 tiers: Free / Pro / EcoChampion / PlanetGuardian', href: '/membership', color: 'purple' },
    { name: 'Marketplace', desc: 'Green goods, IP licenses, digital products', href: '/marketplace', color: 'blue' },
    { name: 'Gamification', desc: 'XP, 9 levels, quests, badges, leaderboard', href: '/gamification', color: 'yellow' },
    { name: 'DIY Kits', desc: '5 hardware kits with full BOM & firmware', href: '/diy-kits', color: 'emerald' },
  ];

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <section className="bg-gradient-to-br from-gray-900 to-gray-800 py-20 px-6 text-center border-b border-gray-800">
        <h1 className="text-5xl font-bold mb-4">Revenue Dashboard</h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto">
          All 5 revenue streams live — real-time metrics across the entire platform.
        </p>
      </section>

      {/* KPI Cards */}
      <section className="max-w-6xl mx-auto py-12 px-6">
        {loading ? (
          <div className="flex justify-center"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-white" /></div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {cards.map((c) => (
              <Link key={c.href} href={c.href} className={`bg-gradient-to-br ${c.color} rounded-2xl p-6 hover:scale-105 transition-transform`}>
                <div className="text-3xl mb-2">{c.icon}</div>
                <div className="text-2xl font-bold">{c.value}</div>
                <div className="text-sm mt-1 opacity-80">{c.label}</div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Module Links */}
      <section className="max-w-6xl mx-auto pb-16 px-6">
        <h2 className="text-2xl font-bold mb-6">Revenue Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map((m) => (
            <Link key={m.href} href={m.href} className="bg-gray-900 rounded-2xl p-6 border border-gray-800 hover:border-white/30 transition-all group">
              <h3 className="text-xl font-bold mb-2 group-hover:text-white">{m.name}</h3>
              <p className="text-gray-400 text-sm">{m.desc}</p>
              <div className="mt-4 text-sm text-gray-500 group-hover:text-white transition-colors">
                View module &rarr;
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
