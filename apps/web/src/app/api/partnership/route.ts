import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

interface InquiryPayload {
  organization?: string;
  contact_name?: string;
  email?: string;
  partner_type?: string;
  tracks?: string[];
  sectors?: string[];
  commitment?: string;
  message?: string;
  consent?: boolean;
  context_code?: string;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(body: InquiryPayload): string[] {
  const errors: string[] = [];
  if (!body.organization || body.organization.trim().length < 2) errors.push('organization is required');
  if (!body.email || !EMAIL_RE.test(body.email)) errors.push('a valid email is required');
  if (!body.message || body.message.trim().length < 20) errors.push('message must be at least 20 characters');
  if (!body.consent) errors.push('consent is required');
  return errors;
}

function splitName(full?: string): { firstName: string; lastName: string } {
  const parts = (full ?? '').trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return { firstName: '', lastName: '' };
  if (parts.length === 1) return { firstName: parts[0], lastName: '' };
  return { firstName: parts[0], lastName: parts.slice(1).join(' ') };
}

interface TwentyCreated<T> {
  data?: T;
}

// --- Twenty CRM sink -------------------------------------------------------
// Creates a Company, a linked Person, and a Note describing the inquiry.
// Payload shapes verified against a live self-hosted Twenty v2.37 instance.
async function sendToTwenty(
  baseUrl: string,
  apiKey: string,
  body: InquiryPayload,
): Promise<{ companyId?: string; personId?: string; noteId?: string }> {
  const post = async <T>(path: string, payload: unknown): Promise<T> => {
    const res = await fetch(`${baseUrl.replace(/\/$/, '')}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${path} -> ${res.status}: ${text.slice(0, 200)}`);
    }
    return (await res.json()) as T;
  };

  const company = await post<TwentyCreated<{ createCompany?: { id?: string } }>>('/rest/companies', {
    name: body.organization,
  });
  const companyId = company.data?.createCompany?.id;

  const { firstName, lastName } = splitName(body.contact_name);
  const person = await post<TwentyCreated<{ createPerson?: { id?: string } }>>('/rest/people', {
    name: { firstName, lastName },
    emails: { primaryEmail: body.email },
    ...(companyId ? { companyId } : {}),
  });
  const personId = person.data?.createPerson?.id;

  const lines = [
    `**Partner type:** ${body.partner_type ?? '—'}`,
    `**Tracks:** ${(body.tracks ?? []).join(', ') || '—'}`,
    `**Sectors:** ${(body.sectors ?? []).join(', ') || '—'}`,
    `**Commitment:** ${body.commitment || '—'}`,
    `**Context code:** ${body.context_code || '—'}`,
    '',
    body.message ?? '',
  ];
  const note = await post<TwentyCreated<{ createNote?: { id?: string } }>>('/rest/notes', {
    title: `Partnership inquiry — ${body.organization}`,
    bodyV2: { markdown: lines.join('\n') },
  });
  const noteId = note.data?.createNote?.id;

  return { companyId, personId, noteId };
}

export async function POST(request: Request) {
  let body: InquiryPayload;
  try {
    body = (await request.json()) as InquiryPayload;
  } catch {
    return NextResponse.json({ ok: false, delivered: false, error: 'invalid_json' }, { status: 400 });
  }

  const errors = validate(body);
  if (errors.length > 0) {
    return NextResponse.json({ ok: false, delivered: false, error: 'validation_failed', errors }, { status: 422 });
  }

  const twentyUrl = process.env.TWENTY_API_URL;
  const twentyKey = process.env.TWENTY_API_KEY;

  // Preferred sink: Twenty CRM (Company + Person + Note).
  if (twentyUrl && twentyKey) {
    try {
      const ids = await sendToTwenty(twentyUrl, twentyKey, body);
      return NextResponse.json({ ok: true, delivered: true, sink: 'twenty', ...ids });
    } catch (err) {
      return NextResponse.json(
        {
          ok: false,
          delivered: false,
          error: 'twenty_failed',
          detail: err instanceof Error ? err.message : 'unknown',
        },
        { status: 502 },
      );
    }
  }

  // Fallback: generic webhook (e.g. a Twenty workflow trigger, n8n, CRM).
  const webhook = process.env.PARTNERSHIP_INTAKE_WEBHOOK;
  if (!webhook) {
    return NextResponse.json(
      {
        ok: false,
        delivered: false,
        error: 'intake_not_configured',
        message:
          'Partnership intake is not connected. Set TWENTY_API_URL + TWENTY_API_KEY, or PARTNERSHIP_INTAKE_WEBHOOK, on the server.',
      },
      { status: 503 },
    );
  }

  const record = {
    ...body,
    submitted_at: new Date().toISOString(),
    source: 'ecos-web/partnerships/intake',
  };

  try {
    const res = await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) {
      return NextResponse.json(
        { ok: false, delivered: false, error: 'upstream_rejected', status: res.status },
        { status: 502 },
      );
    }
  } catch (err) {
    return NextResponse.json(
      { ok: false, delivered: false, error: 'upstream_unreachable', detail: err instanceof Error ? err.message : 'unknown' },
      { status: 502 },
    );
  }

  return NextResponse.json({ ok: true, delivered: true, sink: 'webhook' });
}
