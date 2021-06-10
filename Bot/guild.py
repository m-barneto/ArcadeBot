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
        if c.author.id in self.pending_invites:
            print('Getting rid of old pending invite...')
            await self.pending_invites.pop(c.author.id).msg.delete()
        print(f'{c.author.name} has started a game.')
        invite = await Filler.create_invite(c, args)
        if invite is not None:
            self.pending_invites[c.author.id] = invite
        else:
            print('Something bad happened w/ the invite')

    async def setup_game(self, msg_id: int):
        invite = None
        for inv in self.pending_invites:
            if msg_id == self.pending_invites[inv].msg.id:
                invite = self.pending_invites[inv]
                break
        if not invite:
            print('RUH ROH RAGGY')
            return

        if invite.msg.id in self.games:
            print('Other rut roh raggy')
            return

        self.games[invite.msg.id] = Bot.gamelobby.GameLobby(invite, self)
        await self.games[invite.msg.id].setup()
        self.pending_invites.pop(invite.main_member.id)
