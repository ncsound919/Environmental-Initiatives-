# Venture Foundry Documentation

This directory contains comprehensive documentation for the **Venture Foundry Engine**, a gamified Web3 platform designed to transform ideas into revenue-generating assets through collaborative quest completion.

---

## 📚 Documents in This Directory

### 1. [venture_foundry_rundown.md](./venture_foundry_rundown.md)
**Full Platform Breakdown (5K+ words)**

Complete guide covering:
- Platform overview and value proposition
- User journeys (Founder, Contributor, End User)
- Business logic and revenue model
- Technical architecture and stack
- Implementation guide (Phases 1-3)
- FAQ and key terms

**Read Time:** ~30 minutes  
**Audience:** Technical teams, product managers, stakeholders

---

### 2. [foundry_blueprint.md](./foundry_blueprint.md)
**Technical Deep-Dive (8K+ words)**

Detailed specification including:
- Mathematical foundations for all 6 Codex metrics
- Algorithm specifications (quest recommendation, reputation)
- Code architecture (backend, frontend, smart contracts)
- Smart contract design with Solidity examples
- Week-by-week implementation timeline
- Testing strategy and security considerations

**Read Time:** ~45 minutes  
**Audience:** Developers, architects, technical leads

---

### 3. [venture_foundry_quick_reference.md](./venture_foundry_quick_reference.md)
**One-Page Cheat Sheet (3K words)**

Quick reference containing:
- 6 Codex metrics at a glance
- Revenue model summary
- Tech stack overview
- Equity & vesting structure
- Database schema
- 90-day launch timeline
- Key formulas
- Financial projections

**Read Time:** ~5 minutes  
**Audience:** Everyone (quick lookup)

---

## 🔗 Related Documentation

### Root Directory Files
- **[Executive_Summary.md](../../Executive_Summary.md)** - 3-page executive summary for decision-makers
- **[README.md](../../README.md)** - Main project README with Venture Foundry overview
- **[DOCS_INDEX.md](../../DOCS_INDEX.md)** - Complete documentation index

---

## 🎯 The Codex Engine: 6 Metrics

The Codex Engine evaluates every idea submission using 6 metrics. **ALL** must pass for a GO verdict:

| Metric | Threshold | What It Measures |
|--------|-----------|------------------|
| **Trueness (T)** | ≥0.60 | Vision clarity vs. noise ratio |
| **Flow (F)** | ≥0.55 | Team velocity vs. resource drag |
| **PCS** | ≥0.62 | Product-channel-skill fit (market + talent) |
| **RPS** | ≥0.50 | Revenue potential vs. execution risk |
| **CU** | ≥0.50 | Team capacity vs. required capacity |
| **Tap10** | - | Top 10 critical business levers |

---

## 🚀 Implementation Files (To Be Added)

The following files are referenced in the documentation but will be added separately:

### codex_engine.py
Python implementation of the 6-metric scoring algorithm.
- Located: `docs/venture-foundry/codex_engine.py`
- Purpose: Score ideas and generate GO/NO_GO verdicts
- Usage: Can be imported as a module or run standalone

### Titan_Tightened_Formulas.csv
Mathematical specifications for all Codex metrics.
- Located: `docs/venture-foundry/Titan_Tightened_Formulas.csv`
- Purpose: Reference for metric calculations with bounds/thresholds
- Format: CSV with columns for metric name, formula, weights, thresholds

### PickScore_Config.csv
Gate rules and fail codes for the Codex Engine.
- Located: `docs/venture-foundry/PickScore_Config.csv`
- Purpose: Configuration for pass/fail logic and suggestion generation
- Format: CSV with gate conditions and corresponding actions

---

## 💡 Getting Started

### For Decision-Makers
1. Start with [Executive_Summary.md](../../Executive_Summary.md) (10 min)
2. Review the business case and financials
3. Understand legal/compliance requirements
4. Decide on next steps (legal review, team assembly)

### For Product/Business Teams
1. Read [venture_foundry_rundown.md](./venture_foundry_rundown.md) (30 min)
2. Understand user journeys and business logic
3. Review revenue model and economics
4. Explore implementation phases

### For Developers
1. Review [foundry_blueprint.md](./foundry_blueprint.md) (45 min)
2. Study the technical architecture
3. Examine smart contract examples
4. Plan development approach

### For Quick Reference
1. Keep [venture_foundry_quick_reference.md](./venture_foundry_quick_reference.md) handy
2. Use it for metric thresholds, formulas, tech stack
3. Reference during development

---

## ⚠️ Legal Notice

**IMPORTANT:** The token and equity distribution mechanisms described in these documents may constitute securities offerings subject to federal and state securities laws.

**Required before implementation:**
1. Engage securities counsel specializing in Web3/digital assets
2. Conduct Howey Test analysis
3. Determine SEC registration vs. exemption strategy
4. Establish KYC/AML compliance procedures
5. Draft proper disclosure documents
6. Set up investor accreditation verification

**Do not implement any token or equity distribution without professional legal guidance.**

---

## 📈 Key Numbers

**Platform Economics:**
- Revenue split: 60% contributors, 15% platform, 15% founder, 10% reinvest
- Token payout: 70% immediate, 30% vested over 12 months
- Equity vesting: 4 years with 1-year cliff
- Platform fee: 15% of marketplace sales

**Year 1 Targets (Base Case):**
- 500+ active contributors
- 50+ products on marketplace
- $500K+ annual marketplace revenue
- Approaching profitability by Month 12-18

**90-Day Launch:**
- Weeks 1-4: Foundation (MVP)
- Weeks 5-8: Alpha (50 users, 5 products)
- Weeks 9-12: Beta (200 users, $10K revenue)

---

## 🛠️ Tech Stack Summary

**Frontend:** React + Next.js + TailwindCSS + RainbowKit  
**Backend:** NestJS + FastAPI + PostgreSQL + Redis  
**Blockchain:** Solidity + Hardhat + Polygon + OpenZeppelin  
**Payments:** Stripe + Circle USDC  
**Storage:** IPFS + PostgreSQL  
**Hosting:** Vercel + Railway/Fly.io

---

## 📞 Questions?

For questions about this documentation:
- Review the FAQ sections in each document
- Check the [DOCS_INDEX.md](../../DOCS_INDEX.md) for related resources
- Open a GitHub issue for clarifications

---

**Version:** 1.0  
**Last Updated:** December 30, 2024  
**Status:** Blueprint/Planning Phase  
**Next Steps:** Legal review, then Phase 1 implementation
