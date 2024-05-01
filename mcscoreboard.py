"""Script for reading Minecraft scoreboard data and processing it into dicts to be more Python-ready.
A method is provided in the main Scoreboard class to dump everything to JSON, as well."""
import re
from pathlib import Path

from nbt.nbt import NBTFile

def dict_from_json_string(json_string: str) -> dict | None:
    matches = re.findall(r'\"(.*?)\": ?\"(.*?)\"', json_string)
    if not matches:
        return None
    return {match[0]:match[1] for match in matches}

class Scoreboard:
    """Takes a scoreboard.dat file and parses it into dictionaries."""
    def __init__(self, dat_path: Path):
        self.data: NBTFile = NBTFile(dat_path, 'rb')['data']

        # TODO: Make these TypedDicts

        self.teams: dict = {}
        for team in self.data['Teams']:
            self.teams[team['Name'].value] = {
                'DeathMessageVisibility': team['DeathMessageVisibility'].value,
                'TeamColor':              team['TeamColor'].value,
                'SeeFriendlyInvisibles':  team['SeeFriendlyInvisibles'].value,
                'CollisionRule':          team['CollisionRule'].value,
                'AllowFriendlyFire':      team['AllowFriendlyFire'].value,
                'MemberNamePrefix':       team['MemberNamePrefix'].value,
                'NameTagVisibility':      team['NameTagVisibility'].value,
                'MemberNameSuffix':       team['MemberNameSuffix'].value,
                'Players':                [player.value for player in team['Players']],
                'DisplayName':            {'json_dict': dict_from_json_string(team['DisplayName'].value), 'json_string': team['DisplayName'].value}
                }
        self.objectives: dict = {}
        for obj in self.data['Objectives']:
            self.objectives[obj['Name'].value] = {
                    'CriteriaName': obj['CriteriaName'].value,
                    'RenderType':   obj['RenderType'].value,
                    'DisplayName':  {'json_dict': dict_from_json_string(obj['DisplayName'].value), 'json_string': obj['DisplayName'].value}
                }
        self.display_slots: dict = {slot:scores for slot, scores in self.data['DisplaySlots'].items()}
        self.player_scores: dict = {}
        for entry in self.data['PlayerScores']:
            player_name: str = entry['Name'].value
            objective: str = entry['Objective'].value
            score: int = entry['Score'].value
            # Make an entry for this player if it doesn't exist
            if player_name not in self.player_scores:
                self.player_scores[player_name] = {}
            self.player_scores[player_name][objective] = score