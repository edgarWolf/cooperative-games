import pytest
from games.game import Game

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
    with pytest.raises(ValueError, match="Contributions have to be greater than or equal to 1."):
        game = Game(num_players=3, contributions=contributions)

    # Test invalid number of players:
    with pytest.raises(ValueError, match="The number of players has to be greater than or equal to 1."):
        game = Game(num_players=0, contributions=contributions)


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


    
    






 