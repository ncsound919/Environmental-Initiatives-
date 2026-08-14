'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { marketplaceApi, type Listing } from '@/lib/api';

export default function MarketplacePage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    Promise.all([marketplaceApi.listings(), marketplaceApi.stats()])
      .then(([l, s]) => { setListings(l); setStats(s as Record<string, unknown>); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const categories = ['all', ...new Set(listings.map((l) => String((l as Record<string, unknown>).category ?? 'other')))];
  const filtered = filter === 'all' ? listings : listings.filter((l) => String((l as Record<string, unknown>).category) === filter);

  return (
    <>
      <PageHeader title="Eco Marketplace" subtitle="Buy, sell, and trade green goods, IP licenses, and digital products." accent="blue">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_listings', 'total_gmv_usd', 'active_sellers'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="blue" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {categories.map((c) => (
            <button key={c} onClick={() => setFilter(c)} className={`pill ${filter === c ? 'blue-active' : ''}`}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </button>
          ))}
        </div>
        {loading ? (
          <div className="grid grid-3"><Skeleton height={180} /><Skeleton height={180} /><Skeleton height={180} /></div>
        ) : (
          <div className="grid grid-3">
            {filtered.map((l) => {
              const item = l as Record<string, unknown>;
              return (
                <Card key={String(item.id)} hoverable accent="var(--blue)" accentBar style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <Badge tone="blue">{String(item.category ?? 'general')}</Badge>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(item.listing_type ?? 'sale')}</span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>{String(item.title ?? 'Product')}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>{String(item.description ?? '')}</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ color: '#60a5fa', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '1.1rem' }}>${String(item.price_usd ?? 0)}</div>
                    <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 1.1rem', background: 'var(--blue)', borderColor: 'var(--blue)', color: '#eff6ff' }}>Buy Now</button>
                  </div>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                    Seller: {String(item.seller_id ?? 'Unknown')} &bull; {String(item.units_sold ?? 0)} sold
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
