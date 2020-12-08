import discord
import json
import asyncio
from praw import Reddit
from discord.ext import commands
from data.utils.functions import read_file
from random import choice, random, randrange, randint


class FunCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.eight_ball_responses = read_file(
            "data/commands/8ball-responses.txt").split('\n')

        # Initialize subreddit
        reddit_creds = json.loads(read_file("reddit_creds.json"))
        self.reddit = Reddit(
            client_id=reddit_creds["client_id"],
            client_secret=reddit_creds["client_secret"],
            username=reddit_creds["username"],
            password=reddit_creds["password"],
            user_agent=reddit_creds["user_agent"]
        )
        self.meme_reddit = self.reddit.subreddit("memes")
        self.dank_meme_reddit = self.reddit.subreddit("dankmemes")
        del reddit_creds

    @commands.command(aliases=["8ball"])
    async def eight_ball(self, ctx, *, to_predict):
        await ctx.send(choice(self.eight_ball_responses))

    @eight_ball.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Atleast tell me what to predict")

    @commands.command(aliases=["flipcoin", "coinflip"])
    async def flip_coin(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Flipped a coin!",
            description=choice(["Got Tails!", "Got heads!"]),
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_author(
            name=f'{ctx.author}',
            icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
        ))

    @commands.command(aliases=["rolldice"])
    async def roll_dice(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Rolled a Dice!",
            description=f"The result was the number {randrange(0, 6)}",
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_author(
            name=f'{ctx.author}',
            icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
        ))

    @commands.command(aliases=['memes'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        hot_memes = list(self.meme_reddit.hot(limit=50))

        meme = hot_memes[randint(0, len(hot_memes) - 1)]
        while not meme.url.startswith("https://i"):
            meme = hot_memes[randint(0, len(hot_memes) - 1)]

        # setting embed
        img = str(meme.url)
        embed = discord.Embed(title=meme.title, url=img, color=discord.Colour.from_rgb(
            randint(0, 255), randint(0, 255), randint(0, 255)))
        embed.set_image(url=img)
        await ctx.send(embed=embed)

    @meme.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I am missing out on a permission, please enable the **\"send embeds\"** permission for me")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(title="You are on a cooldown!", description="You can only use this command once every **5 seconds**, *to get memes in bulk please use the **`z!sendMemes`** command!*", color=discord.Color.from_rgb(255, 0, 0)))

    @commands.command(aliases=["dank memes", 'dank-memes', 'dankmemes', 'dankmeme', 'dank-meme'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dank_meme(self, ctx):
        try:
            hot_memes = list(self.dank_meme_reddit.hot(limit=50))

            meme = hot_memes[randint(0, len(hot_memes) - 1)]
            while not meme.url.startswith("https://i"):
                meme = hot_memes[randint(0, len(hot_memes) - 1)]

            # setting embed
            img = str(meme.url)
            embed = discord.Embed(title=meme.title, url=img, color=discord.Colour.from_rgb(
                randint(0, 255), randint(0, 255), randint(0, 255)))
            embed.set_image(url=img)
            await ctx.send(embed=embed)
        except Exception as e:
            if str(e).endswith("Missing Permissions"):
                await ctx.send("I am missing out on a permission, please enable the **\"send embeds\"** permission for me")

    @dank_meme.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I am missing out on a permission, please enable the **\"send embeds\"** permission for me")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(title="You are on a cooldown!", description="You can only use this command once every **5 seconds**, *to get memes in bulk please use the **`-sendMemes`** command!*", color=discord.Color.from_rgb(255, 0, 0)))

    @commands.command(aliases=['sendmemes', 'send-memes', 'sendmeme', 'send-meme'], cooldown_after_parsing=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def send_memes(self, ctx, to_send: int, dank=None):
        if 0 < to_send <= 25:
            await ctx.send("Sending **"+str(to_send)+"** meme(s)")
            if dank != "dank":
                hot_memes = list(self.meme_reddit.hot(limit=100))
            else:
                hot_memes = list(self.dank_meme_reddit.hot(limit=100))

            for meme in hot_memes:
                if not meme.url.startswith("https://i"):
                    hot_memes.remove(meme)

            while len(hot_memes) > to_send:
                del hot_memes[randint(0, len(hot_memes) - 1)]

            # setting embed
            for meme in hot_memes:
                img = str(meme.url)
                embed = discord.Embed(title=meme.title, url=img, color=discord.Colour.from_rgb(
                    randint(0, 255), randint(0, 255), randint(0, 255)))
                embed.set_image(url=img)
                await ctx.author.send(embed=embed)
                await asyncio.sleep(10)
            await ctx.send("Sent "+ctx.author.mention+" **"+str(to_send)+"** meme(s), hopefully it worked")
        elif to_send == 0:
            await ctx.send("Ok sending no memes")
        else:
            await ctx.send(embed=discord.Embed(title="Amount Limit exceeded!", description="You can only get 25 memes **max**", color=discord.Color.from_rgb(255, 0, 0)))

    @send_memes.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Missing Arguments!", description="Please also tell me how many memes to send! additionally you can write \"dank\" after the amount to get the memes from dank subreddit\nFor e.g. `-sendMemes 10 dank`", color=0xff0000)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("I am missing out on a permission, please enable the **\"send embeds\"** permission for me")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(title="You are on a cooldown!", description="You can only use this command once every **30 seconds**", color=discord.Color.from_rgb(255, 0, 0)))


def setup(client):
    client.add_cog(FunCommands(client))
