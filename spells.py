from typing import Dict, List, Optional, Union, Any
import requests
import json
from Levenshtein import distance
from helper import splitLongStrings
from interactions import SlashCommandChoice

#TODO: make table for spells, add spells as you do requests,
#TODO: check database first then api request then add to db if request is made

# Import API configuration from config_secrets.py
from config_secrets import API_ENDPOINTS

api: str = API_ENDPOINTS["spells"]

def apiResponse(requestUrl: str) -> Dict[str, Any]:
    """
    Make a GET request to the API and return JSON response
    
    Args:
        requestUrl: The API endpoint URL
        
    Returns:
        Dictionary containing the JSON response
        
    Raises:
        requests.RequestException: If the API request fails
        json.JSONDecodeError: If the response isn't valid JSON
    """
    #! HF - try/catch should happen here - json loads will fail if the response isnt right
    response = requests.request("GET", requestUrl)
    jsonObj = json.loads(response.text)
    return jsonObj

nameSpell: List[str] = []
All = apiResponse(API_ENDPOINTS["spells_list"])
for e in All["results"]:
        nameSpell.append(e["slug"])

def checkName(spellName: str) -> str:
    """
    Find the closest matching spell name in the API list
    
    Args:
        spellName: The user-provided spell name to check
        
    Returns:
        The closest matching spell name or "ep" if no spells are loaded
    """
    if len(nameSpell) > 0:
        return min(nameSpell, key=lambda x: distance(str(spellName).lower(), str(x).lower()))
    else:
        return "ep"

def containsNumber(value: Union[str, int]) -> bool:
    """
    Check if a string contains any digits
    
    Args:
        value: The string or number to check
        
    Returns:
        True if the value contains a digit, False otherwise
    """
    for character in str(value):
        if character.isdigit():
            return True
    return False

def getSpell(url: str) -> Optional[List[Union[str, List[str]]]]:
    """
    Get detailed spell information from the API
    
    Args:
        url: The API URL for the specific spell
        
    Returns:
        List containing spell details or None if the request fails
    """
    try:
        spell = apiResponse(url)
    except Exception as e:
        print(f"Problem retrieving info from server or spell name is incorrect: {e}")
        return None

    spellDisc = []
    spellDisc.append(str(spell["name"]))
    spellDisc.append(str(spell["school"]))
    spellDisc.append(spell["level"])

    spellDisc.append(str(spell["casting_time"]))
    dura = str(spell["duration"])
    if spell["requires_concentration"]:
        spellDisc.append(f"Concentration, {dura}")
    else:
        spellDisc.append(str(spell["duration"]))

    spellDisc.append(str(spell["range"]))
    spellDisc.append(str(spell["components"]))

    temp = ""
    if spell["ritual"]:
        if spell["requires_material_components"]:
            temp = "Ritual Spell, " + str(spell["material"])
        else:
            temp = "Ritual Spell, " + "No Materials"
    else:
        try:
            temp = str(spell["material"])
        except:
            temp = "No Materials"
    spellDisc.append(temp)
    spellDisc.append(splitLongStrings(spell["desc"]))
    #print("returning list of spells stuff")
    return spellDisc

def getClassChoices() -> List[SlashCommandChoice]:
    """
    Get all available spell-casting classes from the API
    
    Returns:
        List of SlashCommandChoice objects for each available class
    """
    jsonC = apiResponse(API_ENDPOINTS["spell_list"]) #returns all the classes in the api
    ##setting variables
    class_dec_all = jsonC["results"]
    class_names: List[str] = []
    choices: List[SlashCommandChoice] = []
    
    ##loops thought the sub json obj and adds them to a list of all the slug(readable name) values
    for c in class_dec_all:
        class_names.append(c["slug"])
    
    ##loops through all the sulgs and makes them into a list of slash command choices
    for n in class_names:
        choices.append(SlashCommandChoice(name=n.capitalize(), value=n.capitalize()))
    return choices

def getList(url: str, key: str) -> Union[List[str], str]:
    """
    Get a list of values from an API endpoint filtered by a key
    
    Args:
        url: The API endpoint URL
        key: The JSON key to extract from results
        
    Returns:
        List of extracted values or "empty" if no results found
        
    Note:
        This function will ONLY work with the D&D 5e API structure
    """
    jsonS = apiResponse(url)
    filter_results = jsonS["results"]
    if filter_results == []:
        return "empty"
    names: List[str] = []
    for c in filter_results:
        names.append(c[key])
    return names

if __name__ == "__main__":
    print(getClassChoices())
    #print(getSpell("https://www.dnd5eapi.co/api/spells/flame-blade/", ))