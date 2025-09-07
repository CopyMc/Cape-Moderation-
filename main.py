import discord
from discord.ext import commands
from config import BOT_TOKEN, PREFIX
from database import Database
from moderation import ModerationCommands
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
db = Database()
# Bot Creator And Developer : Copy
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await db.init_db()
    await bot.add_cog(ModerationCommands(bot))
    print("Moderation bot is ready!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ دسترسی denied",
            description="شما دسترسی لازم برای این کامند را ندارید!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    else:
        print(f"Error: {error}")


@bot.command(name="help", aliases=["راهنما"])
async def help_command(ctx):
    embed = discord.Embed(
        title="🎯 راهنمای بات مودریشن",
        description="**دستورات اصلی:**",
        color=0x0099ff
    )
    
    commands_list = [
        ("!پاک کردن [تعداد]", "پاک کردن پیام‌ها"),
        ("!اخطار [کاربر] [دلیل]", "اخطار دادن به کاربر"),
        ("!اخطارها [کاربر]", "مشاهده اخطارهای کاربر"),
        ("!میوت [کاربر] [زمان] [دلیل]", "میوت کردن کاربر"),
        ("!آنمیوت [کاربر]", "آنمیوت کردن کاربر"),
        ("!کیک [کاربر] [دلیل]", "کیک کردن کاربر"),
        ("!بن [کاربر] [دلیل]", "بن کردن کاربر"),
        ("!آنبن [آیدی]", "آنبن کردن کاربر"),
        ("!قفل", "قفل کردن چنل"),
        ("!باز کردن", "باز کردن چنل")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="برای اطلاعات بیشتر با ادمین تماس بگیرید")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(BOT_TOKEN)