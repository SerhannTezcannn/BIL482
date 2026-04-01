from fastapi import APIRouter
from .leaderboard import GlobalLeaderboard

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])
leaderboard = GlobalLeaderboard()

@router.get("")
def get_leaderboard():
    return leaderboard.get_sorted_leaderboard()
