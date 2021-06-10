import discord


class Filler_Invite:
    def __init__(self, game_type, size, whitelist, msg: discord.Message, member: discord.Member):
        self.game_type = game_type
        self.size = size
        self.whitelist = whitelist
        self.msg = msg
        self.main_member = member
        self.joining_member = None
