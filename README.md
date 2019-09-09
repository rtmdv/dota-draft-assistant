# dota-draft-assistant
CLI Draft Assistant for Dota 2

Run from command line to enter draft engine interface prompt.
```
$ python3 dda_cli.py
Draft engine initialized
Help:
        h, help                   show help output
        q, quit                   quit program
        r, reset                  reset picks and weights
        s, status                 show status of picks and weights
        b <hero>, ban <hero>      ban hero from pool
        a <hero>, ally <hero>     ally hero pick
        e <hero>, enemy <hero>    enemy hero pick
        i <hero>, info <hero>     show hero info
>
```

From there, ban heroes and enter picks for allies and enemies, and observe changes to hero weights.

Example weight output deep into a draft:
```
> s
Status:
Bans: Io, Gyrocopter
Enemy picks: Chen, Alchemist, Omniknight, Dark Seer, Sven
Ally picks: Lion, Centaur Warrunner, Winter Wyvern
15 best picks and 5 worst picks:
  2, Meepo
  2, Chaos Knight
  2, Broodmother
  1, Warlock
  1, Visage
  1, Vengeful Spirit
  1, Undying
  1, Tusk
  1, Treant Protector
  1, Tiny
  1, Tinker
  1, Terrorblade
  1, Templar Assassin
  1, Techies
  1, Phantom Lancer
...
  -2, Ember Spirit
  -2, Ancient Apparition
  -3, Razor
  -3, Necrophos
  -3, Enchantress
>
```

#### Requirements:

Requires Python 3.6 or greater.

The code requires a `hero_data.json` file to be present in the working directory to use as data. (I plan to add functionality to customize the file location and allow pointing to an online location for the data). Hero counterpicks are debatable and can change with hero reworks, so I am not publishing my data file at this time, just the code framework to use data in this format.

An example of the json file, with only one hero entry with just a few sample pick relationships:
```
{
  "heroes": [
    {
      "name": "Anti-Mage",
      "aliases": [
        "anti-mage",
        "antimage",
        "am"
      ],
      "good_against": [
        "Bane",
        "Disruptor",
        "Grimstroke"
      ],
      "bad_against": [
        "Arc Warden",
        "Medusa",
        "Spectre"
      ],
      "works_well_with": [
        "Dark Seer",
        "Lion",
        "Shadow Demon"
      ]
    }
  ]
}
```

#### Note on project structure:
I separated the CLI from the draft engine itself to leave room to create other interfaces to the engine in the future, but the combined functionality in one file works for me as it is, so I will separate the code into modules at a later date when the need arises.
