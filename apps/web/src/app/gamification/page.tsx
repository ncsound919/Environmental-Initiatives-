'use client';
import { useEffect, useState } from 'react';
import { gamificationApi } from '@/lib/api';

const LEVEL_COLORS = ['gray', 'green', 'blue', 'purple', 'yellow', 'orange', 'red', 'pink', 'cyan', 'emerald'];

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

  if (loading) return <div className="flex items-center justify-center min-h-screen bg-gray-950"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-yellow-500" /></div>;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <section className="bg-gradient-to-br from-yellow-900 to-orange-700 py-20 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">Gamification & XP System</h1>
        <p className="text-xl text-yellow-100 max-w-2xl mx-auto">
          Earn XP, level up, complete quests, collect badges. Make saving the planet fun.
        </p>
        <div className="flex justify-center gap-8 mt-10">
          {['total_users', 'total_xp_awarded', 'total_quests'].map((k) => (
            <div key={k} className="bg-white/10 rounded-xl p-6 min-w-[140px]">
              <div className="text-3xl font-bold text-yellow-200">{String(stats[k] ?? '—')}</div>
              <div className="text-sm text-yellow-100 mt-1 capitalize">{k.replace(/_/g, ' ')}</div>
            </div>
          ))}
        </div>
      </section>

      <div className="max-w-6xl mx-auto py-16 px-6 grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Leaderboard */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Global Leaderboard</h2>
          <div className="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800">
            {leaderboard.slice(0, 10).map((entry, i) => (
              <div key={String(entry.user_id ?? i)} className={`flex items-center gap-4 p-4 border-b border-gray-800 last:border-0 ${i < 3 ? 'bg-yellow-900/20' : ''}`}>
                <span className={`text-2xl font-bold w-8 text-center ${i === 0 ? 'text-yellow-400' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-orange-400' : 'text-gray-600'}`}>
                  {i + 1}
                </span>
                <div className="flex-1">
                  <div className="font-semibold">{String(entry.user_id ?? 'User')}</div>
                  <div className="text-xs text-gray-400">Level {String(entry.level ?? 1)} &bull; {String(entry.title ?? 'Eco Starter')}</div>
                </div>
                <div className="text-yellow-400 font-bold">{String(entry.total_xp ?? 0)} XP</div>
              </div>
            ))}
          </div>
        </section>

        {/* Levels */}
        <section>
          <h2 className="text-2xl font-bold mb-6">XP Levels</h2>
          <div className="space-y-3">
            {levels.map((lv) => {
              const lvl = lv as Record<string, unknown>;
              const colorIdx = (Number(lvl.level ?? 1) - 1) % LEVEL_COLORS.length;
              const color = LEVEL_COLORS[colorIdx];
              return (
                <div key={String(lvl.level)} className="bg-gray-900 rounded-xl p-4 border border-gray-800 flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full bg-${color}-600 flex items-center justify-center font-bold text-sm`}>
                    {String(lvl.level)}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold">{String(lvl.title ?? 'Level')}</div>
                    <div className="text-xs text-gray-400">{String(lvl.xp_required ?? 0)} XP required</div>
                  </div>
                  <div className="text-sm text-gray-400">{String(lvl.perks ?? '')}</div>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}
