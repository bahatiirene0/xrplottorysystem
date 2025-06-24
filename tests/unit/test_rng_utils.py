import pytest
from rng.utils import generate_winning_picks, calculate_winner_index

class TestRNGUtils:

    def test_calculate_winner_index_deterministic(self):
        assert calculate_winner_index("seed1", 100) == calculate_winner_index("seed1", 100)
        assert calculate_winner_index("seed1", 100) != calculate_winner_index("seed2", 100)

    def test_calculate_winner_index_range(self):
        for i in range(100): # Test a few times with different seeds
            seed = f"test_seed_{i}"
            num_participants = 10
            winner_idx = calculate_winner_index(seed, num_participants)
            assert 0 <= winner_idx < num_participants

    def test_calculate_winner_index_invalid_participants(self):
        with pytest.raises(ValueError, match="Number of participants must be positive."):
            calculate_winner_index("seed", 0)
        with pytest.raises(ValueError, match="Number of participants must be positive."):
            calculate_winner_index("seed", -5)


    # Tests for generate_winning_picks
    def test_generate_winning_picks_deterministic(self):
        seed = "test_seed_for_picks"
        game_config = {"num_picks": 3, "min_digit": 0, "max_digit": 9, "allow_duplicates": False}
        picks1 = generate_winning_picks(seed, game_config)
        picks2 = generate_winning_picks(seed, game_config)
        assert picks1 == picks2

        game_config_dup = {"num_picks": 3, "min_digit": 0, "max_digit": 9, "allow_duplicates": True}
        picks_dup1 = generate_winning_picks(seed, game_config_dup)
        picks_dup2 = generate_winning_picks(seed, game_config_dup)
        assert picks_dup1 == picks_dup2

        # Different seed should produce different results (highly likely)
        assert picks1 != generate_winning_picks("another_seed", game_config)


    def test_generate_winning_picks_correct_number_and_range(self):
        seed = "another_seed"
        game_config = {"num_picks": 5, "min_digit": 1, "max_digit": 50, "allow_duplicates": True}
        picks = generate_winning_picks(seed, game_config)

        assert len(picks) == game_config["num_picks"]
        for pick in picks:
            assert game_config["min_digit"] <= pick <= game_config["max_digit"]

    def test_generate_winning_picks_no_duplicates(self):
        seed = "no_dup_seed"
        # Ensure range is large enough for unique picks
        game_config = {"num_picks": 5, "min_digit": 0, "max_digit": 9, "allow_duplicates": False}
        picks = generate_winning_picks(seed, game_config)

        assert len(picks) == game_config["num_picks"]
        assert len(set(picks)) == game_config["num_picks"] # Check for uniqueness
        for pick in picks:
            assert game_config["min_digit"] <= pick <= game_config["max_digit"]

    def test_generate_winning_picks_allow_duplicates(self):
        seed = "allow_dup_seed"
        # Forcing a small range to make duplicates highly probable if allowed
        game_config = {"num_picks": 10, "min_digit": 0, "max_digit": 2, "allow_duplicates": True}
        picks = generate_winning_picks(seed, game_config)

        assert len(picks) == game_config["num_picks"]
        for pick in picks:
            assert game_config["min_digit"] <= pick <= game_config["max_digit"]
        # It's hard to assert that duplicates *will* occur, but we trust the logic if no error.

    def test_generate_winning_picks_invalid_config(self):
        seed = "test_seed"
        with pytest.raises(ValueError, match="'num_picks' must be a positive integer."):
            generate_winning_picks(seed, {"num_picks": 0, "min_digit": 0, "max_digit": 9})

        with pytest.raises(ValueError, match="'min_val' cannot be greater than 'max_val'."):
            generate_winning_picks(seed, {"num_picks": 3, "min_digit": 10, "max_digit": 0})

        with pytest.raises(ValueError, match="'num_picks' cannot be greater than the range of possible unique values if duplicates are not allowed."):
            generate_winning_picks(seed, {"num_picks": 5, "min_digit": 0, "max_digit": 3, "allow_duplicates": False})

        # This test case specifically checks when num_picks is a string.
        # The first validation it hits is `isinstance(num_picks, int)`.
        with pytest.raises(ValueError, match="'num_picks' must be a positive integer."):
            generate_winning_picks(seed, {"num_picks": "3", "min_digit": 0, "max_digit": 9})

        # This test case checks when min_digit is a string, after num_picks is confirmed as int.
        with pytest.raises(ValueError, match="'min_digit' and 'max_digit' must be integers."):
            generate_winning_picks(seed, {"num_picks": 3, "min_digit": "0", "max_digit": 9})


    def test_generate_winning_picks_edge_case_range_equals_num_picks_no_duplicates(self):
        seed = "edge_case_seed"
        game_config = {"num_picks": 3, "min_digit": 1, "max_digit": 3, "allow_duplicates": False}
        picks = generate_winning_picks(seed, game_config)
        assert len(picks) == 3
        assert sorted(picks) == [1, 2, 3] # Must be these three numbers in some order
        assert len(set(picks)) == 3

    # Example of a test that might fail if the HMAC generation is not robust enough
    # for very tight non-duplicate constraints, though the current implementation has fallbacks.
    # This test is more about stressing the non-duplicate finding logic.
    # def test_generate_winning_picks_stress_no_duplicates(self):
    #     seed = "stress_seed"
    #     # Max number of unique picks from a small range
    #     game_config = {"num_picks": 7, "min_digit": 0, "max_digit": 6, "allow_duplicates": False}
    #     picks = generate_winning_picks(seed, game_config)
    #     assert len(picks) == 7
    #     assert len(set(picks)) == 7
    #     assert min(picks) == 0 and max(picks) == 6
    #     assert all(0 <= p <= 6 for p in picks)
    #     print(f"Stress test (no_dup) picks: {picks}") # Visual check
