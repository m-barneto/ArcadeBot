import discord


class GameLobby:
    def __init__(self, invite, guild):
        self.initialized = False
        # TODO setup single player vs AI games where the joining_member is None
        self.users = [invite.main_member, invite.joining_member]
        self.user_channels = []
        self.guild = guild
        self.invite = invite
        self.game = None

    async def setup(self):
        guild = self.invite.msg.guild
        # admin_role = get(guild.roles, name="Staff")

        self.game = self.invite.game_type(self)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
            #admin_role: discord.PermissionOverwrite(read_messages=True),
        }

        for i in range(self.game.num_channels):
            overwrites[self.users[i]] = discord.PermissionOverwrite(read_messages=True)

            channel = await guild.create_text_channel(
                await self.game.get_channel_name(self.users[i]),
                overwrites=overwrites,
                category=self.guild.bot.get_channel(self.guild.game_channel).category
            )

            self.user_channels.append(channel)

            overwrites.pop(self.users[i])
        await self.game.on_create()

    async def end(self, msg='shutdown'):
        await self.game.on_end()
        for channel in self.user_channels:
            await channel.delete()
        if msg == 'shutdown':
            await self.invite.msg.delete()
        elif msg == 'special':
            pass
        else:
            await self.update_msg(msg)
        self.guild.games.pop(self.invite.msg.id)

    async def input(self, data):
        await self.game.on_input(data)

    async def update_msg(self, content: str):
        await self.invite.msg.edit(content=content)
