import discord

import util
import bot

TOKEN = util.getenv('DISCORD_TOKEN')
client = discord.Client()


state = None


@client.event
async def on_ready():
    print('ログインしました')
    global state
    state = bot.BotState()


@client.event
async def on_message(message):
    if message.author.bot:
        return
    global state
    await state.on_message(message)


@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return
    await state.on_raw_reaction_add(payload)

client.run(TOKEN)
