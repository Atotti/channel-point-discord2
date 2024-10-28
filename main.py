import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
from db import SessionLocal

from service import create_user
from commponent import CreateEventModal, user_points_embed


load_dotenv()

DEFAULT_USER_BALANCE: float = 100.0

TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

db = SessionLocal()

@bot.tree.command(name="create_vote", description="新しいbetを作成します。")
async def create_vote(interaction: discord.Interaction):
    await interaction.response.send_modal(CreateEventModal(db))

@bot.tree.command(name="my_points", description="自分の残高を取得します。")
async def my_points(interaction: discord.Interaction):
    await user_points_embed(db, interaction.user, interaction.channel)

@bot.tree.command(name="register", description="ユーザーを作成します。")
async def register(interaction: discord.Interaction):
    user = create_user(db, interaction.user.name, DEFAULT_USER_BALANCE)
    await interaction.response.send_message(f"{interaction.user.mention} {user.name}を登録しました。")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(TOKEN)
