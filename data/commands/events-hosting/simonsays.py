import discord
from discord.ext import commands
from data.custom.functions import get_role_from_msg, prettify_string
from asyncio import TimeoutError

class SimonSays(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(aliases=['SimonSaysSetup', 'simon-says-setup'])
    @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
    async def simon_says_setup(self, ctx):
        id_list_to_save = {
            'roles' : {},
            'channels' : {}
        }
        
        def wait_for_reply_check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        
        for role_to_set_for in ('simon_says_participant', 'simon_says_controller', 'simon_says_disqualified'):
            while True:
                await ctx.send("Please tell me which role in this Server will belong to {}(s), Either mention it, or just Tell me the name of the role".format(prettify_string(role_to_set_for)))
                message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=60)
                
                if message.content.startswith("<@&"):
                    role_id = int(message.content[3:-1])
                    role = message.guild.get_role(role_id)
                else:
                    for role in message.guild.roles:
                        if role.name == message.content:
                            break
    
                if role == None:
                    await ctx.send('Failed to recognise role (perhaps it doesn\'t exist?), please **only** tell me the role you would like to use (name should be case-sensitive)')
                    continue
            
                if ctx.message.author.roles[-1].position <= role.position:
                    await ctx.send("<a:crossGif:760758713777913876> That role is higher than your highest role!")
                elif ctx.guild.get_member(self.client.user.id).roles[-1].position <= role.position:
                    await ctx.send("<a:crossGif:760758713777913876> My highest role is lower then that role!")
                else:
                    id_list_to_save['roles'][role_to_set_for] = role.id
                    try:
                        await ctx.send(embed=discord.Embed(
                            title="<a:checkGif:760758712876400680> Success", 
                            description=f"<@&{role.id}> is now set as the role for {prettify_string(role_to_set_for)}(s) <a:checkGif:760758712876400680> ",
                            color=discord.Color.green()
                        ))
                    except:
                        await ctx.send(f"<a:checkGif:760758712876400680> {role.name} is now set as the role for {prettify_string(role_to_set_for)}(s).")
                    break
        try:
            self.client.id_list['guild_setup_id_saves'][ctx.guild.id].update(id_list_to_save)
        except KeyError:
            self.client.id_list['guild_setup_id_saves'][ctx.guild.id] = id_list_to_save
        
    @simon_says_setup.error 
    async def clear_error(self, ctx, error):
        if isinstance(error, TimeoutError):
            await ctx.send("You spent too long to reply, please try again")
        else:
            raise error

def setup(client):
    client.add_cog(SimonSays(client))
