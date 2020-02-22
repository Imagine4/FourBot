import discord
from utils import go, conversions, quadratic
import yaml
import secret
import importlib
import io
from datetime import datetime
from discord.ext import commands


def isowner(ctx):
    return ctx.author.id in ctx.bot.config['owners']
    # return ctx.author.id in (212350439532789760, 136611352692129792)


class Game(commands.Converter):
    @staticmethod
    async def convert(ctx, arg):
        return arg, ctx.bot.gogames[arg]


class Commands(commands.Cog):
    def __init__(self, bot):
        # give cog a pointer to bot in case we need it
        self.bot = bot

    @commands.command(aliases=['u'], hidden=True)
    @commands.check(isowner)
    async def update(self, ctx, extension=__name__):
        """Updates the code to implement recent changes."""
        print(extension)
        if extension == "config":
            with open('config.yml', 'r') as config_file:
                ctx.bot.config = yaml.load(config_file)
        elif extension == __name__:
            self.bot.unload_extension(__name__)
            self.bot.load_extension(__name__)
        else:
            importlib.reload(extension)

        await ctx.send("Updated " + extension)

    @commands.command()
    async def source(self, ctx):
        """Posts my GitHub link."""
        await ctx.send("https://github.com/Imagine4/FourBot/")

    @commands.command(hidden=True)
    async def playback(self, ctx, start, end):
        """Plays back chat messages from a starting message ID to an ending message ID."""
        stime = datetime.utcfromtimestamp(conversions.gettime(start)/1000 - 1)
        etime = datetime.utcfromtimestamp(conversions.gettime(end)/1000 + 1)
        msgs = ctx.channel.history(after=stime, before=etime)
        async for msg in msgs:
            await ctx.send(msg.content)

    @commands.command(hidden=True)
    async def solve(self, ctx, a, b, c):
        try:
            answer = quadratic.solve(int(a), int(b), int(c))
        except ValueError:
            await ctx.send("You didn't provide 3 valid numbers.")
        output = f'```{answer[0]}```\n```{answer[1]}```'
        await ctx.send(output)

    @commands.command(name=secret.letter, hidden=True)
    async def secret_command(self, ctx, thing=None, stuff=None):
        if ctx.guild is None:
            message = secret.bleh(thing, stuff)
            if message:
                await ctx.send(message)

    @commands.group(invoke_without_command=True)
    async def go(self, ctx, game: Game, position): 
        """Go, the board game!
        To make a move, use `4.go <game> <position>`. When typing the position, letter goes first, then number.
        Go rules: <https://en.wikipedia.org/wiki/Go_(game)#Rules>"""
        name, game = game
        if ctx.author.id not in (game.p1, game.p2):
            return await ctx.send("You're not in that game!")
            
        if game.gamenotfinished:
            if not ((game.p1 == ctx.author.id and game.turn == go.black) or
                    (game.p2 == ctx.author.id and game.turn == go.white)):
                return await ctx.send("It's not your turn!")    
            try:
                valility = game.nextmove(position)
            except ValueError:
                return await ctx.send(f'"{position}" isn\'t a valid move.')

            if not game.gamenotfinished:
                await ctx.send(
                    "You can remove dead stones if both players move on the same location of the stone. \n"
                    f"If you don't know what that is, or you're done, both players say `4.go {name} end`."
                )

            if valility == "ko":
                await ctx.send("Ko rule prevents that, try again.")
            elif valility == "suicide":
                await ctx.send("Sucide rule prevents that, try again.")
            elif valility == "occupied":
                await ctx.send("That spot is occupied, try again.")
            elif valility == "outofrange":
                await ctx.send("That's outside the board!")
            elif valility == "ok":
                await ctx.send(file=discord.File(game.printboard(), filename=game.encodeboard() + ".png"))
                if game.gamenotfinished:
                    if game.turn == go.black:
                        await ctx.send("Black's turn")
                    else:
                        await ctx.send("White's turn")
                    return
            else:
                await ctx.send("Something's gone horribly wrong...")
        
        else:
            print(game.potentialremoves)
            try:
                try:
                    if position != "end":
                        move = game.processcoords(position)
                except IndexError or ValueError:
                    return await ctx.send("You didn't enter a valid position.")

                if (game.p1 if (ctx.author.id != game.p1) else game.p2) == game.potentialremoves[position]:
                    if position == "end":
                        game.calculateterritory()
                        await ctx.send(
                            f"Black's captures: {game.blackcaptures}\n"
                            f"Black's territory: {game.blackterritory}\n"
                            f"White's captures: {game.whitecaptures}\n"
                            f"White's territory: {game.whiteterritory}\n"
                            f"Komi: 6.5 for white"
                        )

                        blackscores = game.blackcaptures + game.blackterritory
                        whitescores = game.whitecaptures + game.whiteterritory + 6.5

                        if blackscores > whitescores:
                            await ctx.send(f"Winner: Black by {blackscores - whitescores} points")
                        else:
                            await ctx.send(f"Winner: White by {whitescores - blackscores} points")

                        self.bot.gogames.pop(name)
                        return

                    else:
                        game.remstones(move)
                        await ctx.send(content=f"Removed stone at {position}",
                                       file=discord.File(game.printboard(), filename=game.encodeboard() + ".png"))

            except KeyError:
                if position == "end":
                    await ctx.send("End game?")
                else:
                    move = game.processcoords(position)
                    if game.getcolor(move, game.board) is not go.blank:
                        await ctx.send(f"Remove stone at {position}?")
                    else:
                        return await ctx.send("You didn't select a stone.")

                game.potentialremoves[position] = ctx.author.id

                
    @go.command(name="create")
    async def go_create(self, ctx, player2: discord.Member, size: int=19, name=None):
        """Creates a new game of Go."""
        p2 = player2
        p1 = ctx.author
        if size >= 26: return await ctx.channel.send("Why would you ever use a board that big?")
        if not name:
            name = ctx.author.name.split(" ")[0]

        if name in self.bot.gogames:
            return await ctx.send(f"A game already exists named `{name}`, pick a new name.")

        if name in ctx.command.parent.all_commands:
            return await ctx.send("That name is reserved for commands.")

        #if not ctx.message.mentions: await ctx.send("Player 2 needs to be pinged.")

        self.bot.gogames[name] = go.GoGame(size, p1.id, p2.id)

        await ctx.send(f"Game created under the name {name}")
        await ctx.send(file=discord.File(self.bot.gogames[name].printboard(), filename=self.bot.gogames[name].encodeboard() + ".png"))
        await ctx.send(f"{p1.mention} is black. {p2.mention} is white.\nBlack's turn")
    
    @go.command(name="import")
    async def go_import(self, ctx, player2: discord.Member, string, name=None):
        """Allows you to import a game."""
        p1 = ctx.author
        p2 = player2
        if not name: name = ctx.author.name.split(" ")[0]
        if name in self.bot.gogames:
            return await ctx.send(f"A game already exists under `{name}`, pick a new one.")
        
        if name in ctx.command.parent.all_commands:
            return await ctx.send("That name is reserved for commands.")

        if not ctx.message.mentions: await ctx.send("Player 2 needs to be pinged.")
        ctx.bot.gogames[name] = game = go.GoGame(19, p1.id, p2.id)
        try:
            gameinfo = conversions.decodeboard(string)
        except IndexError:
            return await ctx.send("You need enter an encoded board.")
        except Exception:
            return await ctx.send(f"Invalid board. You can use `{ctx.prefix}.go encode` or a board's filename.")
 
        game.importgame(*gameinfo)
        await ctx.send(f'Game imported under the name {name}')
        await ctx.send(file=discord.File(game.printboard(), filename=game.encodeboard() + ".png"))
        await ctx.send(f"Turn: {game.turn}, Captures: {go.black} {game.whitecaptures} {go.white} {game.blackcaptures}")
    
    @go.command(name="encode")
    async def go_encode(self, ctx, game: Game):

        game = game[1]
        try:
            encoding = game.encodeboard()
            await ctx.send(encoding)
        except IndexError:
            await ctx.send("You didn't specify a game.")
        except KeyError:
            await ctx.send("That game doesn't exist.")

    @go.command(name="delete")
    async def go_delete(self, ctx, game: Game):
        """Deletes a Go game you're in."""
        name, game = game
        if ctx.author.id in (game.p1, game.p2):
            self.bot.gogames.pop(name)
            await ctx.send(f"The game {name} no longer exists :thumbsup:")
        else:
            await ctx.send("Hey, that's not your game!")

    @go.command(name="board")
    async def go_board(self, ctx, game: Game):
        """Prints the board, captures, and turn from the given game."""
        game = game[1]
        await ctx.send(file=discord.File(game.printboard(), filename=game.encodeboard() + ".png"))

        if game.gamenotfinished:
            return await ctx.send(f"Turn: {game.turn}, Captures: {go.black} {game.whitecaptures} {go.white} {game.blackcaptures}")
        else:
            return await ctx.send(f"Captures: {go.black} {game.whitecaptures} {go.white} {game.blackcaptures}")

    @go.command()
    @commands.check(isowner)
    async def listgames(self, ctx):
        """List all games of go. Owner only."""
        message = "Go Games:\n"
        for name, game in self.bot.gogames.items():
            message += (name + " - " + str(game.p1) + ", " + str(game.p2) + ", " + game.turn + "\r\n"
                        + str(game.movehistory) + "\r\n"
                        + conversions.encodeboard(game.board, game.turn, game.blackcaptures,
                                                  game.whitecaptures)
                        + "\r\n\r\n")
        #    message += f"{name} - {game.board}\n"
        if len(message) > 2000:
            f = io.StringIO(message)
            await ctx.send(file=discord.File(f, filename="listgames.txt")); f.close()
        else:
            await ctx.send(message)

    @go.after_invoke
    @go_create.after_invoke
    @go_delete.after_invoke
    @go_import.after_invoke
    async def save(self, ctx):
        print("<< saved games >>")
        ctx.bot.save_games()


def setup(bot):
    bot.add_cog(Commands(bot))
