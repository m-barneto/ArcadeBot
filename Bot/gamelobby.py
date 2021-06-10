import discord


class GameLobby:
    def __init__(self, invite, guild):
        # Since I have no clue how to do threadsafe stuff this is probably terrible practice
        # Set a variable to make sure the end command isn't called while this is still being setup
        self.initialized = False

        # TODO setup single player vs AI games where the joining_member is None
        # Store the invite members in our own users list
        self.users = [invite.main_member, invite.joining_member]
        # List used to store the game channels
        self.user_channels = []
        # Keep a reference to the Guild class
        self.guild = guild
        # Keep our own copy of the invite
        self.invite = invite
        # Set the game to None until setup method is called
        self.game = None

    async def setup(self):
        # Get the guild this gamelobby is in
        # This is different to self.guild as the Message.guild attribute returns the discord.Guild class object
        guild = self.invite.msg.guild
        # Allows to set a role other than admin that can view all game channels
        # admin_role = get(guild.roles, name="Staff")

        # Get the game class stored in the invite, for now this is always 'Filler'
        self.game = self.invite.game_type(self)

        # Channel creation permissions, basically creates a private channel with a single member allowed to view it
        overwrites = {
            # Default role can't view
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            # The bot CAN view
            guild.me: discord.PermissionOverwrite(read_messages=True)
            # admin_role: discord.PermissionOverwrite(read_messages=True),
        }

        # Create all the channels the gamemode requires, for filler it's 2
        for i in range(self.game.num_channels):
            # Sets the permission on a per user basis, players are given the read_messages=True overwrite
            overwrites[self.users[i]] = discord.PermissionOverwrite(read_messages=True)

            # Create the channel and keep a reference to it
            channel = await guild.create_text_channel(
                # Create the channel name based on what the gamemode wants it to be
                await self.game.get_channel_name(self.users[i]),
                # Use the overwrites to configure channel permissions
                overwrites=overwrites,
                # Place the new channel under the game-lobby channel category
                category=self.guild.bot.get_channel(self.guild.game_channel).category
            )
            # Append the new channel to the user_channels list
            self.user_channels.append(channel)
            # Pop the user specific permission in overwrites
            overwrites.pop(self.users[i])

        # Call game create method
        await self.game.on_create()

    async def end(self, msg='shutdown'):
        # When the game is over, how should the original invite message look

        # End the game first
        await self.game.on_end()

        # Delete the user channels
        for channel in self.user_channels:
            await channel.delete()

        # If the game end is from the !end command, just delete the original msg
        if msg == 'shutdown':
            await self.invite.msg.delete()
        # If it's a special case, assume the game.on_end() method will handle it
        elif msg == 'special':
            pass
        # Otherwise just put the end reason as the msg
        else:
            await self.update_msg(msg)
        # Remove the game from the guild.games dict
        self.guild.games.pop(self.invite.msg.id)

    async def input(self, data):
        # Pass game input to the game object, this can be different payloads such as Reaction and Message events
        await self.game.on_input(data)

    async def update_msg(self, content: str):
        # Helper method to update the content of the invite msg
        await self.invite.msg.edit(content=content)
