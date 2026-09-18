'use client';
import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { BomChart } from './BomChart';
import { TopologyDiagram } from './TopologyDiagram';
import { TelemetryChart } from './TelemetryChart';
import type { InitiativeSpec, HardwareTier } from '@/lib/initiatives';

const InitiativeScene = dynamic(() => import('./InitiativeScene'), {
  ssr: false,
  loading: () => <div style={{ height: 320, borderRadius: 10, background: 'rgba(2,6,23,0.5)' }} />,
});

const CAP_LEVEL: Record<string, number> = {
  planned: 20,
  scaffold: 45,
  heuristic: 65,
  trained: 85,
  validated: 100,
};

export function InitiativeVisuals({ spec, color }: { spec: InitiativeSpec; color: string }) {
  const [tier, setTier] = useState<'individual' | 'enterprise'>('individual');
  const t: HardwareTier = spec.hardware[tier];
  const it = t.interfaces ?? {};
  const sensors = it.sensors ?? [];
  const actuators = it.actuators ?? [];

  return (
    <>
      <Card style={{ padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.25rem' }}>3D Interface View</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
          Drag to rotate. The core is the {spec.name} device; cyan nodes are declared sensors, amber nodes are actuators.
        </p>
        <InitiativeScene sensors={sensors} actuators={actuators} color={color} label={spec.name} />
        <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.4rem' }}>
          Schematic built from the IDS interface. Motion is illustrative, not live telemetry.
        </p>
      </Card>

      <Card style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>BOM &amp; Power</h2>
          <div style={{ display: 'flex', gap: '0.4rem' }}>
            {(['individual', 'enterprise'] as const).map((k) => (
              <button
                key={k}
                onClick={() => setTier(k)}
                className={`btn ${tier === k ? 'btn-primary' : 'btn-outline'}`}
                style={{ fontSize: '0.78rem', padding: '0.35rem 0.8rem' }}
              >
                {k === 'individual' ? 'Community' : 'Enterprise'}
              </button>
            ))}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
          <Badge tone={t.status === 'verified' ? 'emerald' : 'dim'}>{t.status}</Badge>
          {t.unit && <span className="badge badge-dim">Unit: {t.unit}</span>}
          {t.power && <span className="badge badge-dim">Power: {t.power}</span>}
          {t.buildHours != null && <span className="badge badge-dim">{t.buildHours} h build/install</span>}
        </div>
        {(() => {
          const counts = (t.bom ?? []).reduce<Record<string, number>>((m, b) => {
            const k = b.sourcing || (/^https?:/.test(b.source || '') ? 'vendor-list' : 'estimate');
            m[k] = (m[k] ?? 0) + 1;
            return m;
          }, {});
          const parts = ['vendor-list', 'quote-required', 'quoted', 'estimate']
            .filter((k) => counts[k])
            .map((k) => `${counts[k]} ${k}`);
          return (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.6rem' }}>
              Sourcing: {parts.join(' · ') || '—'}
            </div>
          );
        })()}
        <BomChart bom={t.bom ?? []} color={color} />
      </Card>

      <Card style={{ padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>System Topology</h2>
        <TopologyDiagram
          id={spec.id}
          sensors={sensors}
          actuators={actuators}
          telemetryTopic={it.telemetryTopic}
          controlTopic={it.controlTopic}
          color={color}
        />
      </Card>

      <Card style={{ padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.6rem' }}>Capabilities</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
          {spec.software.capabilities.map((c) => (
            <div key={c.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.2rem' }}>
                <span>{c.name}</span>
                <span style={{ color: 'var(--text-muted)' }}>{c.status}</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${CAP_LEVEL[c.status] ?? 30}%` }} />
              </div>
            </div>
          ))}
        </div>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>Telemetry (demo)</h2>
        <TelemetryChart sensors={sensors} />
      </Card>
    </>
  );
}
