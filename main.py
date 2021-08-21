import discord
import re
from datetime import datetime as dt, date, time, timedelta
from zoneinfo import ZoneInfo
from discord.ext import commands
from aioconsole import aexec
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ.get("KEY")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='m!', owner_id=346555330358149120, intents=intents)

time_command = re.compile(r"!!(.+?)!!")

# def time_to_datetime(hours, minutes):
#     today = date.today()
#     time_offset = time(hours, minutes)
#     formatted_time = dt.combine(today, time, tzinfo=ZoneInfo("Europe/London"))

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message: discord.Message):  
    if message.author.bot:
        return

    if message.content.startswith("m! "):
        message.content = "m!" + message.content[3:]

    if message.content.startswith('m!hello') or "<@837276921913147442>" in message.content or "<@!837276921913147442>" in message.content:
        await message.channel.send('Hello!')
        return

    if matches := time_command.findall(message.content):
        new_message = message.content
        timezone = ZoneInfo("Europe/London")
        now = dt.now(timezone)
        for match in matches:
            if groups := re.findall(r"^(\d\d?):(\d\d)$!", match):
                hours, minutes = groups[0]
                datetime = dt.combine(now.date(), time(int(hours), int(minutes)), tzinfo=timezone)
                new_message = new_message.replace("!!" + match + "!!", f"<t:{int(datetime.timestamp())}:t>", 1)

            if groups := re.findall(r"^(\d\d?):(\d\d) ?(am|pm)$", match):
                hours, minutes, a_pm = groups[0]
                offset = timedelta(hours=0) if a_pm == "am" else timedelta(hours=12)
                datetime = dt.combine(now.date(), time(int(hours), int(minutes)), tzinfo=timezone) + offset
                new_message = new_message.replace("!!" + match + "!!", f"<t:{int(datetime.timestamp())}:t>", 1)

            if groups := re.findall(r"^(\d\d?) ?(am|pm)$", match):
                hours, a_pm = groups[0]
                offset = timedelta(hours=0) if a_pm == "am" else timedelta(hours=12)
                datetime = dt.combine(now.date(), time(int(hours), 0), tzinfo=timezone) + offset
                new_message = new_message.replace("!!" + match + "!!", f"<t:{int(datetime.timestamp())}:t>", 1)
        await message.channel.send(new_message)
    
    await bot.process_commands(message)
    

def is_thread():
    def predicate(ctx: commands.Context):
        return isinstance(ctx.channel, discord.Thread)
    return commands.check(predicate)

@bot.command()
@commands.is_owner()
@is_thread()
async def list(ctx: commands.Context, thing):
    if thing == "members":
        thread_members = await ctx.channel.fetch_members()
        members = []
        for thread_member in thread_members:
            members.append(ctx.guild.get_member(thread_member.id))
        await ctx.send(f"{[member.display_name for member in members]}")

@bot.command()
@commands.is_owner()
@is_thread()
async def give(ctx: commands.Context, thing, role_id):
    if thing == "members":
        role = ctx.guild.get_role(int(role_id))
        thread_members = await ctx.channel.fetch_members()
        for thread_member in thread_members:
            try:
                member = ctx.guild.get_member(thread_member.id)
                await member.add_roles(role)
            except discord.Forbidden as nope:
                print(f"forbidden from adding roles to {member}, reason: {nope.text=}, {nope.status=}, {nope.code=}")
            except discord.HTTPException as nope:
                print(f"couldn't add roles to {member}, reason: {nope.text=}, {nope.status=}, {nope.code=}")

@bot.command()
@commands.is_owner()
@is_thread()
async def remove(ctx: commands.Context, thing, role_id):
    if thing == "members":
        role = ctx.guild.get_role(int(role_id))
        thread_members = await ctx.channel.fetch_members()
        for thread_member in thread_members:
            try:
                member = ctx.guild.get_member(thread_member.id)
                await member.remove_roles(role)
            except discord.Forbidden as nope:
                print(f"forbidden from adding roles to {member}, reason: {nope.text=}, {nope.status=}, {nope.code=}")
            except discord.HTTPException as nope:
                print(f"couldn't add roles to {member}, reason: {nope.text=}, {nope.status=}, {nope.code=}")

@bot.command()
@commands.is_owner()
@is_thread()
async def add(ctx: commands.Context, thing, thread_name, thread_type="public"):
    if thing == "members":
        if thread_type == "public":
            thread_type = discord.ChannelType.public_thread
        elif thread_type == "private":
            thread_type = discord.ChannelType.private_thread
        else:
            return
        members = await ctx.channel.fetch_members()
        parent = ctx.channel.parent
        new_thread = await parent.create_thread(name=thread_name, type=thread_type)
        print(new_thread)
        for member in members:
            await new_thread.add_user(member)

@bot.command()
async def hi(ctx: commands.Context):
    await ctx.send("hello")

@bot.command("eval")
@commands.is_owner()
async def _eval(ctx: commands.Context, *, expression):
    print(expression)
    try:
        output = eval(expression)
        await ctx.send(str(output))
    except Exception as e:
        await ctx.send(str(e))

@bot.command()
@commands.is_owner()
async def aeval(ctx: commands.Context, *, expression: str):
    print(expression)
    try:
        output = await eval(expression)
        await ctx.send(str(output))
    except Exception as e:
        await ctx.send(str(e))

@bot.command("exec")
@commands.is_owner()
async def _exec(ctx: commands.Context, *, expression):
    print(expression)
    try:
        output = "a"
        exec(expression)
        await ctx.send(str(output))
    except Exception as e:
        await ctx.send(str(e))

@bot.command("aexec")
@commands.is_owner()
async def _aexec(ctx: commands.Context, *, expression: str):
    print(expression)
    try:
        output = ""
        await aexec(expression)
        await ctx.send(str(output))
    except Exception as e:
        await ctx.send(str(e))

bot.run(KEY)