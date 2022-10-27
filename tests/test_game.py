import pytest
from games.game import Game
from indices.shapley import ShapleyValue
from indices.banzhaf import BanzhafValue
from indices.gatley import GatelyPoint
from indices.tau import TauValue

def test_constructor():
    """Test the game constructor."""
    # Test a vaild game.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(num_players=3, contributions=contributions)
    expected_coalitions = [
        (1,), (2,), (3,),
        (1,2,), (1,3,), (2,3,),
        (1,2,3,),
    ]
    assert set(game.players) == set([1, 2, 3])
    assert set(game.contributions) == set(contributions)#
    assert set(game.coalitions) == set(expected_coalitions)

    # Test invalid contributions.
    contributions = []
    with pytest.raises(ValueError, match="Vector of contributions does not match length of coalition vector."):
        game = Game(num_players=3, contributions=contributions)

    # Test another invalid contribution vector:
    contributions = [0, -1, -2, 3, 4, 5, 6]
    with pytest.raises(ValueError, match="Contributions have to be greater than or equal to 0."):
        game = Game(num_players=3, contributions=contributions)

    # Test invalid number of players:
    with pytest.raises(ValueError, match="The number of players has to be greater than or equal to 1."):
        game = Game(num_players=0, contributions=contributions)

    # Test non monotone contribution vector:
    with pytest.raises(ValueError, match="Contributions have to grow monotone by coalition size."):
        contributions = [1, 2, 3, 2, 4, 5, 3]
        game = Game(num_players=3, contributions=contributions)
    
    # Test monotonity again for contributions with only one player:
    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    assert set(game.players) == set([1])
    assert set(game.contributions) == set(contributions)
    assert set(game.coalitions) == set([(1,)])


def test_characterisitc_function():
    """Test the characteristic function of a game."""
    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(num_players=3, contributions=contributions)
    expected_output = {
        (1,) : 1, (2,) : 2, (3,): 3,
        (1,2,) : 3, (1,3,) : 4, (2,3,) : 5,
        (1,2,3,) : 6,
    }
    actual_output = game.characteristic_function()
    assert actual_output == expected_output

    # Edge case: 1 player
    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = { (1,) : 1, }
    actual_output = game.characteristic_function()
    assert actual_output == expected_output

def test_get_marginal_contribution():
    """Test the marginal contribution of a player in a coaltion."""
    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(num_players=3, contributions=contributions)

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
    game = Game(num_players=3, contributions=contributions)
    expected_output = [(1,), (2,), (3,)]
    actual_output = game.get_one_coalitions()
    assert expected_output == actual_output

    # Edge case: 1 player
    game = Game(num_players=1, contributions=[1])
    expected_output = [(1,)]
    actual_output = game.get_one_coalitions()
    assert expected_output == actual_output


def test_get_utopia_payoff_vector():
    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [1, 2, 3]
    actual_output = game.get_utopia_payoff_vector()
    assert expected_output == actual_output

    contributions = [0, 0, 0, 60, 60, 60, 72]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [12, 12, 12]
    actual_output = game.get_utopia_payoff_vector()
    assert expected_output

    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [3, 3, 5]
    actual_output = game.get_utopia_payoff_vector()
    assert expected_output

    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [1]
    actual_output = game.get_utopia_payoff_vector()
    assert expected_output == actual_output

def test_get_minimal_rights_vector():

    # Test usual setting.
    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [1, 2, 3]
    actual_output = game.get_minimal_rights_vector()
    assert expected_output == actual_output

    contributions = [0, 0 ,0, 60, 60, 60, 72]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [48, 48, 48]
    actual_output = game.get_minimal_rights_vector()
    assert expected_output == actual_output


    contributions = [2, 4, 5, 18, 14, 9, 24]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [8, 4, 5]
    actual_output = game.get_minimal_rights_vector()
    assert expected_output == actual_output

    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [1, 2, 3]
    actual_output = game.get_minimal_rights_vector()
    assert expected_output
    
    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [1]
    actual_output = game.get_minimal_rights_vector()
    assert expected_output == actual_output
    

def test_get_imputation_vertices():

    contributions = [1, 2, 3, 3, 4, 5, 6]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [
        [1, 2, 3],
    ]
    actual_output = game.get_imputation_vertices()
    assert expected_output == actual_output

    contributions = [1, 2, 3, 3, 5, 5, 8]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [
        [3, 2, 3,],
        [1, 4, 3,],
        [1, 2, 5],
    ]
    actual_output = game.get_minimal_rights_vector()
    assert expected_output

    contributions = [0, 0 ,0, 60, 60, 60, 72]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [
        [72, 0, 0],
        [0, 72, 0],
        [0, 0, 72],
    ]
    actual_output = game.get_imputation_vertices()
    assert expected_output == actual_output

    contributions = [2, 4, 5, 18, 24, 9, 24]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [
        [15, 4, 5],
        [2, 17, 5],
        [2, 4, 18],
    ]
    actual_output = game.get_imputation_vertices()
    assert expected_output == actual_output

    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [
        [1,]
    ]
    actual_output = game.get_imputation_vertices()
    assert expected_output == actual_output


def test_shapley_value():

    contributions = [2, 4, 5, 18, 14, 9, 24]
    shapley = ShapleyValue()
    game = Game(num_players=3, contributions=contributions)
    expected_output = [9.5, 8, 6.5]
    actual_output = shapley.compute(game)
    assert expected_output == actual_output

    contributions = [0, 0, 0, 1, 2, 3, 7.5]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [2, 2.5, 3.0]
    actual_output = shapley.compute(game)
    assert expected_output == actual_output

    contributions = [120, 60, 40, 30, 120, 120, 120, 60, 60, 40, 120, 120, 120, 60, 120]
    game = Game(num_players=4, contributions=contributions)
    expected_output = [80.83333, 20.83333, 10.83333,  7.50000]
    actual_output = shapley.compute(game)
    assert expected_output == pytest.approx(actual_output)


    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [1]
    actual_output = shapley.compute(game)
    assert expected_output == actual_output

    contributions = [42]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [42]
    actual_output = shapley.compute(game)
    assert expected_output == actual_output


def test_banzhaf_value():

    banzhaf = BanzhafValue()

    # Test normalized
    contributions = [0, 0, 0, 1, 2, 1, 3]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [15/13, 9/13, 15/13]
    actual_output = banzhaf.compute(game)
    assert expected_output == pytest.approx(actual_output)

    # Test absolute.
    expected_output = [1.25, 0.75, 1.25]
    actual_output = banzhaf.compute(game, normalized=False)
    assert expected_output == actual_output

    contributions = [0, 0, 0, 1, 2, 1, 4]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [3/2, 1, 3/2]
    actual_output = banzhaf.compute(game)
    assert expected_output == pytest.approx(actual_output)
    
    expected_output = [1.5, 1, 1.5]
    actual_output = banzhaf.compute(game, normalized=False)
    assert expected_output == actual_output

    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [1]
    actual_output = banzhaf.compute(game)
    assert expected_output == actual_output

    contributions = [42]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [42]
    actual_output = banzhaf.compute(game)
    assert expected_output == actual_output


def test_gately_point():
    gately = GatelyPoint()

    contributions = [0, 0, 0, 1, 1, 1, 3.5]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [1.166667, 1.166667, 1.166667]
    actual_output = gately.compute(game)
    assert expected_output == pytest.approx(actual_output)

    contributions = [0, 0, 0, 4, 0, 3, 6]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [18/11, 36/11, 12/11]
    actual_output = gately.compute(game)
    assert expected_output == pytest.approx(actual_output)

    contributions = [0, 0, 0, 1170, 770, 210, 1530]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [827.7049, 476.5574, 225.7377]
    actual_output = gately.compute(game)
    assert expected_output == pytest.approx(actual_output)

    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [1]
    actual_output = gately.compute(game)
    assert expected_output == actual_output

    contributions = [42]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [42]
    actual_output = gately.compute(game)
    assert expected_output == actual_output


def test_tau_value():
    tau = TauValue()

    contributions = [0, 0, 0, 0, 1, 0, 1]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [1/2, 0, 1/2]
    actual_output = tau.compute(game)
    assert expected_output == pytest.approx(actual_output)

    contributions = [2, 4, 5, 18, 14, 9, 24]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [11.5, 7, 5.5]
    actual_output = tau.compute(game)
    assert expected_output == pytest.approx(actual_output)

    contributions = [0, 0, 0, 1, 2, 1, 3]
    game = Game(num_players=3, contributions=contributions)
    expected_output = [1.2, 0.6, 1.2]
    actual_output = tau.compute(game)
    assert expected_output == pytest.approx(actual_output)

    contributions = [1]
    game = Game(num_players=1, contributions=contributions)
    expected_output = [1]
    actual_output = tau.compute(game)
    assert expected_output == actual_output
