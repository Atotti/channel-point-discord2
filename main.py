import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()



TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

class MyModal(Modal, title="Vote 新規作成"):
    name = TextInput(label="タイトル", placeholder="Voteのタイトルを入力してください", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        # モーダルが送信されたときに呼び出される
        await interaction.response.send_message(f"{self.name.value}を作成しました。")

@bot.tree.command(name="create_vote", description="新しい投票を作成します。")
async def create_vote(interaction: discord.Interaction):
    # モーダルを表示
    await interaction.response.send_modal(MyModal())

@bot.tree.command(name="get_points", description="ポイントを取得します。")
async def get_points(interaction: discord.Interaction):
    conn = sqlite3.connect('points.db')
    cursor = conn.cursor()
    cursor.execute('SELECT points FROM user_points WHERE user_id = ?', (interaction.user.id,))
    points = cursor.fetchone()
    conn.close()
    await interaction.response.send_message(f"{interaction.user.name}のポイントは{points[0]}です。")

@bot.tree.command(name="create_user", description="ユーザーを作成します。")
async def create_user(interaction: discord.Interaction):
    conn = sqlite3.connect('points.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_points (user_id) VALUES (?)', (interaction.user.id,))
    conn.commit()
    conn.close()
    await interaction.response.send_message("ユーザーを作成しました。")




@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(TOKEN)
