import discord
from discord.ext import commands
from discord.ui import Button, View
from config import MOD_ROLE, ADMIN_ROLE, MUTE_DURATION, WARN_LIMIT
from database import db
from utilities import create_embed, log_action, check_permissions, ModerationView
import asyncio
import datetime

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name="پاک کردن", aliases=["clear", "purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        if amount > 100:
            amount = 100
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = await create_embed(
            "✅ پیام‌ها پاک شدند",
            f"تعداد {len(deleted) - 1} پیام پاک شد",
            "success"
        )
        await ctx.send(embed=embed, delete_after=5)
    

    @commands.command(name="اخطار", aliases=["warn"])
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await db.add_warn(member.id, ctx.author.id, reason, ctx.guild.id)
        warns = await db.get_warns(member.id, ctx.guild.id)
        
        embed = await create_embed(
            "⚠️ اخطار داده شد",
            f"به {member.mention} اخطار داده شد",
            "warning",
            Reason=reason,
            Total_Warns=str(len(warns))
        )
        await ctx.send(embed=embed)
        await log_action(ctx.guild, "Warn", member, ctx.author, reason)
    

    @commands.command(name="اخطارها", aliases=["warns"])
    @commands.has_permissions(manage_messages=True)
    async def check_warns(self, ctx, member: discord.Member):
        warns = await db.get_warns(member.id, ctx.guild.id)
        
        if not warns:
            embed = await create_embed(
                "📋 اخطارها",
                f"{member.mention} هیچ اخطاری ندارد",
                "info"
            )
        else:
            warn_list = "\n".join([f"{i+1}. {warn[3]} - <t:{int(datetime.datetime.fromisoformat(warn[4]).timestamp())}:R>" for i, warn in enumerate(warns)])
            embed = await create_embed(
                f"📋 اخطارهای {member.name}",
                warn_list,
                "warning",
                Total_Warns=str(len(warns))
            )
        
        await ctx.send(embed=embed)
    
 
    @commands.command(name="حذف_اخطار", aliases=["clearwarns"])
    @commands.has_permissions(manage_messages=True)
    async def clear_warns(self, ctx, member: discord.Member):
        await db.clear_warns(member.id, ctx.guild.id)
        embed = await create_embed(
            "✅ اخطارها حذف شدند",
            f"تمام اخطارهای {member.mention} حذف شدند",
            "success"
        )
        await ctx.send(embed=embed)
    

    @commands.command(name="میوت", aliases=["mute"])
    @commands.has_permissions(manage_roles=True)
    async def mute_user(self, ctx, member: discord.Member, duration: int = 60, *, reason: str = "No reason provided"):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)
        
        await member.add_roles(mute_role)
        await db.add_mute(member.id, ctx.author.id, reason, duration, ctx.guild.id)
        
        embed = await create_embed(
            "🔇 کاربر میوت شد",
            f"{member.mention} برای {duration} دقیقه میوت شد",
            "warning",
            Reason=reason
        )
        await ctx.send(embed=embed)
        

        await asyncio.sleep(duration * 60)
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
    

    @commands.command(name="آنمیوت", aliases=["unmute"])
    @commands.has_permissions(manage_roles=True)
    async def unmute_user(self, ctx, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            embed = await create_embed(
                "🔊 آنمیوت شد",
                f"{member.mention} آنمیوت شد",
                "success"
            )
        else:
            embed = await create_embed(
                "❌ خطا",
                "این کاربر میوت نیست",
                "error"
            )
        await ctx.send(embed=embed)

    @commands.command(name="کیک", aliases=["kick"])
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        embed = await create_embed(
            "👢 کاربر کیک شد",
            f"{member.mention} از سرور کیک شد",
            "warning",
            Reason=reason
        )
        await ctx.send(embed=embed)
        await log_action(ctx.guild, "Kick", member, ctx.author, reason)
    

    @commands.command(name="بن", aliases=["ban"])
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await db.add_ban(member.id, ctx.author.id, reason, ctx.guild.id)
        embed = await create_embed(
            "🔨 کاربر بن شد",
            f"{member.mention} از سرور بن شد",
            "error",
            Reason=reason
        )
        await ctx.send(embed=embed)
        await log_action(ctx.guild, "Ban", member, ctx.author, reason)
    

    @commands.command(name="آنبن", aliases=["unban"])
    @commands.has_permissions(ban_members=True)
    async def unban_user(self, ctx, user_id: int):
        user = discord.Object(id=user_id)
        await ctx.guild.unban(user)
        embed = await create_embed(
            "✅ آنبن شد",
            f"کاربر با آیدی {user_id} آنبن شد",
            "success"
        )
        await ctx.send(embed=embed)
    

    @commands.command(name="قفل", aliases=["lock"])
    @commands.has_permissions(manage_channels=True)
    async def lock_channel(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = await create_embed(
            "🔒 چنل قفل شد",
            "این چنل قفل شد",
            "warning"
        )
        await ctx.send(embed=embed)
    

async def setup(bot):
    await bot.add_cog(ModerationCommands(bot))