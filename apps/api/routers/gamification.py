"""
ECOS Gamification Engine - XP, Levels, Quests, Badges, Leaderboards
Drives engagement and recurring revenue through achievement mechanics
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


# XP multipliers per action type
XP_TABLE = {
    "challenge_submitted": 50,
    "challenge_won": 500,
    "marketplace_sale": 200,
    "marketplace_purchase": 25,
    "bug_report": 30,
    "docs_contribution": 40,
    "forum_post": 10,
    "daily_login": 5,
    "project_deployed": 1000,
    "kit_assembled": 300,
    "sensor_data_submitted": 15,
    "referral_signup": 100,
}

# Level thresholds
LEVEL_THRESHOLDS = [
    (0, "Seedling"),
    (500, "Sprout"),
    (2000, "Grower"),
    (5000, "Cultivator"),
    (15000, "Steward"),
    (40000, "Guardian"),
    (100000, "Champion"),
    (250000, "Architect"),
    (500000, "Legend"),
]


class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    criteria: str


class Quest(BaseModel):
    id: str
    title: str
    description: str
    project_ids: List[int]  # Which projects this quest applies to
    objectives: List[str]
    xp_reward: int
    cash_reward_usd: float = 0.0  # Optional cash bonus
    deadline: Optional[datetime] = None
    is_active: bool = True
    completions: int = 0


class UserProfile(BaseModel):
    user_id: str
    xp: int = 0
    level: int = 1
    level_name: str = "Seedling"
    badges: List[str] = []
    quests_completed: List[str] = []
    streak_days: int = 0
    last_activity: Optional[datetime] = None
    total_earned_usd: float = 0.0


USERS_DB: dict = {}
QUESTS_DB: dict = {}


BADGES = [
    Badge(id="first_challenge", name="First Blood", description="Complete first challenge",
          icon="sword", xp_reward=100, criteria="challenge_won >= 1"),
    Badge(id="market_maker", name="Market Maker", description="First marketplace sale",
          icon="store", xp_reward=250, criteria="marketplace_sale >= 1"),
    Badge(id="data_hero", name="Data Hero", description="Submit 100 sensor readings",
          icon="sensor", xp_reward=500, criteria="sensor_data_submitted >= 100"),
    Badge(id="kit_builder", name="Kit Builder", description="Assemble a DIY kit",
          icon="tools", xp_reward=300, criteria="kit_assembled >= 1"),
    Badge(id="recruiter", name="Recruiter", description="Refer 5 new members",
          icon="people", xp_reward=750, criteria="referral_signup >= 5"),
    Badge(id="legend", name="ECOS Legend", description="Reach Legend level",
          icon="crown", xp_reward=5000, criteria="xp >= 500000"),
]


def compute_level(xp: int) -> tuple[int, str]:
    level = 1
    level_name = "Seedling"
    for i, (threshold, name) in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
            level_name = name
    return level, level_name


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str):
    if user_id not in USERS_DB:
        return UserProfile(user_id=user_id)
    return USERS_DB[user_id]


@router.post("/award-xp")
async def award_xp(user_id: str, action: str, multiplier: float = 1.0):
    """Award XP for a specific action"""
    if action not in XP_TABLE:
        raise HTTPException(400, f"Unknown action: {action}. Valid: {list(XP_TABLE.keys())}")

    xp_earned = int(XP_TABLE[action] * multiplier)

    if user_id not in USERS_DB:
        USERS_DB[user_id] = UserProfile(user_id=user_id)

    profile = USERS_DB[user_id]
    old_level = profile.level
    profile.xp += xp_earned
    profile.level, profile.level_name = compute_level(profile.xp)
    profile.last_activity = datetime.now()

    leveled_up = profile.level > old_level

    return {
        "user_id": user_id,
        "action": action,
        "xp_earned": xp_earned,
        "total_xp": profile.xp,
        "level": profile.level,
        "level_name": profile.level_name,
        "leveled_up": leveled_up,
    }


@router.post("/quests/create", response_model=Quest)
async def create_quest(quest: Quest):
    QUESTS_DB[quest.id] = quest
    return quest


@router.get("/quests", response_model=List[Quest])
async def list_quests(project_id: Optional[int] = None):
    quests = [q for q in QUESTS_DB.values() if q.is_active]
    if project_id:
        quests = [q for q in quests if project_id in q.project_ids]
    return quests


@router.post("/quests/{quest_id}/complete")
async def complete_quest(quest_id: str, user_id: str):
    if quest_id not in QUESTS_DB:
        raise HTTPException(404, "Quest not found")
    quest = QUESTS_DB[quest_id]

    if user_id not in USERS_DB:
        USERS_DB[user_id] = UserProfile(user_id=user_id)
    profile = USERS_DB[user_id]

    if quest_id in profile.quests_completed:
        raise HTTPException(400, "Quest already completed")

    profile.quests_completed.append(quest_id)
    profile.xp += quest.xp_reward
    profile.total_earned_usd += quest.cash_reward_usd
    profile.level, profile.level_name = compute_level(profile.xp)
    quest.completions += 1

    return {
        "message": f"Quest '{quest.title}' completed!",
        "xp_reward": quest.xp_reward,
        "cash_reward": quest.cash_reward_usd,
        "new_xp": profile.xp,
        "level": profile.level_name,
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 100, project_id: Optional[int] = None):
    users = list(USERS_DB.values())
    leaderboard = [
        {
            "rank": i + 1,
            "user_id": u.user_id,
            "xp": u.xp,
            "level_name": u.level_name,
            "badges_count": len(u.badges),
            "quests_completed": len(u.quests_completed),
        }
        for i, u in enumerate(sorted(users, key=lambda x: x.xp, reverse=True)[:limit])
    ]
    return {"leaderboard": leaderboard, "total_users": len(users)}


@router.get("/badges")
async def list_badges():
    return BADGES


@router.get("/xp-table")
async def get_xp_table():
    return {"actions": XP_TABLE, "level_thresholds": [
        {"level": i + 1, "name": name, "xp_required": threshold}
        for i, (threshold, name) in enumerate(LEVEL_THRESHOLDS)
    ]}
