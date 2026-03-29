const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json() as Promise<T>;
}

// Challenges
export const challengesApi = {
  list: () => apiFetch<Challenge[]>('/challenges'),
  get: (id: string) => apiFetch<Challenge>(`/challenges/${id}`),
  submit: (id: string, body: SubmissionBody) =>
    apiFetch<Submission>(`/challenges/${id}/submit`, { method: 'POST', body: JSON.stringify(body) }),
  leaderboard: (id: string) => apiFetch<LeaderboardEntry[]>(`/challenges/${id}/leaderboard`),
  stats: () => apiFetch<ChallengeStats>('/challenges/stats/overview'),
};

// Membership
export const membershipApi = {
  tiers: () => apiFetch<MembershipTier[]>('/membership/tiers'),
  subscribe: (body: SubscribeBody) =>
    apiFetch<Subscription>('/membership/subscribe', { method: 'POST', body: JSON.stringify(body) }),
  status: (userId: string) => apiFetch<MemberStatus>(`/membership/status/${userId}`),
  cancel: (subId: string) =>
    apiFetch<void>(`/membership/cancel/${subId}`, { method: 'DELETE' }),
  revenue: () => apiFetch<MembershipRevenue>('/membership/revenue/summary'),
};

// Marketplace
export const marketplaceApi = {
  listings: () => apiFetch<Listing[]>('/marketplace/listings'),
  get: (id: string) => apiFetch<Listing>(`/marketplace/listings/${id}`),
  create: (body: CreateListingBody) =>
    apiFetch<Listing>('/marketplace/listings', { method: 'POST', body: JSON.stringify(body) }),
  purchase: (id: string, body: PurchaseBody) =>
    apiFetch<Order>(`/marketplace/listings/${id}/purchase`, { method: 'POST', body: JSON.stringify(body) }),
  stats: () => apiFetch<MarketplaceStats>('/marketplace/stats/overview'),
};

// Gamification
export const gamificationApi = {
  profile: (userId: string) => apiFetch<GamificationProfile>(`/gamification/profile/${userId}`),
  addXp: (body: XpBody) =>
    apiFetch<XpResult>('/gamification/xp/add', { method: 'POST', body: JSON.stringify(body) }),
  leaderboard: () => apiFetch<LeaderboardEntry[]>('/gamification/leaderboard'),
  quests: (userId: string) => apiFetch<Quest[]>(`/gamification/quests/${userId}`),
  levels: () => apiFetch<Level[]>('/gamification/levels'),
  stats: () => apiFetch<GamificationStats>('/gamification/stats/overview'),
};

// DIY Kits
export const diyKitsApi = {
  list: () => apiFetch<DiyKit[]>('/kits'),
  get: (id: string) => apiFetch<DiyKit>(`/kits/${id}`),
  order: (id: string, body: KitOrderBody) =>
    apiFetch<KitOrder>(`/kits/${id}/order`, { method: 'POST', body: JSON.stringify(body) }),
  logBuild: (id: string, body: BuildLogBody) =>
    apiFetch<BuildLog>(`/kits/${id}/build-log`, { method: 'POST', body: JSON.stringify(body) }),
  stats: () => apiFetch<KitStats>('/kits/stats/overview'),
};

// Type stubs (expand as needed)
export type Challenge = Record<string, unknown>;
export type Submission = Record<string, unknown>;
export type SubmissionBody = Record<string, unknown>;
export type LeaderboardEntry = Record<string, unknown>;
export type ChallengeStats = Record<string, unknown>;
export type MembershipTier = Record<string, unknown>;
export type SubscribeBody = Record<string, unknown>;
export type Subscription = Record<string, unknown>;
export type MemberStatus = Record<string, unknown>;
export type MembershipRevenue = Record<string, unknown>;
export type Listing = Record<string, unknown>;
export type CreateListingBody = Record<string, unknown>;
export type PurchaseBody = Record<string, unknown>;
export type Order = Record<string, unknown>;
export type MarketplaceStats = Record<string, unknown>;
export type GamificationProfile = Record<string, unknown>;
export type XpBody = Record<string, unknown>;
export type XpResult = Record<string, unknown>;
export type Quest = Record<string, unknown>;
export type Level = Record<string, unknown>;
export type GamificationStats = Record<string, unknown>;
export type DiyKit = Record<string, unknown>;
export type KitOrderBody = Record<string, unknown>;
export type KitOrder = Record<string, unknown>;
export type BuildLogBody = Record<string, unknown>;
export type BuildLog = Record<string, unknown>;
export type KitStats = Record<string, unknown>;
