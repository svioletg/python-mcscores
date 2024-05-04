"""Script for reading Minecraft scoreboard data and processing it into dicts to be more Python-ready.
A method is provided in the main Scoreboard class to dump everything to JSON, as well."""
import json
from pathlib import Path


class Scoreboard:
    """Parses either NBT scoreboard data from a raw `.dat` file or a `.json` file generated by this class into dictionary attributes.

    :param `data_source`: File path to a `.dat` or `.json` file containing scoreboard data. Only JSON files structured like the
    output of this class' `to_json()` method will work.
    
    :param `player_whitelist`: Excludes player usernames from being included in any processed data unless they appear in this list.
        Can either be a list of username strings, or a file path to a valid `whitelist.json` file.
        Some datapacks use 'dummy' players to store data, so this can be useful to sort those out.
    
    :param `player_blacklist`: Opposite effect of the whitelist parameter. Both a whitelist and blacklist cannot be used at the same time.
    
    :param `include_dot_names`: Allows player names starting with a dot (.) to be added to the data. This is common for Bedrock users joining through
        something like Geyser. This will allow any player names beginning with a dot if whitelisting, but will still exclude the name if blacklisting."""
    def __init__(self, data_source: Path | str, player_whitelist: list | Path | str='', player_blacklist: list | Path | str='', include_dot_names: bool = True):
        if player_whitelist and player_blacklist:
            # Raise an error if trying to use a whitelist and a blacklist together.
            # Technically it could work but one would have to take priority, and I can't see
            # many cases where that would realistically be helpful to support.
            raise ValueError('Can\'t use a whitelist and a blacklist at the same time.')
        self.player_whitelist: list = []
        self.player_blacklist: list = []

        if player_whitelist and isinstance(player_whitelist, (Path, str)):
            with open(Path(player_whitelist), 'r', encoding='utf-8') as f:
                whitelist_json = json.load(f)
            for player in whitelist_json:
                # Any bedrock players that connect through geyser or some such will have their name as "unknown" in the whitelist
                # Excluded for safety, just in case
                # In the game, and in the scoreboard, they'll show up as their Java username with a dot in front of it,
                # unfortunately no way to really detect that from this given UUID as far as I'm aware? So we'll just allow
                # any usernames with dots in front of them.
                if not player['uuid'].startswith('00000000-0000-0000-'):
                    self.player_whitelist.append(player['name'])
        

        if player_blacklist and isinstance(player_blacklist, (Path, str)):
            with open(Path(player_blacklist), 'r', encoding='utf-8') as f:
                blacklist_json = json.load(f)
            for player in blacklist_json:
                self.player_blacklist.append(player['name'])
        
        # From this point on we should only be using the self. versions, this is just to avoid confusion
        del player_whitelist, player_blacklist

        if Path(data_source).suffix == '.json':
            with open(Path(data_source), 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            self.teams:         dict = json_data['Teams']
            self.objectives:    dict = json_data['Objectives']
            self.player_scores: dict = json_data['PlayerScores']
            self.display_slots: dict = json_data['DisplaySlots']
        if Path(data_source).suffix == '.dat':
            from nbt.nbt import NBTFile
            self.data: NBTFile = NBTFile(data_source, 'rb')['data']

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
                    'DisplayName':            {'json_dict': json.loads(team['DisplayName'].value), 'json_string': team['DisplayName'].value}
                    }
            self.objectives: dict = {}
            for obj in self.data['Objectives']:
                self.objectives[obj['Name'].value] = {
                        'CriteriaName': obj['CriteriaName'].value,
                        'RenderType':   obj['RenderType'].value,
                        'DisplayName':  {'json_dict': json.loads(obj['DisplayName'].value), 'json_string': obj['DisplayName'].value}
                    }
            self.display_slots: dict = {slot:obj.value for slot,obj in self.data['DisplaySlots'].items()}
            self.player_scores: dict = {}
            for entry in self.data['PlayerScores']:
                player_name: str = entry['Name'].value

                # Skip this player if they're in the blacklist or not in the whitelists
                if (self.player_blacklist and player_name in self.player_blacklist) or \
                    ((self.player_whitelist and player_name not in self.player_whitelist) and (include_dot_names and not player_name.startswith('.'))):
                    continue

                objective: str = entry['Objective'].value
                score: int = entry['Score'].value
                # Make an entry for this player if it doesn't exist
                if player_name not in self.player_scores:
                    self.player_scores[player_name] = {}
                self.player_scores[player_name][objective] = score
    
    def __dict__(self) -> dict:
        """Return a dictionary of this Scoreboard data."""
        return {
            'Teams': self.teams,
            'Objectives': self.objectives,
            'PlayerScores': self.player_scores,
            'DisplaySlots': self.display_slots
            }

    def get_objective_scores(self, target_objective: str, ascending: bool=False) -> list[tuple[str, int]]:
        """Returns a list of tuples containing the player name and player score associated with the given objective,
        by default sorted from highest to lowest.
        
        :param objective: The objective name to retrieve scores for.
        :param ascending: If true, will instead return score rankings from lowest to highest."""
        unsorted_scores = {}
        # Iterate through player's set of objectives
        for player, objectives in self.player_scores.items():
            # Establish a dict entry for them, search through every objective
            unsorted_scores[player] = {}
            for obj, score in objectives.items():
                # If this is our target then store it, and break the loop
                if obj == target_objective:
                    unsorted_scores[player] = score
                    break
            # If nothing was found, don't include an empty dict in the results
            if not unsorted_scores[player]:
                unsorted_scores.pop(player)
        # Sort them highest to lowest, reverse if specified
        # This lambda sorts it by values instead of keys. I don't know how it works, that's just what came up
        return sorted(unsorted_scores.items(), key=lambda x: x[1], reverse=not ascending)
