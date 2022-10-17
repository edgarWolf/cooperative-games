import pytest
from games.weighted_voting_game import WeightedVotingGame


def test_constructor():
    """Test the weighted voting game constructor."""
    # Test a valid weighted voting game.
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_coalitions = [
        (1,), (2,), (3,),
        (1,2,), (1,3,), (2,3,),
        (1,2,3,),
    ]
    assert set(game.weigths) == set(weights)
    assert game.quorum == quorum
    assert set(game.players) == set([1, 2, 3])
    assert set(game.coalitions) == set(expected_coalitions)

    # Test invalid length of weigths vector:
    with pytest.raises(ValueError, match="Length of player vector and weight vector don't match."):
        weights = []
        game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)

    with pytest.raises(ValueError, match="Length of player vector and weight vector don't match."):
            weights = [1, 2, 3, 4]
            game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)

    # Test invalud weights vector:
    with pytest.raises(ValueError, match="Weight vector containns nonallowed negative weights."):
        weights = [-1, 0, 1]
        game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    
    # Test invalid quorum:
    with pytest.raises(ValueError, match="Qurom is only allowed to be greater than 0."):
        weights = [1, 2, 3, ]
        quorum = -1
        game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)


def test_characteristic_function():
    """Test the characteristic function of a weighted voting game."""
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    
    # We can find the winning coalitions (1, 3), (2,3) and (1, 2, 3)
    excpected_output = {
        (1,) : 0, (2,) : 0, (3,) : 0,
        (1, 2,) : 0, (1, 3,) : 1, (2, 3,) : 1,
        (1, 2, 3,) : 1
    }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output

    # Special case: No winning coalition.
    quorum = 99
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    excpected_output = {
        (1,) : 0, (2,) : 0, (3,) : 0,
        (1, 2,) : 0, (1, 3,) : 0, (2, 3,) : 0,
        (1, 2, 3,) : 0
    }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output

    # Special case: All coalitions are winning coalitions..
    quorum = 1
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    excpected_output = {
        (1,) : 1, (2,) : 1, (3,) : 1,
        (1, 2,) : 1, (1, 3,) : 1, (2, 3,) : 1,
        (1, 2, 3,) : 1
    }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output

    # Edge case: 1 player.
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)

    excpected_output = { (1,) : 1 }
    actual_output = game.characteristic_function()
    assert excpected_output == actual_output


def test_get_winning_coalitions():
    """Test the winning coalitions method for weighted voting games."""
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    excpected_output = [(1,3,), (2,3,), (1,2,3,)]
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output

    # Special case: No winning coalition:
    quorum = 99
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    excpected_output = []
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output

    # Special case: All coalitions are winning coalitions.
    quorum = 1
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    excpected_output = [(1,), (2,), (3,), (1,2,), (1,3,), (2,3,), (1,2,3),]
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output

    # Edge case: 1 player:
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)
    excpected_output = [(1,)]
    actual_output = game.get_winning_coalitions()
    assert excpected_output == actual_output


def test_get_pivot_players():
    """Test the pivot players method for weighted voting games."""
    # Test usual cases.
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = {
        (1,3) : [1, 3], (2,3,) : [2,3],
        (1,2,3,) : [3]
    }
    actual_output = game.get_pivot_players()
    assert expected_output == actual_output

    expected_output = {
        (1,): [], (2,) : [], (3,) : [],
        (1,2) : [], (1,3) : [1, 3], (2,3,) : [2,3],
        (1,2,3,) : [3]
    }
    actual_output = game.get_pivot_players(all_coalitions=True)
    assert expected_output == actual_output

    # Special case: No winning coalitions.
    quorum = 99
    game = WeightedVotingGame(3, weights=weights, quorum=quorum)
    expected_output = {}
    actual_output = game.get_pivot_players()
    assert actual_output == expected_output

    expected_output = {
        (1,): [], (2,) : [], (3,) : [],
        (1,2) : [], (1,3) : [], (2,3,) : [],
        (1,2,3,) : []
    }
    actual_output = game.get_pivot_players(all_coalitions=True)
    assert expected_output == actual_output

    # Edge case: 1 player.
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)
    expected_output = {(1,) : [1]}
    actual_output = game.get_pivot_players()
    assert expected_output == actual_output

def test_get_minimal_winning_coalitions():
    weights = [1, 2, 3, ]
    quorum = 4
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [(1,3), (2,3)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    # Special case: No winning coalitions.
    quorum = 99
    game = WeightedVotingGame(3, weights=weights, quorum=quorum)
    expected_output = []
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    # Special case: Only one winning coalition which is minimal.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(num_players=4, weights=weights, quorum=quorum)
    expected_output = [(1,2,3,4)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output

    # Edge case: 1 player.
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)
    expected_output = [(1,)]
    actual_output = game.get_minimal_winning_coalitions()
    assert expected_output == actual_output


def test_shapley_shubik_index():
    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [2/3, 1/6, 1/6]
    actual_output = game.shapley_shubik_index()
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [1/2, 1/2, 0]
    actual_output = game.shapley_shubik_index()
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(num_players=4, weights=weights, quorum=quorum)
    expected_output = [1/4, 1/4, 1/4, 1/4]
    actual_output = game.shapley_shubik_index()
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)
    expected_output = [1]
    actual_output = game.shapley_shubik_index()
    assert expected_output == actual_output


def test_banzhaf_index():
    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [3/5, 1/5, 1/5]
    actual_output = game.banzhaf_index()
    assert expected_output == actual_output

    # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [1/2, 1/2, 0]
    actual_output = game.banzhaf_index()
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(num_players=4, weights=weights, quorum=quorum)
    expected_output = [1/4, 1/4, 1/4, 1/4]
    actual_output = game.banzhaf_index()
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)
    expected_output = [1]
    actual_output = game.banzhaf_index()
    assert expected_output == actual_output

def test_johnston_index():
    # Test usual case.
    weights = [7, 3, 3]
    quorum = 10
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [2/3, 1/6, 1/6]
    actual_output = game.johnston_index()
    assert expected_output == actual_output

   # Special case: One player is never pivot player.
    weights = [8, 4, 1]
    quorum = 10
    game = WeightedVotingGame(num_players=3, weights=weights, quorum=quorum)
    expected_output = [1/2, 1/2, 0]
    actual_output = game.johnston_index()
    assert expected_output == actual_output

    # Special case: Only one winning coalition.
    weights = [2, 1, 1, 1]
    quorum = 5
    game = WeightedVotingGame(num_players=4, weights=weights, quorum=quorum)
    expected_output = [1/4, 1/4, 1/4, 1/4]
    actual_output = game.johnston_index()
    assert expected_output == actual_output

    # Edge case: 1 player
    weights = [1]
    quorum = 1
    game = WeightedVotingGame(num_players=1, weights=weights, quorum=quorum)
    expected_output = [1]
    actual_output = game.johnston_index()
    assert expected_output == actual_output