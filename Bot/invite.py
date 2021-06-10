import discord


class Invite:
    def __init__(self, game_type, args, msg: discord.Message, member: discord.Member):
        self.game_type = game_type
        self.args = args
        self.msg = msg
        self.whitelist = None
        self.main_member = member
        self.joining_member = None
