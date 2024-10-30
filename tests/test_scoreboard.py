"""
Tests for `mc_score_utils`.
"""

from pathlib import Path

import pytest

from mc_score_utils.core import Scoreboard

DATA_DIR = Path('tests/data/')

test_boards = [p.absolute() for p in DATA_DIR.glob('*/scoreboard.dat')]

@pytest.mark.parametrize('fp', test_boards, ids=[p.parent.parts[-1] for p in test_boards])
def test_scoreboard_from_dat(fp: Path): # pylint: disable=missing-function-docstring
    board = Scoreboard(fp)
    assert 'health' in board.display_slots['sidebar']

    assert board.objectives['stone_mined']['CriteriaName'] == 'minecraft.mined:minecraft.stone'
    assert board.objectives['stone_mined']['DisplayName'] == {'text': 'Stone Mined'}
    assert board.player_scores['svioletg']['stone_mined'] == 98

    assert board.objectives['health']['CriteriaName'] == 'health'
    assert board.objectives['health']['DisplayName'] == {'text': 'Health', 'color': 'green'}
    assert board.player_scores['svioletg']['health'] == 20

    assert board.teams == {}
