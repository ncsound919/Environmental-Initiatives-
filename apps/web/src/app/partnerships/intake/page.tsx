'use client';

import { Suspense, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { projects, fundabilityByCode, TRACK_TONES, type FundTrack } from '@/lib/data';

const TRACKS: FundTrack[] = ['Grant', 'Strategic Partner', 'Revenue', 'Affiliate'];

const PARTNER_TYPES = ['Funder / Grant', 'Strategic Partner', 'Customer / Design Partner', 'Affiliate', 'Other'];

type Status = 'idle' | 'submitting' | 'delivered' | 'error';

const field: React.CSSProperties = {
  width: '100%',
  padding: '0.65rem 0.8rem',
  borderRadius: 8,
  border: '1px solid var(--border)',
  background: 'var(--bg-elevated, rgba(255,255,255,0.03))',
  color: 'var(--text)',
  fontSize: '0.9rem',
  fontFamily: 'inherit',
};

const label: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8rem',
  fontWeight: 600,
  marginBottom: '0.35rem',
  color: 'var(--text-muted)',
};

function IntakeForm() {
  const params = useSearchParams();
  const prefilledSector = params.get('sector') ?? '';
  const prefilledCode = params.get('code') ?? '';

  const [status, setStatus] = useState<Status>('idle');
  const [serverMessage, setServerMessage] = useState('');
  const [errors, setErrors] = useState<string[]>([]);

  const [organization, setOrganization] = useState('');
  const [contactName, setContactName] = useState('');
  const [email, setEmail] = useState('');
  const [partnerType, setPartnerType] = useState(PARTNER_TYPES[1]);
  const [tracks, setTracks] = useState<string[]>([]);
  const [sectors, setSectors] = useState<string[]>(prefilledSector ? [prefilledSector] : []);
  const [commitment, setCommitment] = useState('');
  const [message, setMessage] = useState('');
  const [consent, setConsent] = useState(false);

  const toggle = (list: string[], setList: (v: string[]) => void, value: string) => {
    setList(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);
  };

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('submitting');
    setErrors([]);
    setServerMessage('');

    try {
      const res = await fetch('/api/partnership', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization,
          contact_name: contactName,
          email,
          partner_type: partnerType,
          tracks,
          sectors,
          commitment,
          message,
          consent,
          context_code: prefilledCode || undefined,
        }),
      });
      const data = (await res.json().catch(() => ({}))) as {
        ok?: boolean;
        delivered?: boolean;
        message?: string;
        errors?: string[];
      };

      if (res.ok && data.delivered) {
        setStatus('delivered');
        setServerMessage('Received. Your partnership interest has been delivered to the ECOS team.');
      } else {
        setStatus('error');
        setErrors(data.errors ?? []);
        setServerMessage(
          data.message ??
            'Submission was not delivered. Please try again, or contact us directly once a contact channel is published.',
        );
      }
    } catch {
      setStatus('error');
      setServerMessage('Network error — the submission was not delivered.');
    }
  }

  return (
    <>
      <PageHeader
        title="Partnership Interest"
        subtitle="Tell us who you are, which sectors and funding tracks fit, and what you can offer. Submissions are validated server-side and delivered to the partnership queue."
        accent="violet"
      >
        <div style={{ marginTop: '1rem' }}>
          <Link href="/partnerships" className="btn btn-outline" style={{ fontSize: '0.85rem' }}>← Back to Partnerships</Link>
        </div>
      </PageHeader>

      <div className="page-container page-section" style={{ maxWidth: 820 }}>
        {prefilledSector && (
          <Card style={{ padding: '1rem 1.25rem', marginBottom: '1.25rem' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Expressing interest in: </span>
            <strong>{prefilledSector}</strong>
          </Card>
        )}

        <Card style={{ padding: '1.75rem' }}>
          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
            <div className="grid grid-2" style={{ gap: '1rem' }}>
              <div>
                <label style={label} htmlFor="organization">Organization *</label>
                <input id="organization" style={field} value={organization} onChange={(e) => setOrganization(e.target.value)} required />
              </div>
              <div>
                <label style={label} htmlFor="contact_name">Contact name</label>
                <input id="contact_name" style={field} value={contactName} onChange={(e) => setContactName(e.target.value)} />
              </div>
            </div>

            <div className="grid grid-2" style={{ gap: '1rem' }}>
              <div>
                <label style={label} htmlFor="email">Work email *</label>
                <input id="email" type="email" style={field} value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div>
                <label style={label} htmlFor="partner_type">Partner type</label>
                <select id="partner_type" style={field} value={partnerType} onChange={(e) => setPartnerType(e.target.value)}>
                  {PARTNER_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label style={label}>Funding tracks you can support</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {TRACKS.map((t) => {
                  const on = tracks.includes(t);
                  return (
                    <button
                      type="button"
                      key={t}
                      onClick={() => toggle(tracks, setTracks, t)}
                      className={`badge badge-${TRACK_TONES[t]}`}
                      style={{ cursor: 'pointer', opacity: on ? 1 : 0.45, border: on ? '1px solid currentColor' : '1px solid transparent', padding: '0.35rem 0.7rem' }}
                      aria-pressed={on}
                    >
                      {t}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label style={label}>Sectors of interest</label>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                {projects.map((p) => {
                  const on = sectors.includes(p.name);
                  return (
                    <button
                      type="button"
                      key={p.code}
                      onClick={() => toggle(sectors, setSectors, p.name)}
                      className="badge badge-dim"
                      style={{ cursor: 'pointer', opacity: on ? 1 : 0.5, border: on ? `1px solid ${p.color}` : '1px solid transparent', padding: '0.35rem 0.7rem' }}
                      aria-pressed={on}
                    >
                      {p.icon} {p.name}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label style={label} htmlFor="commitment">What you can offer (budget, pilot, offtake, in-kind)</label>
              <input id="commitment" style={field} value={commitment} onChange={(e) => setCommitment(e.target.value)} placeholder="e.g. $50k grant, 1 pilot site, multi-year offtake" />
            </div>

            <div>
              <label style={label} htmlFor="message">Message * (what you want to do with ECOS)</label>
              <textarea id="message" rows={5} style={{ ...field, resize: 'vertical' }} value={message} onChange={(e) => setMessage(e.target.value)} required />
            </div>

            <label style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} style={{ marginTop: '0.2rem' }} />
              I agree that ECOS may store and use this information to respond to my enquiry.
            </label>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <button type="submit" className="btn btn-primary" disabled={status === 'submitting'}>
                {status === 'submitting' ? 'Submitting…' : 'Submit Partnership Interest'}
              </button>
              {status === 'delivered' && <span style={{ color: 'var(--success)', fontSize: '0.85rem' }}>✓ {serverMessage}</span>}
              {status === 'error' && <span style={{ color: 'var(--danger, #ef4444)', fontSize: '0.85rem' }}>{serverMessage}</span>}
            </div>

            {errors.length > 0 && (
              <ul style={{ listStyle: 'none', color: 'var(--danger, #ef4444)', fontSize: '0.82rem' }}>
                {errors.map((e) => <li key={e}>• {e}</li>)}
              </ul>
            )}
          </form>
        </Card>

        <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '1rem' }}>
          No fake confirmations: if the intake destination is not configured, the server returns an explicit error instead of
          pretending the message was sent.
        </p>
      </div>
    </>
  );
}

export default function IntakePage() {
  return (
    <Suspense fallback={<div className="page-container page-section">Loading…</div>}>
      <IntakeForm />
    </Suspense>
  );
}
