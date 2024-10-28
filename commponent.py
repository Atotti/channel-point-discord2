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
    def __init__(self, db, event: Event, timeout=180):
        self.db = db
        self.title = event.title
        self.option_1 = event.option_1
        self.option_2 = event.option_2
        self.event_id = event.id
        super().__init__(timeout=timeout)

        # ボタンラベルを設定
        self.vote1.label = self.option_1
        self.vote2.label = self.option_2


    @discord.ui.button(label="option1", style=discord.ButtonStyle.primary)
    async def vote1(self, button: discord.ui.Button, interaction: discord.Interaction):
        place_bet(self.db, interaction.user.id, self.event_id, self.option_1, 10.0)
        await interaction.response.send_message(f"{interaction.user.mention} がbetしました。")

    @discord.ui.button(label="option2", style=discord.ButtonStyle.premium)
    async def vote2(self, button: discord.ui.Button, interaction: discord.Interaction):
        place_bet(self.db, interaction.user.id, self.event_id, self.option_2, 10.0)
        await interaction.response.send_message(f"{interaction.user.mention} がbetしました。")

    @discord.ui.button(label="締め切る", style=discord.ButtonStyle.danger)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        event = close_event(self.db, self.event_id)
        await event_close_embed(self.db, event, interaction.channel)

    @discord.ui.button(label="結果を確定", style=discord.ButtonStyle.success)
    async def finalize(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(JudgeEventModal(self.db, self.event_id))



class CreateEventModal(discord.ui.Modal, title="bet 新規作成"):
    def __init__(self, db):
        self.db = db
        super().__init__()
    title = discord.ui.TextInput(label="タイトル", placeholder="betのタイトルを入力してください", style=discord.TextStyle.short)
    option_1 = discord.ui.TextInput(label="選択肢1", placeholder="選択肢1を入力してください", style=discord.TextStyle.short)
    option_2 = discord.ui.TextInput(label="選択肢2", placeholder="選択肢2を入力してください", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        event = create_event(self.db, self.title.value, self.option_1.value, self.option_2.value)
        channel = interaction.channel
        await event_board(self.db, event, channel)

async def user_points_embed(db, user, channel):
    user_id = user.id
    embed = Embed(title=f"{user}の残高", color=0x00ff00)
    points = get_user_balance(db, user_id)
    embed.add_field(name="ポイント", value=points, inline=False)

    channel.send(embed=embed)

async def users_points_embed(db, user, channel):
    embed = Embed(title="ユーザーの残高", color=0x00ff00)
    for user in get_all_users(db):
        embed.add_field(name=user.name, value=user.balance, inline=False)

    channel.send(embed=embed)

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

    embed.add_field(name=f"{event.option_1}に投票", value=", ".join([user.name for user in option_1_bet_users]), inline=False)
    embed.add_field(name=f"{event.option_2}に投票", value=", ".join([user.name for user in option_2_bet_users]), inline=False)

    channel.send(embed=embed)

class JudgeEventModal(discord.ui.Modal, title="bet 結果確定"):
    def __init__(self, db, event_id):
        self.db = db
        self.event_id = event_id
        super().__init__()

    def get_option_1(self) -> str:
        return get_event(self.db, self.event_id).option_1

    def get_option_2(self) -> str:
        return get_event(self.db, self.event_id).option_2

    option = discord.ui.Select(label="勝者を選択してください", options=[
        discord.SelectOption(label=get_option_1(), value=get_option_1()),
        discord.SelectOption(label=get_option_1(), value=get_option_1()),
    ])

    async def on_submit(self, interaction: discord.Interaction):
        event = finalize_event(self.db, self.event_id, self.option.value)
        await event_result_embed(self.db, event, interaction.channel)

async def event_result_embed(db, event, channel):
    title = event.title
    winning_option = event.winning_option

    embed = Embed(title=title, description="イベントが終了しました", color=0x00ff00)
    embed.add_field(name="勝者", value=winning_option, inline=False)


    channel.send(embed=embed)
    await users_points_embed(db, channel)
