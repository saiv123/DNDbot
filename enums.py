from enum import Enum

class Channels(Enum):
    Table = "channels"
    Server = "serverID"
    Roll = "rolls"
    Spell = "spells"

class Dice(Enum):
    Table = "DiceRoll"
    UserID = "userID"
    Crit = "crit"
    Natone = "natone"
