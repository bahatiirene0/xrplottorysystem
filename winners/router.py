from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from .models import RecentWinnerInfo
from draws.db import get_draw_history # Using existing function, will filter for completed with winners
from draws.models import Draw # To access Draw fields
from lottery_categories.db import get_category_by_id
from pymongo.errors import PyMongoError

router = APIRouter()

def anonymize_wallet(wallet_address: Optional[str]) -> str:
    if not wallet_address:
        return "N/A"
    if len(wallet_address) > 8: # Basic check
        return f"{wallet_address[:5]}...{wallet_address[-3:]}"
    return wallet_address # Return as is if too short to anonymize well

@router.get("/recent", response_model=List[RecentWinnerInfo], summary="Get a list of recent lottery winners")
def get_recent_winners(
    limit: int = Query(10, gt=0, le=50, description="Number of recent winners to return")
):
    """
    Retrieves a list of recent winners from completed draws.
    """
    recent_winners_info: List[RecentWinnerInfo] = []
    try:
        # Fetch a broader history and then filter.
        # get_draw_history sorts by scheduled_close_time descending.
        # We might need more draws than 'limit' initially to find enough winners.
        # Consider if a dedicated DB query for completed draws with winners would be better for performance.
        # For now, fetch more and filter in application.
        potential_draws = get_draw_history(limit=limit * 2) # Fetch more to ensure we find 'limit' winners

        for draw in potential_draws:
            if len(recent_winners_info) >= limit:
                break # Reached desired number of winners

            if draw.status == "completed" and draw.winner and draw.actual_close_time:
                category = get_category_by_id(draw.category_id)
                category_name = category.name if category else "Unknown Category"
                prize_summary = "Details in Draw" # Placeholder, could be more specific
                if category and category.prize_info:
                    # Example: just take the first key as a summary
                    prize_summary = next(iter(category.prize_info.keys()), "General Prize").replace("_", " ").title()


                winner_info = RecentWinnerInfo(
                    draw_id=draw.id,
                    category_id=draw.category_id,
                    category_name=category_name,
                    winning_wallet_address_anonymized=anonymize_wallet(draw.winner),
                    prize_info_summary=prize_summary, # Simplified for now
                    closed_time=draw.actual_close_time
                )
                recent_winners_info.append(winner_info)

        return recent_winners_info

    except PyMongoError as e:
        print(f"PyMongoError in /winners/recent: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while fetching recent winners: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in /winners/recent: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
