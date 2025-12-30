# Venture Foundry: Technical Blueprint

**Deep-dive specification with mathematical formulas, code examples, and detailed implementation timeline.**

---

## Table of Contents

1. [Mathematical Foundations](#mathematical-foundations)
2. [Algorithm Specifications](#algorithm-specifications)
3. [Code Architecture](#code-architecture)
4. [Smart Contract Design](#smart-contract-design)
5. [Implementation Timeline](#implementation-timeline)
6. [Testing Strategy](#testing-strategy)
7. [Security Considerations](#security-considerations)

---

## Mathematical Foundations

### Codex Engine: Formal Specifications

The Codex Engine uses 6 normalized metrics (0-1 scale) to evaluate idea viability. Each metric has a specific threshold, and ALL must pass for a GO verdict.

#### Metric 1: Trueness (T)

**Definition:** Measures signal-to-noise ratio in idea clarity.

**Mathematical Formula:**
```
T = S / (S + N + ε)

Where:
  S = Σ(wi × si) for i ∈ [1, n] signal factors
  N = Σ(pj × nj) for j ∈ [1, m] noise penalties
  ε = 0.01 (smoothing constant to prevent division by zero)

Signal factors (wi = weight, si = score 0-1):
  s1 = problem_statement_clarity (w1 = 0.30)
  s2 = target_user_specificity (w2 = 0.30)
  s3 = success_criteria_quantified (w3 = 0.20)
  s4 = timeline_realism (w4 = 0.20)

Noise penalties (pj = penalty weight, nj = count):
  n1 = vague_language_count (p1 = -0.10 per instance)
  n2 = missing_key_fields (p2 = -0.20 per field)
  n3 = contradictory_statements (p3 = -0.30 per conflict)

Normalization:
  If T < 0, set T = 0
  If T > 1, set T = 1

Threshold: T ≥ 0.60
```

**Example Calculation:**
```
Idea: "Build a VST plugin for synthwave music"

Signal scores:
  s1 = 0.85 (clear problem: "producers need synthwave generation")
  s2 = 0.90 (specific user: "bedroom producers on Ableton/FL Studio")
  s3 = 0.70 (quantified: "generate 30-second loops, <5% cpu usage")
  s4 = 0.65 (realistic: "12-week timeline with 2 devs")

S = (0.30 × 0.85) + (0.30 × 0.90) + (0.20 × 0.70) + (0.20 × 0.65)
S = 0.255 + 0.270 + 0.140 + 0.130 = 0.795

Noise counts:
  n1 = 2 vague phrases ("innovative", "cutting-edge")
  n2 = 1 missing field (no competitive analysis)
  n3 = 0 contradictions

N = (2 × -0.10) + (1 × -0.20) + (0 × -0.30)
N = -0.20 - 0.20 + 0 = -0.40

T = 0.795 / (0.795 + 0.40 + 0.01) = 0.795 / 1.205 ≈ 0.66

Result: T = 0.66 ≥ 0.60 ✅ PASS
```

---

#### Metric 2: Flow (F)

**Definition:** Measures team velocity potential vs. resource drag.

**Mathematical Formula:**
```
F = V / (V + D + ε)

Where:
  V = Σ(wi × vi) for i ∈ [1, k] velocity factors
  D = Σ(pj × dj) for j ∈ [1, l] drag penalties
  ε = 0.01

Velocity factors:
  v1 = team_skill_match (w1 = 0.40)
  v2 = milestone_clarity (w2 = 0.30)
  v3 = budget_adequacy (w3 = 0.30)

Drag penalties:
  d1 = dependency_bottlenecks (p1 = -0.20 per blocker)
  d2 = unclear_handoffs (p2 = -0.15 per gap)
  d3 = resource_conflicts (p3 = -0.25 per conflict)

Threshold: F ≥ 0.55
```

**Skill Match Sub-Formula:**
```
team_skill_match = min(1.0, Σ(contributor_skill_level / required_skill_level) / num_skills)

Where:
  contributor_skill_level ∈ [1, 10] (1=beginner, 10=expert)
  required_skill_level ∈ [1, 10]
  num_skills = number of distinct skills needed

If no contributor assigned yet, use platform average for domain (e.g., 6.5 for Python devs)
```

---

#### Metric 3: PCS (Product-Channel-Skill Fit)

**Definition:** Geometric mean of market demand and talent availability.

**Mathematical Formula:**
```
PCS = √(MD × TA)

Where:
  MD = Market Demand score (0-1)
  TA = Talent Availability score (0-1)

Market Demand:
  MD = Σ(wi × mi) for i ∈ [1, 3]
  
  m1 = search_volume_normalized (w1 = 0.40)
  m2 = competitor_health (w2 = 0.30)
  m3 = pain_severity (w3 = 0.30)

  search_volume_normalized = log10(monthly_searches + 1) / log10(1000000)
    (1M searches/month = 1.0, <10 searches/month ≈ 0.0)

  competitor_health = 0.5 + (num_competitors - 5) / 20
    (Sweet spot: 3-7 competitors → 0.4-0.6 range)
    (Too many → oversaturated, too few → no market validation)

  pain_severity = founder_self_assessment (1-10) / 10

Talent Availability:
  TA = Σ(wi × ti) for i ∈ [1, 3]

  t1 = skill_frequency_on_platform (w1 = 0.50)
  t2 = historical_completion_rate (w2 = 0.30)
  t3 = domain_maturity (w3 = 0.20)

  skill_frequency_on_platform = num_contributors_with_skill / total_contributors

  historical_completion_rate = completed_quests_in_domain / total_quests_in_domain

  domain_maturity = years_since_domain_launch / 10
    (New domain like "AI Music" → 0.2, Established like "Web Dev" → 1.0)

Threshold: PCS ≥ 0.62
```

**Example:**
```
Idea: "AI Synthwave VST"

Market Demand:
  search_volume: ~5,000/month for "synthwave vst"
    → log10(5001) / log10(1000000) ≈ 3.7 / 6 ≈ 0.62

  competitor_health: 4 existing VSTs (Synthwave Pro, Neon Dreams, etc.)
    → 0.5 + (4 - 5) / 20 = 0.5 - 0.05 = 0.45

  pain_severity: Founder rates as 8/10
    → 0.80

  MD = (0.40 × 0.62) + (0.30 × 0.45) + (0.30 × 0.80)
     = 0.248 + 0.135 + 0.240 = 0.623

Talent Availability:
  skill_frequency: 45 Python + audio DSP devs out of 500 total
    → 45/500 = 0.09

  historical_completion: 12 completed music quests out of 15 posted
    → 12/15 = 0.80

  domain_maturity: AI music tools ≈ 3 years old
    → 3/10 = 0.30

  TA = (0.50 × 0.09) + (0.30 × 0.80) + (0.20 × 0.30)
     = 0.045 + 0.240 + 0.060 = 0.345

PCS = √(0.623 × 0.345) = √0.215 ≈ 0.46

Result: PCS = 0.46 < 0.62 ❌ FAIL

Reason: Talent pool too small. Suggested de-risk action:
  → "Post a training quest first: 'Learn Audio DSP Basics' to expand contributor pool"
```

---

#### Metric 4: RPS (Revenue Priority Score)

**Definition:** Revenue potential vs. execution risk ratio.

**Mathematical Formula:**
```
RPS = RP / (RP + ER + ε)

Where:
  RP = Revenue Potential (0-1)
  ER = Execution Risk (0-1, higher = riskier)
  ε = 0.01

Revenue Potential:
  RP = Σ(wi × ri) for i ∈ [1, 3]

  r1 = market_size_normalized (w1 = 0.40)
  r2 = pricing_power (w2 = 0.30)
  r3 = recurring_revenue_factor (w3 = 0.30)

  market_size_normalized = log10(TAM_in_USD + 1) / log10(1000000000)
    ($1B TAM = 1.0, $1M TAM ≈ 0.6, $10K TAM ≈ 0.4)

  pricing_power = min(1.0, suggested_price / median_competitor_price)
    (Can charge 2x competitor → 1.0, Must charge 0.5x → 0.5)

  recurring_revenue_factor:
    0.2 = one-time purchase
    0.5 = upgrade path (v2, v3)
    0.8 = subscription (monthly/yearly)
    1.0 = usage-based (pay per generation, API calls)

Execution Risk:
  ER = Σ(pj × ej) for j ∈ [1, 3]

  e1 = technical_complexity (p1 = 0.30)
  e2 = regulatory_burden (p2 = 0.20)
  e3 = unvalidated_assumptions (p3 = 0.15)

  technical_complexity = num_hard_dependencies / 10
    (0 dependencies → 0.0, 5+ novel algorithms → 0.5+)

  regulatory_burden = num_compliance_requirements / 5
    (GDPR only → 0.2, GDPR + HIPAA + FDA → 0.6)

  unvalidated_assumptions = num_untested_hypotheses / 10

Threshold: RPS ≥ 0.50
```

---

#### Metric 5: CU (Capacity Utilization)

**Definition:** Available team capacity vs. required capacity.

**Mathematical Formula:**
```
CU = AC / RC

Where:
  AC = Available Capacity (total hours committable)
  RC = Required Capacity (estimated hours needed)

If CU > 1.0, team has excess capacity (good)
If 0.5 ≤ CU ≤ 1.0, team is appropriately loaded (ideal)
If CU < 0.5, team is overcommitted (fail)

Available Capacity:
  AC = Σ(contributor_hours_per_week × num_weeks_until_deadline)
  
  Include:
    - Founder committed hours
    - Accepted contributor hours
    - Budgeted outsourced hours (if applicable)

Required Capacity:
  RC = Σ(quest_estimated_hours) × overhead_multiplier

  overhead_multiplier = 1.5 (accounts for meetings, reviews, integration)

Threshold: CU ≥ 0.50
```

**Example:**
```
Project: AI Synthwave VST (12-week timeline)

Available Capacity:
  - Founder: 10 hours/week × 12 weeks = 120 hours
  - Dev 1: 20 hours/week × 12 weeks = 240 hours
  - Dev 2: 15 hours/week × 12 weeks = 180 hours
  - Designer: 8 hours/week × 12 weeks = 96 hours
  
  AC = 120 + 240 + 180 + 96 = 636 hours

Required Capacity:
  Quest breakdown:
    - ML engine: 180 hours
    - VST wrapper: 120 hours
    - UI design: 60 hours
    - Sound library: 40 hours
    - Testing: 80 hours
    - Documentation: 30 hours
  
  Total raw: 510 hours
  With 1.5x overhead: 510 × 1.5 = 765 hours

  RC = 765 hours

CU = 636 / 765 ≈ 0.83

Result: CU = 0.83 ≥ 0.50 ✅ PASS (but tight—only 17% buffer)

Warning: "Team has minimal slack. Consider extending deadline or reducing scope."
```

---

#### Metric 6: Tap10 (Top Business Levers)

**Definition:** Categorical ranking of the 10 most critical success factors.

**Formula:** Multi-attribute decision analysis (MADA)

```
For each lever L in [L1, L2, ..., L10]:
  Impact_Score[L] = Σ(wi × fi[L]) for i ∈ [1, k] factors

Factors (context-dependent):
  f1 = revenue_impact (w1 = 0.30)
  f2 = risk_reduction (w2 = 0.25)
  f3 = time_to_value (w3 = 0.20)
  f4 = resource_efficiency (w4 = 0.15)
  f5 = strategic_alignment (w5 = 0.10)

Each fi[L] scored 0-1 based on idea specifics.

Output: Ranked list of top 3-5 levers
```

**The 10 Levers:**
1. **Product Quality** - Core feature completeness, UX polish
2. **Marketing Reach** - Distribution channels, audience size
3. **Pricing Strategy** - Price point optimization, packaging
4. **Distribution Channel** - Platform choice (web, app stores, plugins)
5. **Team Velocity** - Development speed, agile practices
6. **Customer Support** - Onboarding, docs, help desk
7. **Brand Positioning** - Market differentiation, messaging
8. **Technical Infrastructure** - Scalability, reliability, performance
9. **Legal Compliance** - Licensing, privacy, regulatory
10. **Community Engagement** - User feedback loops, co-creation

**Example Output:**
```
Idea: "AI Synthwave VST"

Tap10 Analysis:
  1. Product Quality (0.92) - Critical: Sound quality must rival commercial VSTs
  2. Marketing Reach (0.78) - Important: Target YouTube producers, Splice
  3. Distribution Channel (0.71) - Important: VST marketplaces (Plugin Boutique, etc.)
  4. Team Velocity (0.65) - Moderate: 12-week timeline is aggressive
  5. Pricing Strategy (0.58) - Moderate: $49-$99 range competitive

Actionable Insights:
  - Allocate 40% budget to sound design quality
  - Partner with YouTube music channels for launches
  - Negotiate featured placement on Plugin Boutique
```

---

### Verdict Logic

**Algorithm:**
```python
def calculate_verdict(idea):
    # Calculate all 6 metrics
    T = calculate_trueness(idea)
    F = calculate_flow(idea)
    PCS = calculate_pcs(idea)
    RPS = calculate_rps(idea)
    CU = calculate_cu(idea)
    TAP10 = calculate_tap10(idea)
    
    # Check thresholds
    thresholds = {
        'T': 0.60,
        'F': 0.55,
        'PCS': 0.62,
        'RPS': 0.50,
        'CU': 0.50
    }
    
    failures = []
    for metric, threshold in thresholds.items():
        score = locals()[metric]  # Get variable by name
        if score < threshold:
            failures.append({
                'metric': metric,
                'score': score,
                'threshold': threshold,
                'gap': threshold - score
            })
    
    if len(failures) == 0:
        return {
            'verdict': 'GO',
            'message': 'All metrics passed. Proceed to quest fracturing.',
            'scores': {'T': T, 'F': F, 'PCS': PCS, 'RPS': RPS, 'CU': CU},
            'top_levers': TAP10[:5]
        }
    else:
        return {
            'verdict': 'NO_GO',
            'message': f'{len(failures)} metric(s) failed. De-risking quests recommended.',
            'scores': {'T': T, 'F': F, 'PCS': PCS, 'RPS': RPS, 'CU': CU},
            'failures': failures,
            'suggestions': generate_derisking_suggestions(failures)
        }

def generate_derisking_suggestions(failures):
    """Generate actionable next steps for each failed metric."""
    suggestions = []
    
    for fail in failures:
        if fail['metric'] == 'T':
            suggestions.append({
                'title': 'Clarify Vision',
                'quest': 'Create 1-page product spec with problem/solution/success metrics',
                'estimated_time': '2-4 hours',
                'budget': '$50 ECOS'
            })
        
        elif fail['metric'] == 'F':
            suggestions.append({
                'title': 'Build Milestone Roadmap',
                'quest': 'Define 4-6 week sprints with clear deliverables',
                'estimated_time': '4-6 hours',
                'budget': '$100 ECOS'
            })
        
        elif fail['metric'] == 'PCS':
            if fail['gap'] > 0.2:  # Large gap
                suggestions.append({
                    'title': 'Grow Talent Pool',
                    'quest': 'Create tutorial content to onboard new contributors in this domain',
                    'estimated_time': '1-2 weeks',
                    'budget': '$500 ECOS'
                })
            else:  # Small gap
                suggestions.append({
                    'title': 'Validate Market Demand',
                    'quest': 'Survey 50 target users, gather pre-orders',
                    'estimated_time': '1 week',
                    'budget': '$200 ECOS'
                })
        
        elif fail['metric'] == 'RPS':
            suggestions.append({
                'title': 'Build MVP First',
                'quest': 'Create simplified version to validate core assumption',
                'estimated_time': '3-4 weeks',
                'budget': '$1,000 ECOS'
            })
        
        elif fail['metric'] == 'CU':
            suggestions.append({
                'title': 'Recruit Co-Founder',
                'quest': 'Find technical co-founder to share workload (20+ hrs/week)',
                'estimated_time': '2-4 weeks',
                'budget': '$0 (equity only)'
            })
    
    return suggestions
```

---

## Algorithm Specifications

### Quest Recommendation Engine

**Purpose:** Match contributors to quests based on skills, history, and preferences.

**Algorithm:** Collaborative filtering + skill-based ranking

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class QuestRecommender:
    def __init__(self):
        self.contributor_profiles = {}  # {user_id: skill_vector}
        self.quest_requirements = {}     # {quest_id: skill_vector}
        self.interaction_matrix = None   # Sparse matrix of user-quest interactions
    
    def build_skill_vector(self, skills_dict):
        """
        Convert skills dict to fixed-length vector.
        
        Skills dict format:
          {'python': 8, 'react': 6, 'audio_dsp': 9, ...}
        
        Returns:
          numpy array of length 100 (covering all platform skills)
        """
        skill_order = self.get_canonical_skill_order()
        vector = np.zeros(len(skill_order))
        
        for skill, level in skills_dict.items():
            if skill in skill_order:
                idx = skill_order.index(skill)
                vector[idx] = level / 10.0  # Normalize to 0-1
        
        return vector
    
    def recommend_quests(self, user_id, top_n=10):
        """
        Recommend quests for a user.
        
        Combines:
          1. Skill match (cosine similarity)
          2. Collaborative filtering (users with similar history)
          3. Diversity (avoid recommending same domain repeatedly)
        """
        user_vector = self.contributor_profiles[user_id]
        
        # 1. Skill-based scores
        skill_scores = {}
        for quest_id, quest_vector in self.quest_requirements.items():
            # Cosine similarity between user skills and quest needs
            similarity = cosine_similarity(
                user_vector.reshape(1, -1),
                quest_vector.reshape(1, -1)
            )[0][0]
            
            # Penalty for under-qualification
            skill_gap = np.maximum(0, quest_vector - user_vector)
            gap_penalty = np.sum(skill_gap) * 0.1
            
            skill_scores[quest_id] = max(0, similarity - gap_penalty)
        
        # 2. Collaborative filtering scores
        cf_scores = self._collaborative_filtering_scores(user_id)
        
        # 3. Diversity bonus
        diversity_scores = self._diversity_scores(user_id)
        
        # Combine scores (weighted)
        final_scores = {}
        for quest_id in skill_scores.keys():
            final_scores[quest_id] = (
                0.50 * skill_scores.get(quest_id, 0) +
                0.30 * cf_scores.get(quest_id, 0) +
                0.20 * diversity_scores.get(quest_id, 0)
            )
        
        # Sort and return top N
        ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        return [quest_id for quest_id, score in ranked[:top_n]]
    
    def _collaborative_filtering_scores(self, user_id):
        """Find similar users and recommend quests they completed."""
        # Simplified version; production would use matrix factorization
        similar_users = self._find_similar_users(user_id, top_k=20)
        
        quest_scores = {}
        for similar_user, similarity_score in similar_users:
            completed_quests = self._get_completed_quests(similar_user)
            for quest_id in completed_quests:
                if quest_id not in quest_scores:
                    quest_scores[quest_id] = 0
                quest_scores[quest_id] += similarity_score
        
        # Normalize
        max_score = max(quest_scores.values()) if quest_scores else 1
        return {q: s/max_score for q, s in quest_scores.items()}
    
    def _diversity_scores(self, user_id):
        """Boost quests in domains user hasn't worked on recently."""
        recent_domains = self._get_recent_domains(user_id, last_n=5)
        domain_counts = {}
        for domain in recent_domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        quest_scores = {}
        for quest_id, quest_meta in self.quest_requirements.items():
            domain = quest_meta['domain']
            # Inverse frequency bonus
            quest_scores[quest_id] = 1.0 / (1 + domain_counts.get(domain, 0))
        
        return quest_scores
```

---

### Reputation System

**Purpose:** Assign contributor levels based on performance.

**Formula:**
```
Reputation_Points = Σ(Quest_Difficulty × Quality_Multiplier × On_Time_Bonus)

Where:
  Quest_Difficulty ∈ [1, 5] (Beginner=1, Advanced=5)
  
  Quality_Multiplier:
    1.0 = Acceptable (met minimum requirements)
    1.5 = Good (exceeded expectations)
    2.0 = Excellent (outstanding work, reusable for future quests)
  
  On_Time_Bonus:
    1.2 = Delivered early (>2 days before deadline)
    1.0 = On time
    0.8 = Late (but still delivered)

Level Thresholds:
  Level 1: 0-99 points
  Level 2: 100-299 points
  Level 3: 300-699 points
  Level 4: 700-1499 points
  Level 5: 1500-2999 points
  Level 6: 3000-5999 points
  Level 7: 6000-9999 points
  Level 8: 10000-19999 points
  Level 9: 20000-39999 points
  Level 10: 40000+ points
```

**Level Benefits:**
| Level | Badge | Quest Access | Token Multiplier | Max Equity/Quest |
|-------|-------|--------------|------------------|------------------|
| 1 | Novice | Beginner only | 1.0x | 0.5% |
| 2 | Apprentice | Beginner + Intermediate | 1.05x | 1.0% |
| 3 | Skilled | All difficulty levels | 1.10x | 2.0% |
| 4 | Expert | + Early access to new quests | 1.15x | 3.0% |
| 5 | Master | + Can propose own quests | 1.20x | 5.0% |
| 6+ | Legend | + DAO voting power | 1.25x+ | 10.0%+ |

---

## Code Architecture

### Backend Service Structure

```
backend/
├── apps/
│   ├── api-gateway/              # NestJS - Main API
│   │   ├── src/
│   │   │   ├── auth/             # JWT authentication
│   │   │   ├── users/            # User management
│   │   │   ├── quests/           # Quest CRUD
│   │   │   ├── ideas/            # Idea submission
│   │   │   ├── marketplace/      # Product listings
│   │   │   ├── payments/         # Stripe integration
│   │   │   └── websockets/       # Realtime updates
│   │   └── main.ts
│   │
│   └── codex-engine/             # Python FastAPI - Scoring
│       ├── main.py
│       ├── metrics/
│       │   ├── trueness.py
│       │   ├── flow.py
│       │   ├── pcs.py
│       │   ├── rps.py
│       │   ├── cu.py
│       │   └── tap10.py
│       └── recommender/
│           └── quest_recommender.py
│
├── packages/
│   ├── database/                 # Prisma schema + migrations
│   ├── contracts/                # Solidity smart contracts
│   ├── types/                    # Shared TypeScript types
│   └── utils/                    # Shared utilities
│
└── docker-compose.yml
```

### Frontend Application Structure

```
frontend/
├── apps/
│   ├── quest-board/              # Main quest browsing app
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   │   ├── index.tsx              # Quest list
│   │   │   │   ├── quest/[id].tsx         # Quest detail
│   │   │   │   └── submit-idea.tsx        # Idea submission
│   │   │   ├── components/
│   │   │   │   ├── QuestCard.tsx
│   │   │   │   ├── CodexScoreDisplay.tsx
│   │   │   │   └── ApplicationForm.tsx
│   │   │   └── hooks/
│   │   │       ├── useQuests.ts
│   │   │       └── useWallet.ts
│   │   └── next.config.js
│   │
│   ├── marketplace/              # Product marketplace
│   │   └── src/
│   │       ├── pages/
│   │       │   ├── index.tsx              # Product grid
│   │       │   ├── product/[id].tsx       # Product detail
│   │       │   └── checkout.tsx           # Purchase flow
│   │       └── components/
│   │           ├── ProductCard.tsx
│   │           └── ProvenanceDisplay.tsx
│   │
│   └── dashboard/                # Contributor/Founder dashboard
│       └── src/
│           ├── pages/
│           │   ├── my-quests.tsx          # Active quests
│           │   ├── earnings.tsx           # Revenue tracking
│           │   └── portfolio.tsx          # Equity holdings
│           └── components/
│               ├── VestingSchedule.tsx
│               └── RoyaltyChart.tsx
│
└── packages/
    ├── ui/                       # Shared React components
    └── web3/                     # Wallet connection logic
```

---

## Smart Contract Design

### Contract: QuestRewardDistributor

**Purpose:** Handle quest completion payouts with automatic vesting.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract QuestRewardDistributor is AccessControl, ReentrancyGuard {
    bytes32 public constant QUEST_MANAGER_ROLE = keccak256("QUEST_MANAGER_ROLE");
    
    IERC20 public ecosToken;
    
    struct VestingSchedule {
        address contributor;
        uint256 immediateAmount;   // 70% paid instantly
        uint256 vestedAmount;      // 30% vested over 12 months
        uint256 vestingStart;
        uint256 vestingDuration;   // 365 days
        uint256 claimed;
        bool revoked;
    }
    
    mapping(bytes32 => VestingSchedule) public schedules;
    
    event RewardGranted(
        bytes32 indexed questId,
        address indexed contributor,
        uint256 totalAmount,
        uint256 immediateAmount,
        uint256 vestedAmount
    );
    
    event VestedTokensClaimed(
        bytes32 indexed questId,
        address indexed contributor,
        uint256 amount
    );
    
    event VestingRevoked(
        bytes32 indexed questId,
        address indexed contributor,
        uint256 unvestedAmount
    );
    
    constructor(address _ecosToken) {
        ecosToken = IERC20(_ecosToken);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(QUEST_MANAGER_ROLE, msg.sender);
    }
    
    /**
     * @dev Grant reward to contributor upon quest completion
     * @param questId Unique identifier for the quest
     * @param contributor Address of the contributor
     * @param totalAmount Total token reward (100%)
     */
    function grantReward(
        bytes32 questId,
        address contributor,
        uint256 totalAmount
    ) external onlyRole(QUEST_MANAGER_ROLE) nonReentrant {
        require(schedules[questId].contributor == address(0), "Reward already granted");
        require(contributor != address(0), "Invalid contributor address");
        require(totalAmount > 0, "Amount must be positive");
        
        uint256 immediate = (totalAmount * 70) / 100;
        uint256 vested = totalAmount - immediate;
        
        schedules[questId] = VestingSchedule({
            contributor: contributor,
            immediateAmount: immediate,
            vestedAmount: vested,
            vestingStart: block.timestamp,
            vestingDuration: 365 days,
            claimed: 0,
            revoked: false
        });
        
        // Transfer immediate 70%
        require(
            ecosToken.transferFrom(msg.sender, contributor, immediate),
            "Immediate transfer failed"
        );
        
        emit RewardGranted(questId, contributor, totalAmount, immediate, vested);
    }
    
    /**
     * @dev Claim vested tokens
     * @param questId Quest identifier
     */
    function claimVested(bytes32 questId) external nonReentrant {
        VestingSchedule storage schedule = schedules[questId];
        require(msg.sender == schedule.contributor, "Not authorized");
        require(!schedule.revoked, "Vesting revoked");
        
        uint256 vested = calculateVestedAmount(questId);
        uint256 claimable = vested - schedule.claimed;
        require(claimable > 0, "Nothing to claim");
        
        schedule.claimed += claimable;
        
        require(
            ecosToken.transferFrom(
                address(this),
                msg.sender,
                claimable
            ),
            "Transfer failed"
        );
        
        emit VestedTokensClaimed(questId, msg.sender, claimable);
    }
    
    /**
     * @dev Calculate currently vested amount
     * @param questId Quest identifier
     * @return Amount of tokens vested so far
     */
    function calculateVestedAmount(bytes32 questId) public view returns (uint256) {
        VestingSchedule memory schedule = schedules[questId];
        
        if (schedule.revoked) {
            return schedule.claimed; // No new vesting after revocation
        }
        
        if (block.timestamp < schedule.vestingStart) {
            return 0;
        }
        
        uint256 elapsed = block.timestamp - schedule.vestingStart;
        
        if (elapsed >= schedule.vestingDuration) {
            return schedule.vestedAmount; // Fully vested
        }
        
        // Linear vesting
        return (schedule.vestedAmount * elapsed) / schedule.vestingDuration;
    }
    
    /**
     * @dev Revoke vesting (admin only, for violations)
     * @param questId Quest identifier
     */
    function revokeVesting(bytes32 questId)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        nonReentrant
    {
        VestingSchedule storage schedule = schedules[questId];
        require(!schedule.revoked, "Already revoked");
        
        uint256 vested = calculateVestedAmount(questId);
        uint256 unvested = schedule.vestedAmount - vested;
        
        schedule.revoked = true;
        
        // Return unvested tokens to treasury
        require(
            ecosToken.transfer(msg.sender, unvested),
            "Return transfer failed"
        );
        
        emit VestingRevoked(questId, schedule.contributor, unvested);
    }
}
```

---

### Contract: RoyaltyDistributor

**Purpose:** Automatically distribute marketplace sales to equity holders.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract RoyaltyDistributor is Ownable, ReentrancyGuard {
    IERC20 public paymentToken; // USDC or ECOS
    
    struct ProductRoyalties {
        address[] contributors;
        uint256[] equityPercentages; // Basis points (10000 = 100%)
        uint256 totalDistributed;
    }
    
    mapping(bytes32 => ProductRoyalties) public products;
    
    event RoyaltyDistributed(
        bytes32 indexed productId,
        uint256 totalAmount,
        uint256 timestamp
    );
    
    event PaymentReceived(
        bytes32 indexed productId,
        address indexed contributor,
        uint256 amount
    );
    
    constructor(address _paymentToken) Ownable(msg.sender) {
        paymentToken = IERC20(_paymentToken);
    }
    
    /**
     * @dev Register product royalty structure
     * @param productId Unique product identifier
     * @param contributors Array of contributor addresses
     * @param equityPercentages Array of equity percentages (basis points)
     */
    function registerProduct(
        bytes32 productId,
        address[] calldata contributors,
        uint256[] calldata equityPercentages
    ) external onlyOwner {
        require(
            contributors.length == equityPercentages.length,
            "Array length mismatch"
        );
        
        uint256 totalEquity = 0;
        for (uint256 i = 0; i < equityPercentages.length; i++) {
            totalEquity += equityPercentages[i];
        }
        require(totalEquity == 10000, "Equity must sum to 100%");
        
        products[productId] = ProductRoyalties({
            contributors: contributors,
            equityPercentages: equityPercentages,
            totalDistributed: 0
        });
    }
    
    /**
     * @dev Distribute royalties from a sale
     * @param productId Product identifier
     * @param saleAmount Total sale amount (60% of which goes to contributors)
     */
    function distributeRoyalties(bytes32 productId, uint256 saleAmount)
        external
        onlyOwner
        nonReentrant
    {
        ProductRoyalties storage product = products[productId];
        require(product.contributors.length > 0, "Product not registered");
        
        uint256 contributorShare = (saleAmount * 60) / 100; // 60% to contributors
        
        for (uint256 i = 0; i < product.contributors.length; i++) {
            uint256 amount = (contributorShare * product.equityPercentages[i]) / 10000;
            
            require(
                paymentToken.transferFrom(msg.sender, product.contributors[i], amount),
                "Transfer failed"
            );
            
            emit PaymentReceived(productId, product.contributors[i], amount);
        }
        
        product.totalDistributed += contributorShare;
        
        emit RoyaltyDistributed(productId, contributorShare, block.timestamp);
    }
}
```

---

## Implementation Timeline

### Week-by-Week Detailed Plan

#### **Week 1: Foundation**

**Days 1-2: Infrastructure Setup**
- [ ] Create GitHub organization
- [ ] Set up Nx monorepo
- [ ] Configure ESLint, Prettier, Husky
- [ ] Deploy PostgreSQL instance (Railway/Supabase)
- [ ] Deploy Redis instance
- [ ] Set up CI/CD (GitHub Actions)

**Days 3-4: Smart Contract Development**
- [ ] Initialize Hardhat project
- [ ] Write QuestRewardDistributor contract
- [ ] Write RoyaltyDistributor contract
- [ ] Write unit tests (Hardhat + Chai)
- [ ] Deploy to Polygon Mumbai testnet
- [ ] Verify contracts on PolygonScan

**Days 5-7: Database & API Foundation**
- [ ] Design Prisma schema (users, ideas, quests, etc.)
- [ ] Run migrations
- [ ] Build NestJS API gateway
- [ ] Implement JWT authentication
- [ ] Create /health, /users, /quests endpoints
- [ ] Test with Postman/Insomnia

**Milestone:** Basic infrastructure operational

---

#### **Week 2: Core Quest Features**

**Days 8-10: Quest Board Frontend**
- [ ] Bootstrap Next.js app
- [ ] Design quest card component
- [ ] Implement quest list view (with filters)
- [ ] Build quest detail page
- [ ] Connect to API via React Query

**Days 11-12: Quest Submission Flow**
- [ ] Create idea submission form
- [ ] Build quest fracturing UI (drag-drop quest builder)
- [ ] Implement quest application modal
- [ ] Add file upload for deliverables

**Days 13-14: Wallet Integration**
- [ ] Integrate RainbowKit for wallet connect
- [ ] Build wallet context provider
- [ ] Add ENS name resolution
- [ ] Test with MetaMask + WalletConnect

**Milestone:** Users can browse quests, submit ideas, apply

---

#### **Week 3: Codex Engine (Simplified)**

**Days 15-17: Python Scoring Service**
- [ ] Build FastAPI app
- [ ] Implement Trueness metric
- [ ] Implement Flow metric
- [ ] Implement simplified PCS (manual inputs for now)
- [ ] Create /score endpoint
- [ ] Test with sample ideas

**Days 18-19: Integration with API Gateway**
- [ ] Call Codex engine from NestJS
- [ ] Display scores on frontend
- [ ] Build score explanation UI
- [ ] Add fail code messaging

**Days 20-21: De-risking Quest Generator**
- [ ] Implement suggestion engine
- [ ] Create auto-quest templates
- [ ] Test NO_GO → suggestion flow

**Milestone:** Codex scoring operational

---

#### **Week 4: Marketplace MVP**

**Days 22-24: Product Listing**
- [ ] Build marketplace frontend (Next.js)
- [ ] Create product card component
- [ ] Implement product detail page
- [ ] Add search/filter functionality

**Days 25-27: Payment Integration**
- [ ] Set up Stripe account
- [ ] Integrate Stripe Checkout
- [ ] Build webhook handler for payments
- [ ] Implement download delivery (S3/IPFS)

**Day 28: End-to-End Test**
- [ ] Create test quest
- [ ] Complete test quest
- [ ] Mint test product
- [ ] Purchase test product
- [ ] Verify payment distribution

**Milestone:** Full MVP functional

---

### Weeks 5-12: See Implementation Guide in venture_foundry_rundown.md

---

## Testing Strategy

### Unit Tests

**Backend (Jest + Supertest):**
```typescript
describe('Codex Engine', () => {
  it('should calculate Trueness metric correctly', () => {
    const idea = {
      problem_statement_clarity: 0.85,
      target_user_specificity: 0.90,
      success_criteria_quantified: 0.70,
      timeline_realism: 0.65,
      vague_language_count: 2,
      missing_key_fields: 1,
      contradictory_statements: 0
    };
    
    const result = calculateTrueness(idea);
    expect(result).toBeCloseTo(0.66, 2);
  });
  
  it('should return NO_GO for ideas below threshold', () => {
    const badIdea = {
      /* Low scores */
    };
    
    const verdict = calculateVerdict(badIdea);
    expect(verdict.verdict).toBe('NO_GO');
    expect(verdict.suggestions.length).toBeGreaterThan(0);
  });
});
```

**Smart Contracts (Hardhat + Chai):**
```javascript
describe("QuestRewardDistributor", function () {
  it("Should distribute 70% immediately and vest 30%", async function () {
    const [owner, contributor] = await ethers.getSigners();
    const totalReward = ethers.parseEther("1000");
    
    await distributor.grantReward(questId, contributor.address, totalReward);
    
    const schedule = await distributor.schedules(questId);
    expect(schedule.immediateAmount).to.equal(ethers.parseEther("700"));
    expect(schedule.vestedAmount).to.equal(ethers.parseEther("300"));
  });
  
  it("Should allow claiming vested tokens after 6 months", async function () {
    // ... fast forward time by 6 months
    await ethers.provider.send("evm_increaseTime", [180 * 24 * 60 * 60]);
    
    await distributor.connect(contributor).claimVested(questId);
    
    const claimed = await distributor.schedules(questId).claimed;
    expect(claimed).to.be.closeTo(ethers.parseEther("150"), ethers.parseEther("1"));
  });
});
```

### Integration Tests

**End-to-End Quest Flow:**
```typescript
describe('Quest Completion Flow', () => {
  it('should complete full quest lifecycle', async () => {
    // 1. Founder submits idea
    const idea = await api.post('/ideas', ideaData);
    expect(idea.codex_verdict).toBe('GO');
    
    // 2. Founder creates quest
    const quest = await api.post('/quests', { idea_id: idea.id, ...questData });
    
    // 3. Contributor applies
    const application = await api.post('/quest-applications', {
      quest_id: quest.id,
      contributor_id: contributor.id
    });
    
    // 4. Founder accepts
    await api.patch(`/quest-applications/${application.id}`, { status: 'accepted' });
    
    // 5. Contributor submits work
    await api.patch(`/quests/${quest.id}`, {
      status: 'review',
      deliverable_url: 'https://github.com/...'
    });
    
    // 6. Founder approves
    await api.patch(`/quests/${quest.id}`, { status: 'completed' });
    
    // 7. Verify smart contract payout
    const balance = await ecosToken.balanceOf(contributor.wallet_address);
    expect(balance).toBeGreaterThan(0);
  });
});
```

---

## Security Considerations

### Smart Contract Security

**Vulnerabilities to Prevent:**
1. **Reentrancy:** Use OpenZeppelin's ReentrancyGuard
2. **Integer Overflow:** Use Solidity 0.8+ (built-in overflow protection)
3. **Access Control:** Role-based permissions via AccessControl
4. **Front-Running:** Use commit-reveal schemes for sensitive operations

**Audit Checklist:**
- [ ] All external calls use checks-effects-interactions pattern
- [ ] No delegatecall to untrusted contracts
- [ ] All token transfers checked for return values
- [ ] Gas limits considered for loops
- [ ] Event emissions for all state changes

### API Security

**Authentication:**
- JWT tokens with 24-hour expiration
- Refresh token rotation
- Rate limiting: 100 requests/minute per IP

**Input Validation:**
```typescript
import { z } from 'zod';

const QuestSchema = z.object({
  title: z.string().min(10).max(100),
  description: z.string().min(50).max(2000),
  token_reward: z.number().positive().max(10000),
  equity_percentage: z.number().min(0.1).max(10.0),
  deadline: z.date().min(new Date(Date.now() + 7*24*60*60*1000)) // At least 7 days
});
```

**SQL Injection Prevention:**
- Use Prisma ORM (parameterized queries only)
- Never concatenate user input into SQL

**XSS Prevention:**
- Sanitize all user-generated content
- Use Content Security Policy headers
- Escape HTML in React (automatic with JSX)

---

**Version:** 1.0  
**Last Updated:** December 30, 2024  
**Status:** Technical Specification  
**Review:** Requires legal + security audit before production deployment
