#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Artyom Bychkov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""CLI Draft Assistant for Dota 2"""

import io
import json
import operator
from typing import List, Dict, Tuple


class Hero:
    """Hero class for storing and accessing hero information."""

    name: str
    aliases: List[str]
    good_against: List[str]
    bad_against: List[str]
    works_well_with: List[str]

    def __init__(self, name, aliases, good_against, bad_against,
                 works_well_with):
        self.name = name
        self.aliases = aliases
        self.good_against = good_against
        self.bad_against = bad_against
        self.works_well_with = works_well_with

    def dict(self):
        """Return dictionary representation of hero info."""
        return {
            'name': self.name,
            'aliases': self.aliases,
            'good_against': self.good_against,
            'bad_against': self.bad_against,
            'works_well_with': self.works_well_with,
        }

    def pretty_print(self) -> str:
        """Return human readable string representation of hero info."""
        return ('Name: ' + self.name + '\n'
                'Aliases: ' + ', '.join(self.aliases) + '\n'
                'Good against: ' + ', '.join(self.good_against) + '\n'
                'Bad against: ' + ', '.join(self.bad_against) + '\n'
                'Works well with: ' + ', '.join(self.works_well_with))


class DraftEngine:
    """Back end engine for draft assistant."""

    _hero_data: Dict[str, Hero]
    _hero_alias_map: Dict[str, str]
    _hero_weights: Dict[str, int]
    _bans: List[str]
    _ally_picks: List[str]
    _enemy_picks: List[str]
    _max_picks: int = 5

    def __init__(self, hero_data):
        self._hero_data = {}
        self._hero_alias_map = {}

        for hero in hero_data["heroes"]:
            self._hero_data[hero["name"]] = Hero(
                hero["name"],
                hero["aliases"],
                hero["good_against"],
                hero["bad_against"],
                hero["works_well_with"],
            )

        for hero_name in self._hero_data:
            # map each aliases to hero name
            for hero_alias in self._hero_data[hero_name].aliases:
                self._hero_alias_map[hero_alias] = hero_name

            # add lowercase hero name as well in case not present
            self._hero_alias_map[hero_name.lower()] = hero_name

        # initialize other instance attributes for start of draft
        self.reset()

    def reset(self):
        """Reset engine, clearing picks and resetting hero weights to 0."""
        self._bans = []
        self._ally_picks = []
        self._enemy_picks = []
        self._hero_weights = {}

        for hero_name in self._hero_data:
            self._hero_weights[hero_name] = 0

    def resolve_hero_name(self, alias: str):
        """Check for lowercase alias in hero alias map.

        Return hero name from map if found, else return None.
        """
        alias = alias.lower()
        if alias in self._hero_alias_map:
            return self._hero_alias_map[alias]
        return None

    def ally_hero_pick(self, hero_pick: str) -> Tuple[str, bool]:
        """Process ally hero pick and update hero weights."""

        if not hero_pick:
            return 'Hero argument required', False

        hero_name = self.resolve_hero_name(hero_pick)
        if not hero_name:
            return f'No hero name or alias found matching: {hero_pick}', False

        if len(self._ally_picks) >= self._max_picks:
            return 'Max ally hero picks reached', False

        if hero_name in self._bans:
            return f'Hero {hero_name} banned', False
        if hero_name in self._ally_picks or hero_name in self._enemy_picks:
            return f'Hero {hero_name} already picked', False

        # passed validation, process pick
        self._ally_picks.append(hero_name)

        # remove picked hero from weights pool
        if hero_name in self._hero_weights:
            del self._hero_weights[hero_name]

        # increase weight of heroes ally pick works well with
        for other_hero in self._hero_data[hero_name].works_well_with:
            if other_hero in self._hero_weights:
                self._hero_weights[other_hero] += 1

        return f'Ally hero pick: {hero_name}, hero weights updated', True

    def enemy_hero_pick(self, hero_pick: str) -> Tuple[str, bool]:
        """Process enemy hero pick and update hero weights."""

        if not hero_pick:
            return 'Hero argument required', False

        hero_name = self.resolve_hero_name(hero_pick)
        if not hero_name:
            return f'No hero name or alias found matching {hero_pick}', False

        if len(self._enemy_picks) >= self._max_picks:
            return 'Max enemy hero picks reached', False

        if hero_name in self._bans:
            return f'Hero {hero_name} banned', False
        if hero_name in self._ally_picks or hero_name in self._enemy_picks:
            return f'Hero {hero_name} already picked', False

        # passed validation, process pick
        self._enemy_picks.append(hero_name)

        # remove picked hero from weights pool
        if hero_name in self._hero_weights:
            del self._hero_weights[hero_name]

        # decrease weight of heroes enemy pick is good against
        for other_hero in self._hero_data[hero_name].good_against:
            if other_hero in self._hero_weights:
                self._hero_weights[other_hero] -= 1

        # increase weight of heroes enemy pick is bad against
        for other_hero in self._hero_data[hero_name].bad_against:
            if other_hero in self._hero_weights:
                self._hero_weights[other_hero] += 1

        return f'Enemy hero pick: {hero_name}, hero weights updated', True

    def ban_hero(self, hero: str) -> Tuple[str, bool]:
        """Ban hero, removing it from pool."""
        if not hero:
            return 'Hero argument required', False

        hero_name = self.resolve_hero_name(hero)
        if not hero_name:
            return f'No hero name or alias found matching {hero}', False

        if hero_name in self._bans:
            return f'Hero {hero_name} already banned', False
        if hero_name in self._ally_picks or hero_name in self._enemy_picks:
            return f'Hero {hero_name} already picked', False

        # passed validation, process pick
        self._bans.append(hero_name)

        # remove picked hero from weights pool
        if hero_name in self._hero_weights:
            del self._hero_weights[hero_name]

        return f'Hero banned: {hero_name}, hero weights updated', True

    def hero_info(self, hero: str) -> Tuple[str, bool]:
        """Get and return pretty printed hero information."""
        # check existence
        if not hero:
            return 'Hero argument required', False

        hero_name = self.resolve_hero_name(hero)
        if not hero_name:
            return f'No hero name or alias found matching {hero}', False

        return self._hero_data[hero_name].pretty_print(), True

    def sorted_hero_weights(self) -> List[Tuple[str, int]]:
        """Sort hero weights dict by value in descending order."""
        sorted_weights = sorted(self._hero_weights.items(),
                                key=operator.itemgetter(1))
        return sorted_weights[::-1]

    @property
    def bans(self) -> List[str]:
        """Return list of banned heroes."""
        return self._bans

    @property
    def ally_picks(self) -> List[str]:
        """Return list of ally picks."""
        return self._ally_picks

    @property
    def enemy_picks(self) -> List[str]:
        """Return list of enemy picks."""
        return self._enemy_picks


class DraftCLI:
    """Command line interface for draft engine."""

    _draft_engine: DraftEngine
    _prompt_str: str = "> "

    def __init__(self, hero_data):
        self._draft_engine = DraftEngine(hero_data)
        print('Draft engine initialized')
        self._help()

    def _prompt(self):
        """Prompt for user input and process command.

        Returns boolean for whether to continue prompting or exit.
        """
        cmd = input(self._prompt_str)
        return self._process_command(cmd)

    def _process_command(self, cmd: str) -> bool:
        """Process command from prompt.

        Returns boolean for whether to continue prompting or exit.
        """
        cmd_split = cmd.split()
        if not cmd_split:
            return True

        cmd_base = cmd_split[0]
        if len(cmd_split) > 1:
            cmd_params = ' '.join(cmd_split[1:])
        else:
            cmd_params = ''

        if cmd_base in ('h', 'help'):
            self._help()
        elif cmd_base in ('q', 'quit'):
            print('Quitting')
            return False
        elif cmd_base in ('r', 'reset'):
            self._draft_engine.reset()
            print('Reset draft engine')
        elif cmd_base in ('s', 'status'):
            self._display_hero_weights()
        elif cmd_base in ('a', 'ally'):
            out, success = self._draft_engine.ally_hero_pick(cmd_params)
            print(out)
            if success:
                self._display_hero_weights()
        elif cmd_base in ('e', 'enemy'):
            out, success = self._draft_engine.enemy_hero_pick(cmd_params)
            print(out)
            if success:
                self._display_hero_weights()
        elif cmd_base in ('b', 'ban'):
            out, success = self._draft_engine.ban_hero(cmd_params)
            print(out)
        elif cmd_base in ('i', 'info'):
            out, success = self._draft_engine.hero_info(cmd_params)
            print(out)
        else:
            print('Invalid command')
            self._help()

        return True

    @staticmethod
    def _help():
        """Print out command help."""
        print("""Help:
        h, help                   show help output
        q, quit                   quit program
        r, reset                  reset picks and weights
        s, status                 show status of picks and weights
        b <hero>, ban <hero>      ban hero from pool
        a <hero>, ally <hero>     ally hero pick
        e <hero>, enemy <hero>    enemy hero pick
        i <hero>, info <hero>     show hero info""")

    def _display_hero_weights(self):
        """Print out subset of hero weights, showing best and worst picks."""
        weights = self._draft_engine.sorted_hero_weights()
        num_heroes = len(weights)

        # default list 10 best heroes and 5 worst
        # in the future, add commands for configuring values
        num_best = 15
        num_worst = 5
        assert num_heroes >= num_best
        assert num_heroes >= num_worst

        print('Status:')
        print('Bans: ' + ', '.join(self._draft_engine.bans))
        print('Enemy picks: ' + ', '.join(self._draft_engine.enemy_picks))
        print('Ally picks: ' + ', '.join(self._draft_engine.ally_picks))

        print(f'{num_best} best picks and {num_worst} worst picks:')
        for i in range(0, num_best):
            print(f'  {weights[i][1]}, {weights[i][0]}')

        print('...')
        for i in range(num_heroes - num_worst, num_heroes):
            print(f'  {weights[i][1]}, {weights[i][0]}')

    def run(self):
        """Run CLI, looping prompt until exit."""
        while self._prompt():
            pass


def main():
    """Main for running DDA CLI."""
    # TODO: add argument handling for different file name
    hero_data_file = 'hero_data.json'
    try:
        with io.open(hero_data_file, 'r', encoding='utf-8-sig') as json_file:
            hero_data = json.load(json_file)
    except FileNotFoundError:
        print(f'error: file {hero_data_file} not found')
        return

    draft_cli = DraftCLI(hero_data)
    draft_cli.run()


if __name__ == '__main__':
    main()
