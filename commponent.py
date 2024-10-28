import time
import discord.ui
from service import create_event, place_bet, get_user_balance, close_event, finalize_event, get_event, get_all_users
from discord import Embed
from models import Event

async def event_board(db, event: Event, channel):
    title = event.title
    option_1 = event.option_1
    option_2 = event.option_2

    embed = Embed(title=title, description="イベントが作成されました。", color=0x00ff00)
    embed.add_field(name="選択肢1", value=option_1, inline=False)
    embed.add_field(name="選択肢2", value=option_2, inline=False)
    vote_button = EventView(db, event)

    await channel.send(embed=embed, view=vote_button)

class EventView(discord.ui.View):
    def __init__(self, db, event: Event, timeout=None):
        super().__init__(timeout=timeout)
        self.db = db
        self.option_1 = event.option_1
        self.option_2 = event.option_2
        self.event_id = event.id

        # ボタンをインスタンス化してラベルを動的に設定
        self.vote1 = discord.ui.Button(label=f"{self.option_1}に賭ける", style=discord.ButtonStyle.primary, custom_id="vote_option_1")
        self.vote1.callback = self.vote1_callback  # コールバック関数を設定
        self.add_item(self.vote1)  # Viewにボタンを追加

        self.vote2 = discord.ui.Button(label=f"{self.option_2}に賭ける", style=discord.ButtonStyle.primary, custom_id="vote_option_2")
        self.vote2.callback = self.vote2_callback
        self.add_item(self.vote2)

        self.close_button = discord.ui.Button(label="締め切る", style=discord.ButtonStyle.danger, custom_id="close_event")
        self.close_button.callback = self.close_callback
        self.add_item(self.close_button)

        self.finalize_button = discord.ui.Button(label="結果を確定", style=discord.ButtonStyle.success, custom_id="finalize_event")
        self.finalize_button.callback = self.finalize_callback
        self.add_item(self.finalize_button)

    # 各ボタンのコールバック関数
    async def vote1_callback(self, interaction: discord.Interaction):
        place_bet(self.db, interaction.user.id, self.event_id, self.option_1, 10.0)
        await interaction.response.send_message(f"{interaction.user.mention} が10ポイントbetしました。")

    async def vote2_callback(self, interaction: discord.Interaction):
        place_bet(self.db, interaction.user.id, self.event_id, self.option_2, 10.0)
        await interaction.response.send_message(f"{interaction.user.mention} が10ポイントbetしました。")

    async def close_callback(self, interaction: discord.Interaction):
        event = close_event(self.db, self.event_id)
        await event_close_embed(self.db, event, interaction.channel)
        await interaction.response.send_message("イベントを締め切りました。", ephemeral=True)

    async def finalize_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("勝者を選択してください:", view=JudgeEventView(self.db, self.event_id), ephemeral=True)



class CreateEventModal(discord.ui.Modal, title="bet 新規作成"):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.event_title = discord.ui.TextInput(label="タイトル", placeholder="betのタイトルを入力してください", style=discord.TextStyle.short)
        self.option_1 = discord.ui.TextInput(label="選択肢1", placeholder="選択肢1を入力してください", style=discord.TextStyle.short)
        self.option_2 = discord.ui.TextInput(label="選択肢2", placeholder="選択肢2を入力してください", style=discord.TextStyle.short)

        # フィールドをモーダルに追加
        self.add_item(self.event_title)
        self.add_item(self.option_1)
        self.add_item(self.option_2)

    async def on_submit(self, interaction: discord.Interaction):
        event = create_event(self.db, self.event_title.value, self.option_1.value, self.option_2.value)
        channel = interaction.channel
        await event_board(self.db, event, channel)
        await interaction.response.send_message("イベントが作成されました！", ephemeral=True)

async def user_points_embed(db, user, channel):
    user_id = user.id
    embed = Embed(title=f"{user}の残高", color=0x00ff00)
    points = get_user_balance(db, user_id)
    embed.add_field(name="ポイント", value=points, inline=False)

    await channel.send(embed=embed)

async def users_points_embed(db, channel):
    embed = Embed(title="ユーザーの残高", color=0x00ff00)
    for user in get_all_users(db):
        embed.add_field(name=user.name, value=user.balance, inline=False)

    await channel.send(embed=embed)

async def event_close_embed(db, event, channel):
    option_1_bet = 0
    option_2_bet = 0

    for bet in event.bets:
        if bet.option == event.option_1:
            option_1_bet += bet.amount
        elif bet.option == event.option_2:
            option_2_bet += bet.amount

    option_1_bet_users = []
    option_2_bet_users = []

    for bet in event.bets:
        if bet.option == event.option_1:
            option_1_bet_users.append(bet.user)
        elif bet.option == event.option_2:
            option_2_bet_users.append(bet.user)


    embed = Embed(title=f"{event.title}は締め切られました。", color=0x00ff00)
    embed.add_field(name=event.option_1, value=f"{option_1_bet}ポイント", inline=True)
    embed.add_field(name=event.option_2, value=f"{option_2_bet}ポイント", inline=True)

    embed.add_field(name=f"{event.option_1}にbet", value=", ".join([user.name for user in option_1_bet_users]), inline=False)
    embed.add_field(name=f"{event.option_2}にbet", value=", ".join([user.name for user in option_2_bet_users]), inline=False)

    await channel.send(embed=embed)

class JudgeEventView(discord.ui.View):
    def __init__(self, db, event_id):
        super().__init__(timeout=None)
        self.db = db
        self.event_id = event_id

        # 選択肢を動的に取得して設定
        option_1 = get_event(self.db, self.event_id).option_1
        option_2 = get_event(self.db, self.event_id).option_2

        # 勝者を選択するためのドロップダウンメニューを追加
        self.option_select = discord.ui.Select(
            placeholder="勝者を選択してください",
            options=[
                discord.SelectOption(label=option_1, value=option_1),
                discord.SelectOption(label=option_2, value=option_2),
            ]
        )
        self.option_select.callback = self.select_callback
        self.add_item(self.option_select)

    async def select_callback(self, interaction: discord.Interaction):
        # 選択したオプションを取得
        selected_option = self.option_select.values[0]

        # 勝者を確定し、結果をチャンネルに送信
        event = finalize_event(self.db, self.event_id, selected_option)
        await event_result_embed(self.db, event, interaction.channel)
        await interaction.response.send_message(f"勝者が '{selected_option}' に設定されました！", ephemeral=True)

async def event_result_embed(db, event, channel):
    title = event.title
    winning_option = event.winning_option

    embed = Embed(title=title, description="イベントが終了しました", color=0x00ff00)
    embed.add_field(name="勝者", value=winning_option, inline=False)


    await channel.send(embed=embed)
    await users_points_embed(db, channel)
