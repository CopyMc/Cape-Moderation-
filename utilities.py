import discord
from discord.ui import Button, View, Select
from config import COLORS
from database import db

class ModerationView(View):
    def __init__(self, user_id: int, action: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.action = action
    
    @discord.ui.button(label="تایید", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: Button):

        pass
    
    @discord.ui.button(label="لغو", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="عمل لغو شد!", view=None)

async def create_embed(title: str, description: str, color: str, **kwargs):
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS.get(color, COLORS["info"])
    )
    
    for key, value in kwargs.items():
        embed.add_field(name=key, value=value, inline=False)
    
    return embed

async def log_action(guild: discord.Guild, action: str, user: discord.Member, 
                    moderator: discord.Member, reason: str = "None"):
    log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
    if log_channel:
        embed = await create_embed(
            f"📝 {action}",
            f"**User:** {user.mention}\n**Moderator:** {moderator.mention}\n**Reason:** {reason}",
            "info"
        )
        await log_channel.send(embed=embed)

async def check_permissions(ctx, required_permission):
    if getattr(ctx.author.guild_permissions, required_permission):
        return True
    
    embed = await create_embed(
        "❌ دسترسی denied",
        f"شما دسترسی `{required_permission}` را ندارید!",
        "error"
    )
    await ctx.send(embed=embed)
    return False