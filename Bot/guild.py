from discord.ext.commands import Context

import Bot.gamelobby
from Bot.filler import Filler


class Guild:
    def __init__(self, bot):
        # Keep a reference to the bot
        self.bot = bot
        # The channel where challenges can be sent in
        self.game_channel = None
        # key is the invite message id
        self.games = {}
        # key is the main member who initiated the invite
        self.pending_invites = {}

    async def setup(self, channel):
        # Setup was called for this guild, with the provided game_lobby channel
        self.game_channel = channel.id
        print(f'Assigned channel {self.game_channel}!')

    async def challenge(self, c, args):
        # If the user that made the challenge already has an open invte
        if c.author.id in self.pending_invites:
            print('Getting rid of old pending invite...')
            # Remove it
            await self.pending_invites.pop(c.author.id).msg.delete()
        print(f'{c.author.name} has started a game.')
        # Ask the Filler class to create an invite for us using the command args
        invite = await Filler.create_invite(c, args)
        # If creation was successful
        if invite:
            # Add the invite to pending_invites dict
            self.pending_invites[c.author.id] = invite
        else:
            print('Something bad happened w/ the invite')

    async def setup_game(self, msg_id: int):
        # Setup a game based on an invite message's id
        invite = None
        # For all invites in our pending_invites
        for inv in self.pending_invites:
            # If our msg_id matches the invite's msg_id
            if msg_id == self.pending_invites[inv].msg.id:
                # Set the invite to that one
                invite = self.pending_invites[inv]
                break
        # If no invite was found print a very detailed error message
        if not invite:
            print('RUH ROH RAGGY')
            return

        # If the invite is already being used for a game print another super helpful error message
        if invite.msg.id in self.games:
            print('Other rut roh raggy')
            return

        # Create the GameLobby and put it in our games dict
        self.games[invite.msg.id] = Bot.gamelobby.GameLobby(invite, self)
        # Call setup on the new gamelobby
        await self.games[invite.msg.id].setup()
        # Remove the invite from the pending dict
        self.pending_invites.pop(invite.main_member.id)
