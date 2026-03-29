'use client';
import { useEffect, useState } from 'react';
import { membershipApi, type MembershipTier } from '@/lib/api';

const TIER_COLORS: Record<string, string> = {
  Free: 'from-gray-700 to-gray-600',
  Pro: 'from-blue-700 to-blue-500',
  EcoChampion: 'from-green-700 to-emerald-500',
  PlanetGuardian: 'from-purple-700 to-violet-500',
};

export default function MembershipPage() {
  const [tiers, setTiers] = useState<MembershipTier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    membershipApi.tiers()
      .then(setTiers)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center min-h-screen bg-gray-950"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" /></div>;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <section className="bg-gradient-to-br from-purple-900 to-violet-700 py-20 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">Membership & Perks</h1>
        <p className="text-xl text-purple-100 max-w-2xl mx-auto">
          Unlock exclusive tools, analytics, and rewards. Invest in the planet, earn for it.
        </p>
      </section>

      <section className="max-w-6xl mx-auto py-16 px-6">
        <h2 className="text-3xl font-bold mb-10 text-center">Choose Your Tier</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {tiers.map((t) => {
            const tier = t as Record<string, unknown>;
            const name = String(tier.name ?? 'Tier');
            const perks = (tier.perks as string[]) ?? [];
            const popular = tier.popular as boolean;
            return (
              <div
                key={name}
                className={`relative bg-gray-900 rounded-2xl overflow-hidden border ${
                  popular ? 'border-purple-500 ring-2 ring-purple-500' : 'border-gray-800'
                }`}
              >
                {popular && (
                  <div className="absolute top-0 left-0 right-0 text-center text-xs font-bold bg-purple-600 py-1">
                    MOST POPULAR
                  </div>
                )}
                <div className={`bg-gradient-to-r ${TIER_COLORS[name] ?? 'from-gray-700 to-gray-600'} h-2`} />
                <div className="p-6 pt-8">
                  <h3 className="text-2xl font-bold mb-1">{name}</h3>
                  <div className="text-3xl font-bold text-purple-300 mb-1">
                    {tier.price_monthly === 0 ? 'Free' : `$${String(tier.price_monthly)}/mo`}
                  </div>
                  {tier.price_annual ? (
                    <div className="text-sm text-gray-400 mb-4">${String(tier.price_annual)}/yr</div>
                  ) : <div className="mb-4" />}
                  <ul className="space-y-2 mb-6">
                    {perks.map((p: string) => (
                      <li key={p} className="flex items-start gap-2 text-sm text-gray-300">
                        <span className="text-green-400 mt-0.5">&#10003;</span>{p}
                      </li>
                    ))}
                  </ul>
                  <button
                    className={`w-full py-2 rounded-lg font-semibold text-sm transition-colors ${
                      popular
                        ? 'bg-purple-600 hover:bg-purple-500 text-white'
                        : 'bg-gray-700 hover:bg-gray-600 text-white'
                    }`}
                  >
                    {tier.price_monthly === 0 ? 'Get Started' : 'Subscribe'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
