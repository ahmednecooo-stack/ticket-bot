import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="ticket", description="Open a new ticket")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
    await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)
    await channel.send(f"Hello {interaction.user.mention}, staff will be with you soon!\nType `!close` to close this ticket.")

@bot.tree.command(name="close", description="Close this ticket")
async def close(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("Closing ticket in 3 seconds...")
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("This is not a ticket channel!", ephemeral=True)

@bot.command()
async def close(ctx):
    if "ticket-" in ctx.channel.name:
        await ctx.send("Closing ticket...")
        await ctx.channel.delete()

bot.run(os.getenv("DISCORD_TOKEN"))
