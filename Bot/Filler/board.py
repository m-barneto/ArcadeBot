import random

from Bot.Filler.tile import Tile


class Board:
    def __init__(self, size, data):
        self.data = data
        self.size = size
        self.game_over = False

        self.board = []
        for y in range(size):
            self.board += [[0] * size]
            for x in range(size):
                self.board[y][x] = Tile(self.rand_color(), -1)
        self.board[0][0].team = 0
        self.board[size - 1][size - 1].team = 1
        self.fair_board()

    def get_scores(self, player1, player2):
        player1.score = 0
        player2.score = 0
        val = True
        for y in self.board:
            for tile in y:
                if tile.team == -1:
                    val = False
                elif tile.team == player1.team:
                    player1.score += 1
                elif tile.team == player2.team:
                    player2.score += 1
        self.game_over = val
        return player1, player2

    def get_rand_except(self, ex):
        valid = list(set(self.data.filler_emotes).difference(ex))
        return self.data.filler_emotes.index(valid[random.randint(0, len(valid) - 1)])

    def rand_color(self):
        return random.randint(0, len(self.data.filler_emotes) - 1)

    def fair_board(self):
        # Make sure the player starting pieces arent the same color
        while self.board[0][0].color == self.board[self.size - 1][self.size - 1].color:
            self.board[0][0].color = self.rand_color()

        # Make sure surrounding tiles aren't the same color as player 1's starting piece
        while self.board[0][0].color == self.board[0][1].color:
            self.board[0][1].color = self.rand_color()
        while self.board[0][0].color == self.board[1][0].color:
            self.board[1][0].color = self.rand_color()
        # Make sure the surrounding tiles around player 1 aren't the same color as each other
        while self.board[0][1].color == self.board[1][0].color:
            self.board[0][1].color = self.rand_color()

        # Make sure surrounding tiles aren't the same color as player 2's starting piece
        while self.board[self.size - 1][self.size - 1].color == self.board[self.size - 1][self.size - 2].color:
            self.board[self.size - 1][self.size - 2].color = self.rand_color()
        while self.board[self.size - 1][self.size - 1].color == self.board[self.size - 2][self.size - 1].color:
            self.board[self.size - 2][self.size - 1].color = self.rand_color()
        # Make sure the surrounding tiles around player 2 aren't the same color as each other
        while self.board[self.size - 1][self.size - 2].color == self.board[self.size - 2][self.size - 1].color:
            self.board[self.size - 1][self.size - 2].color = self.rand_color()

        for y in range(self.size):
            for x in range(self.size):
                # region poop
                if y == 0 and x == 0:
                    continue
                if y == 1 and x == 0:
                    continue
                if y == 0 and x == 1:
                    continue
                if y == self.size - 1 and x == self.size - 1:
                    continue
                if y == self.size - 2 and x == self.size - 1:
                    continue
                if y == self.size - 1 and x == self.size - 2:
                    continue
                # endregion
                neighbors = [
                    self.get_adj(x, y, 0, 1),
                    self.get_adj(x, y, 0, -1),
                    self.get_adj(x, y, 1, 0),
                    self.get_adj(x, y, -1, 0)
                ]
                ex = []
                for n in neighbors:
                    if n:
                        ex.append(self.data.filler_emotes[self.board[n[1]][n[0]].color])
                self.board[y][x].color = self.get_rand_except(ex)

    def get_player_colors(self, num_players):
        if num_players == 2:
            return [self.board[0][0].color, self.board[self.size - 1][self.size - 1].color]
        elif num_players == 4:
            return [self.board[0][0].color, self.board[self.size - 1][self.size - 1].color,
                    self.board[0][self.size - 1].color, self.board[self.size - 1][0].color]

    def get_adj(self, x, y, ox, oy):
        if x + ox > self.size - 1 or x + ox < 0 or y + oy > self.size - 1 or y + oy < 0:
            return None
        return x + ox, y + oy

    def get_neighbors(self, x, y, tiles, to_add, player):
        neighbors = [
            self.get_adj(x, y, 0, 1),
            self.get_adj(x, y, 0, -1),
            self.get_adj(x, y, 1, 0),
            self.get_adj(x, y, -1, 0)
        ]

        for n in neighbors:
            if n:
                if self.board[n[1]][n[0]].team == player.team:
                    self.board[n[1]][n[0]].color = player.color
                if self.board[n[1]][n[0]].color != player.color:
                    continue
                if n not in tiles:
                    to_add[n] = False
        tiles[(x, y)] = True

    def get_connected(self, x, y, player):
        #         x  y   checked
        tiles = {(x, y): False}
        while False in tiles.values():
            to_add = {}
            for tile in tiles:
                if not tiles[tile]:
                    self.get_neighbors(tile[0], tile[1], tiles, to_add, player)
            tiles.update(to_add)
        return tiles

    def do_move(self, choice, player):
        player.color = choice
        connected = {}
        if player.team == 0:
            self.board[0][0].color = choice
            connected = self.get_connected(0, 0, player)
        elif player.team == 1:
            self.board[self.size - 1][self.size - 1].color = choice
            connected = self.get_connected(self.size - 1, self.size - 1, player)

        for tile in connected:
            if self.board[tile[1]][tile[0]].team == player.team:
                self.board[tile[1]][tile[0]].color = player.color
            if self.board[tile[1]][tile[0]].color == player.color:
                self.board[tile[1]][tile[0]].team = player.team

    def render(self):
        render = ''
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x].team == -1:
                    render += self.data.filler_emotes[self.board[y][x].color]
                else:
                    render += self.data.circle_emotes[self.board[y][x].color]
            render += '\n'
        return render
