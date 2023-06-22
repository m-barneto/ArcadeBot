# ArcadeBot
Discord bot for server-contained pvp arcade games

A player can initialize a game against a specific player in the server or leave it open so the first person to accept the challenge gets to play.

Once the game is started a separate chat channel is created that contains the interactable game board as well as a synced messages log so that players can message eachother without exiting the channel.

The original invite message in the lobby chat channel will be turned into a live board showing each player's score and updating as they play.

The game is controlled using reactions under the interactable game board, players will select the color they would like to change into and absorb nearby tiles.

Once the game is complete (All tiles absorbed), the separate chat channels will be removed and the original invite message will show the player's scores and who won the game, along with a board showing the end state of the game.

![example](https://github.com/m-barneto/ArcadeBot/assets/4347791/a5444023-a582-4192-8cf0-7e837c17f81d)
