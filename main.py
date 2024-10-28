import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
import os
from dotenv import load_dotenv
from db import SessionLocal

from service import create_user, create_event, place_bet, finalize_event, get_user_balance

load_dotenv()

DEFAULT_USER_BALANCE: float = 100.0

TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

db = SessionLocal()

class CreateEventModal(Modal, title="投票 新規作成"):
    title = TextInput(label="タイトル", placeholder="Voteのタイトルを入力してください", style=discord.TextStyle.short)
    option_1 = TextInput(label="選択肢1", placeholder="選択肢1を入力してください", style=discord.TextStyle.short)
    option_2 = TextInput(label="選択肢2", placeholder="選択肢2を入力してください", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        event = create_event(db, self.title.value, self.option_1.value, self.option_2.value)
        await interaction.response.send_message(f"「{event.title}」を作成しました。") # ここで作成した投票の情報を表示する

@bot.tree.command(name="create_vote", description="新しい投票を作成します。")
async def create_vote(interaction: discord.Interaction):
    # モーダルを表示
    await interaction.response.send_modal(CreateEventModal())

@bot.tree.command(name="my_points", description="ポイントを取得します。")
async def my_points(interaction: discord.Interaction):
    points = get_user_balance(db, interaction.user.id)
    await interaction.response.send_message(f"{interaction.user.name}のポイントは{points}です。")

@bot.tree.command(name="register", description="ユーザーを作成します。")
async def register(interaction: discord.Interaction):
    user = create_user(db, interaction.user.name, DEFAULT_USER_BALANCE)
    await interaction.response.send_message(f"{user.name}を登録しました。")




@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(TOKEN)
