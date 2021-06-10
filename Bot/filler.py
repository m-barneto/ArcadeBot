import discord

from Bot.Filler.board import Board
from Bot.Filler.filler_invite import Filler_Invite
from Bot.Filler.player import Player

from Bot.gameinterface import GameInterface


class Filler(GameInterface):
    def __init__(self, lobby):
        # Save reference to GameLobby
        self.lobby = lobby
        # Set number of required channels for this game
        self.num_channels = 2
        # Create a list to store players in the game
        self.players = []
        # Create a list to keep a reference to the chatlog messages
        self.chat = []
        # TODO have a dice roll to see who goes first
        self.turn = lobby.users[0].id
        # Initialize the game board using the size argument in the invite
        # The Data.get() is a singleton that I used because I couldn't figure out a circular import
        self.board = Board(lobby.invite.size, Data.get())

    @staticmethod
    async def create_invite(c, args):
        # TODO fix this aweful spaghetti code, I literally have 2 sections of duplicate code
        try:
            # Default size is 9
            size = 9
            whitelist = []
            member = None
            if len(args) > 0:
                size = max(3, min(14, int(args[0])))
                if len(args) > 1:
                    if args[1].lower() == 'ai':
                        whitelist.append('ai')
                    elif args[1].startswith('<@!') and args[1].endswith('>'):
                        member = await c.guild.fetch_member(int(args[1][3:len(args[1]) - 1]))
                        whitelist.append(member.id)
                        if member is None:
                            msg = await c.send('Unable to find user.')
                            await msg.delete(delay=3)
                            await c.message.delete(delay=3)
                            return None
                    else:
                        raise ValueError
            if len(args) > 0:
                if len(args) > 1:
                    if args[1].lower() == 'ai':
                        msg = None
                    else:
                        msg = f'{c.author.display_name} has challenged {member.display_name} to a {args[0]}x{args[0]} game of Filler!\nReact with :white_check_mark: to accept!'
                else:
                    msg = f'{c.author.display_name} has started a {args[0]}x{args[0]} game of Filler!\nReact with :white_check_mark: to accept!'
            else:
                msg = f'{c.author.name} has started a 9x9 game of Filler!\nReact with :white_check_mark: to accept!'
            if msg is None:
                print('ai game setup')
                await c.message.delete()
                return None
            else:
                invite_msg = await c.send(msg)
                await invite_msg.add_reaction('\U00002705')
                await c.message.delete()
                print(f'Made filler invite')
                return Filler_Invite(Filler, size, whitelist, invite_msg, c.author)
        except ValueError:
            msg = await c.send('Invalid arguments...')
            await msg.delete(delay=3)
            await c.message.delete(delay=3)
            return None

    async def get_channel_name(self, member: discord.member):
        return f'filler-{member.name}'

    async def on_create(self):
        i = 0
        for user in self.lobby.users:
            # send a game instruction msg into the user channels
            embed = discord.Embed(title="Filler", color=0x55ACEE)
            if i == 0:
                embed.add_field(name='Board (your turn)', value=self.board.render(), inline=False)
                embed.add_field(name='Score',
                                value=f'{user.display_name}: {1} - {self.lobby.users[1].display_name}: {1}')
            else:
                embed.add_field(name='Board (waiting on opponent)', value=self.board.render(), inline=False)
                embed.add_field(name='Score',
                                value=f'{self.lobby.users[0].display_name}: {1} - {user.display_name}: {1}')
            self.chat.append(await self.lobby.user_channels[i].send("Chat:"))
            msg = await self.lobby.user_channels[i].send(embed=embed)
            for reaction in self.board.data.filler_emotes:
                await msg.add_reaction(reaction)

            self.players.append(Player(user.id, msg, self.board.get_player_colors(2)[i], i))
            i += 1
        embed = discord.Embed(title='Filler', color=0x55ACEE)
        embed.add_field(name=f'{self.lobby.users[0].display_name}: {1} - {self.lobby.users[1].display_name}: {1}',
                        value=self.board.render())

        await self.lobby.invite.msg.clear_reactions()
        await self.lobby.invite.msg.edit(content=None, embed=embed)

        self.lobby.initialized = True

    async def on_end(self):
        pass

    async def on_input(self, data):
        if isinstance(data, discord.RawReactionActionEvent):
            channel = self.lobby.guild.bot.get_channel(data.channel_id)
            msg = await channel.fetch_message(data.message_id)
            await msg.remove_reaction(data.emoji, data.member)

            if data.user_id == self.turn:
                choice = Data.get().filler_emotes.index(data.emoji.name)
                for player in self.players:
                    if choice == player.color:
                        break
                else:
                    i = self.lobby.user_channels.index(channel)
                    self.board.do_move(choice, self.players[i])
                    embed_dict = self.players[i].embed_msg.embeds[0].to_dict()

                    o_player = 0
                    if i == 0:
                        o_player = 1

                    p1, p2 = self.board.get_scores(self.players[i], self.players[o_player])

                    for field in embed_dict['fields']:
                        if field['name'] == 'Board (your turn)':
                            field['name'] = 'Board (waiting on opponent)'
                            field['value'] = self.board.render()
                        elif field['name'] == 'Score':
                            field[
                                'value'] = f'{self.lobby.users[i].display_name}: {p1.score} - {self.lobby.users[o_player].display_name}: {p2.score}'

                    await self.players[i].embed_msg.edit(embed=discord.Embed.from_dict(embed_dict))

                    for field in embed_dict['fields']:
                        if field['name'] == 'Board (waiting on opponent)':
                            field['name'] = 'Board (your turn)'
                            field['value'] = self.board.render()
                        elif field['name'] == 'Score':
                            field[
                                'value'] = f'{self.lobby.users[i].display_name}: {p1.score} - {self.lobby.users[o_player].display_name}: {p2.score}'

                    await self.players[o_player].embed_msg.edit(embed=discord.Embed.from_dict(embed_dict))
                    self.turn = self.players[o_player].id

                    inv_dict = self.lobby.invite.msg.embeds[0].to_dict()
                    for field in inv_dict['fields']:
                        field[
                            'name'] = f'{self.lobby.users[0].display_name}: {self.players[0].score} - {self.lobby.users[1].display_name}: {self.players[1].score}'
                        field['value'] = self.board.render()
                        break
                    await self.lobby.invite.msg.edit(embed=discord.Embed.from_dict(inv_dict))
                    if self.board.game_over:
                        embed = discord.Embed(title='Filler', color=0x55ACEE)
                        if p1.score > p2.score:
                            # p1 wins
                            embed.add_field(
                                name=f'{self.lobby.users[i].display_name} has beaten' +
                                     f' {self.lobby.users[o_player].display_name}' +
                                     ' in a game of Filler!',
                                value=self.board.render()
                            )
                            embed.add_field(
                                name='Score',
                                value=f'{self.lobby.users[i].display_name}: {self.players[i].score} - ' +
                                      f'{self.lobby.users[o_player].display_name}: {self.players[o_player].score}',
                                inline=False
                            )
                            embed.set_thumbnail(url=self.lobby.users[i].avatar_url)
                        elif p2.score > p1.score:
                            # p2 wins
                            embed.add_field(
                                name=f'{self.lobby.users[o_player].display_name} has beaten' +
                                     f' {self.lobby.users[i].display_name}' +
                                     ' in a game of Filler!',
                                value=self.board.render()
                            )
                            embed.add_field(
                                name='Score',
                                value=f'{self.lobby.users[o_player].display_name}: {self.players[o_player].score} -' +
                                      f' {self.lobby.users[i].display_name}: {self.players[i].score}',
                                inline=False
                            )
                            embed.set_thumbnail(url=self.lobby.users[o_player].avatar_url)
                        else:
                            embed.add_field(
                                name=f'{self.lobby.users[0].display_name} and {self.lobby.users[1].display_name} ' +
                                     'have tied a game of Filler!',
                                value=self.board.render()
                            )
                            await self.lobby.end(
                                f'{self.lobby.users[0].display_name} and {self.lobby.users[1].display_name} ' +
                                'have tied the game!')

                        await self.lobby.invite.msg.edit(content=None, embed=embed)
                        await self.lobby.invite.msg.clear_reactions()
                        await self.lobby.end('special')

        elif isinstance(data, discord.Message):
            """
            activity
            application
            attachments
            author
            call
            channel
            channel_mentions
            clean_content
            content
            created_at
            edited_at
            embeds
            flags
            guild
            id
            jump_url
            mention_everyone
            mentions
            nonce
            pinned
            raw_channel_mentions
            raw_mentions
            raw_role_mentions
            reactions
            reference
            role_mentions
            stickers
            system_content
            tts
            type
            webhook_id
            """
            name = data.author.display_name
            content = data.clean_content
            await data.delete()
            for chat_msg in self.chat:
                await chat_msg.edit(content=(chat_msg.content + f'\n{name}: {content}'))


class Data:
    __instance = None

    @staticmethod
    def get():
        if Data.__instance is None:
            Data()
        return Data.__instance

    def __init__(self):
        if Data.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Data.__instance = self
        """
        roy g bip
        bgopry
        """
        self.filler_emotes = [
            u"\U0001F7E5",  # r
            u"\U0001F7E7",  # o
            u"\U0001F7E8",  # y
            u"\U0001F7E9",  # g
            u"\U0001F7E6",  # b
            u"\U0001F7EA"  # p
        ]
        self.circle_emotes = [
            u"\U0001F534",
            u"\U0001F7E0",
            u"\U0001F7E1",
            u"\U0001F7E2",
            u"\U0001F535",
            u"\U0001F7E3"
        ]
