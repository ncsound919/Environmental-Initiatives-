'use client';
import { useEffect, useState } from 'react';
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

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-green-500" /></div>;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Hero */}
      <section className="bg-gradient-to-br from-green-900 to-emerald-700 py-20 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">Public Challenges & Dev Bounties</h1>
        <p className="text-xl text-green-100 max-w-2xl mx-auto">
          Compete, collaborate, and earn rewards while building a greener planet.
        </p>
        <div className="flex justify-center gap-8 mt-10">
          {['total_challenges', 'active_challenges', 'total_prize_pool'].map((k) => (
            <div key={k} className="bg-white/10 rounded-xl p-6 min-w-[140px]">
              <div className="text-3xl font-bold text-green-300">{String(stats[k] ?? '—')}</div>
              <div className="text-sm text-green-100 mt-1 capitalize">{k.replace(/_/g, ' ')}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Challenge Grid */}
      <section className="max-w-6xl mx-auto py-16 px-6">
        <h2 className="text-3xl font-bold mb-8">Active Challenges</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {challenges.map((c) => {
            const ch = c as Record<string, unknown>;
            return (
              <div key={String(ch.id)} className="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800 hover:border-green-500 transition-all">
                <div className="bg-gradient-to-r from-green-800 to-emerald-600 h-3" />
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold bg-green-900 text-green-300 px-3 py-1 rounded-full">{String(ch.category ?? 'General')}</span>
                    <span className="text-xs text-gray-400">{String(ch.difficulty ?? 'Medium')}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{String(ch.title ?? 'Challenge')}</h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{String(ch.description ?? '')}</p>
                  <div className="flex items-center justify-between">
                    <div className="text-green-400 font-bold">${String(ch.prize_usd ?? 0)} prize</div>
                    <button className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                      Enter Challenge
                    </button>
                  </div>
                  <div className="mt-4 flex gap-2 text-xs text-gray-500">
                    <span>{String(ch.participants ?? 0)} participants</span>
                    <span>•</span>
                    <span>Ends {String(ch.deadline ?? 'TBD')}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
