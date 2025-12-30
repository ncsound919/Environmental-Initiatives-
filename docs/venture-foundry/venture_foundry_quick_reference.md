# Venture Foundry: Quick Reference

**One-page guide for quick review of key metrics, tech stack, and implementation overview.**

---

## 🎯 What is Venture Foundry?

A gamified Web3 platform that transforms ideas into revenue-generating products through quest-based collaboration. Contributors earn equity + perpetual royalties.

**Core Loop:**
1. Founders post ideas → Codex Engine scores them
2. GO ideas fracture into quests
3. Contributors claim and complete quests
4. Smart contracts pay tokens + vest equity
5. Products launch on marketplace
6. Sales distribute as royalties to all contributors

---

## 📊 The 6 Codex Metrics

| Metric | Threshold | What It Measures | Formula Summary |
|--------|-----------|------------------|-----------------|
| **Trueness (T)** | ≥0.60 | Vision clarity vs. noise | S / (S + N + ε) |
| **Flow (F)** | ≥0.55 | Team velocity vs. drag | V / (V + D + ε) |
| **PCS** | ≥0.62 | Market demand + talent fit | √(MD × TA) |
| **RPS** | ≥0.50 | Revenue potential vs. risk | RP / (RP + ER + ε) |
| **CU** | ≥0.50 | Team capacity vs. required | AC / RC |
| **Tap10** | - | Top business levers | Ranked list (1-10) |

**Verdict Logic:**
- **ALL** metrics ≥ threshold → **GO** (proceed to quest fracturing)
- **ANY** metric < threshold → **NO_GO** (de-risking quests recommended)

---

## 💰 Revenue Model

**Every $100 marketplace sale:**
```
├─ $60 → Contributors (royalties, split by equity %)
├─ $15 → Platform operations
├─ $15 → Founder/Quest-giver
└─ $10 → Reinvestment pool
```

**Platform Revenue Streams:**
1. Marketplace fees (15% of sales)
2. Quest listing fees ($50-$500 optional)
3. Premium subscriptions ($29/month for analytics)
4. White-label licensing (custom pricing)

---

## 🏗️ Tech Stack

### Frontend
- **Framework:** React + Next.js (TypeScript)
- **Styling:** TailwindCSS
- **State:** React Query + Zustand
- **Web3:** RainbowKit + Wagmi + Viem
- **Hosting:** Vercel

### Backend
- **API:** NestJS (Node.js) + FastAPI (Python)
- **Database:** PostgreSQL + Prisma ORM
- **Cache:** Redis
- **Queue:** Bull (for async jobs)
- **Hosting:** Railway / Fly.io

### Blockchain
- **Network:** Polygon (mainnet + Mumbai testnet)
- **Language:** Solidity 0.8.20+
- **Framework:** Hardhat
- **Libraries:** OpenZeppelin (ERC20, AccessControl, ReentrancyGuard)

### Integrations
- **Payments:** Stripe + Circle USDC
- **Storage:** IPFS (files) + PostgreSQL (metadata)
- **Auth:** JWT + WalletConnect
- **Notifications:** SendGrid (email) + Discord webhooks
- **Analytics:** PostHog

---

## 🔐 Equity & Vesting

### Token Payout (Upon Quest Completion)
- **70% immediate:** Paid instantly as ECOS tokens
- **30% vested:** Linear unlock over 12 months

### Company Equity (Traditional 4-year vesting)
- **Year 1:** 0% until month 12, then 25% cliff
- **Years 2-4:** Remaining 75% vests monthly (2.0833%/month)

### Example: $500 ECOS + 0.5% Equity Quest Reward

**Tokens:**
- Day 1: Receive $350 ECOS (70%)
- Months 1-12: $12.50/month (30% vested)

**Equity:**
- Months 1-11: 0%
- Month 12: 0.125% (first cliff)
- Months 13-48: 0.0104167%/month

**Royalties (perpetual):**
- Product sells $10K/month
- 60% to contributors = $6K
- Your 0.5% equity = $30/month forever

---

## 🗂️ Database Schema (Key Tables)

```sql
users           → id, wallet_address, email, reputation_level, total_earned_usd
ideas           → id, founder_id, title, codex_scores (JSON), verdict, status
quests          → id, idea_id, title, token_reward, equity_percentage, status
quest_applications → id, quest_id, contributor_id, proposal_text, status
equity_stakes   → id, idea_id, contributor_id, percentage, vested_percentage
products        → id, idea_id, name, price_usd, total_revenue_usd
transactions    → id, product_id, buyer_id, amount_usd, tx_hash
```

---

## 🎮 Gamification Features

### Reputation System
**Levels 1-10** based on quest completions:
- **Level 1:** 0-99 points (Beginner quests only)
- **Level 3:** 300-699 points (All quest difficulties)
- **Level 5:** 1500+ points (Can propose quests, early access)
- **Level 10:** 40K+ points (DAO voting, 1.25x token multiplier)

**Points Earned:**
```
Points = Quest_Difficulty × Quality_Multiplier × On_Time_Bonus

Quest_Difficulty: 1-5 (Beginner to Advanced)
Quality_Multiplier: 1.0 (acceptable) to 2.0 (excellent)
On_Time_Bonus: 1.2 (early), 1.0 (on time), 0.8 (late)
```

### Badges
- **Polymath:** Complete quests in 5+ different domains
- **Speedrunner:** Average <14 days per quest
- **Trusted:** Reach Level 20 reputation
- **Founding 50:** First 50 platform users (exclusive NFT)

### Seasons
- **Quarterly themes:** "Q1 Light Quest", "Summer of Sound"
- **Bonus multipliers:** 10-20% extra tokens during season
- **Exclusive NFT rewards:** Collectible for top performers

---

## 📅 90-Day Launch Timeline

| Phase | Weeks | Key Milestone | Success Metric |
|-------|-------|---------------|----------------|
| **Foundation** | 1-4 | Quest board + marketplace + contracts | 3 live quests, first dev onboarded |
| **Alpha** | 5-8 | Codex integration, 50 users, 5 products | $2K revenue, 50% retention |
| **Beta** | 9-12 | Cross-domain quests, DAO voting | $10K revenue, 200+ contributors |

### Week 1: Infrastructure
- Monorepo setup (Nx/Turborepo)
- PostgreSQL + Redis deployment
- Smart contracts on Mumbai testnet
- CI/CD pipeline

### Week 2: Core Features
- Quest board UI
- User authentication (wallet)
- Quest CRUD endpoints
- Basic marketplace

### Week 3: Codex Engine
- Python scoring service
- 6-metric implementation
- Score display UI
- De-risking suggestions

### Week 4: Payments
- Stripe integration
- Smart contract payout testing
- Download delivery (IPFS)
- End-to-end test

### Weeks 5-8: Alpha Launch
- Recruit "Founding 50" contributors
- Launch 10+ real quests
- Ship first 5 products
- Implement gamification (leaderboards, badges)

### Weeks 9-12: Beta Expansion
- Cross-domain quests (code + music + art)
- DAO governance (Snapshot voting)
- Partner portal (white-label)
- Marketing campaign → 200+ users

---

## 🔍 Key Formulas (At a Glance)

### Trueness
```
T = Signal / (Signal + Noise + 0.01)
Signal = Weighted sum of clarity factors
Noise = Penalty for vague/missing/contradictory content
```

### Flow
```
F = Velocity / (Velocity + Drag + 0.01)
Velocity = Team skills + clear milestones + budget
Drag = Bottlenecks + unclear handoffs + conflicts
```

### PCS
```
PCS = √(Market_Demand × Talent_Availability)
Market_Demand = Search volume + competitor analysis + pain severity
Talent_Availability = Skill frequency + completion rate + domain maturity
```

### RPS
```
RPS = Revenue_Potential / (Revenue_Potential + Execution_Risk + 0.01)
Revenue_Potential = Market size + pricing power + recurring model
Execution_Risk = Complexity + regulatory + unvalidated assumptions
```

### CU (Capacity Utilization)
```
CU = Available_Hours / (Required_Hours × 1.5)
If CU < 0.5 → Team overcommitted (FAIL)
If 0.5 ≤ CU ≤ 1.0 → Ideal range (PASS)
If CU > 1.0 → Excess capacity (PASS, but underutilized)
```

---

## 🚨 Legal Compliance Checklist

> **⚠️ CRITICAL:** Do NOT launch without professional securities counsel review.

**Required Steps:**
- [ ] Engage securities attorney (Week 0, before any implementation)
- [ ] Conduct Howey Test analysis on token + equity structure
- [ ] Determine SEC registration vs. exemption strategy (Reg D, Reg A+)
- [ ] Establish KYC/AML procedures
- [ ] Draft contributor agreements (classification, vesting, tax withholding)
- [ ] Set up cap table management system
- [ ] Implement accredited investor verification (for equity)
- [ ] Create disclosure documents (risks, terms, privacy policy)
- [ ] Ongoing regulatory monitoring (SEC, FinCEN, state securities boards)

**Jurisdictional Considerations:**
- US: Securities Act of 1933, Investment Advisers Act
- EU: MiFID II, GDPR
- International: Consult local counsel for each contributor's jurisdiction

---

## 📈 Financial Projections (Year 1)

| Scenario | Q1 | Q2 | Q3 | Q4 | Annual |
|----------|-----|------|------|------|---------|
| **Optimistic** | $10K | $50K | $150K | $400K | $610K |
| **Base Case** | $5K | $20K | $80K | $300K | $405K |
| **Conservative** | $2K | $8K | $30K | $150K | $190K |

**Base Case Assumptions:**
- 200 active contributors by Q4
- 50+ products on marketplace by Q4
- Avg product revenue: $2K/month (Q4)
- Platform net revenue: ~12% of marketplace sales
- Breakeven: Month 12-18 depending on growth

---

## 🎯 Success Metrics (Month 12)

**User Metrics:**
- 500+ registered contributors
- 100+ completed quests
- 50+ products on marketplace
- 50%+ contributor retention rate

**Financial Metrics:**
- $500K+ annual marketplace revenue
- $60K platform net revenue (12% of sales)
- 5+ viral success stories
- Approaching operational breakeven

**Platform Metrics:**
- DAO governance active (10+ proposals)
- First white-label partner signed
- 95%+ uptime
- <2 second average API response time

---

## 🛠️ Smart Contract Addresses (Mainnet - TBD)

**Polygon Network:**
```
ECOSToken:               0x... (ERC20)
QuestRewardDistributor:  0x... (Vesting + payouts)
EquityVault:             0x... (Equity management)
RoyaltyDistributor:      0x... (Marketplace sales)
```

**Mumbai Testnet (Active):**
```
ECOSToken:               0x... (Test tokens)
QuestRewardDistributor:  0x... (Testing vesting)
```

Get test tokens: [Mumbai Faucet](https://faucet.polygon.technology/)

---

## 🔗 Key Links

**Documentation:**
- Full Rundown: `/docs/venture-foundry/venture_foundry_rundown.md`
- Technical Blueprint: `/docs/venture-foundry/foundry_blueprint.md`
- Executive Summary: `/Executive_Summary.md`

**APIs (When Live):**
- Quest Board: `https://quests.venturefoundry.io`
- Marketplace: `https://marketplace.venturefoundry.io`
- API Gateway: `https://api.venturefoundry.io`
- API Docs: `https://api.venturefoundry.io/docs`

**Community:**
- Discord: TBD
- Twitter: TBD
- GitHub: github.com/ncsound919/Environmental-Initiatives-

---

## 🤔 Common Questions

**Q: How is this different from freelance platforms?**  
A: Contributors get equity + perpetual royalties, not just one-time payments. You own part of what you build.

**Q: Why blockchain/tokens instead of traditional payments?**  
A: Instant, automated, trustless distribution. No lawyers, no paperwork delays, global accessibility.

**Q: What if a product doesn't sell?**  
A: Quest rewards are guaranteed upon completion regardless of sales. Royalties are a bonus.

**Q: Can contributors sell their equity?**  
A: Yes, after vesting completes (subject to securities laws and platform terms).

**Q: What's the path to profitability?**  
A: Platform profitable at ~$50K/month marketplace revenue (15% fee → $7.5K/month vs. ~$5-8K operating costs).

---

## 📞 Next Steps

**For Founders/Stakeholders:**
1. **Engage legal counsel** (securities attorney specializing in Web3)
2. Review full documentation
3. Decide: Build in-house vs. agency
4. Assemble team (product, engineering, legal, marketing)

**For Developers:**
1. Review Technical Blueprint
2. Clone starter repo (when available)
3. Set up local environment
4. Contribute to first quests

**For Contributors:**
1. Join Discord community (when live)
2. Complete profile + skill assessment
3. Browse quest board
4. Apply to first quest

---

## 🔐 Security

**Audits Required Before Mainnet:**
- [ ] Smart contract audit (Trail of Bits, OpenZeppelin, etc.)
- [ ] Penetration testing (API + frontend)
- [ ] Code review (internal + external)
- [ ] Legal compliance review (securities counsel)

**Bug Bounty Program (Post-Launch):**
- Critical: Up to $50K ECOS
- High: Up to $10K ECOS
- Medium: Up to $2K ECOS
- Low: Up to $500 ECOS

---

**Version:** 1.0  
**Last Updated:** December 30, 2024  
**Status:** Quick Reference Guide  
**License:** Proprietary - RegenCity Ecosystem

---

## 📝 Cheat Sheet

**Codex Thresholds:** T≥0.60, F≥0.55, PCS≥0.62, RPS≥0.50, CU≥0.50  
**Token Split:** 70% immediate, 30% vested (12 months)  
**Equity Vesting:** 4 years, 1-year cliff  
**Royalty Split:** 60% contributors, 15% platform, 15% founder, 10% reinvest  
**Reputation Levels:** 1-10 (100 pts each until L5, then exponential)  
**Platform Fee:** 15% of marketplace sales  
**Tech Stack:** React+Next, NestJS+FastAPI, PostgreSQL, Polygon, Stripe  
**Timeline:** 4 weeks MVP, 8 weeks Alpha, 12 weeks Beta  
**Success Metric:** 500 users, $500K ARR by Month 12
