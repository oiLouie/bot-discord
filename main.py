from keep_alive import keep_alive
import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import pytz
import os
import json

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Canais
CHANNEL_ID_MOOD_CHECKIN = 1378137261392007209  # Mood check-in (embeds do humor)
CHANNEL_ID_TASKS = 1377485005319573557  # Tarefas diárias
CHANNEL_ID_REPORT = 1378563997321924678  # Relatório diário das tarefas

USER_ID = 1089325052492783687  # ID da little

# Arquivo para salvar o progresso
DATA_FILE = "data.json"

# Emojis e tarefas diárias
tasks_list = {
    " Morning & Night Hygiene": "🦷",
    " Make Your Bed": "🛏️",
    " Nom Noms": "🍽️",
    " Shower Time": "🚿",
    " Drink Water": "💧",
    " Bedtime": "🌙",
    " Positive Affirmation": "🌈",
    " Journal (optional)": "📓"
}

daily_tasks_completed = {}


def load_data():
    global daily_tasks_completed
    try:
        with open(DATA_FILE, "r") as f:
            daily_tasks_completed = json.load(f)
    except FileNotFoundError:
        daily_tasks_completed = {}
    except json.JSONDecodeError:
        daily_tasks_completed = {}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(daily_tasks_completed, f, indent=4)


@bot.event
async def on_ready():
    print(f"Bot conectado como: {bot.user}")
    load_data()  # Carrega o progresso salvo ao iniciar
    send_mood_checkin.start()
    send_daily_tasks.start()
    send_daily_report.start()


@tasks.loop(minutes=1)
async def send_mood_checkin():
    now = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
    if now.hour == 13 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID_MOOD_CHECKIN)
        if channel:
            mention = f"<@{USER_ID}>"
            embed = discord.Embed(
                title="❤️ Mood Check-In *(pick a heart to match your feels)*:",
                description=("• 💖 Super happi\n"
                             "• 💛 Feeling calm and okay\n"
                             "• 💙 A bit sadge\n"
                             "• 💔 Not okay & need cuddles pls :(\n\n"
                             f"{mention}"),
                color=0xFF69B4)
            message = await channel.send(embed=embed)
            for emoji in ["💖", "💛", "💙", "💔"]:
                await message.add_reaction(emoji)


@tasks.loop(minutes=1)
async def send_daily_tasks():
    now = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
    if now.hour == 13 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID_TASKS)
        if channel:
            mention = f"<@{USER_ID}>"
            embed = discord.Embed(
                title="🌼 Daily Tasks for My Darling",
                description="\n".join(
                    [f"{emoji} {task}"
                     for task, emoji in tasks_list.items()]) +
                f"\n\n{mention}",
                color=0xFFC0CB)
            message = await channel.send(embed=embed)

            # Inicializa o dia no dicionário e salva
            date_str = now.strftime("%Y-%m-%d")
            daily_tasks_completed[date_str] = {emoji: False for emoji in tasks_list.values()}
            save_data()

            for emoji in tasks_list.values():
                await message.add_reaction(emoji)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    date_str = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    emoji = str(reaction.emoji)
    if date_str in daily_tasks_completed and emoji in daily_tasks_completed[date_str]:
        daily_tasks_completed[date_str][emoji] = True
        save_data()  # Salva progresso após cada reação


# ... código anterior sem mudanças ...

@tasks.loop(minutes=1)
async def send_daily_report():
    now = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
    if now.hour == 23 and now.minute == 0:
        date_str = now.strftime("%Y-%m-%d")
        if date_str in daily_tasks_completed:
            completed = [
                emoji for emoji, done in daily_tasks_completed[date_str].items()
                if done
            ]
            total = len(daily_tasks_completed[date_str])
            count = len(completed)
            melancias = "🍉" * count
            channel = bot.get_channel(CHANNEL_ID_REPORT)
            if channel:
                mention = f"<@{USER_ID}>"
                embed = discord.Embed(
                    title="📋 Daily Report",
                    description=(
                        f"Tasks completed today: **{count} / {total}**\n"
                        f"{melancias if melancias else 'No melons today...'}\n\n"
                        f"{mention}"
                    ),
                    color=0x90EE90)
                await channel.send(embed=embed)

                # Envia o comando para adicionar pontos (melancias) para ela
                # Ajuste 'fizzywizzy111' para o username correto do usuário do outro bot
                points_command = f"/modifybal add user:@fizzywizzy111 amount:{count}"
                await channel.send(points_command)
                
@bot.command()
async def puppylog(ctx):
    date_str = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    if date_str not in daily_tasks_completed:
        await ctx.send("No data for today yet, sweetheart.")
        return
    status = ""
    for emoji, done in daily_tasks_completed[date_str].items():
        mark = "✅" if done else "❌"
        task = next(task for task, em in tasks_list.items() if em == emoji)
        status += f"{mark} {emoji} {task}\n"
    await ctx.send(f"**Today's Puppy Log:**\n{status}")


@bot.command()
async def melancias(ctx):
    total = 0
    for date in daily_tasks_completed:
        total += sum(1 for done in daily_tasks_completed[date].values() if done)
    await ctx.send(f"Total 🍉 collected so far: **{total}**")


@bot.command()
async def marco(ctx):
    await ctx.send("pollo!")


@bot.command()
async def sendtasks(ctx):
    channel = bot.get_channel(CHANNEL_ID_TASKS)
    if channel:
        mention = f"<@{USER_ID}>"
        embed = discord.Embed(
            title="🌼 Daily Tasks for My Lil Baby",
            description="\n".join(
                [f"{emoji} {task}"
                 for task, emoji in tasks_list.items()]) + f"\n\n{mention}",
            color=0xFFC0CB)
        message = await channel.send(embed=embed)

        # Inicializa o dia no dicionário e salva
        date_str = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
        daily_tasks_completed[date_str] = {emoji: False for emoji in tasks_list.values()}
        save_data()

        for emoji in tasks_list.values():
            await message.add_reaction(emoji)

    await ctx.send("Sent daily tasks embed for testing, my silly bean!")


keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
