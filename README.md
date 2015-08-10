# HaxballParser
Parses Haxball replays and outputs them in a human readable format.

Python port of https://github.com/jonnyynnoj/haxball-replay-parser

---

### Installation
	python setup.py install
---
### Usage
	Make sure Scripts/ is in PATH
	haxballparser # Will parse hbr files in current directory
	haxballparser C:/Path/to/folder/with/hbr/files/
	haxballparser C:/Path/to/hbr/file/
---
### Embedding
```python
from HaxballParser import dump
file = "C:/Path/to/file"
dumpresp = dump(file)
dumpraw = dumpresp.result
prettyres = dumpresp.prettify()
```
Short example of a result (dumpraw):

    {'Version': 12,
     'Replay length': '00:18:02',
     'Room Name': 'POATTAO RUSLTERS SEALS',
     'Locked': True,
     'Score Limit': 0,
     'Time Limit': 7,
     'Red score': 0,
     'Blue score': 0,
     'Current match time': '00:00:00',
     'Paused': False,
     'Stadium': 'Big Easy',
     'In progress': True,
     'Players': [Player(ID=2, name=scotta\a, country=us, team=Spectator, admin=True, avatar=o7),
                 Player(ID=13, name=qt stream, country=us, team=Spectator, admin=False, avatar=:),
                 Player(ID=8, name=texas, country=us, team=Blue, admin=False, avatar=yo),
                 ...],
     'Actions': [Action(time=00:00:00, senderID=6, action=playerChat, parsed=Said: GL DIAF),
                 Action(time=00:00:00, senderID=15, action=playerChat, parsed=Said: I will type),
                 ...]}
Short example of a pretty output (prettyres):

    REPLAY INFO
      Version 12
      Length: 00:18:02

    ROOM INFO
      Room name: POATTAO RUSLTERS SEALS
      Scores: Red 0 - 0 Blue
      Time limit: 7 - Score limit: 0
      Current match time: 00:00:00
      Match in progress: True

    PLAYERS LIST
      Red:
        Prizzle
        Ben Roethlisberger
        Justin (-09)
        trololo
      Blue:
        texas
        {c}row 
        dr feli
        yew
      Spectators:
        scotta\a
        qt stream
        GReddy
        Scooter
      Throughout the replay:
        Joined:
          tgfp
        Left/Kicked/Banned:
          tgfp

    ACTION LIST
    (00:00:00) Ben Roethlisberger -> Said: GL DIAF
    (00:00:00) Justin (-09) -> Said: I will type
    (00:00:01) scotta\a -> Said: good luck
    (00:00:01) Ben Roethlisberger -> Said: HARF HARF HARF
    ...