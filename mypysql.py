import mysql.connector
from typing import Final
from enums import *
from config_secrets import DATABASE_CONFIG
'''
#*EXIT CODES
-1 = some error
0 = sucessfully run
1 = already in table
'''
def exe(command, params=None):
    try:
        # Ensure the connection is still alive
        if not DB.is_connected():
            print("Reconnecting to MySQL...")
            DB.reconnect(attempts=3, delay=2)  # Attempt to reconnect
            global shell  # Update the cursor after reconnecting
            shell = DB.cursor()

        # Execute query
        if params:
            shell.execute(command, params)
        else:
            shell.execute(command)
        
        return shell.fetchall()  # Fetch and return results
    
    except mysql.connector.errors.OperationalError as e:
        print(f"MySQL Error: {e}")
        return None  # Return None if query execution fails

# Database connection using configuration from config_secrets.py
DB = mysql.connector.connect(**DATABASE_CONFIG)
shell = DB.cursor()
##myuser localSai

####################################################
#####CHECKING IF TABLE EXISTS AND CREATE IF NOT#####
####################################################

#!WEIRD if statments are not working to check if the tables names are in the output of SHOW TABLES
exe("SHOW TABLES")
if(f'{Channels.Table.value}') in shell:
    print("found spells")
else:
    exe(f"CREATE TABLE IF NOT EXISTS {Channels.Table.value} (serverID BIGINT(255) PRIMARY KEY, {Channels.Roll.value} BIGINT(255), {Channels.Spell.value} BIGINT(255))")

if(f'{Dice.Table.value}') in shell:
    print("found dice")
else:
    exe(f"CREATE TABLE IF NOT EXISTS {Dice.Table.value} ({Dice.UserID.value} BIGINT(255) PRIMARY KEY, {Dice.Crit.value} BIGINT(255), {Dice.Natone.value} BIGINT(255))")

def upDateChannels(guildID: int, channelID: int, type: Channels):
    # Check if the server exists in the table
    result = exe(f"SELECT 1 FROM {Channels.Table.value} WHERE {Channels.Server.value} = %s", (guildID,))
    
    if result:
        # If the server exists, update the existing entry
        exe(f"UPDATE {Channels.Table.value} SET {type.value} = %s WHERE {Channels.Server.value} = %s", (channelID, guildID))
    else:
        # Otherwise, insert a new row
        exe(f"INSERT INTO {Channels.Table.value} ({Channels.Server.value}, {type.value}) VALUES (%s, %s)", (guildID, channelID))

    DB.commit()
    return 0  # Successfully added or updated

def getChannels(key: int, table: Enum) -> tuple:
    if table == Channels:
        result = exe(f"SELECT {Channels.Roll.value}, {Channels.Spell.value} FROM {Channels.Table.value} WHERE {Channels.Server.value} = %s", (key,))
    elif table == Dice:
        result = exe(f"SELECT {Dice.Crit.value}, {Dice.Natone.value} FROM {Dice.Table.value} WHERE {Dice.UserID.value} = %s", (key,))
    else:
        return (None, None)  # Default return for invalid table input

    if result and len(result) > 0:
        return result[0]  # Return row as-is (None values stay None)
    else:
        return (None, None)  # Return None tuple if no entry found


def increaseValue(userID: int, colName: Dice):
    # Check if the user exists
    result = exe(f"SELECT {colName.value} FROM {Dice.Table.value} WHERE {Dice.UserID.value} = %s", (userID,))
    
    if result:
        # User exists, increment the value
        current_value = result[0][0]  # Fetch column value
        new_value = (current_value or 0) + 1  # Handle None (NULL case)
        exe(f"UPDATE {Dice.Table.value} SET {colName.value} = %s WHERE {Dice.UserID.value} = %s", (new_value, userID))
    else:
        # User does not exist, insert new row
        exe(f"INSERT INTO {Dice.Table.value} ({Dice.UserID.value}, {colName.value}) VALUES (%s, %s)", (userID, 1))
    
    DB.commit()
    return 0