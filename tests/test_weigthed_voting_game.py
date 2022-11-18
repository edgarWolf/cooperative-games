import pytest
from games.weighted_voting_game import WeightedVotingGame
from indices.power_indices import *


def test_constructor():
    """Test the weighted voting game constructor."""
    # Test a valid weighted voting game.
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_coalitions = [
        (1,), (2,), (3,),
        (1, 2,), (1, 3,), (2, 3,),
        (1, 2, 3,),
    ]
    assert set(game.contributions) == set(weights)
    assert game.quorum == quorum
    assert set(game.players) == set([1, 2, 3])
    assert set(game.coalitions) == set(expected_coalitions)

    # Test invalid length of weigths vector:
    with pytest.raises(ValueError, match="No contributions provided."):
        weights = []
        game = WeightedVotingGame(contributions=weights, quorum=quorum)

    # Test invalud weights vector:
    with pytest.raises(ValueError, match="Weight vector containns nonallowed negative weights."):
        weights = [-1, 0, 1]
        game = WeightedVotingGame(contributions=weights, quorum=quorum)

    # Test invalid quorum:
    with pytest.raises(ValueError, match="Qurom is only allowed to be greater than 0."):
        weights = [1, 2, 3, ]
        quorum = -1
        game = WeightedVotingGame(contributions=weights, quorum=quorum)


def test_characteristic_function():
    """Test the characteristic function of a weighted voting game."""
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)

    # We can find the winning coalitions (1, 3), (2,3) and (1, 2, 3)
    excpected_output = {
        (1,): 0, (2,): 0, (3,): 0,
        (1, 2,): 0, (1, 3,): 1, (2, 3,): 1,
        (1, 2, 3,): 1
    }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output

    # Special case: No winning coalition.
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    excpected_output = {
        (1,): 0, (2,): 0, (3,): 0,
        (1, 2,): 0, (1, 3,): 0, (2, 3,): 0,
        (1, 2, 3,): 0
    }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output

    # Special case: All coalitions are winning coalitions..
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    excpected_output = {
        (1,): 1, (2,): 1, (3,): 1,
        (1, 2,): 1, (1, 3,): 1, (2, 3,): 1,
        (1, 2, 3,): 1
    }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output

    # Edge case: 1 player.
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)

    excpected_output = {(1,): 1}
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output


def test_null_player():
    contributions = [50, 30, 20, 0]
    quorum = 51
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = [4]
    actual_output = game.null_players()
    assert expected_output == actual_output

    contributions = [50, 30, 20, 0]
    quorum = 200
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = [1, 2, 3, 4]
    actual_output = game.null_players()
    assert expected_output == actual_output

    contributions = [50, 30, 20, 1]
    quorum = 1
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = []
    actual_output = game.null_players()
    assert expected_output == actual_output

    contributions = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = []
    actual_output = game.null_players()
    assert expected_output == actual_output

    contributions = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = [1]
    actual_output = game.null_players()
    assert expected_output == actual_output


def test_get_winning_coalitions():
    """Test the winning coalitions method for weighted voting games."""
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    excpected_output = [(1, 3,), (2, 3,), (1, 2, 3,)]
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output

    # Special case: No winning coalition:
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    excpected_output = []
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output

    # Special case: All coalitions are winning coalitions.
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    excpected_output = [(1,), (2,), (3,), (1, 2,), (1, 3,), (2, 3,), (1, 2, 3), ]
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output

    # Edge case: 1 player:
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    excpected_output = [(1,)]
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output


def test_winning_coalitions_without_null_players():
    contributions = [50, 30, 20, 0]
    quorum = 51
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = [(1, 2), (1, 3,), (1, 2, 3)]
    actual_output = game.winning_coalitions_without_null_players()
    assert expected_output == actual_output

    contributions = [50, 30, 20, 0]
    quorum = 200
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = []
    actual_output = game.winning_coalitions_without_null_players()
    assert expected_output == actual_output

    contributions = [50, 30, 20, 1]
    quorum = 1
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = [(1,), (2,), (3,), (4,), (1, 2), (1, 3,), (1, 4,), (2, 3), (2, 4), (3, 4), (1, 2, 3), (1, 2, 4,),
                       (1, 3, 4), (2, 3, 4), (1, 2, 3, 4)]
    actual_output = game.winning_coalitions_without_null_players()
    assert expected_output == actual_output

    contributions = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = [(1,)]
    actual_output = game.winning_coalitions_without_null_players()
    assert expected_output == actual_output

    contributions = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=contributions, quorum=quorum)
    expected_output = []
    actual_output = game.winning_coalitions_without_null_players()
    assert expected_output == actual_output


def test_get_pivot_players():
    """Test the pivot players method for weighted voting games."""
    # Test usual cases.
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = {
        (1, 3): [1, 3], (2, 3,): [2, 3],
        (1, 2, 3,): [3]
    }
    actual_output = game.get_pivot_players()
    assert expected_output == actual_output

    expected_output = {
        (1,): [], (2,): [], (3,): [],
        (1, 2): [], (1, 3): [1, 3], (2, 3,): [2, 3],
        (1, 2, 3,): [3]
    }
    actual_output = game.get_pivot_players(all_coalitions=True)
    assert expected_output == actual_output

    # Special case: No winning coalitions.
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = {}
    actual_output = game.get_pivot_players()
    assert actual_output == expected_output

    expected_output = {
        (1,): [], (2,): [], (3,): [],
        (1, 2): [], (1, 3): [], (2, 3,): [],
        (1, 2, 3,): []
    }
    actual_output = game.get_pivot_players(all_coalitions=True)
    assert expected_output == actual_output

    # Edge case: 1 player.
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = {(1,): [1]}
    actual_output = game.get_pivot_players()
    assert expected_output == actual_output


def test_get_minimal_winning_coalitions():
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 3), (2, 3)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 2), (1, 3)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    # Special case: No winning coalitions.
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = []
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    # Special case: Only one winning coalition which is minimal.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 2, 3, 4)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    # Edge case: 1 player.
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1,)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output


def test_preferred_player():
    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = 1
    actual_output = game.preferred_player(1, 2)
    assert expected_output == actual_output
    actual_output = game.preferred_player(2, 1)
    assert expected_output == actual_output
    expected_output = 1
    actual_output = game.preferred_player(1, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 1)
    assert expected_output == actual_output
    expected_output = None
    actual_output = game.preferred_player(2, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 2)
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = 1
    actual_output = game.preferred_player(1, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 1)
    assert expected_output == actual_output
    expected_output = 2
    actual_output = game.preferred_player(2, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 2)
    assert expected_output == actual_output
    expected_output = 1
    actual_output = game.preferred_player(1, 2)
    assert expected_output == actual_output
    actual_output = game.preferred_player(2, 1)
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = 1
    actual_output = game.preferred_player(1, 2)
    assert expected_output == actual_output
    actual_output = game.preferred_player(2, 1)
    assert expected_output == actual_output
    actual_output = game.preferred_player(1, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 1)
    assert expected_output == actual_output
    actual_output = game.preferred_player(1, 4)
    assert expected_output == actual_output
    actual_output = game.preferred_player(4, 1)
    assert expected_output == actual_output
    expected_output = None
    actual_output = game.preferred_player(2, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 2)
    assert expected_output == actual_output
    actual_output = game.preferred_player(2, 4)
    assert expected_output == actual_output
    actual_output = game.preferred_player(4, 2)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 4)
    assert expected_output == actual_output
    actual_output = game.preferred_player(4, 3)
    assert expected_output == actual_output

    weights = [5, 2, 2, 1, 1]
    quorum = 6
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = 1
    actual_output = game.preferred_player(1, 2)
    assert expected_output == actual_output
    actual_output = game.preferred_player(2, 1)
    assert expected_output == actual_output
    expected_output = 1
    actual_output = game.preferred_player(1, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 1)
    assert expected_output == actual_output
    expected_output = 1
    actual_output = game.preferred_player(1, 4)
    assert expected_output == actual_output
    actual_output = game.preferred_player(4, 1)
    assert expected_output == actual_output
    expected_output = 1
    actual_output = game.preferred_player(1, 5)
    assert expected_output == actual_output
    actual_output = game.preferred_player(5, 1)
    assert expected_output == actual_output
    expected_output = None
    actual_output = game.preferred_player(2, 3)
    assert expected_output == actual_output
    actual_output = game.preferred_player(3, 2)
    assert expected_output == actual_output
    expected_output = 2
    actual_output = game.preferred_player(2, 4)
    assert expected_output == actual_output
    actual_output = game.preferred_player(4, 2)
    assert expected_output == actual_output
    expected_output = 2
    actual_output = game.preferred_player(2, 5)
    assert expected_output == actual_output
    actual_output = game.preferred_player(5, 2)
    assert expected_output == actual_output
    expected_output = 3
    actual_output = game.preferred_player(3, 4)
    assert expected_output == actual_output
    actual_output = game.preferred_player(4, 3)
    assert expected_output == actual_output
    expected_output = 3
    actual_output = game.preferred_player(3, 5)
    assert expected_output == actual_output
    actual_output = game.preferred_player(5, 3)
    assert expected_output == actual_output
    expected_output = None
    actual_output = game.preferred_player(4, 5)
    assert expected_output == actual_output
    actual_output = game.preferred_player(5, 4)
    assert expected_output == actual_output

    # Test invalid players.
    with pytest.raises(ValueError, match="Specified players are note part of the game."):
        game.preferred_player(0, 1)
        game.preferred_player(1, 99)
        game.preferred_player(-1, 1)


def test_get_shift_minimal_winning_coalitions():
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 3)]
    actual_output = game.get_shift_winning_coalitions()
    assert expected_output == actual_output

    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 2), (1, 3)]
    actual_output = game.get_shift_winning_coalitions()
    assert expected_output == actual_output

    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 2)]
    actual_output = game.get_shift_winning_coalitions()
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 2, 3, 4)]
    actual_output = game.get_shift_winning_coalitions()
    assert expected_output == actual_output

    weights = [5, 40, 26, 25, 4]
    quorum = 51
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(3, 4,)]
    actual_output = game.get_shift_winning_coalitions()
    assert expected_output == actual_output

    weights = [5, 2, 2, 1, 1]
    quorum = 6
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [(1, 4), (1, 5,), (2, 3, 4, 5), ]
    actual_output = game.get_shift_winning_coalitions()
    assert expected_output == actual_output


def test_player_ranking():
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = {
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): None
    }
    actual_output = game.get_player_ranking()
    assert expected_output == actual_output

    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = {
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): 2,
    }
    actual_output = game.get_player_ranking()
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = {
        (1, 2): 1,
        (1, 3): 1,
        (1, 4): 1,
        (2, 3): None,
        (2, 4): None,
        (3, 4): None

    }
    actual_output = game.get_player_ranking()
    assert expected_output == actual_output


def test_shapley_shubik_index():
    # Instantiate instance of shapley shubik index.
    shapley = ShapleyShubikIndex()

    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [2 / 3, 1 / 6, 1 / 6]
    actual_output = shapley.compute(game=game)
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = shapley.compute(game=game)
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = shapley.compute(game=game)
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = shapley.compute(game=game)
    assert expected_output == actual_output


def test_banzhaf_index():
    # Instantiate instance of banzhaf index.
    banzhaf = BanzhafIndex()

    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [3 / 5, 1 / 5, 1 / 5]
    actual_output = banzhaf.compute(game=game)
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = banzhaf.compute(game=game)
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = banzhaf.compute(game=game)
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = banzhaf.compute(game=game)
    assert expected_output == actual_output


def test_johnston_index():
    # Instantiate instance of johnston index.
    johnston = JohnstonIndex()

    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [2 / 3, 1 / 6, 1 / 6]
    actual_output = johnston.compute(game=game)
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = johnston.compute(game=game)
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = johnston.compute(game=game)
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = johnston.compute(game=game)
    assert expected_output == actual_output


def test_pgi_index():
    # Instantiate instance of banzhaf index.
    pgi = PublicGoodIndex()

    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 4, 1 / 4]
    actual_output = pgi.compute(game=game)
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = pgi.compute(game=game)
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = pgi.compute(game=game)
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = pgi.compute(game=game)
    assert expected_output == actual_output


def test_phi_index():
    # Instantiate instance of banzhaf index.
    phi = PublicHelpIndex()

    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [3 / 7, 2 / 7, 2 / 7]
    actual_output = phi.compute(game=game)
    assert expected_output == pytest.approx(actual_output)

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [2 / 5, 2 / 5, 1 / 5]
    actual_output = phi.compute(game=game)
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = phi.compute(game=game)
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = phi.compute(game=game)
    assert expected_output == actual_output


def test_shift_index():
    # Instantiate instance of banzhaf index.
    shift = ShiftIndex()

    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 0, 1 / 2]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output

    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 4, 1 / 4]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output

    weights = [5, 2, 2, 1, 1]
    quorum = 6
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 8, 1 / 8, 1 / 4, 1 / 4]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output

    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output

    weights = [5, 40, 26, 25, 4]
    quorum = 51
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 1 / 2, 1 / 2, 0]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = shift.compute(game=game)
    assert expected_output == actual_output


def test_egalitarian_index():
    e = EgalitarianIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 3, 1 / 3, 1 / 3]
    actual_output = e.compute(game=game)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = e.compute(game=game)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = e.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = e.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = e.compute(game=game)
    assert expected_output == actual_output


def test_gn_minus_index():
    g = GnMinusIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = g.compute(game=game)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = g.compute(game=game)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = g.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = g.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = g.compute(game=game)
    assert expected_output == actual_output


def test_nevison_index():
    nevison = NevisonIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [2 / 4, 2 / 4, 1 / 4]
    actual_output = nevison.compute(game=game)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 8, 1 / 8, 1 / 8, 1 / 8]
    actual_output = nevison.compute(game=game)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = nevison.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = nevison.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = nevison.compute(game=game)
    assert expected_output == actual_output


def test_koenig_and_braeuninger_index():
    kb = KoenigAndBraeuningerIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1, 1, 1 / 2]
    actual_output = kb.compute(game=game)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1, 1, 1, 1]
    actual_output = kb.compute(game=game)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = kb.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = kb.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = kb.compute(game=game)
    assert expected_output == actual_output


def test_rae_index():
    rae = RaeIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [3 / 4, 3 / 4, 1 / 2]
    actual_output = rae.compute(game=game, normalized=False)
    assert expected_output == actual_output

    # Normalized
    expected_output = [3 / 8, 3 / 8, 1 / 4]
    actual_output = rae.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [9 / 16, 9 / 16, 9 / 16, 9 / 16]
    actual_output = rae.compute(game=game, normalized=False)
    assert expected_output == actual_output

    # Normalized
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = rae.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 1 / 2]
    actual_output = rae.compute(game=game, normalized=False)
    assert expected_output == actual_output

    # Normalized
    expected_output = [1 / 3, 1 / 3, 1 / 3]
    actual_output = rae.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = rae.compute(game=game, normalized=False)
    assert expected_output == actual_output

    # Normalized
    expected_output = [1]
    actual_output = rae.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2]
    actual_output = rae.compute(game=game, normalized=False)
    assert expected_output == actual_output

    # Normalized
    expected_output = [1]
    actual_output = rae.compute(game=game, normalized=True)
    assert expected_output == actual_output

def test_solidarity_value():
    s = SolidarityValue()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [7 / 18, 7 / 18, 4 / 18]
    actual_output = s.compute(game=game)
    assert expected_output == pytest.approx(actual_output)

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = s.compute(game=game)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = s.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = s.compute(game=game)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = s.compute(game=game)
    assert expected_output == actual_output


def test_holler_index():
    holler = HollerIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1, 1, 0]
    actual_output = holler.compute(game=game, normalized=False)
    assert  expected_output == actual_output

    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = holler.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1, 1, 1, 1]
    actual_output = holler.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = holler.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = holler.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [0, 0, 0]
    actual_output = holler.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = holler.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [1]
    actual_output = holler.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = holler.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [0]
    actual_output = holler.compute(game=game, normalized=True)
    assert expected_output == actual_output

def test_deegan_packel_index():
    dpi = DeeganPackelIndex()

    weights = [1, 1, 0]
    quorum = 2
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = dpi.compute(game=game, normalized=False)
    assert  expected_output == actual_output

    expected_output = [1 / 2, 1 / 2, 0]
    actual_output = dpi.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = dpi.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    actual_output = dpi.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1, 1, 0]
    quorum = 5
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0, 0, 0]
    actual_output = dpi.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [0, 0, 0]
    actual_output = dpi.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1]
    quorum = 1
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [1]
    actual_output = dpi.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [1]
    actual_output = dpi.compute(game=game, normalized=True)
    assert expected_output == actual_output

    weights = [1]
    quorum = 99
    game = WeightedVotingGame(contributions=weights, quorum=quorum)
    expected_output = [0]
    actual_output = dpi.compute(game=game, normalized=False)
    assert expected_output == actual_output

    expected_output = [0]
    actual_output = dpi.compute(game=game, normalized=True)
    assert expected_output == actual_output
