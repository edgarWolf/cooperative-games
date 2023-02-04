import numpy as np
import pytest
from cooperative_games.games import Game
from cooperative_games.indices.power_values import (
    ShapleyValue,
    BanzhafValue,
    GatelyPoint,
    TauValue,
)


def test_constructor():
    """Test the game constructor."""
    # Test a vaild game.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_coalitions = [
        (1,), (2,), (3,),
        (1, 2,), (1, 3,), (2, 3,),
        (1, 2, 3,),
    ]
    assert set(game.players) == set([1, 2, 3])
    assert set(game.contributions) == set(contributions)
    assert set(game.coalitions) == set(expected_coalitions)

    # Test invalid contributions.
    contributions = []
    with pytest.raises(ValueError, match="No contributions provided"):
        game = Game(contributions=contributions)

    # Contributions not a base of 2 - 1, i.e. not representing all possible coalition payoffs.
    contributions = [1, 2, 3, 4]
    with pytest.raises(ValueError, match="Invalid length of the contributions vector."):
        game = Game(contributions=contributions)

    # Test another invalid contribution vector:
    contributions = [0, -1, -2, 3, 4, 5, 6]
    with pytest.raises(ValueError, match="Contributions have to be greater than or equal to 0."):
        game = Game(contributions=contributions)

    # Test non monotone contribution vector:
    with pytest.raises(ValueError, match="Contributions have to grow monotone by coalition size."):
        contributions = [1, 2, 3, 2, 4, 5, 3]
        game = Game(contributions=contributions)

    # Test monotonity again for contributions with only one player:
    contributions = [1]
    game = Game(contributions=contributions)
    assert set(game.players) == set([1])
    assert set(game.contributions) == set(contributions)
    assert set(game.coalitions) == set([(1,)])


def test_repr():
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = "3 players game"
    expected_output += "\n"
    expected_output += "contributions = [1, 2, 3, 3, 4, 5, 6]"
    actual_output = game.__repr__()
    assert expected_output == actual_output

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = "1 player game"
    expected_output += "\n"
    expected_output += "contributions = [1]"
    actual_output = game.__repr__()
    assert expected_output == actual_output


def test_characterisitc_function():
    """Test the characteristic function of a game."""
    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = {
        (1,): 1, (2,): 2, (3,): 3,
        (1, 2,): 3, (1, 3,): 4, (2, 3,): 5,
        (1, 2, 3,): 6,
    }
    actual_output = game.characteristic_function()
    assert actual_output == expected_output

    # Edge case: 1 player
    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = {(1,): 1, }
    actual_output = game.characteristic_function()
    assert actual_output == expected_output


def test_get_marginal_contribution():
    """Test the marginal contribution of a player in a coaltion."""
    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(contributions=contributions)

    # Test case 1: Marginal contribution for own coalition.
    selected_player = 1
    selected_coalition = (1,)
    expected_contribution = 1
    actual_contribution = game.get_marginal_contribution(coalition=selected_coalition, player=selected_player)
    assert expected_contribution == actual_contribution

    # Test case 2: Marginal contribution for coalition of two.
    # Payoff((1,3)) = 5; Payoff((1,3) / (1,)) = Payoff((3,)) = 3 --> Marg. Contr. (1,) = Payoff((1,3,)) - Payoff((3,)) = 5 - 3 = 2
    selected_coalition = (1, 3,)
    expected_contribution = 2
    actual_contribution = game.get_marginal_contribution(coalition=selected_coalition, player=selected_player)
    assert expected_contribution == actual_contribution

    # Test case 3: Marginal contribution for grand coaltion.
    # Payoff((1,2,3,)) = 8; Payoff((1,2,3,) / (1,)) = Payoff((2,3,)) = 5 --> Marg. Contr. (1,) = Payoff((1,2,3,)) - Payoff((2,3,)) = 8 - 5 = 3
    selected_coalition = (1, 2, 3,)
    expected_contribution = 3
    actual_contribution = game.get_marginal_contribution(coalition=selected_coalition, player=selected_player)
    assert expected_contribution == actual_contribution


def test_get_one_coalitions():
    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = [(1,), (2,), (3,)]
    actual_output = game.get_one_coalitions()
    assert expected_output == actual_output

    # Edge case: 1 player
    game = Game(contributions=[1])
    expected_output = [(1,)]
    actual_output = game.get_one_coalitions()
    assert expected_output == actual_output


def test_get_utopia_payoff_vector():
    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = np.array([1, 2, 3])
    actual_output = game.get_utopia_payoff_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 0, 0, 60, 60, 60, 72]
    game = Game(contributions=contributions)
    expected_output = np.full((3,), 12)
    actual_output = game.get_utopia_payoff_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(contributions=contributions)
    expected_output = np.array([3, 3, 5])
    actual_output = game.get_utopia_payoff_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.ones((1,))
    actual_output = game.get_utopia_payoff_vector()
    assert np.array_equal(expected_output, actual_output)


def test_get_minimal_rights_vector():
    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = np.array([1, 2, 3])
    actual_output = game.get_minimal_rights_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 0, 0, 60, 60, 60, 72]
    game = Game(contributions=contributions)
    expected_output = np.full((3,), 48)
    actual_output = game.get_minimal_rights_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [2, 4, 5, 18, 14, 9, 24]
    game = Game(contributions=contributions)
    expected_output = np.array([8, 4, 5])
    actual_output = game.get_minimal_rights_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(contributions=contributions)
    expected_output = np.array([1, 2, 3])
    actual_output = game.get_minimal_rights_vector()
    assert np.array_equal(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.ones((1,))
    actual_output = game.get_minimal_rights_vector()
    assert np.array_equal(expected_output, actual_output)


def test_get_imputation_vertices():
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([1, 2, 3]),
    ])
    actual_output = game.get_imputation_vertices()
    assert np.array_equal(expected_output, actual_output)

    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([1, 2, 5]),
        np.array([1, 4, 3]),
        np.array([3, 2, 3]),
    ])
    actual_output = game.get_imputation_vertices()
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 0, 0, 60, 60, 60, 72]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([0, 0, 72]),
        np.array([0, 72, 0]),
        np.array([72, 0, 0]),
    ])
    actual_output = game.get_imputation_vertices()
    assert np.array_equal(expected_output, actual_output)

    contributions = [2, 4, 5, 18, 24, 9, 24]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([2, 4, 18]),
        np.array([2, 17, 5]),
        np.array([15, 4, 5]),
    ])
    actual_output = game.get_imputation_vertices()
    assert np.array_equal(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([1])
    ])
    actual_output = game.get_imputation_vertices()
    assert np.array_equal(expected_output, actual_output)

def test_is_imputation():
    contributions = [0, 1, 2, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expceted_output = True
    actual_output = game.is_in_imputation_set([1.5, 1, 3.5])
    assert expceted_output == actual_output

    expceted_output = False
    actual_output = game.is_in_imputation_set([2.05, 2, 2])
    assert expceted_output == actual_output

    contributions = [1]
    game = Game(contributions=contributions)
    expceted_output = True
    actual_output = game.is_in_imputation_set([1])
    assert expceted_output == actual_output

    contributions = [99]
    game = Game(contributions=contributions)
    expceted_output = False
    actual_output = game.is_in_imputation_set([1])
    assert expceted_output == actual_output

def test_is_in_core():
    contributions = [0, 1, 2, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = True
    actual_output = game.is_in_core([1, 2, 3])
    assert expected_output == actual_output

    expected_output = False
    actual_output = game.is_in_core([1, 2, 4])
    assert expected_output == actual_output

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = True
    actual_output = game.is_in_core([1])
    assert expected_output == actual_output

    contributions = [99]
    game = Game(contributions=contributions)
    expected_output = False
    actual_output = game.is_in_core([1])
    assert expected_output == actual_output


def test_get_core_vertices():
    contributions = [2, 4, 5, 18, 14, 9, 24]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([8, 10, 6]),
        np.array([9, 10, 5]),
        np.array([14, 4, 6]),
        np.array([15, 4, 5]),
    ])
    actual_output = game.get_core_vertices()
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 1, 2, 3, 4, 5, 6]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([1, 2, 3]),
    ])
    actual_output = game.get_core_vertices()
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 0, 0, 60, 80, 100, 135]
    game = Game(contributions=contributions)
    expected_output = np.array([
        np.array([5, 55, 75]),
        np.array([35, 25, 75]),
        np.array([35, 55, 45]),
    ])
    actual_output = game.get_core_vertices()
    assert np.array_equal(expected_output, actual_output)

    # contributions = [5, 2, 4, 7, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 35]
    # game = Game(contributions=contributions)
    # expected_output = np.array([
    #     np.array([5, 10, 10, 10]),
    #     np.array([7.5, 7.5, 7.5, 12.5]),
    #     np.array([7.5, 7.5, 12.5, 7.5]),
    #     np.array([10, 5, 10, 10]),
    #     np.array([12.5, 7.5, 7.5, 7.5]),
    #     np.array([10, 10, 5, 10]),
    #     np.array([7.5, 12.5, 7.5, 7.5]),
    #     np.array([12, 8, 8, 7]),
    #     np.array([8, 12, 8, 7]),
    #     np.array([8, 8, 12, 7]),
    # ])
    # actual_output = game.get_core_vertices()
    # assert np.array_equal(expected_output, actual_output)


def test_is_convex():
    contributions = [0, 0, 0, 1, 1, 1, 5]
    game = Game(contributions=contributions)
    expected_output = True
    actual_output = game.is_convex()
    assert expected_output == actual_output

    contributions = [0, 0, 0, 1, 2, 1, 4]
    game = Game(contributions=contributions)
    expected_output = True
    actual_output = game.is_convex()
    assert expected_output == actual_output

    contributions = [1, 2, 3, 4, 5, 6, 7]
    game = Game(contributions=contributions)
    expected_output = False
    actual_output = game.is_convex()
    assert expected_output == actual_output


def test_is_super_additive():
    contributions = [1, 1, 1, 2, 2, 2, 3]
    game = Game(contributions=contributions)
    expected_output = True
    actual_output = game.is_additive()
    assert expected_output == actual_output

    contributions = [0, 0, 0, 40, 50, 20, 100]
    game = Game(contributions=contributions)
    expected_output = False
    actual_output = game.is_additive()
    assert expected_output == actual_output

    contributions = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4]
    game = Game(contributions=contributions)
    expected_output = True
    actual_output = game.is_additive()
    assert expected_output == actual_output


def test_shapley_value():
    contributions = [2, 4, 5, 18, 14, 9, 24]
    shapley = ShapleyValue()
    game = Game(contributions=contributions)
    expected_output = np.array([9.5, 8, 6.5])
    actual_output = shapley.compute(game)
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 0, 0, 1, 2, 3, 7.5]
    game = Game(contributions=contributions)
    expected_output = np.array([2, 2.5, 3.0])
    actual_output = shapley.compute(game)
    assert np.array_equal(expected_output, actual_output)

    contributions = [120, 60, 40, 30, 120, 120, 120, 60, 60, 40, 120, 120, 120, 60, 120]
    game = Game(contributions=contributions)
    expected_output = np.array([80.83333, 20.83333, 10.83333, 7.50000])
    actual_output = shapley.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.ones((1,))
    actual_output = shapley.compute(game)
    assert np.array_equal(expected_output, actual_output)

    contributions = [42]
    game = Game(contributions=contributions)
    expected_output = np.array([42])
    actual_output = shapley.compute(game)
    assert np.array_equal(expected_output, actual_output)


def test_banzhaf_value():
    banzhaf = BanzhafValue()

    # Test normalized
    contributions = [0, 0, 0, 1, 2, 1, 3]
    game = Game(contributions=contributions)
    expected_output = np.array([15 / 13, 9 / 13, 15 / 13])
    actual_output = banzhaf.compute(game)
    assert np.allclose(expected_output, actual_output)

    # Test absolute.
    expected_output = np.array([1.25, 0.75, 1.25])
    actual_output = banzhaf.compute(game, normalized=False)
    assert np.array_equal(expected_output, actual_output)

    contributions = [0, 0, 0, 1, 2, 1, 4]
    game = Game(contributions=contributions)
    expected_output = np.array([3 / 2, 1, 3 / 2])
    actual_output = banzhaf.compute(game)
    assert np.allclose(expected_output, actual_output)

    expected_output = np.array([1.5, 1, 1.5])
    actual_output = banzhaf.compute(game, normalized=False)
    assert np.array_equal(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.ones((1,))
    actual_output = banzhaf.compute(game)
    assert np.array_equal(expected_output, actual_output)

    contributions = [42]
    game = Game(contributions=contributions)
    expected_output = np.array([42])
    actual_output = banzhaf.compute(game)
    assert expected_output == actual_output


def test_gately_point():
    gately = GatelyPoint()

    contributions = [0, 0, 0, 1, 1, 1, 3.5]
    game = Game(contributions=contributions)
    expected_output = np.full((3,), 1.166667)
    actual_output = gately.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [0, 0, 0, 4, 0, 3, 6]
    game = Game(contributions=contributions)
    expected_output = np.array([18 / 11, 36 / 11, 12 / 11])
    actual_output = gately.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [0, 0, 0, 1170, 770, 210, 1530]
    game = Game(contributions=contributions)
    expected_output = np.array([827.7049, 476.5574, 225.7377])
    actual_output = gately.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.ones((1,))
    actual_output = gately.compute(game)
    assert np.array_equal(expected_output, actual_output)

    contributions = [42]
    game = Game(contributions=contributions)
    expected_output = np.array([42])
    actual_output = gately.compute(game)
    assert np.array_equal(expected_output, actual_output)


def test_tau_value():
    tau = TauValue()

    contributions = [0, 0, 0, 0, 1, 0, 1]
    game = Game(contributions=contributions)
    expected_output = np.array([1 / 2, 0, 1 / 2])
    actual_output = tau.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [2, 4, 5, 18, 14, 9, 24]
    game = Game(contributions=contributions)
    expected_output = np.array([11.5, 7, 5.5])
    actual_output = tau.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [0, 0, 0, 1, 2, 1, 3]
    game = Game(contributions=contributions)
    expected_output = np.array([1.2, 0.6, 1.2])
    actual_output = tau.compute(game)
    assert np.allclose(expected_output, actual_output)

    contributions = [1]
    game = Game(contributions=contributions)
    expected_output = np.array([1])
    actual_output = tau.compute(game)
    assert np.array_equal(expected_output, actual_output)
