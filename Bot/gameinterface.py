import discord


class GameInterface:
    async def get_channel_name(self, member: discord.member):
        return f'game-{member.name}'

    async def on_create(self):
        pass

    async def on_end(self):
        pass

    async def on_input(self, data):
        pass
