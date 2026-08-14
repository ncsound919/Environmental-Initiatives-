'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Skeleton } from '@/components/Skeleton';
import { membershipApi, type MembershipTier } from '@/lib/api';

const TIER_ACCENTS: Record<string, string> = {
  Free: '#64748b',
  Pro: '#3b82f6',
  EcoChampion: '#10b981',
  PlanetGuardian: '#a78bfa',
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

  return (
    <>
      <PageHeader title="Membership & Perks" subtitle="Unlock exclusive tools, analytics, and rewards. Invest in the planet, earn for it." accent="violet">
        {loading && <StatBandLoading />}
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading" style={{ textAlign: 'center' }}>Choose Your Tier</h2>
        {loading ? (
          <div className="grid grid-4"><Skeleton height={280} /><Skeleton height={280} /><Skeleton height={280} /><Skeleton height={280} /></div>
        ) : (
          <div className="grid grid-4">
            {tiers.map((t) => {
              const tier = t as Record<string, unknown>;
              const name = String(tier.name ?? 'Tier');
              const perks = (tier.perks as string[]) ?? [];
              const popular = tier.popular as boolean;
              const accent = TIER_ACCENTS[name] ?? '#64748b';
              return (
                <Card key={name} style={{ padding: '1.5rem', position: 'relative', borderColor: popular ? accent : undefined, boxShadow: popular ? `0 0 24px ${accent}33` : undefined }}>
                  {popular && (
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, textAlign: 'center', fontSize: '0.7rem', fontWeight: 700, background: accent, color: '#fff', padding: '0.3rem 0' }}>
                      MOST POPULAR
                    </div>
                  )}
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: popular ? '1rem' : 0 }}>{name}</h3>
                  <div style={{ fontSize: '1.7rem', fontWeight: 700, color: accent, fontFamily: 'var(--font-mono)', margin: '0.3rem 0 0.2rem' }}>
                    {tier.price_monthly === 0 ? 'Free' : `$${String(tier.price_monthly)}/mo`}
                  </div>
                  {tier.price_annual ? (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>${String(tier.price_annual)}/yr</div>
                  ) : <div style={{ marginBottom: '1rem' }} />}
                  <ul style={{ listStyle: 'none', marginBottom: '1.5rem' }}>
                    {perks.map((p: string) => (
                      <li key={p} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                        <span style={{ color: 'var(--success)', marginTop: '0.1rem' }}>&#10003;</span>{p}
                      </li>
                    ))}
                  </ul>
                  <button className="btn btn-primary" style={{ width: '100%', background: accent, borderColor: accent, color: '#fff' }}>
                    {tier.price_monthly === 0 ? 'Get Started' : 'Subscribe'}
                  </button>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

function StatBandLoading() {
  return <div className="stat-band"><Skeleton height={90} /><Skeleton height={90} /><Skeleton height={90} /><Skeleton height={90} /></div>;
}
