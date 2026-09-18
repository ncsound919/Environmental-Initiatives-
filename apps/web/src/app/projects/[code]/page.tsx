'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { projects, fundabilityByCode, TRACK_TONES } from '@/lib/data';
import { getInitiativeSpec, type HardwareTier } from '@/lib/initiatives';
import { InitiativeVisuals } from '@/components/viz/InitiativeVisuals';
import { withOpacity } from '@/lib/utils';

const DOCUMENSO_URL = process.env.NEXT_PUBLIC_DOCUMENSO_URL || 'http://localhost:3400';

function TierBlock({ tier, icon, label }: { tier: HardwareTier; color: string; icon: string; label: string }) {
  const gap = tier.missing ?? [];
  return (
    <div style={{ padding: '1rem', borderRadius: 10, border: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap' }}>
        <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{icon} {label}: {tier.name}</div>
        <Badge tone={tier.status === 'verified' ? 'emerald' : 'dim'}>{tier.status}</Badge>
      </div>
      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>{tier.audience}</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.6rem' }}>
        {tier.unit && <span className="badge badge-dim">Unit: {tier.unit}</span>}
        {tier.power && <span className="badge badge-dim">Power: {tier.power}</span>}
        {tier.buildHours != null && <span className="badge badge-dim">{tier.buildHours} h build</span>}
        {tier.topology && <span className="badge badge-dim">{tier.topology}</span>}
      </div>
      {tier.interfaces && (
        <div style={{ marginTop: '0.7rem', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          <div><strong>Telemetry:</strong> <code>{tier.interfaces.telemetryTopic}</code></div>
          {(tier.interfaces.sensors?.length ?? 0) > 0 && <div><strong>Sensors:</strong> {tier.interfaces.sensors!.join(', ')}</div>}
          {(tier.interfaces.actuators?.length ?? 0) > 0 && <div><strong>Actuators:</strong> {tier.interfaces.actuators!.join(', ')}</div>}
        </div>
      )}
      {tier.bom && tier.bom.length > 0 && (
        <div style={{ marginTop: '0.7rem', fontSize: '0.8rem' }}>
          <strong>BOM:</strong> {tier.bom.map((b) => `${b.part} ×${b.qty}`).join(', ')}
        </div>
      )}
      {tier.status === 'draft' && gap.length > 0 && (
        <div style={{ marginTop: '0.7rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--amber, #f59e0b)', marginBottom: '0.3rem' }}>Still to build</div>
          <ul style={{ listStyle: 'none', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {gap.map((g) => <li key={g} style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>✗ {g}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function ProjectDetailPage() {
  const params = useParams();
  const code = params.code as string;
  const project = projects.find((p) => p.code === code);
  const fundability = project ? fundabilityByCode[project.code] : undefined;
  const spec = project ? getInitiativeSpec(project.code) : undefined;

  if (!project) {
    return (
      <div className="page-container page-section">
        <h1 className="page-title">Project Not Found</h1>
        <p className="section-sub">The requested project does not exist.</p>
        <Link href="/projects" className="btn btn-primary">Back to Initiatives</Link>
      </div>
    );
  }

  return (
    <>
      <PageHeader title={`${project.icon} ${project.name}`} subtitle={project.type} accent="emerald">
        <div style={{ display: 'flex', gap: '0.8rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <Badge tone="cyan">Phase {project.phase}</Badge>
          {fundability && <Badge tone="amber">{fundability.stage}</Badge>}
          {fundability?.tracks.map((t) => (
            <Badge key={t} tone={TRACK_TONES[t]}>{t}</Badge>
          ))}
          <Badge tone="dim">{project.readiness}% build checklist (self-assessed)</Badge>
        </div>
      </PageHeader>

      <div className="page-container page-section">
        <div className="grid grid-2" style={{ gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', alignItems: 'start' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {fundability && (
              <Card style={{ padding: '1.5rem', borderTop: `3px solid ${project.color}` }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                  <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Funding & Partnership</h2>
                  <Link href="/partnerships/intake" className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>
                    Partner with {project.name} →
                  </Link>
                </div>

                <div style={{ marginTop: '1rem', padding: '0.9rem 1rem', borderRadius: 10, background: withOpacity(project.color, 10) }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.3rem' }}>The Ask</div>
                  <div style={{ fontSize: '0.95rem' }}>{fundability.ask}</div>
                </div>

                <div className="grid grid-2" style={{ marginTop: '1.25rem', gap: '1.25rem' }}>
                  <div>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.5rem' }}>Use of Funds</h3>
                    <ul style={{ listStyle: 'none' }}>
                      {fundability.useOfFunds.map((u) => (
                        <li key={u} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0.25rem 0', display: 'flex', gap: '0.5rem' }}><span style={{ color: project.color }}>•</span>{u}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.5rem' }}>Milestones</h3>
                    <ul style={{ listStyle: 'none' }}>
                      {fundability.milestones.map((m) => (
                        <li key={m} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0.25rem 0', display: 'flex', gap: '0.5rem' }}><span style={{ color: project.color }}>◦</span>{m}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="grid grid-2" style={{ marginTop: '1.25rem', gap: '1.25rem' }}>
                  <div>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.35rem' }}>Grant Targets</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{fundability.grantTargets.join(' · ')}</p>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '0.75rem 0 0.35rem' }}>Ideal Partner</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{fundability.partnerProfile}</p>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '0.75rem 0 0.35rem' }}>Offtake Sought</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{fundability.offtake}</p>
                  </div>
                  <div>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.5rem' }}>Evidence</h3>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--success)', marginBottom: '0.3rem' }}>Proven today</div>
                    <ul style={{ listStyle: 'none', marginBottom: '0.75rem' }}>
                      {fundability.evidence.proven.map((e) => (
                        <li key={e} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', padding: '0.15rem 0', display: 'flex', gap: '0.45rem' }}><span style={{ color: 'var(--success)' }}>✓</span>{e}</li>
                      ))}
                    </ul>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--amber, #f59e0b)', marginBottom: '0.3rem' }}>Still missing</div>
                    <ul style={{ listStyle: 'none' }}>
                      {fundability.evidence.missing.map((e) => (
                        <li key={e} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', padding: '0.15rem 0', display: 'flex', gap: '0.45rem' }}><span style={{ color: 'var(--text-dim)' }}>✗</span>{e}</li>
                      ))}
                    </ul>
                    <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '0.75rem' }}>Revenue target: {fundability.arrTarget}</p>
                  </div>
                </div>
              </Card>
            )}

            {spec && (
              <Card style={{ padding: '1.5rem' }}>
                <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.25rem' }}>Hardware Setups</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  Community build and enterprise deployment, from the Initiative Development Spec ({spec.code}).
                </p>
                <p style={{ color: 'var(--text-dim)', fontSize: '0.78rem', marginBottom: '1rem' }}>
                  &ldquo;verified&rdquo; = spec, interfaces, firmware, power and sourcing checks passed by the gate — BOM prices are vendor list estimates, not quotes, and not a physical build.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
                  <TierBlock tier={spec.hardware.individual} color={project.color} icon="🏘️" label="Community" />
                  <TierBlock tier={spec.hardware.enterprise} color={project.color} icon="🏢" label="Enterprise" />
                </div>
              </Card>
            )}

            {spec && <InitiativeVisuals spec={spec} color={project.color} />}

            {spec && (
              <Card style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                  <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Founding Readiness</h2>
                  <Badge tone={spec.founding.status === 'not_started' ? 'dim' : 'emerald'}>{spec.founding.status.replace('_', ' ')}</Badge>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.4rem' }}>
                  {spec.founding.ventureName} — a {spec.founding.structure} of {spec.founding.parent} / {spec.founding.division}.
                </p>
                <div style={{ marginTop: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {([
                    ['Hardware pilot', spec.founding.readiness.hardwarePilot],
                    ['Partner LOI signed', spec.founding.readiness.partnerLoi],
                    ['Unit economics', spec.founding.readiness.unitEconomics],
                  ] as Array<[string, boolean]>).map(([label, done]) => (
                    <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                      <span style={{ color: done ? 'var(--success)' : 'var(--text-dim)' }}>{done ? '✓ ready' : '✗ not yet'}</span>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: '0.9rem', padding: '0.8rem 1rem', borderRadius: 10, background: withOpacity(project.color, 8) }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.25rem' }}>Capital ask</div>
                  <div style={{ fontSize: '0.9rem' }}>{spec.founding.capitalAsk}</div>
                  {spec.founding.offtake && <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>Offtake: {spec.founding.offtake}</div>}
                </div>
                <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                  <Link href={`/partnerships/intake?sector=${encodeURIComponent(project.name)}&code=${encodeURIComponent(project.code)}`} className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>Submit partnership interest</Link>
                  <a href={DOCUMENSO_URL} target="_blank" rel="noreferrer" className="btn btn-outline" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>Sign LOI (Documenso)</a>
                </div>
              </Card>
            )}

            {[
              ['Description', project.description],
              ['Business Model', project.businessModel],
              ['RegenCity Role', project.regenCityRole],
            ].map(([title, body]) => (
              <Card key={title} style={{ padding: '1.5rem' }}>
                <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>{title}</h2>
                <p style={{ lineHeight: 1.7, color: 'var(--text-muted)' }}>{body}</p>
              </Card>
            ))}

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Strategic Partnership Needs</h2>
              <ul style={{ listStyle: 'none' }}>
                {project.partnershipNeeds.map((need, i) => (
                  <li key={i} style={{ padding: '0.6rem 0', borderBottom: i < project.partnershipNeeds.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    <span style={{ color: project.color }}>🤝</span>{need}
                  </li>
                ))}
              </ul>
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Affiliate Marketing Opportunities</h2>
              <ul style={{ listStyle: 'none' }}>
                {project.affiliateOpportunities.map((opp, i) => (
                  <li key={i} style={{ padding: '0.6rem 0', borderBottom: i < project.affiliateOpportunities.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    <span style={{ color: project.color }}>📣</span>{opp}
                  </li>
                ))}
              </ul>
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Features</h2>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {project.features.map((feature, i) => (
                  <span key={i} className="badge badge-emerald" style={{ background: withOpacity(project.color, 14), color: project.color }}>{feature}</span>
                ))}
              </div>
            </Card>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Tech Stack</h2>
              <ul style={{ listStyle: 'none' }}>
                {project.techStack.map((tech, i) => (
                  <li key={i} style={{ padding: '0.7rem 0', borderBottom: i < project.techStack.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    <span style={{ color: project.color }}>•</span>{tech}
                  </li>
                ))}
              </ul>
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>API Endpoints</h2>
              {project.apiEndpoints.length > 0 ? (
                <ul style={{ listStyle: 'none' }}>
                  {project.apiEndpoints.map((endpoint, i) => (
                    <li key={i} className="code-block" style={{ marginBottom: '0.5rem' }}>{endpoint}</li>
                  ))}
                </ul>
              ) : (
                <p style={{ color: 'var(--text-dim)' }}>No API endpoints available yet.</p>
              )}
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Resource Needs</h2>
              {project.resourceNeeds.map((group, gi) => (
                <div key={gi} style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.4rem' }}>{group.category}</div>
                  <ul style={{ listStyle: 'none' }}>
                    {group.items.map((item, ii) => (
                      <li key={ii} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0.25rem 0', borderBottom: ii < group.items.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', gap: '0.4rem' }}>
                        <span style={{ color: 'var(--text-dim)' }}>–</span>{item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Project Info</h2>
              {[['Project ID', project.id], ['Code', project.code], ['Phase', String(project.phase)], ['Readiness', `${project.readiness}%`]].map(([label, value]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0' }}>
                  <span style={{ color: 'var(--text-dim)' }}>{label}</span>
                  <span style={{ fontWeight: 500 }}>{value}</span>
                </div>
              ))}
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
