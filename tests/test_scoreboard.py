"""
Tests for `mc_score_utils`.
"""

from pathlib import Path

from mc_score_utils.mc_score_utils import Scoreboard

DAT_FILE = Path('tests/data/scoreboard.dat')

TEST_BOARD = Scoreboard(DAT_FILE)

def test_scoreboard_from_dat(): # pylint: disable=missing-function-docstring
    assert 'health' in TEST_BOARD.display_slots['sidebar']
    assert TEST_BOARD.objectives['stone_mined']['CriteriaName'] == 'minecraft.mined:minecraft.stone'
    assert TEST_BOARD.player_scores['svioletg']['health'] == 20
    assert TEST_BOARD.teams == {}
