import json
import discord
import go
import re

from discord.ext import commands

gogames = {}


def isowner(ctx):
    return ctx.author.id in ctx.bot.config['owners']
    #return ctx.author.id in (212350439532789760, 136611352692129792)

class Go:
    def __init__(self, bot):
        #give cog a pointer to bot in case we need it
        self.bot = bot
    
    @commands.command(aliases=['u'])
    @commands.check(isowner)
    async def update(self, ctx):
        """Update the bot"""
        #Unload this extension then reload it
        self.bot.unload_extension(__name__)
        self.bot.load_extension(__name__)

        await ctx.send("Updated")

    @commands.command()
    async def source(self, ctx):
        """Get my source code"""
        await ctx.send("https://github.com/Imagine4/FourBot/")

    @commands.command()
    @commands.check(isowner)
    async def listgames(self, ctx):
        """List all games of go"""
        message = "Go Games:\n"
        for game in gogames.keys():
            theboard = gogames[game].board
            message += f"{game} - {theboard}\n"
        await ctx.send(message)

    @commands.group(invoke_without_command=True)
    async def go(self, ctx, game_name, position): 
        """Make a move"""
        try:
            game = gogames[game_name]
        except KeyError:
            return await ctx.send("There's no Go command or game named that.")
        
        if ctx.author.id not in (game.p1, game.p2):
            return await ctx.send("You're not in a game!")
            
        if game.gamenotfinished:

            if not ((game.p1 == ctx.author.id and game.turn == go.black) or
                    (game.p2 == ctx.author.id and game.turn == go.white)):
                return await ctx.send("It's not your turn!")    

            valility = game.nextmove(game.turn, position)

            if not game.gamenotfinished:
                await ctx.send(
                    "You can remove dead stones if both players move on the same location of the stone. \n"
                    f"If you don't know what that is, or you're done, say `4.go end {game_name}`."
                )

            if valility == "ko":
                await ctx.send("Ko rule prevents that, try again.")
            elif valility == "suicide":
                await ctx.send("Sucide rule prevents that, try again.")
            elif valility == "occupied":
                await ctx.send("That spot is occupied, try again.")
            elif valility == "ok":
                await ctx.send(f"```{game.printboard(game.board)}```")
                if game.gamenotfinished:
                    if game.turn == go.black:
                        await ctx.send("Black's turn")
                    else:
                        await ctx.send("White's turn")
                    return
            else:
                await ctx.send("Something's gone horribly wrong")
        
        else:
            try:
                if position in game.potentialremoves:
                    game.remstones(game.processcoords(position))
                    await ctx.send(f"```{game.printboard(game.board)}``` \n Removed {position}")
                else:
                    game.potentialremoves.append(position)
                    await ctx.send("Remove {position}?")

            except IndexError or ValueError:
                return await ctx.send("Um... you didn't enter a valid move...")
                
    @go.command(name="create")
    async def go_create(self, ctx, player2: discord.Member, size: int=19, name=None):
        """Create a game"""
        p2 = player2
        p1 = ctx.author
        if not name:
            name = ctx.author.name.split(" ")[0]

        if name in gogames:
            return await ctx.send(f"A game already exists under `{gamenameinput}`, pick a new one.")

        if name in ("create", "delete", "end", "board"):
            return await ctx.send("That name is reserved for commands.")

        if not ctx.message.mentions: await ctx.send("You may want to ping player 2.")

        gogames[name] = go.GoGame(size, p1.id, p2.id)

        await ctx.send(f"Game created under the name {name}")
        await ctx.send(f"```{gogames[name].printboard(gogames[name].board)}```")
        await ctx.send(f"{p1.mention} is black. {p2.mention} is white.\nBlack's turn")


    @go.command(name="delete")
    async def go_delete(self, ctx, name): 
        try:
            game = gogames[name]
        except KeyError:
            return await ctx.send("I can't find the game you mentioned.")

        if ctx.author.id in (game.p1, game.p2):
            gogames.pop(name)
            await ctx.send(f"The game {name} no longer exists :thumbsup:")
        else:
            await ctx.send("Hey, that's not your game!")

    @go.command(name="end")
    async def go_end(self, ctx, game):
        """End a game"""
        try:
            game = gogames[game]
        except KeyError:
            return await ctx.send("I can't find the game you mentioned.")

        if game.gamenotfinished:
            return await ctx.send("You game isn't done!")
            return
        else:
            await ctx.send(
                f"Black's captures: {game.blackcaptures}\n"
                f"Black's territory: {game.whiteterritory}\n"
                f"White's captures: {game.whitecaptures}\n"
                f"White's territory: {game.whiteterritory}"
            )

            blackscores = game.blackcaptures + game.blackterritory
            whitescores = game.whitecaptures + game.whiteterritory + 6.5

            if blackscores > whitescores:
                await ctx.send("Winner: Black by {blackscores - whitescores} points")
            else:
                await ctx.send("Winner: White by {whitescores - blackscores} points")

            gogames.pop(game)
            return

    @go.command(name="board")
    async def go_board(self, ctx, game):
        """Get a board"""    
        try:
            game = gogames[arr[2]]
        except KeyError:
            await ctx.send("I can't find the game you mentioned.")
            return

            await ctx.send(f"```{game.printboard(game.board)}```")

            if game.gamenotfinished:
                if game.turn == go.black:
                    await ctx.send("Black's turn")
                else:
                    await ctx.send("White's turn")
                return


def setup(bot):
    bot.add_cog(Go(bot))
