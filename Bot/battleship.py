import discord

from Bot.gameinterface import GameInterface


class BattleShip(GameInterface):
    def __init__(self, lobby):
        self.lobby = lobby
        self.num_channels = 2

    async def get_channel_name(self, member: discord.member):
        return f'battleship-{member.name}'

    async def on_create(self):
        # send a game instruction msg into the user channels
        embed = discord.Embed(title="Destroyer", description='Place your ship.', color=0x55ACEE)
        embed.set_author(name='Battleship!', icon_url='https://www.pngrepo.com/download/323821/battleship.png')
        # embed.set_image(url='https://www.pngrepo.com/download/323821/battleship.png')
        embed.set_thumbnail(
            url='https://lh3.googleusercontent.com/proxy/ch9h42mP-EPuRogTf0mlwXVnJzA1SSh_e52NVm3VpVRxfebzPtcuSX9vF91FPFbrZFu1Yd20deLYhiW1AVVRNt7Akr4NfuoE')
        # embed.add_field(name="Destroyer", value="<:boom:>", inline=False)
        width = 8
        height = 8
        arr = [[0] * height for i in range(width)]

        val = ''
        for i in range(height):
            for j in range(width):
                val += ':ocean:'  # str(arr[i][j])
            val += '\n'
        embed.add_field(name='Board', value=val, inline=True)

        await self.lobby.user_channels[0].send(embed=embed)
        await self.lobby.user_channels[1].send(embed=embed)

    async def on_end(self):
        pass

    async def on_input(self, data):
        channel = None
        if isinstance(data, discord.RawReactionActionEvent):
            channel = self.lobby.guild.bot.get_channel(data.channel_id)
            await channel.send('reaction')
        elif isinstance(data, discord.Message):
            channel = data.channel
            await channel.send('msg')

    async def update(self):
        pass
