import asyncio

import discord
from discord import Message
from discord.ext import commands
from dotenv import load_dotenv
import os

import platform

# Fixes event loop exception when shutting down bot through code, not really needed just makes shutdown cleaner
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from Bot.guild import Guild

# Loads bot token from .env file, which isn't committed to repo
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Set bot command prefix to '!'
client = commands.Bot(command_prefix='!')
# Initialize a dict containing all the guilds the bot is in
guilds = {}


async def setup_guild(guild):
    # Setup a Guild class representation for them in the guilds dict
    guilds[guild.id] = Guild(client)
    # Loop through all channels in the guild
    for channel in guild.channels:
        # Hardcoded channel name to set the lobby, which is the only place allowing this bot's commands
        # TODO Allow server to set it's own lobby channel and implement saving/loading server-specific info
        if channel.name == 'lobby-main':
            # Call setup on the guild, providing the found channel, then exit the for-loop
            await guilds[guild.id].setup(channel)
            break


@client.event
async def on_ready():
    # Set bot presence to show how many servers it's in, as well as setting online status
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f'over {len(client.guilds)} servers.'))
    # Loop through all guilds the bot is in
    for guild in client.guilds:
        # Initializes our own Guild class and adds it to the guilds dict
        await setup_guild(guild)
    # Finished initialization
    print(f'{client.user.name} is ready...')


@client.event
async def on_guild_join(guild):
    # Called when a newly joined guild appears
    # Initializes our own Guild class and adds it to the guilds dict
    await setup_guild(guild)


@client.event
async def on_guild_remove(guild):
    # Remove the guild from our guilds dict
    guilds.pop(guild.id)


async def handle_invite(e):
    # Ensure emoji added was the correct one
    if str(e.emoji) != '✅':
        return False

    # Make sure an invite was found for the message clicked
    invite = None
    # For each invite in the guilds pending_invites dict
    for inv in guilds[e.guild_id].pending_invites.values():
        # If the invite msg_id is equal to the events msg id
        if inv.msg.id == e.message_id:
            # We found the invite the event belongs to
            invite = inv
            break

    # If no invite was found return False
    if not invite:
        return False

    # If the invite has a whitelist for who can join it
    if invite.whitelist:
        # If the user that reacted isn't in that list
        if e.user_id not in invite.whitelist:
            # Return False
            return False
    else:
        # Otherwise, if the user that reacted is the actual owner of the invite, also return False
        if e.user_id == invite.main_member.id:
            return False

    # Set the second member to the user that added the reaction
    invite.joining_member = e.member
    # Setup the game
    await guilds[e.guild_id].setup_game(e.message_id)
    return True


def get_game(e):
    # For all games in this guild's game dict
    # The key of this dict is the invite msg id
    for msg_id in guilds[e.guild_id].games:
        # For each user channel the game owns
        for channel in guilds[e.guild_id].games[msg_id].user_channels:
            # If the event channel is equal to any of those channels
            if e.channel_id == channel.id:
                # Return the game object
                return guilds[e.guild_id].games[msg_id]
    # If no game was found, return None
    return None


async def handle_game_input(e):
    # Get the game the event was from
    game = get_game(e)
    # Make sure a game was found for the message
    if not game:
        return False
    # Pass event to game's input method
    await game.input(e)
    # Confirm that this was a game input
    return True


@client.event
async def on_raw_reaction_add(e):
    # Return if the reaction event is from the bot itself adding the emoji
    if e.member.id == client.user.id:
        return

    # Helper method to handle reacting to an invite msg
    if await handle_invite(e):
        return
    else:
        # If it's not an invite message, handle a game input reaction
        await handle_game_input(e)


@client.event
async def on_message(msg: Message):
    # Make sure the msg author isn't the bot itself
    if msg.author.id == client.user.id:
        return

    # Get the guild the msg is in
    guild = guilds[msg.guild.id]
    # Loop through all games in the guild
    for game in guild.games.values():
        # If the channel the message is in is a game channel
        if msg.channel in game.user_channels:
            # Pass the msg to the game's input method
            await game.input(msg)
            break
    # Process commands regardless, otherwise this event would block normal commands too
    await client.process_commands(msg)


@client.command()
async def c(ctx, *args):
    # Challenge command
    # If the command was called in the game channel
    if ctx.channel.id == guilds[ctx.guild.id].game_channel:
        # Create the challenge/invite
        await guilds[ctx.guild.id].challenge(ctx, args)
    else:
        # Notify the user that they're in the wrong channel
        msg = await ctx.send('The game is not available in this channel.')
        # Delete both the user msg and bot response msg after 3 seconds
        await msg.delete(delay=3.0)
        await ctx.message.delete(delay=3.0)


@client.command()
async def end(ctx):
    # This command only cleans up the guild it was called in

    # Make sure only Mattdokn can run this command
    if ctx.author.id == 137672086536585217:
        # Delete the command msg
        await ctx.message.delete()
        # While games are running in this guild
        while guilds[ctx.guild.id].games:
            # Get the game at the top of the list
            game = list(guilds[ctx.guild.id].games.values())[0]
            print(f'Ending game {game.user_channels}.')
            # Wait for the game to initialize if it's still working
            while not game.initialized:
                await asyncio.sleep(.05)
            # End the game
            await game.end()
        # While there are open invites
        while guilds[ctx.guild.id].pending_invites:
            # Get the invite at the top of the list
            invite = list(guilds[ctx.guild.id].pending_invites.values())[0]
            # Delete the invite message
            await invite.msg.delete()
            # Pop it from the pending_invites dict
            guilds[ctx.guild.id].pending_invites.pop(invite.main_member.id)


# Starts the bot using our token
client.run(TOKEN)
