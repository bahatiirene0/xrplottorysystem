import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any, List

# client fixture is from tests/conftest.py

# Helper to reduce boilerplate if needed, or just call client.post directly
def create_category(client: TestClient, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = client.post("/api/lottery_categories/", json=payload)
    assert response.status_code == 201
    return response.json()

class TestAPIFlows:

    # Store created IDs to use in subsequent tests or for cleanup if needed
    created_category_ids: List[str] = []

    def test_lottery_category_management_flow(self, test_client: TestClient):
        """
        Tests CRUD operations for lottery categories.
        Covers: creating raffle and pick_n_digits categories, listing, getting by ID.
        """
        client = test_client # Use the fixture from conftest.py

        # 1. Create a "raffle" category
        raffle_payload = {
            "name": "API Test Raffle Weekly",
            "description": "A weekly raffle created via API test.",
            "draw_interval_type": "weekly",
            "draw_interval_value": 1,
            "ticket_price": 2.5,
            "prize_info": {"main_prize": "75% of pool"},
            "is_active": True,
            "game_type": "raffle",
            # game_config can be empty for raffle or omitted if model has default
            "game_config": {}
        }
        raffle_cat_response = client.post("/api/lottery_categories/", json=raffle_payload)
        assert raffle_cat_response.status_code == 201
        raffle_cat_data = raffle_cat_response.json()
        assert raffle_cat_data["name"] == raffle_payload["name"]
        assert raffle_cat_data["game_type"] == "raffle"
        assert "id" in raffle_cat_data
        TestAPIFlows.created_category_ids.append(raffle_cat_data["id"])
        raffle_cat_id = raffle_cat_data["id"]

        # 2. Create a "pick_n_digits" category
        pickn_payload = {
            "name": "API Test Pick 4 Daily",
            "description": "A daily Pick 4 game created via API test.",
            "draw_interval_type": "daily",
            "draw_interval_value": 1,
            "ticket_price": 1.0,
            "prize_info": {"match_4": "Jackpot $1000"},
            "is_active": True,
            "game_type": "pick_n_digits",
            "game_config": {
                "num_picks": 4,
                "min_digit": 0,
                "max_digit": 9,
                "allow_duplicates": False
            }
        }
        pickn_cat_response = client.post("/api/lottery_categories/", json=pickn_payload)
        assert pickn_cat_response.status_code == 201
        pickn_cat_data = pickn_cat_response.json()
        assert pickn_cat_data["name"] == pickn_payload["name"]
        assert pickn_cat_data["game_type"] == "pick_n_digits"
        assert pickn_cat_data["game_config"]["num_picks"] == 4
        assert "id" in pickn_cat_data
        TestAPIFlows.created_category_ids.append(pickn_cat_data["id"])
        pickn_cat_id = pickn_cat_data["id"]

        # 3. List all categories
        list_response = client.get("/api/lottery_categories/")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert isinstance(list_data, list)
        assert len(list_data) >= 2 # Assuming clean DB or only these two

        found_raffle = any(cat["id"] == raffle_cat_id for cat in list_data)
        found_pickn = any(cat["id"] == pickn_cat_id for cat in list_data)
        assert found_raffle
        assert found_pickn

        # 4. Get raffle category by ID
        get_raffle_response = client.get(f"/api/lottery_categories/{raffle_cat_id}")
        assert get_raffle_response.status_code == 200
        get_raffle_data = get_raffle_response.json()
        assert get_raffle_data["id"] == raffle_cat_id
        assert get_raffle_data["name"] == raffle_payload["name"]

        # 5. Get pick_n_digits category by ID
        get_pickn_response = client.get(f"/api/lottery_categories/{pickn_cat_id}")
        assert get_pickn_response.status_code == 200
        get_pickn_data = get_pickn_response.json()
        assert get_pickn_data["id"] == pickn_cat_id
        assert get_pickn_data["game_config"]["num_picks"] == 4

        # 6. Update a category (e.g., deactivate raffle category)
        update_payload = {"is_active": False, "description": "Deactivated raffle"}
        update_response = client.put(f"/api/lottery_categories/{raffle_cat_id}", json=update_payload)
        assert update_response.status_code == 200
        updated_raffle_data = update_response.json()
        assert updated_raffle_data["is_active"] is False
        assert updated_raffle_data["description"] == "Deactivated raffle"

        # Verify the update by getting it again
        get_updated_raffle_response = client.get(f"/api/lottery_categories/{raffle_cat_id}")
        assert get_updated_raffle_response.status_code == 200
        assert get_updated_raffle_response.json()["is_active"] is False

        # 7. List only active categories
        list_active_response = client.get("/api/lottery_categories/?active_only=true")
        assert list_active_response.status_code == 200
        active_list_data = list_active_response.json()
        assert not any(cat["id"] == raffle_cat_id for cat in active_list_data) # Deactivated raffle should not be here
        assert any(cat["id"] == pickn_cat_id for cat in active_list_data)    # Active pickn should be here

        # 8. Delete a category (e.g. the deactivated raffle)
        delete_response = client.delete(f"/api/lottery_categories/{raffle_cat_id}")
        assert delete_response.status_code == 204 # No content

        # Verify deletion
        get_deleted_response = client.get(f"/api/lottery_categories/{raffle_cat_id}")
        assert get_deleted_response.status_code == 404
        TestAPIFlows.created_category_ids.remove(raffle_cat_id)


    # We can add more test methods here for other flows
    # For example, test_raffle_game_end_to_end_flow, test_pick_n_game_end_to_end_flow etc.
    # Each test method will get a fresh 'test_client' if the fixture scope is 'function'.
    # The created_category_ids list is a class variable, so it persists across method calls
    # within the same test run if not managed carefully or if tests are not fully isolated
    # regarding shared state like this.
    # For true isolation, each test should manage its own created resources or use unique names.
    # However, for a flow, sometimes one test sets up data for the next.
    # Let's make created_category_ids an instance variable if we want per-instance tracking,
    # or pass IDs explicitly. For now, class variable is simple for sequential conceptual flow.
    # A better way for cleanup or sharing IDs is via pytest fixtures or return values.

    # For now, we'll keep this simple and assume the test runner executes tests in some order,
    # and the mongomock clearing in conftest.py handles isolation between test *functions*.
    # If TestAPIFlows.created_category_ids were to be used by another test *method* in this class,
    # it would see IDs from previous methods unless cleared.
    # We should clear it or make tests fully independent.
    # For this illustrative test, we'll rely on the mongomock clearing per function.
    # The created_category_ids list is mostly for debugging/visibility here.

    # Placeholder for future cleanup if needed at the end of all tests in this class
    # @classmethod
    # def teardown_class(cls):
    #     # If we needed to manually clean up (e.g., if not using function-scoped mongomock clearing)
    #     # client = TestClient(app) # A way to get a client for cleanup
    #     # for cat_id in cls.created_category_ids:
    #     #     client.delete(f"/api/lottery_categories/{cat_id}") # Ignore errors if already deleted
    #     # cls.created_category_ids.clear()
    #     pass


    def test_raffle_game_end_to_end_flow(self, test_client: TestClient):
        """
        Tests a full raffle game flow:
        1. Create a raffle category.
        2. Manually create a draw for it (pending_open).
        3. Process pending draws to open it.
        4. Buy tickets from two different wallets.
        5. Close the draw.
        6. Check winner announcement.
        7. Verify next draw auto-creation.
        """
        client = test_client

        # 1. Create Raffle Category
        from datetime import datetime, timedelta # Moved import here
        raffle_payload = {
            "name": "API Test Raffle E2E",
            "draw_interval_type": "daily", # For auto-scheduling next
            "draw_interval_value": 1,
            "ticket_price": 1.0,
            "game_type": "raffle",
            "is_active": True
        }
        cat_response = client.post("/api/lottery_categories/", json=raffle_payload)
        assert cat_response.status_code == 201, cat_response.text
        raffle_cat_id = cat_response.json()["id"]

        # 2. Manually Create a Draw (pending_open)
        open_time_dt = datetime.utcnow() - timedelta(minutes=1) # Ensure it's openable now
        close_time_dt = datetime.utcnow() + timedelta(minutes=5) # Close in 5 mins

        draw_payload = {
            "category_id": raffle_cat_id,
            "scheduled_open_time": open_time_dt.isoformat(),
            "scheduled_close_time": close_time_dt.isoformat(),
        }
        draw_response = client.post("/api/draws/", json=draw_payload)
        assert draw_response.status_code == 201, draw_response.text
        draw_data = draw_response.json()
        draw_id = draw_data["id"]
        assert draw_data["status"] == "pending_open"

        # 3. Process Pending Draws to Open it
        process_response = client.post(f"/api/draws/process_pending_draws?category_id={raffle_cat_id}")
        assert process_response.status_code == 200, process_response.text
        # Check if at least one draw was opened, message might vary slightly
        assert "draw(s) opened" in process_response.json()["message"]

        get_draw_response = client.get(f"/api/draws/{draw_id}")
        assert get_draw_response.status_code == 200, get_draw_response.text
        opened_draw_data = get_draw_response.json()
        assert opened_draw_data["status"] == "open"
        assert opened_draw_data.get("actual_open_time") is not None

        # 4. Buy Tickets
        ticket_payload_w1 = {"wallet_address": "walletRaffle1", "num_tickets": 2, "category_id": raffle_cat_id}
        buy_response_w1 = client.post("/api/tickets/buy", json=ticket_payload_w1)
        assert buy_response_w1.status_code == 200, buy_response_w1.text
        assert len(buy_response_w1.json()["tickets"]) == 2

        ticket_payload_w2 = {"wallet_address": "walletRaffle2", "num_tickets": 3, "category_id": raffle_cat_id}
        buy_response_w2 = client.post("/api/tickets/buy", json=ticket_payload_w2)
        assert buy_response_w2.status_code == 200, buy_response_w2.text
        assert len(buy_response_w2.json()["tickets"]) == 3

        # 5. Close the Draw
        # Ensure close_time_dt is slightly in the past if strict check is done, or ensure it's "open"
        # For this test, we assume manual closure of an "open" draw is fine.
        # If a test needs to wait for scheduled_close_time, mocking time (e.g. with freezegun) is needed.

        close_response = client.post(f"/api/draws/close/{draw_id}")
        assert close_response.status_code == 200, close_response.text
        closed_draw_data = close_response.json()
        assert closed_draw_data["status"] == "completed"
        assert closed_draw_data.get("ledger_hash") is not None
        assert "winners_by_tier" in closed_draw_data

        if closed_draw_data["participants"]:
             assert len(closed_draw_data["winners_by_tier"]) == 1
             winner_info = closed_draw_data["winners_by_tier"][0]
             assert winner_info["prize_tier_name"] == "Raffle Winner"
             assert winner_info["wallet_address"] in ["walletRaffle1", "walletRaffle2"]
        else:
            assert len(closed_draw_data["winners_by_tier"]) == 0


        # 6. Check Winner Announcement
        winners_response = client.get("/api/winners/recent?limit=5")
        assert winners_response.status_code == 200, winners_response.text
        winners_data = winners_response.json()

        found_our_winner = False
        if closed_draw_data["participants"] and closed_draw_data["winners_by_tier"]:
            expected_winner_wallet = closed_draw_data["winners_by_tier"][0]["wallet_address"]
            for winner_entry in winners_data:
                if winner_entry["draw_id"] == draw_id:
                    found_our_winner = True
                    # Anonymized check can be tricky if exact anonymization isn't known/stable
                    # For now, let's trust the previous check on winner_info["wallet_address"]
                    # assert winner_entry["winning_wallet_address_anonymized"].startswith(expected_winner_wallet[:5])
                    assert expected_winner_wallet.startswith(winner_entry["winning_wallet_address_anonymized"][:5])

                    break
            assert found_our_winner, "Closed draw's winner not found in recent winners list."

        # 7. Verify Next Draw Auto-Creation
        all_draws_for_cat_resp = client.get(f"/api/draws/history?category_id={raffle_cat_id}&limit=10")
        assert all_draws_for_cat_resp.status_code == 200, all_draws_for_cat_resp.text
        all_draws_for_cat = all_draws_for_cat_resp.json()

        next_pending_draw = None
        for d_item in all_draws_for_cat: # Renamed d to d_item to avoid conflict
            if d_item["id"] != draw_id and d_item["status"] == "pending_open":
                # Check if its scheduled_open_time matches the closed_draw_data's scheduled_close_time
                # Need to parse string dates to datetime for proper comparison if not already objects
                # For this test, assuming string comparison is okay if format is identical
                if d_item["scheduled_open_time"] == closed_draw_data["scheduled_close_time"]:
                    next_pending_draw = d_item
                    break

        assert next_pending_draw is not None, f"Next pending draw was not auto-created or not found as expected. Draws found: {all_draws_for_cat}"
        assert next_pending_draw["category_id"] == raffle_cat_id
        assert next_pending_draw["scheduled_open_time"] == closed_draw_data["scheduled_close_time"]


    def test_pick_n_game_end_to_end_flow(self, test_client: TestClient):
        """
        Tests a full "Pick N Digits" game flow:
        1. Create a pick_n_digits category.
        2. Manually create a draw.
        3. Open the draw.
        4. Buy tickets with selections (one potential winner, one loser).
        5. Close the draw.
        6. Verify winning_selection and winner.
        7. Verify next draw auto-creation.
        """
        client = test_client
        from datetime import datetime, timedelta

        # 1. Create Pick N Category
        pickn_payload = {
            "name": "API Test Pick3 E2E",
            "draw_interval_type": "hourly",
            "draw_interval_value": 1,
            "ticket_price": 0.5,
            "game_type": "pick_n_digits",
            "game_config": {"num_picks": 3, "min_digit": 0, "max_digit": 9, "allow_duplicates": False},
            "is_active": True,
            "prize_info": {"match_3": "Jackpot"}
        }
        cat_response = client.post("/api/lottery_categories/", json=pickn_payload)
        assert cat_response.status_code == 201, cat_response.text
        pickn_cat_id = cat_response.json()["id"]
        pickn_cat_game_config = pickn_payload["game_config"]


        # 2. Manually Create a Draw
        open_time_dt = datetime.utcnow() - timedelta(minutes=1)
        close_time_dt = datetime.utcnow() + timedelta(minutes=5)
        draw_payload = {
            "category_id": pickn_cat_id,
            "scheduled_open_time": open_time_dt.isoformat(),
            "scheduled_close_time": close_time_dt.isoformat(),
        }
        draw_response = client.post("/api/draws/", json=draw_payload)
        assert draw_response.status_code == 201, draw_response.text
        draw_id = draw_response.json()["id"]

        # 3. Open the Draw
        process_response = client.post(f"/api/draws/process_pending_draws?category_id={pickn_cat_id}")
        assert process_response.status_code == 200, process_response.text
        get_draw_resp = client.get(f"/api/draws/{draw_id}")
        assert get_draw_resp.json()["status"] == "open"


        # 4. Buy Tickets
        # To make this test deterministic for winner, we need to know what the winning numbers will be.
        # The winning numbers depend on the ledger_hash when the draw is closed.
        # For a true E2E test without mocking the RNG deeply, we can't predetermine the winner.
        # So, we'll buy tickets and then check if *a* winner was chosen IF their numbers matched.
        # OR, we can inspect the `winning_selection` after close and see if any purchased ticket matches.

        # Wallet P3 buys a ticket, e.g., [1, 2, 3]
        ticket_payload_w3 = {
            "wallet_address": "walletPickN1", "num_tickets": 1, "category_id": pickn_cat_id,
            "selection": [1, 2, 3]
        }
        buy_response_w3 = client.post("/api/tickets/buy", json=ticket_payload_w3)
        assert buy_response_w3.status_code == 200, buy_response_w3.text
        ticket_w3_id = buy_response_w3.json()["tickets"][0]

        # Wallet P4 buys another ticket, e.g., [7, 8, 9]
        ticket_payload_w4 = {
            "wallet_address": "walletPickN2", "num_tickets": 1, "category_id": pickn_cat_id,
            "selection": [7, 8, 9]
        }
        buy_response_w4 = client.post("/api/tickets/buy", json=ticket_payload_w4)
        assert buy_response_w4.status_code == 200, buy_response_w4.text


        # 5. Close the Draw
        close_response = client.post(f"/api/draws/close/{draw_id}")
        assert close_response.status_code == 200, close_response.text
        closed_draw_data = close_response.json()

        assert closed_draw_data["status"] == "completed"
        assert closed_draw_data.get("ledger_hash") is not None
        assert "winning_selection" in closed_draw_data
        assert closed_draw_data["winning_selection"] is not None
        winning_picks = closed_draw_data["winning_selection"].get("picks")
        assert isinstance(winning_picks, list)
        assert len(winning_picks) == pickn_cat_game_config["num_picks"]
        for pick in winning_picks:
            assert pickn_cat_game_config["min_digit"] <= pick <= pickn_cat_game_config["max_digit"]
        if not pickn_cat_game_config["allow_duplicates"]:
            assert len(set(winning_picks)) == len(winning_picks)

        # 6. Verify winner (if any)
        winners_by_tier = closed_draw_data.get("winners_by_tier", [])
        expected_winner_wallet = None
        if winning_picks == [1, 2, 3]: # Wallet P3's pick
            expected_winner_wallet = "walletPickN1"
        elif winning_picks == [7, 8, 9]: # Wallet P4's pick
            expected_winner_wallet = "walletPickN2"

        if expected_winner_wallet:
            assert len(winners_by_tier) == 1, f"Expected 1 winner, got {len(winners_by_tier)}. Winning picks: {winning_picks}"
            winner_info = winners_by_tier[0]
            assert winner_info["wallet_address"] == expected_winner_wallet
            assert winner_info["prize_tier_name"] == f"Jackpot - Match {pickn_cat_game_config['num_picks']}"
            assert winner_info["ticket_id"] == (ticket_w3_id if expected_winner_wallet == "walletPickN1" else buy_response_w4.json()["tickets"][0])
        else:
            assert len(winners_by_tier) == 0, f"Expected 0 winners if picks {winning_picks} didn't match [1,2,3] or [7,8,9]. Winners: {winners_by_tier}"


        # 7. Verify Next Draw Auto-Creation (similar to raffle test)
        all_draws_for_cat_resp = client.get(f"/api/draws/history?category_id={pickn_cat_id}&limit=10")
        assert all_draws_for_cat_resp.status_code == 200, all_draws_for_cat_resp.text
        all_draws_for_cat = all_draws_for_cat_resp.json()

        next_pending_draw = None
        for d_item in all_draws_for_cat:
            if d_item["id"] != draw_id and d_item["status"] == "pending_open":
                if d_item["scheduled_open_time"] == closed_draw_data["scheduled_close_time"]:
                    next_pending_draw = d_item
                    break

        assert next_pending_draw is not None, f"Next pending PickN draw was not auto-created or not found. Draws: {all_draws_for_cat}"
        assert next_pending_draw["category_id"] == pickn_cat_id


    def test_referral_system_basic_flow(self, test_client: TestClient):
        """
        Tests basic referral system flow:
        1. Referrer gets a referral code.
        2. Referee uses the code during their first ticket purchase.
        3. Verify referral link creation and status update.
        4. Verify referrer and referee stats.
        """
        client = test_client
        from datetime import datetime, timedelta

        # --- Setup: Create a category and an open draw for ticket purchase ---
        ref_category_payload = {
            "name": "Referral Test Cat", "draw_interval_type": "manual",
            "ticket_price": 1.0, "game_type": "raffle", "is_active": True
        }
        cat_resp = client.post("/api/lottery_categories/", json=ref_category_payload)
        assert cat_resp.status_code == 201, cat_resp.text
        ref_cat_id = cat_resp.json()["id"]

        open_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
        close_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        draw_payload = {
            "category_id": ref_cat_id,
            "scheduled_open_time": open_time,
            "scheduled_close_time": close_time
        }
        draw_resp = client.post("/api/draws/", json=draw_payload)
        assert draw_resp.status_code == 201, draw_resp.text
        # draw_id = draw_resp.json()["id"] # No, this is the draw_id of the just created draw

        # We need to get the ID of the *open* draw that the ticket will be bought for
        # The ticket purchase logic handles finding/creating an open draw.
        # For this test, ensure one is open by processing.
        process_resp = client.post(f"/api/draws/process_pending_draws?category_id={ref_cat_id}")
        assert process_resp.status_code == 200, process_resp.text
        # --- End Setup ---

        referrer_wallet = "referrerWallet123"
        referee_wallet = "refereeWallet456"

        # 1. Referrer gets a referral code
        code_payload = {"wallet_address": referrer_wallet}
        code_response = client.post("/api/referrals/code", json=code_payload)
        assert code_response.status_code == 200, code_response.text
        referrer_code_data = code_response.json()
        assert "code" in referrer_code_data
        referral_code_str = referrer_code_data["code"]
        assert referrer_code_data["usage_count"] == 0

        # 2. Referee uses the code during their first ticket purchase
        buy_payload_referee = {
            "wallet_address": referee_wallet,
            "num_tickets": 1,
            "category_id": ref_cat_id,
            "referral_code": referral_code_str
        }
        buy_response_referee = client.post("/api/tickets/buy", json=buy_payload_referee)
        assert buy_response_referee.status_code == 200, buy_response_referee.text

        # 3. Verify referral link creation and status update (implicitly done by API)
        # We check this via stats endpoints.

        # 4. Verify referrer stats
        referrer_stats_response = client.get(f"/api/referrals/stats/{referrer_wallet}")
        assert referrer_stats_response.status_code == 200, referrer_stats_response.text
        referrer_stats = referrer_stats_response.json()
        assert referrer_stats["referral_code"] == referral_code_str
        assert referrer_stats["referral_code_usage_count"] == 1
        assert referrer_stats["successful_referrals_count"] == 1

        # 5. Verify referee stats
        referee_stats_response = client.get(f"/api/referrals/stats/{referee_wallet}")
        assert referee_stats_response.status_code == 200, referee_stats_response.text
        referee_stats = referee_stats_response.json()
        assert referee_stats["referral_code"] is None
        assert referee_stats["referred_by"] == referrer_wallet

        # 6. Referee tries to use a code again
        referrer2_wallet = "referrerWallet789"
        code_payload2 = {"wallet_address": referrer2_wallet}
        code_response2 = client.post("/api/referrals/code", json=code_payload2)
        referral_code_str2 = code_response2.json()["code"]

        buy_payload_referee_again = {
            "wallet_address": referee_wallet,
            "num_tickets": 1,
            "category_id": ref_cat_id,
            "referral_code": referral_code_str2
        }
        buy_response_referee_again = client.post("/api/tickets/buy", json=buy_payload_referee_again)
        assert buy_response_referee_again.status_code == 200

        referrer_stats_response_after = client.get(f"/api/referrals/stats/{referrer_wallet}")
        assert referrer_stats_response_after.status_code == 200
        referrer_stats_after = referrer_stats_response_after.json()
        assert referrer_stats_after["referral_code_usage_count"] == 1
        assert referrer_stats_after["successful_referrals_count"] == 1

        referrer2_stats_response = client.get(f"/api/referrals/stats/{referrer2_wallet}")
        assert referrer2_stats_response.status_code == 200
        referrer2_stats = referrer2_stats_response.json()
        assert referrer2_stats["referral_code_usage_count"] == 0
        assert referrer2_stats["successful_referrals_count"] == 0


    def test_invalid_inputs_and_error_conditions(self, test_client: TestClient):
        """
        Tests various invalid inputs and error conditions for different endpoints.
        """
        client = test_client
        from datetime import datetime, timedelta

        # Setup a valid category and draw for some tests
        category_payload = {
            "name": "Error Test Cat", "draw_interval_type": "manual",
            "ticket_price": 1.0, "game_type": "raffle", "is_active": True
        }
        cat_resp = client.post("/api/lottery_categories/", json=category_payload)
        assert cat_resp.status_code == 201
        error_test_cat_id = cat_resp.json()["id"]

        pickn_category_payload = {
            "name": "Error PickN Cat", "draw_interval_type": "manual", "ticket_price": 1.0,
            "game_type": "pick_n_digits",
            "game_config": {"num_picks": 3, "min_digit": 0, "max_digit": 9, "allow_duplicates": False},
            "is_active": True
        }
        pickn_cat_resp = client.post("/api/lottery_categories/", json=pickn_category_payload)
        assert pickn_cat_resp.status_code == 201
        error_test_pickn_cat_id = pickn_cat_resp.json()["id"]


        # Test 5.1: Ticket purchase with invalid category_id
        invalid_cat_payload = {
            "wallet_address": "walletError1", "num_tickets": 1,
            "category_id": "non_existent_category_id"
        }
        response = client.post("/api/tickets/buy", json=invalid_cat_payload)
        assert response.status_code == 404 # Category not found

        # Test 5.2: Ticket purchase for PickN game with missing selection
        missing_selection_payload = {
            "wallet_address": "walletError2", "num_tickets": 1,
            "category_id": error_test_pickn_cat_id
            # "selection" is missing
        }
        response = client.post("/api/tickets/buy", json=missing_selection_payload)
        assert response.status_code == 400 # Selection required for pick_n_digits
        assert "Selection is required" in response.json()["detail"]

        # Test 5.3: Ticket purchase for PickN game with invalid selection (e.g., too few numbers)
        invalid_selection_payload = {
            "wallet_address": "walletError3", "num_tickets": 1,
            "category_id": error_test_pickn_cat_id,
            "selection": [1, 2] # Expecting 3 picks
        }
        response = client.post("/api/tickets/buy", json=invalid_selection_payload)
        assert response.status_code == 400
        assert "Expected 3 picks" in response.json()["detail"]

        # Test 5.4: Ticket purchase for Raffle game with selection data provided
        raffle_with_selection_payload = {
            "wallet_address": "walletError4", "num_tickets": 1,
            "category_id": error_test_cat_id, # This is a raffle category
            "selection": [1,2,3]
        }
        response = client.post("/api/tickets/buy", json=raffle_with_selection_payload)
        assert response.status_code == 400
        assert "Selection data is not applicable" in response.json()["detail"]

        # Test 5.5: Close a non-existent draw
        response = client.post("/api/draws/close/non_existent_draw_id")
        assert response.status_code == 404 # Draw not found (assuming ID format doesn't cause 422 first)
                                           # If ID format is checked, it might be 422 for "invalid ObjectId" like string

        # Test 5.6: Create a draw with invalid category_id
        invalid_draw_payload = {
            "category_id": "non_existent_category_id",
            "scheduled_open_time": (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            "scheduled_close_time": (datetime.utcnow() + timedelta(minutes=20)).isoformat()
        }
        response = client.post("/api/draws/", json=invalid_draw_payload)
        assert response.status_code == 400 # Category not found for draw creation
        assert "not found" in response.json()["detail"]

        # Test 5.7: Create a draw with open time >= close time
        bad_times_payload = {
            "category_id": error_test_cat_id,
            "scheduled_open_time": (datetime.utcnow() + timedelta(minutes=20)).isoformat(),
            "scheduled_close_time": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        response = client.post("/api/draws/", json=bad_times_payload)
        assert response.status_code == 400
        assert "open time must be before scheduled close time" in response.json()["detail"]

        # Test 5.8: Use an invalid referral code format (too short/long - if model has length validation)
        # Our model has min_length=6, max_length=10 for referral_code in TicketPurchaseRequest
        # First, ensure a valid draw is open for error_test_cat_id
        open_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
        close_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        client.post("/api/draws/", json={
            "category_id": error_test_cat_id,
            "scheduled_open_time": open_time,
            "scheduled_close_time": close_time
        }) # Create draw
        client.post(f"/api/draws/process_pending_draws?category_id={error_test_cat_id}") # Open it

        short_ref_code_payload = {
            "wallet_address": "walletError5", "num_tickets": 1, "category_id": error_test_cat_id,
            "referral_code": "abc" # Too short
        }
        response = client.post("/api/tickets/buy", json=short_ref_code_payload)
        assert response.status_code == 422 # Pydantic validation error for field length


# More test classes or functions can be added for other API modules/flows
# e.g., TestDrawFlows, TestTicketFlows, TestReferralFlows
