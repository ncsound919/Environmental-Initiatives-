'use client';
import { useEffect, useState } from 'react';
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

  if (loading) return <div className="flex items-center justify-center min-h-screen bg-gray-950"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-emerald-500" /></div>;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <section className="bg-gradient-to-br from-emerald-900 to-teal-700 py-20 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">DIY Hardware Kits</h1>
        <p className="text-xl text-emerald-100 max-w-2xl mx-auto">
          Build real environmental monitoring & energy hardware. Full BOM, firmware, community builds.
        </p>
        <div className="flex justify-center gap-8 mt-10">
          {['total_kits', 'total_revenue_usd', 'community_builds'].map((k) => (
            <div key={k} className="bg-white/10 rounded-xl p-6 min-w-[140px]">
              <div className="text-3xl font-bold text-emerald-200">{String(stats[k] ?? '—')}</div>
              <div className="text-sm text-emerald-100 mt-1 capitalize">{k.replace(/_/g, ' ')}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto py-16 px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kits.map((kit) => {
            const k = kit as Record<string, unknown>;
            const bom = (k.bom as Array<Record<string, unknown>>) ?? [];
            return (
              <div
                key={String(k.id)}
                className="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800 hover:border-emerald-500 transition-all cursor-pointer"
                onClick={() => setSelected(selected?.id === k.id ? null : k)}
              >
                <div className="bg-gradient-to-r from-emerald-800 to-teal-600 h-3" />
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold bg-emerald-900 text-emerald-300 px-3 py-1 rounded-full">
                      {String(k.category ?? 'Hardware')}
                    </span>
                    <span className="text-xs text-gray-400">{String(k.difficulty ?? 'Intermediate')}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{String(k.title ?? 'Kit')}</h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{String(k.description ?? '')}</p>

                  {selected?.id === k.id && (
                    <div className="mt-2 mb-4 bg-gray-800 rounded-xl p-4">
                      <div className="text-sm font-semibold text-emerald-300 mb-2">Bill of Materials</div>
                      <ul className="space-y-1">
                        {bom.map((part, i) => (
                          <li key={i} className="flex justify-between text-xs text-gray-300">
                            <span>{String(part.component ?? '')}</span>
                            <span className="text-gray-500">${String(part.unit_cost_usd ?? 0)} x{String(part.qty ?? 1)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-4">
                    <div>
                      <div className="text-emerald-400 font-bold text-xl">${String(k.price_usd ?? 0)}</div>
                      <div className="text-xs text-gray-500">{String(k.units_sold ?? 0)} sold &bull; {String(k.community_builds ?? 0)} community builds</div>
                    </div>
                    <button
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                      onClick={(e) => { e.stopPropagation(); }}
                    >
                      Order Kit
                    </button>
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
