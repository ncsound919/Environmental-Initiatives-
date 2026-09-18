'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { projects, fundabilityByCode, TRACK_TONES, type FundTrack } from '@/lib/data';
import { withOpacity } from '@/lib/utils';

const TRACKS: FundTrack[] = ['Grant', 'Strategic Partner', 'Revenue', 'Affiliate'];
const FILTERS: (FundTrack | 'All')[] = ['All', ...TRACKS];

const TRACK_DESCRIPTIONS: Record<FundTrack, string> = {
  Grant: 'Non-dilutive capital and in-kind research support (USDA, DOE, EPA, NSF, climate foundations).',
  'Strategic Partner': 'OEMs, utilities, municipalities, farms, and labs for pilots, supply, and offtake.',
  Revenue: 'Paying design partners, campuses, and operators for products and subscriptions.',
  Affiliate: 'Consultants, integrators, and media partners who earn recurring commissions.',
};

export default function PartnershipsPage() {
  const [activeTrack, setActiveTrack] = useState<FundTrack | 'All'>('All');

  const coveredCount = useMemo(
    () => projects.filter((p) => fundabilityByCode[p.code]?.tracks.includes(activeTrack as FundTrack)).length,
    [activeTrack],
  );

  const visible = useMemo(() => {
    if (activeTrack === 'All') return projects;
    return projects.filter((p) => fundabilityByCode[p.code]?.tracks.includes(activeTrack));
  }, [activeTrack]);

  return (
    <>
      <PageHeader
        title="Partnerships & Strategic Alliances"
        subtitle="ECOS is a portfolio of 13 climate-tech initiatives seeking a blended mix of grants, strategic partners, and revenue design partners. Every sector has a defined ask, use of funds, and target profile."
        accent="violet"
      >
        <StatBand>
          <KpiCard value="13" label="Sectors" accent="violet" />
          <KpiCard value="4" label="Funding Tracks" accent="cyan" />
          <KpiCard value="13" label="Defined Asks" accent="amber" />
          <KpiCard value="3" label="Lead Sectors (pilot-ready)" accent="emerald" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">How We Fund and Build</h2>
        <p className="section-sub">A blended model: non-dilutive grants de-risk early sectors, strategic partners provide pilots and offtake, and revenue partners pay for deployed products.</p>
        <div className="grid grid-4" style={{ marginBottom: '2.5rem' }}>
          {TRACKS.map((t) => (
            <Card key={t} style={{ padding: '1.25rem' }}>
              <Badge tone={TRACK_TONES[t]}>{t}</Badge>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.6rem' }}>{TRACK_DESCRIPTIONS[t]}</p>
            </Card>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          <div>
            <h2 className="section-heading" style={{ marginBottom: '0.2rem' }}>Sectors</h2>
            <p className="section-sub" style={{ margin: 0 }}>
              {activeTrack === 'All' ? `All ${projects.length} sectors` : `${coveredCount} sector${coveredCount === 1 ? '' : 's'} seeking ${activeTrack}`}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {FILTERS.map((t) => {
              const active = activeTrack === t;
              return (
                <button
                  key={t}
                  onClick={() => setActiveTrack(t)}
                  className={`btn ${active ? 'btn-primary' : 'btn-outline'}`}
                  style={{ fontSize: '0.8rem', padding: '0.45rem 0.9rem' }}
                >
                  {t}
                </button>
              );
            })}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {visible.map((project) => {
            const f = fundabilityByCode[project.code];
            return (
              <Card key={project.id} style={{ overflow: 'hidden' }}>
                <div style={{ background: withOpacity(project.color, 10), padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '2rem' }}>{project.icon}</span>
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <h3 style={{ fontWeight: 700, fontSize: '1.1rem' }}>{project.name}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{project.type} · {f?.stage ?? 'Stage not set'}</p>
                  </div>
                  <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                    {f?.tracks.map((t) => <Badge key={t} tone={TRACK_TONES[t]}>{t}</Badge>)}
                  </div>
                  <Link
                    href={`/partnerships/intake?sector=${encodeURIComponent(project.name)}&code=${encodeURIComponent(project.code)}`}
                    className="btn btn-outline"
                    style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
                  >
                    Express Interest →
                  </Link>
                </div>

                {f && (
                  <div style={{ padding: '1.5rem' }}>
                    <div style={{ padding: '0.85rem 1rem', borderRadius: 10, background: withOpacity(project.color, 8), marginBottom: '1.25rem' }}>
                      <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.25rem' }}>The Ask</div>
                      <div style={{ fontSize: '0.92rem' }}>{f.ask}</div>
                    </div>

                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                      <div>
                        <h4 style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.75rem' }}>🤝 Strategic Needs</h4>
                        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                          {project.partnershipNeeds.map((need, i) => (
                            <li key={i} style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', gap: '0.5rem' }}><span style={{ color: 'var(--text-dim)', flexShrink: 0 }}>•</span>{need}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.75rem' }}>📣 Affiliate Marketing</h4>
                        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                          {project.affiliateOpportunities.map((opp, i) => (
                            <li key={i} style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', gap: '0.5rem' }}><span style={{ color: 'var(--text-dim)', flexShrink: 0 }}>•</span>{opp}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        <Card accent="var(--violet, #8b5cf6)" accentBar style={{ padding: '2rem', textAlign: 'center', marginTop: '2.5rem' }}>
          <h2 className="section-heading">Want to engage across the portfolio?</h2>
          <p className="section-sub" style={{ maxWidth: 560, margin: '0.4rem auto 1.5rem' }}>
            Tell us who you are and which sectors or tracks fit. Submissions go directly to our partnership queue.
          </p>
          <Link href="/partnerships/intake" className="btn btn-primary">Submit a Partnership Interest</Link>
        </Card>
      </div>
    </>
  );
}
