import interactions
from interactions.client.utils import link_in_embed
from interactions import Client, Intents, listen
from interactions import slash_command, OptionType, SlashContext, SlashCommandChoice, SlashCommandOption, Permissions, ContextType, ChannelType
from spells import getSpell, containsNumber, checkName, getClassChoices, getList
from dice import rollDiceString
from helper import gen_invis, splitLongStrings
from mypysql import getChannels, upDateChannels, increaseValue
from enums import Channels, Dice
from config_secrets import (
    DISCORD_BOT_TOKEN,
    DND_CHANNELS,
    ROLL_COLORS,
    API_ENDPOINTS
)
import random

bot = Client(sync_interactions=True,intents=Intents.ALL)
#Channel IDs imported from config_secrets.py
dndChannels = DND_CHANNELS

#random hex number generator to FFFFFF
def randomHex():
    return f"{random.randint(0, 0xFFFFFF):06x}"

#LOCAL FUNCTIONS
def AuthCheck(channelID: int, guildID: int, authorID: int, typeCheck: str = None):
    roll, spell = getChannels(int(guildID), Channels)  # Assuming getChannels returns a tuple (roll, spell)
    print(f"{channelID} | {guildID} | {authorID} | {typeCheck}")
    if typeCheck == 's':
        return (channelID in dndChannels or channelID == spell) and authorID != bot.user.id
    elif typeCheck == 'd':
        return (channelID in dndChannels or channelID == roll) and authorID != bot.user.id

# Colors imported from config_secrets.py

def colorVal(roll_total, dice_sides, dice_rolls):
    """
    Determine the color based on the quality of a dice roll
    
    Args:
        roll_total: The total value of the roll(s) without modifier
        dice_sides: The number of sides on the die (e.g., 20 for d20)
        dice_rolls: List of individual dice results
    
    Returns:
        Color hex code based on roll quality
    """
    # For multiple dice, use the average
    if len(dice_rolls) > 1:
        roll_total = round(float(roll_total/len(dice_rolls)))
    
    # Special case for d2 (coin flips)
    if dice_sides < 3:
        return ROLL_COLORS['FAILURE'] if roll_total < dice_sides else ROLL_COLORS['CRITICAL']
    
    # For regular dice, split into thirds
    threshold = dice_sides / 3
    if roll_total <= threshold:
        return ROLL_COLORS['FAILURE']    # Bottom third is bad
    elif roll_total <= 2 * threshold:
        return ROLL_COLORS['AVERAGE']    # Middle third is average
    else:
        return ROLL_COLORS['CRITICAL']   # Top third is great


@listen()
async def on_ready():
    print("Ready")

def format_roll_result(roll_result, dice_str, user_name, user_avatar, user_id):
    """Format the dice roll result into an embed"""
    rolls, modifier, max_sides = roll_result[1], roll_result[2], roll_result[3]
    total = roll_result[0]
    
    # Calculate base roll without modifier
    if len(rolls) > 1:
        base_roll = int(round(float((total - modifier) / len(rolls))))  # avg rolls without modifier
    else:
        base_roll = total - modifier  # single roll without modifier

    # Format the roll display
    # Ensure rolls is treated as a list
    roll_list = rolls if isinstance(rolls, list) else [rolls]
    
    if len(roll_list) == 1:
        roll_display = str(roll_list[0])
    else:
        roll_display = str(roll_list)
    
    if modifier != 0:
        roll_display += f" + {modifier}"

    # Create embed
    embed = interactions.Embed(
        title=dice_str,
        description=f"Sum: {total}",
        color=colorVal(total - modifier, max_sides, rolls)
    )
    embed.add_field(name="Dice", value=roll_display)
    
    # Determine footer text based on roll quality
    if base_roll == 1:
        increaseValue(int(user_id), Dice.Natone)
        footer = f"{user_name} rolled a natural 1"
    elif base_roll == max_sides:
        increaseValue(int(user_id), Dice.Crit)
        footer = f"{user_name} rolled a natural {max_sides}"
    else:
        quality = "amazing" if max_sides - base_roll < max_sides * 0.5 else "poor"
        footer = f"This {quality} roll was made by {user_name}"

    embed.set_thumbnail(user_avatar)
    embed.set_footer(text=footer, icon_url=user_avatar)
    return embed

@listen()
async def on_message_create(event: interactions.events.MessageCreate):
    # Quick check if this is a potential dice roll
    if not AuthCheck(event.message.channel.id, event.message.guild.id, event.message.author.id, 'd'):
        return

    msg = event.message.content
    
    # Ignore if it starts with a command prefix
    if any(msg.startswith(prefix) for prefix in "!/.#&?<@:;"):
        return
        
    # Process potential dice roll
    if containsNumber(msg):
        roll = rollDiceString(msg, event.message.author.id)
        if roll == "Error":
            error_embed = interactions.Embed(
                title="Error",
                description=f"Invalid dice roll\nInput: {msg}\nPlease use format: 2d10+3 (max: 20d100)",
                color="#FFFF00"
            )
            await event.message.reply(embed=error_embed)
        else:
            result_embed = format_roll_result(roll, msg, event.message.author.username, event.message.author.avatar.url, event.message.author.id)
            await event.message.delete()
            await event.message.channel.send(embed=result_embed, silent=True)

@slash_command(
    name="set",
    description = "Set channels",
    sub_cmd_name="spell",
    sub_cmd_description="Sets the channel for the spells command",
    default_member_permissions=Permissions.MANAGE_CHANNELS | Permissions.MANAGE_GUILD | Permissions.ADMINISTRATOR,
    contexts =[ContextType.GUILD],
    options=[
        SlashCommandOption(
            name="channel",
            description= "Channels in server",
            required = True,
            type = OptionType.CHANNEL,
            channel_types=[ChannelType.GUILD_TEXT]
        )
    ]
)
async def setspellchannel(ctx: SlashContext, channel):
    if channel == 0:
        await ctx.send("Please choose a channel")
    else:
        upDateChannels(int(ctx.guild_id), int(channel.id), Channels.Spell)
        await ctx.send(f"<#{channel.id}> has been set as your Spells channel! :)")

@slash_command(
    name="set",
    description = "Set channels",
    sub_cmd_name="roll",
    sub_cmd_description="Sets the channel for the spells command",
    default_member_permissions=Permissions.MANAGE_CHANNELS | Permissions.MANAGE_GUILD | Permissions.ADMINISTRATOR,
    contexts =[ContextType.GUILD],
    options=[
        SlashCommandOption(
            name="channel",
            description= "Channels in server",
            required = True,
            type = OptionType.CHANNEL,
            channel_types=[ChannelType.GUILD_TEXT]
        )
    ]
)
async def setrollchannel(ctx: SlashContext, channel):
    if channel == 0:
        await ctx.send("Please choose a channel")
    else:
        upDateChannels(int(ctx.guild_id), int(channel.id), Channels.Roll)
        await ctx.send(f"<#{channel.id}> has been set as your dice roll channel! :)")

@slash_command(
    name="spell",
    description="Get a spell",
    options=[
        SlashCommandOption(
            name="spell_name",
            description="Gets you info on the spell",
            required=False,
            type=OptionType.STRING
        ),
        SlashCommandOption(
            name="spell_school",
            description="The spell's school",
            required=False,
            type=OptionType.STRING,
            choices = [
                SlashCommandChoice(name="Abjuration", value="Abjuration"),
                SlashCommandChoice(name="Conjuration", value="Conjuration"),
                SlashCommandChoice(name="Divination", value="Divination"),
                SlashCommandChoice(name="Enchantment", value="Enchantment"),
                SlashCommandChoice(name="Evocation", value="Evocation"),
                SlashCommandChoice(name="Illusion", value="Illusion"),
                SlashCommandChoice(name="Necromancy", value="Necromancy"),
                SlashCommandChoice(name="Transmutation", value="Transmutation")
            ]
        ),
        SlashCommandOption(
            name="spell_class",
            description="Class of the spell",
            required=False,
            type=OptionType.STRING,
            choices = getClassChoices()
        ),
        SlashCommandOption(
            name="spell_level",
            description="Level of the spell",
            required=False,
            type=OptionType.INTEGER,
            choices= [
                SlashCommandChoice(name="0", value=0),
                SlashCommandChoice(name="1", value=1),
                SlashCommandChoice(name="2", value=2),
                SlashCommandChoice(name="3", value=3),
                SlashCommandChoice(name="4", value=4),
                SlashCommandChoice(name="5", value=5),
                SlashCommandChoice(name="6", value=6),
                SlashCommandChoice(name="7", value=7),
                SlashCommandChoice(name="8", value=8),
                SlashCommandChoice(name="9", value=9)
            ]
        )
    ]
)
async def spell(ctx: SlashContext, spell_name: str = None, spell_school: str = None, spell_class: str = None, spell_level: int = -1):
    if not AuthCheck(ctx.channel_id, ctx.guild_id, ctx.author_id, 's'):
        print(AuthCheck(ctx.channel_id, ctx.guild_id, ctx.author_id, 's'))
        await ctx.send("This is channel is not set to use the spells command")
        return
    if not (spell_name or spell_school or spell_class or spell_level):
        await ctx.send("You must provide at least one option!")
    elif spell_name is not None:
        usrSpellName = spell_name
        if not(containsNumber(usrSpellName)):
            usrSpellName = checkName(usrSpellName).lower()
            if usrSpellName == "ep":
                await ctx.send("Internal error, list empty")
        else:
            await ctx.send("Not a valid name for a spell.")
            return
        # appendSpellName = "spells/" + usrSpellName
        url = API_ENDPOINTS["spells"] + usrSpellName

        spellObj = []
        spellObj = getSpell(url)
        embed = interactions.Embed(title=spellObj[0], description=spellObj[1] + " | " + spellObj[2], color=f"#{randomHex()}")

        embed.add_field(name="Casting Time", value=spellObj[3])
        embed.add_field(name="Duration", value=spellObj[4])

        embed.add_field(name="range", value=spellObj[5])
        embed.add_field(name="components", value=str(spellObj[6]))

        embed.add_field(name="Materials", value=spellObj[7])
        embed.add_field(name="Description", value=spellObj[8][0])
        for e in spellObj[8][1:]:
            embed.add_field(name=gen_invis(), value=e)
        embed.add_field(name=link_in_embed("Link to Api", url), value=gen_invis())
    elif spell_name is None and (spell_school or spell_class or spell_level):
        apiURL_base = API_ENDPOINTS["spells_search"]
        Title = ""
        if spell_school:
            apiURL_base+=f"&school={spell_school}"
            Title += spell_school+" "
        if spell_class:
            apiURL_base+=f"&spell_lists={spell_class.lower()}"
            Title += spell_class+" "
        if spell_level or spell_level == 0 and spell_level != -1:
            apiURL_base+=f"&level_int={spell_level}"
            Title += f"Level {spell_level}"
        print(apiURL_base)
        names = getList(apiURL_base, "slug")
        if names == "empty":
            embed = interactions.Embed(title=Title,description="No spells were found" ,color="#FFFF00")
            embed.set_footer(text=link_in_embed("Link to Api", apiURL_base))
        else:
            formatNames = splitLongStrings("\n".join(names))
            embed = interactions.Embed(title=f"{Title} Spells",color=f"#{randomHex()}")
            for e in formatNames:
                embed.add_field(name=f"{len(names)} were found", value=e)
            embed.add_field(name=link_in_embed("Link to Api", apiURL_base), value=gen_invis())
    await ctx.send(embeds=embed)

@slash_command(
    name="dice_stats",
    description="Get Your statistics on your dice rolls."
)
async def stats(ctx: SlashContext):
    crit, natone = getChannels(int(ctx.author_id), Dice)
    if crit == None:
        crit = 0
    if natone == None:
        natone = 0

    embed = interactions.Embed(title=ctx.author.nick, color=f"#{randomHex()}")
    embed.add_field(name="Critical Rolls",value=crit)
    embed.add_field(name="Natural One Rolls", value=natone)
    await ctx.send(embeds=embed)

@slash_command(
    name = "help",
    description= "Get help with the bot"
)
async def help(ctx: SlashContext):
    embed = interactions.Embed(title="Don't know how to use the bot?", description="Don't worry this will tell you everything you need to know.", color="#FFFF00")
    embed.add_field(
        name="Dice Roller",value=(
            "This bot has a basic dice roller. To set it up, an admin must assign "
            "a channel for rolling dice.\nTo set the channel, use:\n"
            "'/set roll channel:[type name of channel]'\nOnce set, you can type "
            "commands like '1d20+4'. The limitations are 20d100+[modifier].\n"
            "You can replace '+' with '-' as well."
        ),)
    embed.add_field(
        name="Spell",value=(
            "This is a slash command, but before using it, an admin must set a channel for spell commands.\n"
            "To set the channel, use:'/set spell channel:[type name of channel]'\n"
            "This command uses an API to gather information on the spells you want to look up.\n"
            "If the API does not have the spell you're looking for, it will find the spell "
            "that is mathematically closest to what you searched for.\nThis also "
            "means you can misspell names, and it will do its best to find the "
            "closest matching spell."
            ))
    await ctx.send(embeds=embed)

# Bot token imported from config_secrets.py
bot.start(DISCORD_BOT_TOKEN)