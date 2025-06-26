from typing import Dict, Any, List, Optional
import logging

from .models import AchievementEventType, AchievementDefinition, AchievementCriteria, UserAchievement
from . import db as gamification_db # Renamed to avoid conflict with gamification_db module itself
from users.db import get_user_by_wallet_address # To get user info if needed

logger = logging.getLogger(__name__)

class GamificationService:
    def __init__(self):
        # Cache definitions? For now, fetch each time or on startup if few.
        # If many definitions, caching with periodic refresh would be good.
        pass

    def _check_criterion(self, event_data: Dict[str, Any], criterion: AchievementCriteria) -> bool:
        """Checks if a single event_data satisfies a single criterion."""
        conditions = criterion.conditions

        # Count check (e.g., number of tickets in one purchase, number of referrals in one action)
        # For achievements like "buy 10 tickets", this 'count' refers to a single event's count.
        # Aggregated counts over time are not handled by this simple check;
        # that would require storing progress.
        if conditions.count is not None:
            event_count = event_data.get("count", 0) # Event must provide 'count' if criterion uses it
            if event_count < conditions.count:
                return False

        if conditions.min_amount is not None:
            event_amount = event_data.get("amount", 0.0) # Event must provide 'amount'
            if event_amount < conditions.min_amount:
                return False

        if conditions.category_id is not None:
            event_category_id = event_data.get("category_id")
            if event_category_id != conditions.category_id:
                return False

        if conditions.tier_name is not None:
            event_tier_name = event_data.get("tier_name")
            if event_tier_name != conditions.tier_name:
                return False

        # Add more specific condition checks here based on AchievementCriteriaValue fields
        return True


    def process_event(self, user_wallet_address: str, event_type: AchievementEventType, event_data: Optional[Dict[str, Any]] = None):
        """
        Processes an event for a user and checks if any achievements are unlocked.
        event_data contains details specific to the event_type.

        Example event_data:
        - TICKET_PURCHASE: {"count": 1, "category_id": "cat123", "total_value": 5.0}
        - DRAW_WIN: {"prize_amount": 100.0, "tier_name": "Jackpot", "category_id": "cat123", "draw_id": "draw456"}
        - REFERRAL_SUCCESS: {"count": 1} (for one successful referral)
        """
        if event_data is None:
            event_data = {}

        logger.info(f"Processing event: User '{user_wallet_address}', Type '{event_type.value}', Data '{event_data}'")

        active_definitions: List[AchievementDefinition] = gamification_db.get_all_achievement_definitions(active_only=True)
        if not active_definitions:
            logger.debug("No active achievement definitions found.")
            return

        for definition in active_definitions:
            if gamification_db.check_if_user_has_achievement(user_wallet_address, str(definition.id)):
                # logger.debug(f"User {user_wallet_address} already has achievement '{definition.name}'. Skipping.")
                continue

            all_criteria_met_for_this_event = True
            # This simple model assumes all criteria for an achievement must match the *same* event type
            # and be satisfied by the *current* single event.

            # Filter criteria relevant to the current event_type
            relevant_criteria = [crit for crit in definition.criteria if crit.event_type == event_type]

            if not relevant_criteria and definition.criteria:
                # If definition has criteria, but none match current event type, it can't be earned by this event.
                all_criteria_met_for_this_event = False
            elif not definition.criteria: # Achievement with no criteria (auto-granted on some other condition perhaps?)
                # This case should be handled by specific logic if needed, or ensure definitions always have criteria.
                # For now, assume definitions always have criteria relevant to some event.
                pass


            for criterion in relevant_criteria: # Iterate through criteria that match the event type
                if not self._check_criterion(event_data, criterion):
                    all_criteria_met_for_this_event = False
                    break # One criterion not met for this event, so this achievement isn't earned by this event

            # Check if there are other criteria types in the definition that were NOT processed by this event.
            # If so, this event alone cannot grant the achievement.
            # This logic assumes an achievement requires ALL its defined criteria to be met simultaneously by one event
            # if those criteria match the event type, or if other criteria types exist, they must be met by other means (not covered here).
            # A more robust system would track progress for each criterion.

            # Simplified: if all *relevant* criteria (those matching the event type) are met by this single event,
            # AND there are no other types of criteria defined for this achievement, then grant.
            # This means an achievement can only be triggered by one type of event.

            other_criteria_types_exist = any(crit.event_type != event_type for crit in definition.criteria)
            if other_criteria_types_exist and relevant_criteria : # If this event matched some, but others are pending
                 all_criteria_met_for_this_event = False # Cannot grant with this event alone

            if all_criteria_met_for_this_event and relevant_criteria: # Must have matched at least one relevant criterion
                logger.info(f"User '{user_wallet_address}' meets criteria for achievement '{definition.name}' (ID: {definition.id}) with event '{event_type.value}'.")
                granted_achievement = gamification_db.grant_achievement_to_user(user_wallet_address, definition)
                if granted_achievement:
                    logger.info(f"Achievement '{definition.name}' granted to user '{user_wallet_address}'. Points: {definition.points_reward}")
                    # Potentially trigger other actions, like notifications (out of scope for this service)
                else:
                    logger.error(f"Failed to grant achievement '{definition.name}' to user '{user_wallet_address}' despite meeting criteria.")

        # Direct loyalty points update based on event (optional, if not tied to achievements)
        # Example:
        # if event_type == AchievementEventType.TICKET_PURCHASE:
        #     points_for_purchase = event_data.get("count", 0) * 1 # 1 point per ticket
        #     if points_for_purchase > 0:
        #         gamification_db.update_user_loyalty_points(user_wallet_address, points_for_purchase)
        #         logger.info(f"Awarded {points_for_purchase} loyalty points to {user_wallet_address} for ticket purchase.")


# Global service instance (or use FastAPI dependency injection)
gamification_service = GamificationService()
