class Player:
    def __init__(self, user_id, embed_msg, color, team):
        self.id = user_id
        self.embed_msg = embed_msg
        self.score = 1
        self.color = color
        self.team = team
