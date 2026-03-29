/**
 * ECOS Stripe Billing Engine
 * Usage-based metering + SaaS subscription tiers for all 13 projects
 */
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY ?? '', {
  apiVersion: '2024-04-10',
  typescript: true,
});

/** SaaS tier pricing - maps to Stripe Price IDs in your dashboard */
export const ECOS_PLANS = {
  free: {
    name: 'ECOS Free',
    priceId: process.env.STRIPE_PRICE_FREE ?? '',
    projectLimit: 1,
    telemetryRetentionDays: 7,
    apiCallsPerMonth: 1_000,
  },
  pro: {
    name: 'ECOS Pro',
    priceId: process.env.STRIPE_PRICE_PRO ?? '',
    projectLimit: 5,
    telemetryRetentionDays: 90,
    apiCallsPerMonth: 100_000,
  },
  enterprise: {
    name: 'ECOS Enterprise',
    priceId: process.env.STRIPE_PRICE_ENTERPRISE ?? '',
    projectLimit: 13,
    telemetryRetentionDays: 365,
    apiCallsPerMonth: Infinity,
  },
} as const;

export type EcosPlan = keyof typeof ECOS_PLANS;

/** Stripe metered usage event names */
export const USAGE_EVENTS = {
  API_CALL: 'ecos_api_call',
  TELEMETRY_RECORD: 'ecos_telemetry_record',
  AI_INFERENCE: 'ecos_ai_inference',
  CARBON_CREDIT: 'ecos_carbon_credit',
} as const;

/**
 * Create or retrieve a Stripe Customer for an ECOS user.
 */
export async function getOrCreateCustomer(
  userId: string,
  email: string,
  name?: string,
): Promise<Stripe.Customer> {
  // Search by metadata to avoid duplicates
  const existing = await stripe.customers.search({
    query: `metadata['ecos_user_id']:'${userId}'`,
    limit: 1,
  });
  if (existing.data.length > 0) {
    return existing.data[0];
  }
  return stripe.customers.create({
    email,
    name,
    metadata: { ecos_user_id: userId },
  });
}

/**
 * Subscribe a customer to an ECOS plan.
 */
export async function createSubscription(
  customerId: string,
  plan: EcosPlan,
): Promise<Stripe.Subscription> {
  const priceId = ECOS_PLANS[plan].priceId;
  if (!priceId) {
    throw new Error(`Stripe price ID not configured for plan: ${plan}`);
  }
  return stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: priceId }],
    payment_behavior: 'default_incomplete',
    payment_settings: { save_default_payment_method: 'on_subscription' },
    expand: ['latest_invoice.payment_intent'],
    metadata: { ecos_plan: plan },
  });
}

/**
 * Record metered API usage for a subscription.
 * Call this on every API request to track usage.
 */
export async function recordUsage(
  subscriptionItemId: string,
  quantity: number,
  event: keyof typeof USAGE_EVENTS,
  timestamp?: number,
): Promise<Stripe.UsageRecord> {
  return stripe.subscriptionItems.createUsageRecord(subscriptionItemId, {
    quantity,
    timestamp: timestamp ?? Math.floor(Date.now() / 1000),
    action: 'increment',
  });
}

/**
 * Generate a Stripe Billing Portal session so users can self-manage
 * their subscription, payment method, and invoices.
 */
export async function createBillingPortalSession(
  customerId: string,
  returnUrl: string,
): Promise<Stripe.BillingPortal.Session> {
  return stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: returnUrl,
  });
}

/**
 * Handle incoming Stripe webhooks.
 * Call this from your /api/webhooks/stripe endpoint.
 */
export function constructWebhookEvent(
  rawBody: Buffer,
  signature: string,
): Stripe.Event {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) throw new Error('STRIPE_WEBHOOK_SECRET not set');
  return stripe.webhooks.constructEvent(rawBody, signature, secret);
}

/**
 * Process a Stripe webhook event.
 * Returns the action taken for logging.
 */
export async function processWebhookEvent(
  event: Stripe.Event,
): Promise<{ action: string; data: unknown }> {
  switch (event.type) {
    case 'customer.subscription.created':
    case 'customer.subscription.updated': {
      const sub = event.data.object as Stripe.Subscription;
      return {
        action: 'subscription_updated',
        data: {
          customerId: sub.customer,
          status: sub.status,
          plan: sub.metadata.ecos_plan,
        },
      };
    }
    case 'customer.subscription.deleted': {
      const sub = event.data.object as Stripe.Subscription;
      return {
        action: 'subscription_cancelled',
        data: { customerId: sub.customer },
      };
    }
    case 'invoice.payment_succeeded': {
      const inv = event.data.object as Stripe.Invoice;
      return {
        action: 'payment_succeeded',
        data: { customerId: inv.customer, amount: inv.amount_paid },
      };
    }
    case 'invoice.payment_failed': {
      const inv = event.data.object as Stripe.Invoice;
      return {
        action: 'payment_failed',
        data: { customerId: inv.customer, amount: inv.amount_due },
      };
    }
    default:
      return { action: 'unhandled', data: { type: event.type } };
  }
}

/**
 * Estimate monthly bill for a given usage (for the /api/billing/estimate endpoint).
 */
export function estimateMonthlyBill(
  plan: EcosPlan,
  usage: {
    apiCalls: number;
    telemetryRecords: number;
    aiInferences: number;
  },
): { plan: string; basePrice: number; usageFees: number; total: number } {
  const basePrices: Record<EcosPlan, number> = {
    free: 0,
    pro: 299,       // $299/mo
    enterprise: 999, // $999/mo base
  };
  // Overage rates (per 1000 units)
  const limits = ECOS_PLANS[plan];
  const overageApiCalls = Math.max(
    0,
    usage.apiCalls - limits.apiCallsPerMonth,
  );
  const usageFees = (overageApiCalls / 1000) * 0.01 // $0.01 per 1000 API calls over limit
    + (usage.aiInferences / 1000) * 0.50;           // $0.50 per 1000 AI inferences

  const base = basePrices[plan];
  return {
    plan: ECOS_PLANS[plan].name,
    basePrice: base,
    usageFees: Math.round(usageFees * 100) / 100,
    total: Math.round((base + usageFees) * 100) / 100,
  };
}

export default {
  stripe,
  ECOS_PLANS,
  USAGE_EVENTS,
  getOrCreateCustomer,
  createSubscription,
  recordUsage,
  createBillingPortalSession,
  constructWebhookEvent,
  processWebhookEvent,
  estimateMonthlyBill,
};
