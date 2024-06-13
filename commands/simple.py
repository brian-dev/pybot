import os
import discord

from datetime import datetime
from discord import app_commands
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
MY_GUILD = discord.Object(id=GUILD_ID)
GENERAL_CHANNEL_ID = os.getenv("GENERAL_CHANNEL_ID")


def get_current_date_time():
    return datetime.now()

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # Synchronize the app commands to one guild.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def get_date_time(interaction: discord.Interaction):
    # Provides the user with a message response containing the current date/time
    current_time = get_current_date_time().strftime('%H:%M')
    current_day = get_current_date_time().strftime("%A, %B %d")
    await interaction.response.send_message(f'Hi, {interaction.user.mention}. The current date and time is '
                                            f'{current_day} at {current_time} hours.')


@client.tree.command()
@app_commands.describe(birth_year_value='Your year of birth.',)
async def age(interaction: discord.Interaction, birth_year_value: int):
    # Calculates age based on birth year and current year with personalized message.
    year = get_current_date_time().year
    await interaction.response.send_message(f'Hello, {interaction.user}! You were born in {birth_year_value} and '
                                            f'you are or are turning {year - birth_year_value} '
                                            f'years old this year.')


# Changes the display of the parameter on Discord.
@client.tree.command()
@app_commands.rename(text_to_send='name')
@app_commands.describe(text_to_send='Send your name to the channel!')
async def send(interaction: discord.Interaction, text_to_send: str):
    # Takes user input and send it to the channel
    await interaction.response.send_message(text_to_send)


# Creates an optional parameter for a user.
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    # Prints when a member has joined
    # If no member is explicitly provided then use the command user
    member = member or interaction.user

    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


# This context menu command only works on members
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


# This context menu command only works on messages
@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # Send this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(int(GENERAL_CHANNEL_ID))

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)


client.run(TOKEN)
