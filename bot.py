import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🎫 افتح تيكت", style=discord.ButtonStyle.blurple, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        for ch in guild.text_channels:
            if ch.name == f"ticket-{interaction.user.name.lower()}":
                await interaction.response.send_message(f"عندك تيكت مفتوح: {ch.mention}", ephemeral=True)
                return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        staff_role = discord.utils.get(guild.roles, name="Staff")
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"تم فتح التيكت: {channel.mention}", ephemeral=True)
        embed = discord.Embed(title="🎫 تيكت جديد", description=f"اهلا {interaction.user.mention}\nاكتب مشكلتك هنا والادمن هيرد عليك.", color=0x2b2d31)
        await channel.send(embed=embed, view=TicketControlView())

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="✅ استلام", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send(f"✅ تم استلام التيكت بواسطة {interaction.user.mention}")
        await interaction.response.send_message("تم الاستلام!", ephemeral=True)
    @discord.ui.button(label="🔒 اغلاق", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("سيتم اغلاق التيكت بعد 3 ثواني...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(TicketControlView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="setup", description="عمل لوحة التيكتات")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 الدعم الفني", description="عندك مشكلة؟ دوس على الزرار اللي تحت عشان تفتح تيكت والادمن هيكلمك.", color=0x5865F2)
    await interaction.response.send_message(embed=embed, view=TicketView())

@bot.tree.command(name="close", description="اغلاق التيكت")
async def close_cmd(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("سيتم الاغلاق...")
        await asyncio.sleep(2)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("دي مش روم تيكت!", ephemeral=True)

@bot.tree.command(name="claim", description="استلام التيكت")
async def claim_cmd(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message(f"✅ تم استلام التيكت بواسطة {interaction.user.mention}")
    else:
        await interaction.response.send_message("دي مش روم تيكت!", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
