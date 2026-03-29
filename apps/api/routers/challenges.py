"""
ECOS Revenue Engine - Challenges & Dev Bounties Router
Public challenges, dev bounties with escrow, milestone-based payouts
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


# ============= MODELS =============
class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"      # $50-200
    INTERMEDIATE = "intermediate"  # $200-1000
    ADVANCED = "advanced"      # $1000-5000
    EXPERT = "expert"          # $5000-25000


class ChallengeType(str, Enum):
    CODE = "code"              # Feature dev, bug fixes
    HARDWARE = "hardware"      # PCB design, firmware
    DATA = "data"              # ML models, datasets
    CREATIVE = "creative"      # Design, docs, video
    RESEARCH = "research"      # White papers, analysis


class ChallengeStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Challenge(BaseModel):
    id: str
    title: str
    description: str
    project_id: int  # P01-P13
    challenge_type: ChallengeType
    difficulty: DifficultyLevel
    bounty_usd: float = Field(ge=0)
    escrow_held: bool = True
    status: ChallengeStatus = ChallengeStatus.OPEN
    milestones: List[str] = []
    required_skills: List[str] = []
    submission_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    winner_id: Optional[str] = None
    completed_at: Optional[datetime] = None


class Submission(BaseModel):
    id: str
    challenge_id: str
    developer_id: str
    github_pr_url: Optional[str] = None
    demo_url: Optional[str] = None
    description: str
    milestone_progress: dict  # {"milestone_1": True, ...}
    submitted_at: datetime = Field(default_factory=datetime.now)
    reviewed: bool = False
    score: Optional[float] = None  # 0-100
    payout_released: bool = False


class ChallengeCreate(BaseModel):
    title: str = Field(min_length=10, max_length=200)
    description: str = Field(min_length=50)
    project_id: int = Field(ge=1, le=13)
    challenge_type: ChallengeType
    difficulty: DifficultyLevel
    bounty_usd: float = Field(ge=50, le=25000)
    milestones: List[str] = Field(min_items=1, max_items=10)
    required_skills: List[str] = []
    deadline_days: int = Field(ge=3, le=90, default=30)


class SubmissionCreate(BaseModel):
    challenge_id: str
    github_pr_url: Optional[str] = None
    demo_url: Optional[str] = None
    description: str = Field(min_length=100)


# ============= IN-MEMORY STORAGE (Replace with DB) =============
CHALLENGES_DB: dict[str, Challenge] = {}
SUBMISSIONS_DB: dict[str, Submission] = {}


# ============= ENDPOINTS =============

@router.get("/", response_model=List[Challenge])
async def list_challenges(
    project_id: Optional[int] = None,
    status: Optional[ChallengeStatus] = None,
    difficulty: Optional[DifficultyLevel] = None,
    challenge_type: Optional[ChallengeType] = None
):
    """List all challenges with optional filters"""
    challenges = list(CHALLENGES_DB.values())
    
    if project_id:
        challenges = [c for c in challenges if c.project_id == project_id]
    if status:
        challenges = [c for c in challenges if c.status == status]
    if difficulty:
        challenges = [c for c in challenges if c.difficulty == difficulty]
    if challenge_type:
        challenges = [c for c in challenges if c.challenge_type == challenge_type]
    
    return sorted(challenges, key=lambda x: x.bounty_usd, reverse=True)


@router.post("/create", response_model=Challenge)
async def create_challenge(challenge: ChallengeCreate):
    """Create a new public challenge with escrowed bounty"""
    challenge_id = f"CH{len(CHALLENGES_DB) + 1:05d}"
    deadline = datetime.now() + timedelta(days=challenge.deadline_days)
    
    new_challenge = Challenge(
        id=challenge_id,
        title=challenge.title,
        description=challenge.description,
        project_id=challenge.project_id,
        challenge_type=challenge.challenge_type,
        difficulty=challenge.difficulty,
        bounty_usd=challenge.bounty_usd,
        milestones=challenge.milestones,
        required_skills=challenge.required_skills,
        deadline=deadline
    )
    
    CHALLENGES_DB[challenge_id] = new_challenge
    return new_challenge


@router.get("/{challenge_id}", response_model=Challenge)
async def get_challenge(challenge_id: str):
    """Get challenge details"""
    if challenge_id not in CHALLENGES_DB:
        raise HTTPException(404, f"Challenge {challenge_id} not found")
    return CHALLENGES_DB[challenge_id]


@router.post("/{challenge_id}/submit", response_model=Submission)
async def submit_solution(challenge_id: str, submission: SubmissionCreate, developer_id: str = "dev_placeholder"):
    """Submit a solution to a challenge"""
    if challenge_id not in CHALLENGES_DB:
        raise HTTPException(404, f"Challenge {challenge_id} not found")
    
    challenge = CHALLENGES_DB[challenge_id]
    if challenge.status != ChallengeStatus.OPEN:
        raise HTTPException(400, f"Challenge is {challenge.status}, not accepting submissions")
    
    submission_id = f"SUB{len(SUBMISSIONS_DB) + 1:05d}"
    milestone_progress = {f"milestone_{i+1}": False for i in range(len(challenge.milestones))}
    
    new_submission = Submission(
        id=submission_id,
        challenge_id=challenge_id,
        developer_id=developer_id,
        github_pr_url=submission.github_pr_url,
        demo_url=submission.demo_url,
        description=submission.description,
        milestone_progress=milestone_progress
    )
    
    SUBMISSIONS_DB[submission_id] = new_submission
    CHALLENGES_DB[challenge_id].submission_count += 1
    
    return new_submission


@router.post("/{challenge_id}/review/{submission_id}")
async def review_submission(challenge_id: str, submission_id: str, score: float = Field(ge=0, le=100), feedback: str = ""):
    """Review and score a submission (admin only)"""
    if submission_id not in SUBMISSIONS_DB:
        raise HTTPException(404, "Submission not found")
    
    submission = SUBMISSIONS_DB[submission_id]
    submission.reviewed = True
    submission.score = score
    
    # Auto-release payout if score >= 80
    if score >= 80 and not submission.payout_released:
        challenge = CHALLENGES_DB[challenge_id]
        submission.payout_released = True
        challenge.status = ChallengeStatus.COMPLETED
        challenge.winner_id = submission.developer_id
        challenge.completed_at = datetime.now()
        
        return {
            "message": f"Submission approved! ${challenge.bounty_usd} released to developer",
            "score": score,
            "payout": challenge.bounty_usd
        }
    
    return {"message": "Submission reviewed", "score": score, "payout_released": False}


@router.get("/{challenge_id}/submissions", response_model=List[Submission])
async def get_submissions(challenge_id: str):
    """Get all submissions for a challenge"""
    return [s for s in SUBMISSIONS_DB.values() if s.challenge_id == challenge_id]


@router.get("/leaderboard/top-earners")
async def get_top_earners(limit: int = 50):
    """Get top bounty earners (gamification)"""
    earnings = {}
    for submission in SUBMISSIONS_DB.values():
        if submission.payout_released:
            challenge = CHALLENGES_DB[submission.challenge_id]
            dev_id = submission.developer_id
            earnings[dev_id] = earnings.get(dev_id, 0) + challenge.bounty_usd
    
    leaderboard = [{"developer_id": dev, "total_earned": amount} 
                   for dev, amount in sorted(earnings.items(), key=lambda x: x[1], reverse=True)]
    
    return {"leaderboard": leaderboard[:limit], "total_developers": len(earnings)}


@router.get("/stats/overview")
async def get_challenge_stats():
    """Get overall challenge platform statistics"""
    total_bounties = sum(c.bounty_usd for c in CHALLENGES_DB.values())
    paid_out = sum(c.bounty_usd for c in CHALLENGES_DB.values() if c.status == ChallengeStatus.COMPLETED)
    
    by_status = {}
    for challenge in CHALLENGES_DB.values():
        by_status[challenge.status] = by_status.get(challenge.status, 0) + 1
    
    return {
        "total_challenges": len(CHALLENGES_DB),
        "total_bounty_pool_usd": total_bounties,
        "paid_out_usd": paid_out,
        "escrow_held_usd": total_bounties - paid_out,
        "by_status": by_status,
        "total_submissions": len(SUBMISSIONS_DB),
        "avg_bounty_usd": total_bounties / len(CHALLENGES_DB) if CHALLENGES_DB else 0
    }
