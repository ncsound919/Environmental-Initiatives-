'use client';
import { useEffect, useState } from 'react';
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

  if (loading) return <div className="flex items-center justify-center min-h-screen bg-gray-950"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-blue-500" /></div>;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <section className="bg-gradient-to-br from-blue-900 to-cyan-700 py-20 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">Eco Marketplace</h1>
        <p className="text-xl text-blue-100 max-w-2xl mx-auto">
          Buy, sell, and trade green goods, IP licenses, and digital products.
        </p>
        <div className="flex justify-center gap-8 mt-10">
          {['total_listings', 'total_gmv_usd', 'active_sellers'].map((k) => (
            <div key={k} className="bg-white/10 rounded-xl p-6 min-w-[140px]">
              <div className="text-3xl font-bold text-blue-200">{String(stats[k] ?? '—')}</div>
              <div className="text-sm text-blue-100 mt-1 capitalize">{k.replace(/_/g, ' ')}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto py-16 px-6">
        <div className="flex gap-3 mb-8 flex-wrap">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setFilter(c)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                filter === c ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((l) => {
            const item = l as Record<string, unknown>;
            return (
              <div key={String(item.id)} className="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800 hover:border-blue-500 transition-all">
                <div className="bg-gradient-to-r from-blue-800 to-cyan-600 h-3" />
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold bg-blue-900 text-blue-300 px-3 py-1 rounded-full capitalize">
                      {String(item.category ?? 'general')}
                    </span>
                    <span className="text-xs text-gray-400">{String(item.listing_type ?? 'sale')}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{String(item.title ?? 'Product')}</h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{String(item.description ?? '')}</p>
                  <div className="flex items-center justify-between">
                    <div className="text-blue-300 font-bold text-xl">${String(item.price_usd ?? 0)}</div>
                    <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                      Buy Now
                    </button>
                  </div>
                  <div className="mt-3 text-xs text-gray-500">
                    Seller: {String(item.seller_id ?? 'Unknown')} &bull; {String(item.units_sold ?? 0)} sold
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
