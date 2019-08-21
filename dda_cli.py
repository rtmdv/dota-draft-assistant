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

    def __init__(self, name, aliases, good_against,
                 bad_against, works_well_with):
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


class DraftEngine:
    """Back end engine for draft assistant."""

    hero_data: Dict[str, Hero]
    hero_alias_map: Dict[str, str]
    hero_weights: Dict[str, int]
    ally_picks: List[str]
    enemy_picks: List[str]

    def __init__(self, hero_data):
        self.hero_data = {}
        self.hero_alias_map = {}
        # TODO: load in hero data and set up alias map
        self.reset()

    def reset(self):
        self.ally_picks = []
        self.enemy_picks = []
        self.hero_weights = {}

    def resolve_hero_name(self, alias: str):
        pass

    def ally_hero_pick(self, hero_pick: str):
        """Process ally hero pick and update hero weights."""
        return 0

    def enemy_hero_pick(self, hero_pick: str):
        """Process enemy hero pick and update hero weights."""
        return 0

    def hero_info(self, hero: str):
        # check existence
        return self.hero_data[hero].dict()

    def sorted_hero_weights(self) -> List[Tuple[str, int]]:
        """Sort hero weights dict by value and return list of tuples."""
        sorted_weights = sorted(self.hero_weights.items(),
                                key=operator.itemgetter(1))
        return sorted_weights


class DraftCLI:
    """Command line interface for draft engine."""

    draft_engine: DraftEngine
    prompt_str: str = "> "

    def __init__(self, hero_data):
        self.draft_engine = DraftEngine(hero_data)
        print('Draft engine initialized')

    def prompt(self):
        """Prompt for user input and process command.

        Returns boolean for whether to continue prompting or exit.
        """
        cmd = input(self.prompt_str)
        return self.process_command(cmd)

    def process_command(self, cmd: str):
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
            self.help()
        elif cmd_base in ('q', 'quit'):
            print('Quitting')
            return False
        elif cmd_base in ('r', 'reset'):
            self.draft_engine.reset()
            print('Reset draft engine')
        elif cmd_base in ('a', 'ally'):
            if cmd_params:
                self.draft_engine.ally_hero_pick(cmd_params)
            else:
                print('Hero argument required')
                self.help()
        elif cmd_base in ('e', 'enemy'):
            if cmd_params:
                self.draft_engine.enemy_hero_pick(cmd_params)
            else:
                print('Hero argument required')
                self.help()
        elif cmd_base in ('i', 'info'):
            if cmd_params:
                print(self.draft_engine.hero_info(cmd_params))
            else:
                print('Hero argument required')
                self.help()
        else:
            print('Invalid command')
            self.help()

        return True

    def help(self):
        """Print out command help."""
        print("""Help:
        h, help
        q, quit
        r, reset
        a <hero>, ally <hero>
        e <hero>, enemy <hero>
        i <hero>, info <hero>""")

    def run(self):
        """Run CLI, looping prompt until exit."""
        while self.prompt():
            pass


def main():
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
