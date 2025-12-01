
import asyncio
import discord # type: ignore
import os
import json
import secrets
import random as rnd
from datetime import datetime, timezone, timedelta
from discord.ext import commands # type: ignore
from dotenv import load_dotenv # type: ignore
from apikeys import *
from pathlib import Path



load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
rate_limit_bypass = 0

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

#####
RED = "\033[31m"
BLACK = "\033[90m"
WHITE = "\033[37m"
MAGENTA = "\033[38;5;199m"
MAGENTA_2 = "\033[38;5;206m"
MAGENTA_3 = "\033[38;5;213m"
MAGENTA_4 = "\033[38;5;219m"
YELLOW = "\033[33m"
RESET = "\033[0m"
GREEN = "\033[32m"
#-#-#
s = "System"
a = "Action"
r = "Error!"
# on ready
@bot.event
async def on_ready():
    status = discord.Status.dnd
    global start_count
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"| {bot.user} | Online <> Online <> Online Online <> Online <> Online <> Online Online <> Online <> Online |")
    print("-----------------------------------------------------------------------------------------------------------")
    await asyncio.sleep(0.5)
    print(" ")
    await asyncio.sleep(0.5)
    print(" ")
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{s}" + RED + "] " + MAGENTA + "Bot is " + RED +"ONLINE" + RESET)
    await asyncio.sleep(1)
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{s}" + RED + "] " + MAGENTA_2 + "Bot is " + MAGENTA +"Ready!" + RESET)

    # --- START: SUPPORT + DELETE ---
    channel_id = 1441909240959733770  # ID
    try:
        # channel true?:
        channel = bot.get_channel(channel_id)
        if channel is None:
            channel = await bot.fetch_channel(channel_id)
    except Exception as e:
        print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{r}" + RED + "] " + MAGENTA + f"Channel fetch error: {e}" + RESET)
        channel = None

    if channel is None:
        print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{r}" + RED + "] " + MAGENTA + "Channel not found, skipping cleanup." + RESET)
    else:
        # ellenőrizzük, hogy a botnak van-e jogosultsága törölni
        perms = channel.permissions_for(channel.guild.me) if getattr(channel, "guild", None) else None
        if not perms or not perms.manage_messages:
            print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{r}" + RED + "] " + MAGENTA + "Missing Manage Messages permission in the target channel. Skipping cleanup." + RESET)
        else:
            total_deleted1 = 0
            try:
                # először bulk purge 100-as chunkokban (ez gyors, de 14+ napos üzeneteket nem törli)
                while True:
                    deleted = await channel.purge(limit=100, bulk=True)
                    if not deleted:
                        break
                    total_deleted1 += len(deleted)
                    # ha kevesebb mint 100 jött, akkor valószínűleg vége
                    if len(deleted) < 100:
                        break
                    await asyncio.sleep(1)  # rövid pihi a rate-limitek miatt

                # bulk purge után lehetnek még régi (>14 nap) üzenetek — ezeket egyesével töröljük
                async for msg in channel.history(limit=None, oldest_first=True):
                    try:
                        # csak akkor töröljük, ha a msg még megvan (history adja vissza)
                        await msg.delete()
                        total_deleted1 += 1
                        await asyncio.sleep(0.5)  # lassabb, hogy ne ütközzünk rate-limitbe
                    except Exception:
                        # ha valami miatt nem megy (pl. permissions vagy rate limit), folytatjuk
                        pass
                
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{s}" + RED + "] " + MAGENTA_4 + f"Cleanup finished, total deleted:" + MAGENTA_2 + f"{total_deleted1}" + RESET)
            except Exception as e:
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{r}" + RED + "] " + MAGENTA_2 + f"Error during purge: {e}" + RESET)

            # --- küldjük be a help menüt ugyanabba a csatornába ---
            try:
                # help embed + view létrehozása (ugyanaz, mint a .help parancsban)
                view = MyView()
                embed = discord.Embed(
                    title="",
                    color=discord.Color.purple(),
                    description="""
**<:customemoji:1441548226762113175> ➥ ⫷Bot Commands⫸**
​​​‍‌​<:customemoji:1441548403342446662> Learn how the bot works!
-# In this category, you’ll find all commands that help you understand the bot’s functions, status, and basic usage.
Useful if you’re new to the server or want better control over the bot.

**<:customemoji:1441548226762113175> ➥ ⋖Economy Commands⋗**
<:customemoji:1441548403342446662> Build your wealth and progress!
-# Here you can find all economy-related functions: earning money, buying ranks, rewards, statistics, and everything related to the server’s economy system.
Perfect for those who enjoy collecting or competing.

**<:customemoji:1441548226762113175> ➥ ◃Admin Commands▹**
<:customemoji:1441548403342446662> Tools for staffs.
-# This section is for admins only. It contains commands to control the server, manage members, moderate the chat, or configure the bot’s features.
Helpful for every moderator and admin to ensure smooth operation.

**Developer Sends:** *( its only available if the bot is online until we dont finish )*
"""
                )
                # 'file' változó a te kódodban már fent definiálva van; ha nincs, kommenteld ki vagy add meg a helyes útvonalat
                try:
                    await channel.send(file=file, embed=embed, view=view)
                except Exception:
                    # ha a file küldése gondot okoz (pl. nincs fájl), küldjük csak az embedet
                    await channel.send(embed=embed, view=view)
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA + "Help menu " + MAGENTA_4 + "sent to the channel." + RESET)
            except Exception as e:
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{r}" + RED + "] " + MAGENTA + f"Failed" + MAGENTA_3 + "to send help menu: {e}" + RESET)
    # --- END: SUPPORT ---



@bot.command()
async def status(ctx):
    ctx_author_2 = ctx.author
    embed7 = discord.Embed(
        title="Status checking...",
        description="Once the **status check** is completed, we will send a **message**. The average waiting time is around **4–5 m**inutes.",
        color=discord.Color.orange()
    )
    embed7.set_footer(text=f"Requested by {ctx.author}")
    statuscheck = discord.Embed(
        title="Your check is **done**!",
        description="Status = ✅",
        color=discord.Color.green()
    )
    statuscheck.set_footer(text=f"Response time: `5 minute`.")
    await ctx.send(embed=embed7)
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_3 + f"{ctx.author} checking the bot! " + MAGENTA_4 + "With command: .status!")
    await asyncio.sleep(300)
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_3 + f"{ctx.author} checked the bot! " + MAGENTA_4 + "With command: .status!")
    await ctx.author.send(embed=statuscheck)




def is_drowys():
    def predicate(ctx):
        global MY_USER_ID
        return ctx.author.id == MY_USER_ID
    return commands.check(predicate)


@bot.command()
@is_drowys()
async def dm(ctx, member: discord.Member, *, message):
    """Küld privát üzenetet a megadott felhasználónak."""
    ctx_author_3me = member
    ctx_author_3m = message
    ctx_author_3 = ctx.author
    try:
        await member.send(message)
        embed6 = discord.Embed(
            title="**Sending dm...**",
            description=f"Sending dm to {member.mention} with message: `{message}`",
            color=discord.Color.orange()
        )
        embed6.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed6, delete_after=3)
        embed7 = discord.Embed(
            title="**Dm just sent!**",
            description=f"{ctx.author.mention} - > Dm just sent to {member.mention} with message: `{message}`",
            color=discord.Color.orange()
        )
        embed7.set_footer(text=f"Requested by {ctx.author}")
        await asyncio.sleep(3)
        print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA + f"{ctx.author} Sending a DM to " + MAGENTA_2 + f"{member.mention}" + MAGENTA + " with message: " + MAGENTA_2 + f"{ctx_author_3m}")
        await ctx.send(embed=embed7)
          
    except:
        await ctx.send(f"❌ Dm - > {member.mention}")


@bot.command()
@commands.is_owner()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed1 = discord.Embed(
        title="**Kick**",                        
        description=f"**{member.mention} got kicked out by {ctx.author.mention}.**",
        color=discord.Color.red()
    )
    embed1.add_field(
        name="**Reason**",
        value=reason or "No reason provided"
    )
    embed1.set_footer(text=f"Requested by {ctx.author}")
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_2 + f"{ctx.author} just kicked out " + MAGENTA_3 + f"{member}" + MAGENTA_4 + " with reason: " + MAGENTA + f"{reason}")
    await ctx.send(embed=embed1)

@bot.command()
@commands.is_owner()
async def ban(ctx, member: discord.Member, *, reason=None):
    global Ban_count
    await member.ban(reason=reason)
    embed1 = discord.Embed(
        title="**Ban**",                        
        description=f"**{member.mention} got banned out by {ctx.author.mention}.**",
        color=discord.Color.red()
    )
    embed1.add_field(
        name="**Reason**",
        value=reason or "No reason provided"
    )
    embed1.set_footer(text=f"Requested by {ctx.author}")
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_3 + f"{ctx.author} just banned out " + MAGENTA_4 + f"{member}" + MAGENTA + " with reason: " + MAGENTA_2 + f"{reason}")
    await ctx.send(embed=embed1)
    Ban_count += 1

@bot.command()
@commands.is_owner()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            global Ban_count
            await ctx.guild.unban(user)
            print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_3 + f"{ctx.author} just unbanned " + MAGENTA_4 + f"{member}")
            await ctx.send(f"{user.mention} Got unbanned.")
            Ban_count -= 1
            return
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_4 + f"{ctx.author} just tried to unbann " + MAGENTA_3 + f"{member}" + MAGENTA_4 + "but he wasnt on the banned list!")
    await ctx.send(f"{member} was not found in banned list.")

@bot.command()
async def help1(ctx):
    embed = discord.Embed(
        title="**Command Help | User commands**",
        description="Here's a list of all the available commands you can use:",
        color=discord.Color.gold()
    )

    # Több soros érték a Bot szekcióhoz
    embed.add_field(
        name="**🤖 Bot**",
        value="""
`.ping`
`.status`
`.---`
""",
        inline=False
    )

    embed.set_footer(text=f"Requested by {ctx.author.mention}")
    embed.set_image(url="https://i.postimg.cc/Lg5J0628/help-admin-Made-with-Clipchamp-(2).gif")
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA + f"{ctx.author} used .help ")
    await ctx.send(embed=embed)



@bot.command()
async def ping(ctx):
    await ctx.send("Pong")

@bot.command()
@is_drowys()
async def shutdown(ctx):
    embed1 = discord.Embed(
        title="Bot ShutDown",                        
        description="The bot is **shutting down.**",
        color=discord.Color.red()
    )
    embed1.set_footer(text=f"Requested by {ctx.author}")
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_2 + f"{ctx.author} just make the bot off! ")
    await ctx.send(embed=embed1)                    
    await bot.close()
    print("The Bot is Down")

@bot.command()
@commands.is_owner()
async def create_texts(ctx, text_channel_name: str, amount: int):
    """Létrehoz megadott számú szöveges csatornát a szerveren."""
    created_channels = []
    for i in range(1, amount + 1):
        channel_name = f"{text_channel_name}-{i}"
        channel = await ctx.guild.create_text_channel(channel_name)
        created_channels.append(channel.name)
    
    embed5 = discord.Embed(
        title="Creating text-channel**s**...",
        description=f"Created {amount} channels named {text_channel_name}!",
        color=discord.Color.orange()
    )
    embed5.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed5)
    print(f"| {bot.user} | Created {amount} channel successfully named {text_channel_name}! <> <> <> Requested {ctx.author}!")


@bot.command(name="create_text", aliases=["channel_text"])
@commands.is_owner()
async def create_text(ctx, text_channel_name: str):
    guild = ctx.guild

    await guild.create_text_channel(text_channel_name)
    embed2 = discord.Embed(
        title="Creating text-channel...",
        description=f"<> <> <> --- {text_channel_name} --- <> <> <>",
        color=discord.Color.orange()
    )
    embed2.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed2)
    print(f"| {bot.user} | Created a channel named {text_channel_name}! <> <> <> Requested {ctx.author}!")


@bot.command()
@commands.is_owner()
async def remove(ctx, *, channel_name):
    guild = ctx.guild
    channel = discord.utils.get(guild.channels, name=channel_name)

    if channel is None:
        embed3 = discord.Embed(
            title="Removing **channel**...",
            description=f"**Searching...**",
            color=discord.Color.orange()
        )
        embed3.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed3, delete_after=3)
        await asyncio.sleep(3)
        embed4 = discord.Embed(
            title="**Failed**.!.",
            description=f"There is no channel named `{channel_name}` **!**",
            color=discord.Color.red()
        )
        embed4.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed4)
    else:
        await channel.delete()
        await ctx.send("Removed ( beta answer )")

@bot.command()
@commands.is_owner()
async def clear(ctx, amount: str):
    global rate_limit_bypass
    rate_limit_bypass_counter = 20
    """
    .clear <szám>   -> törli az utolsó <szám> üzenetet
    .clear all      -> törli az összes üzenetet a csatornában (chunkokban)
    """
    try:
        await ctx.message.delete()
    except Exception:
        pass

    # Botnak legyen Manage Messages joga
    if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.send("❌ DEBUG | Error cp1 | **Tipp:** .error_cp1", delete_after=6)
        return

    # 'all' eset — chunkokban törlés (100-as darabok), majd régi üzenetek egyesével
    if isinstance(amount, str) and amount.lower() == "all":
        total_deleted = 0
        try:
            while True:
                deleted = await ctx.channel.purge(limit=100, bulk=True)
                if not deleted:
                    break
                total_deleted += len(deleted)
                if len(deleted) < 100:
                    break
                await asyncio.sleep(1)
            # régi üzenetek egyesével (14+ nap miatt)
            async for msg in ctx.channel.history(limit=None, oldest_first=True):
                try:
                    await msg.delete()
                    total_deleted += 1
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
        except Exception as e:
            await ctx.send(f"❌ Hiba törlés közben: {e}", delete_after=6)
            return

        await ctx.send(f"✅ Deleted total: {total_deleted} messages!", delete_after=6)
        return

    # rate limit bypass logika — egyszer, a szám szerinti törlés előtt
    if rate_limit_bypass == {rate_limit_bypass_counter}:
        print(
            RED + "[" + RESET + f"{bot.user}" + RED + "][" + RESET + f"{s}" + RED + "] "
            + MAGENTA_4 + f"Bypassing the rate-limit!" + MAGENTA + "|"
            + MAGENTA_4 + "Counter: " + MAGENTA_2 + f"{rate_limit_bypass}"
            + MAGENTA_4 + "New Counter flag on: " + MAGENTA_3 + f"{rate_limit_bypass_counter}"
        )
        rate_limit_bypass_counter += 20
        await asyncio.sleep(3.5)

    rate_limit_bypass += 1
    await asyncio.sleep(0.15)

    # szám eset
    try:
        n = int(amount)
        if n <= 0:
            await ctx.send("❌ You can add only **positive** numbers!", delete_after=5)
            return
        deleted = await ctx.channel.purge(limit=n, bulk=True)
        await ctx.send(f"✅ Deleted: {len(deleted)} Messages.", delete_after=5)
    except ValueError:
        await ctx.send("❌ Wrong usage! `.clear <number>` or `.clear all`.", delete_after=6)

@bot.command()
async def error_cp1(ctx):
    await ctx.send(f"**Wiki |** *cp1*: the bot do not have `Manage Messages` permission!")
    await ctx.send(f"Requested by {ctx.author.mention}!", delete_after=2)



@bot.command()
@commands.is_owner()
async def create_voices(ctx, text_channel_name: str, amount: int):
    """Létrehoz megadott számú szöveges csatornát a szerveren."""
    created_channels = []
    for i in range(1, amount + 1):
        channel_name = f"{text_channel_name}-{i}"
        channel = await ctx.guild.create_voice_channel(channel_name)
        created_channels.append(channel.name)
    
    embed5 = discord.Embed(
        title="Creating voice-channel**s**...",
        description=f"Created {amount} voices named {text_channel_name}!",
        color=discord.Color.orange()
    )
    embed5.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed5)
    print(f"| {bot.user} | Created {amount} voices successfully named {text_channel_name}! <> <> <> Requested {ctx.author}!")


@bot.command(name="create_voice", aliases=["channel_voice"])
@commands.is_owner()
async def create_voice(ctx, text_channel_name: str):
    guild = ctx.guild

    await guild.create_voice_channel(text_channel_name)
    embed2 = discord.Embed(
        title="Creating voice-channel...",
        description=f"<> <> <> --- {text_channel_name} --- <> <> <>",
        color=discord.Color.orange()
    )
    embed2.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed2)
    print(f"| {bot.user} | Created a channel named {text_channel_name}! <> <> <> Requested {ctx.author}!")











#
#
#
# Határ
#
#
# ---------------------- Updated Versions ---------------------- ---------------------- Updated Versions ---------------------- V1.1
balances_file = Path("balances.json")
balances_lock = asyncio.Lock()

roulette_wheel = {
    0: "green",
    1: "red", 2: "black", 3: "red", 4: "black", 5: "red", 6: "black",
    7: "red", 8: "black", 9: "red", 10: "black", 11: "black", 12: "red",
    13: "black", 14: "red", 15: "black", 16: "red", 17: "black", 18: "red",
    19: "red", 20: "black", 21: "red", 22: "black", 23: "red", 24: "black",
    25: "red", 26: "black", 27: "red", 28: "black", 29: "black", 30: "red",
    31: "black", 32: "red", 33: "black", 34: "red", 35: "black", 36: "red"
}

# class + def # ------------------------- START
# <.help support menu>
class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Support menu | 0-24",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="➥ ⫷Bot Commands⫸", description="Ez az első lehetőség", value="1"),
            discord.SelectOption(label="➥ ⋖Economy Commands⋗", description="Ez a második lehetőség", value="2"),
            discord.SelectOption(label="➥ ◃Admin Commands▹", description="Ez a harmadik lehetőség", value="3"),
            discord.SelectOption(label="➥     ◂ Roles ▸", description="Ez a harmadik lehetőség", value="4")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # now use the select.values
        value = select.values[0]
        try:
            if value == '4':
                embed = discord.Embed(
                    title="Level Roles & Perks <:frog:1441894115343335424>",
                    color=discord.Color.purple(),
                    description="""
You can level up by participating in our voice & chat channels. The more active you are, the higher level you get, the better perks you receive! You can check your own level with the /rank command.

**[<@&1441821871287959744>]**━━━<:bullet_point:1441853261857423360>━━**[<@&1441825818262245468>]**⠀➤ Access to [channelid]

**[<@&1441821979786350723>]**━━━<:bullet_point:1441853261857423360>━━**[<@&1441825818262245468>]**⠀➤ Access to [channelid]

**[<@&1441822238000287947>]**━━<:bullet_point:1441853261857423360>━━**[<@&1441825818262245468>]**⠀➤ Grants you the ability to add reactions  

**[<@&1441822471090081922>]**━━<:bullet_point:1441853261857423360>━━**[<@&1441825860851073285>]**⠀➤ Change your nickname

**[<@&1441822828625399859>]**━━<:bullet_point:1441853261857423360>━━**[<@&1441825860851073285>]**⠀➤ Grants you priority in voice channels

**[<@&1441823106602635284>]**━━<:bullet_point:1441853261857423360>━━**[<@&1441825860851073285>]**⠀➤ Grants you the ability to embed links

**[<@&1441823248382693406>]**━━<:bullet_point:1441853261857423360>━━**[<@&1441825917776429207>]**⠀➤ Unlock premium economy bot features

**[<@&1441823605330673764>]**━━<:bullet_point:1441853261857423360>━━**[<@&1441826019941159065>]**⠀➤ Custom status message powered by the bot

**[<@&1441823970730053632>]**━<:bullet_point:1441853261857423360>━━**[<@&1441826073489707038>]**⠀➤ Obtain a custom role
"""
                )
                # respond to the interaction (required)
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA + f"We got hit <> {value} ")
                file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png")
                await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

            elif value == '3':
                if not getattr(interaction.user, "guild_permissions", None) or not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("You need Administrator permission to view this menu.", ephemeral=True)
                    return
                embed = discord.Embed(
                    title="""
                    ▼——————————————▼
          Admin Commands <:verified:1441895122370429108>
▲——————————————▲                    """,
                    color=discord.Color.purple(),
                    description="""

<:se_one:1441853308263333888> `.kick {username} {reason}`
<:se_one:1441853308263333888> `.ban {username} {reason}`
<:se_one:1441853308263333888> `.unban {username}`
<:se_one:1441853308263333888> `.create_text {channelname}`
<:se_one:1441853308263333888> `.create_texts {channelname} {amount}`
<:se_one:1441853308263333888> `.create_voice {voicename}`
<:se_one:1441853308263333888> `.create_voices {voicename} {amount}`
<:se_one:1441853308263333888> `.remove {channelname}`
<:se_one:1441853308263333888> `.dm {username} {message}`
<:se_one:1441853308263333888> `.clear {number}` **or** `{all}`
<:se_one:1441853308263333888> `.status`
<:se_one:1441853308263333888> `.help_admin`
<:se_one:1441853308263333888> `.wiki`
<:banner:1441853285454577745> `.shutdown request` <- Warning .wiki_001 (not working rn)

"""
            )
                file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png")
                await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_2 + f"We got hit <> {value} ")
            elif value == '2':
                embed = discord.Embed(
                    title="⤴Economy commands⤵",
                    color=discord.Color.purple(),
                    description="""

# Coming soon! 2-5 day!

"""
                )
                file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png")
                await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_4 + f"We got hit <> {value} ")
            elif value == '1':
                embed = discord.Embed(
                    title="Bot commands",
                    color = discord.Color.purple(),
                    description="""


<:se_one:1441853308263333888> `.ping`
<:se_one:1441853308263333888> `.status`
<:se_one:1441853308263333888> `.randomjoke ( coming soon ) `
<:se_one:1441853308263333888> `.music {music} ( coming soon )`
<:banner:1441853285454577745> `.emojiplay ( coming soon )`
<:banner:1441853285454577745> `.wiki ( coming soon )`

"""
                )
                file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png")
                await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
                print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_3 + f"We got hit <> {value} ")
            else:
                # fallback — acknowledge to avoid "interaction failed"
                await interaction.response.send_message("Unknown option", ephemeral=True)

        except Exception as e:
            # If response was already sent earlier (rare), use followup
            try:
                await interaction.followup.send("An error occurred while processing the menu.", ephemeral=True)
            except:
                pass
            # Log to console for debugging
            print(f"Error in select_callback: {e}")
file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png") 

def generate_otp(length: int = 6) -> str:
    # secrets használata biztonságos véletlenhez
    alphabet = '0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


    # fallback: pytz ha telepítve van
    try:
        import pytz
        def get_budapest_now():
            return datetime.now(pytz.timezone("Europe/Budapest"))
    except Exception:
        # végső fallback (nem kezeli jól a DST-t, de legalább van valami)
        def get_budapest_now():
            return datetime.now(timezone(timedelta(hours=1)))


    # ha pytz sincs, már van egy fallback fent (UTC+1)
    if 'get_budapest_now' not in globals():
        def get_budapest_now():
            return datetime.now(timezone(timedelta(hours=1)))

class Wiki_bs(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Commands", style=discord.ButtonStyle.primary, custom_id="wiki_commands_btn")
    async def commands_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Successfully pressed Commands!", ephemeral=True)

    @discord.ui.button(label="Self Actions", style=discord.ButtonStyle.primary, custom_id="wiki_self_actions_btn")
    async def self_actions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Successfully pressed Self Actions!", ephemeral=True)

    @discord.ui.button(label="Report", style=discord.ButtonStyle.primary, custom_id="wiki_report_btn")
    async def report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Successfully pressed Report!", ephemeral=True)

    @discord.ui.button(label="Errors", style=discord.ButtonStyle.danger, custom_id="wiki_errors_btn")
    async def errors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Successfully pressed Errors!", ephemeral=True)
# class + def # ------------------------- END


# --------------------------------------- <.help>
@bot.command()
async def help(ctx):
    view = MyView()
    embed = discord.Embed(
        title="",
        color=discord.Color.purple(),
        description="""
        

**<:customemoji:1441548226762113175> ➥ ⫷Bot Commands⫸**
​​​‍‌​<:customemoji:1441548403342446662> Learn how the bot works!
-# In this category, you’ll find all commands that help you understand the bot’s functions, status, and basic usage.
Useful if you’re new to the server or want better control over the bot.

**<:customemoji:1441548226762113175> ➥ ⋖Economy Commands⋗**
<:customemoji:1441548403342446662> Build your wealth and progress!
-# Here you can find all economy-related functions: earning money, buying ranks, rewards, statistics, and everything related to the server’s economy system.
Perfect for those who enjoy collecting or competing.

**<:customemoji:1441548226762113175> ➥ ◃Admin Commands▹**
<:customemoji:1441548403342446662> Tools for staffs.
-# This section is for admins only. It contains commands to control the server, manage members, moderate the chat, or configure the bot’s features.
Helpful for every moderator and admin to ensure smooth operation.
"""
    )
    file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png")
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_3 + f"{ctx.author} just used .help! ")
    await ctx.send(file=file, embed=embed, view=view)
# --------------------------------------- <.help_admin>
@bot.command()
async def help_admin(ctx):
    # make sure this is used in a guild (not in DMs)
    if ctx.guild is None:
        await ctx.send("This command can only be used in a server.", delete_after=5)
        return

    # check the actual administrator permission
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need Administrator permission to view this menu.", delete_after=5)
        return

    embed = discord.Embed(
        title="▼——————————————▼\nAdmin Commands <:verified:1441895122370429108>\n▲——————————————▲",
        color=discord.Color.purple(),
        description="""
<:se_one:1441853308263333888> `.kick {username} {reason}`
<:se_one:1441853308263333888> `.ban {username} {reason}`
<:se_one:1441853308263333888> `.unban {username}`
<:se_one:1441853308263333888> `.create_text {channelname}`
<:se_one:1441853308263333888> `.create_texts {channelname} {amount}`
<:se_one:1441853308263333888> `.create_voice {voicename}`
<:se_one:1441853308263333888> `.create_voices {voicename} {amount}`
<:se_one:1441853308263333888> `.remove {channelname}`
<:se_one:1441853308263333888> `.dm {username} {message}`
<:se_one:1441853308263333888> `.clear {number}` **or** `{all}`
<:se_one:1441853308263333888> `.status`
<:se_one:1441853308263333888> `.help_admin`
<:se_one:1441853308263333888> `.wiki`
<:banner:1441853285454577745> `.shutdown request` <- Warning .wiki_001 (not working rn)
"""
    )
    # adjust the file path to be valid for your bot's environment
    file = discord.File("C:/Users/Btomi/Desktop/DC BOT/Support.png", filename="file.png")
    await ctx.send(embed=embed, file=file, delete_after=300)

    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{a}" + RED + "] " + MAGENTA_2 + f"Using: " + MAGENTA_3 + " .help_admin ")
# --------------------------------------- <.info>
@bot.command()
@is_drowys()
async def info(ctx):
    bot_name = value=bot.user.name
    bot_id = value=bot.user.id
    bot_latency = value=f"{round(bot.latency * 1000)} ms"
    OTP = generate_otp(6)
    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{s}" + RED + "] " + MAGENTA_2 + f"{ctx.author} Using .info! " + MAGENTA)
    print(RED + "                                            OTP: " + GREEN + f"{OTP}" + MAGENTA)
    embed = discord.Embed(
        title="[ Info ] [ Info ] [ Info ] [ Info ] [ Info ] [ Info ] [ Info ] [ Info ]",
        color=discord.Color.purple(),
        description=f"""
▼——————————————▼ ▼——————————————▼
<:se_one:1441853308263333888> **Bot name**: `{bot_name}`
<:se_one:1441853308263333888> **Bot ID**: `{bot_id}`
<:se_one:1441853308263333888> **Latency**: `{bot_latency}`
<:se_one:1441853308263333888> **Developer**: `Drowys`
<:se_one:1441853308263333888> **Token**: `off`
<:se_one:1441853308263333888> **— — — — — — — — — — — — — — — — — — — — — — —**
<:banner:1441853285454577745> **Message OTP**: `{OTP}` Requested by: `{ctx.author}`
▲——————————————▲ ▲——————————————▲
""")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    file = discord.File("C:/Users/Btomi/Desktop/DC BOT/images/Information.png", filename="file.png")
    await ctx.send(embed=embed, file=file, delete_after=300)
# --------------------------------------- <.wiki>
@bot.command()
async def wiki(ctx):
    embed = discord.Embed(
        title="--------------------Wikipedia-------------------",
        color=discord.Color.purple(),
        description="""
Welcome to the Wiki — a quick reference for this bot. 
Use the buttons below to browse Commands, Self
Actions, Report issues, or view Errors. If you need
help, contact a moderator or use the report button.
""")
    file = discord.File("C:/Users/Btomi/Desktop/DC BOT/images/Guidelines.png", filename="file.png")
    await ctx.send(embed=embed, view=Wiki_bs(), file=file)
# --------------------------------------- <.random>             TESTER
@bot.command()
async def random(ctx):
    rannum = rnd.randint(1, 100)

    print(RED + "["+ RESET + f"{bot.user}" + RED + "][" + RESET + f"{s}" + RED + "] " + MAGENTA_2 + f"{rannum} Just generated by {ctx.author}" + MAGENTA)

    await ctx.send(f"Your number is: " f"{rannum}")

    # Írás stringként
    with open("rannum.txt", "a", encoding="utf-8") as file:
        file.write(str(rannum) + "\n")
# --------------------------------------- <.read>               TESTER
@bot.command()
@is_drowys()
async def read(ctx):
    with open("rannum.txt", "r", encoding="utf-8") as file:
        content = file.read()

    await ctx.send("Rannum.txt = " + content)
# --------------------------------------- <.ranclear>           TESTER
@bot.command()
@is_drowys()
async def ranclear(ctx):
    with open("rannum.txt", "w", encoding="utf-8") as file:
        file.write("")
# --------------------------------------- <.work>
@bot.command()
async def work(ctx):
    earned = rnd.randint(1000, 6000)
    user_id = str(ctx.author.id)
    balances = {}

    # Ha a fájl létezik és nem üres
    if os.path.exists("balances.json") and os.path.getsize("balances.json") > 0:
        with open("balances.json", "r", encoding="utf-8") as f:
            balances = json.load(f)

    # Hozzáadás
    balances[user_id] = balances.get(user_id, 0) + earned

    # Mentés
    with open("balances.json", "w", encoding="utf-8") as f:
        json.dump(balances, f, indent=4)

    await ctx.send(f"{ctx.author.mention}, you earned `{earned}` coins!")
# --------------------------------------- <.bal>
@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    balances = {}
    with open("balances.json", "r", encoding="utf-8") as f:
        balances = json.load(f)

    balances[user_id] = balances.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention} You have {balances[user_id]}")

#############
bot.run(TOKEN) # <--- START
#############