import random

#string in format ({number}d{number})+{number} else error
def rollDiceString(diceString, ID):
    # Convert to lowercase and verify basic format
    diceString = diceString.lower()
    if diceString.count("d") != 1 or sum(diceString.count(op) for op in ["+", "-"]) > 1:
        return "Error"

    # Parse the dice string into components
    modifier = 0
    dice_parts = diceString.split("d")
    
    if len(dice_parts) != 2:
        return "Error"
        
    num_dice = dice_parts[0]
    # Handle the modifier part
    sides_part = dice_parts[1]
    if "+" in sides_part:
        sides, mod = sides_part.split("+")
        modifier = int(mod) if mod.isdigit() else "Error"
    elif "-" in sides_part:
        sides, mod = sides_part.split("-")
        modifier = -int(mod) if mod.isdigit() else "Error"
    else:
        sides = sides_part
        
    # Validate all numbers
    try:
        num_dice = int(num_dice)
        sides = int(sides)
        if isinstance(modifier, str):
            return "Error"
    except ValueError:
        return "Error"
        
    # Roll the dice
    inputRoll = rollDice(num_dice, sides, ID)
    if inputRoll == "Error":
        return "Error"
        
    sumRoll = inputRoll[0] + modifier
    listRoll = inputRoll[1]
    
    # Return in exact format: [sum of dice + modifier, list of rolls, modifier, max number on die]
    return [sumRoll, listRoll, modifier, sides]

#################################
#########Helper function#########
#################################

#dice roller with number dice and number of sides on dice with max dice 20 and max sides 100 save each dice roll
def rollDice(numberDice, numberSides, usrID):
    ##check if they are numbers if not then throws error
    try:
        int(numberDice)
        int(numberSides)
    except ValueError:
        return "Error"

    ##limitation to all uses except owner to prevent messages being longer than discord limit
    #! HF - make userid part of a config file (or maybe a list of userid's instead of just one)
    if (numberDice > 20 or numberSides > 100) and (not usrID == 1038719939747532820):
        return "Error"
    dice = []
    for i in range(numberDice):
        dice.append(random.randint(1, numberSides))
    #[sum  of dice, all roles of dice]
    return [sum(dice), dice]
