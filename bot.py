import json  # ← 読み上げチャンネルの保存に使う

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests  

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # ボイスチャンネル用

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔊 ElevenLabsで音声生成する関数
def generate_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        return True
    else:
        print("音声生成に失敗:", response.status_code, response.text)
        return False

def get_character_usage():
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "xi-api-key": ELEVEN_API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        used = data.get("character_count", 0)
        limit = data.get("character_limit", 1)
        remaining = limit - used
        return remaining, limit
    else:
        print("❌ 使用量の取得に失敗:", response.status_code)
        return None, None


@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send(
        "🐬 ボイスチャンネルに入室しました\n"
        "\n"
        "📣 このBotはユーザーの支援で運営されています！\n"
        "💖 ご支援はこちら → https://mahito-discord.fanbox.cc/"
    )
    else:
        await ctx.send("先にボイスチャンネルに入ってね！")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから退出しました！")
    else:
        await ctx.send("まだボイスチャンネルにいないよ！")

@bot.command()
async def say(ctx, *, message: str):
    if ctx.channel.name != "読み上げ":
        await ctx.send("このチャンネルでは読み上げできません！")
        return

    await ctx.send(f"読み上げます: {message}")

    if generate_speech(message):
        if ctx.voice_client:
            ctx.voice_client.play(discord.FFmpegPCMAudio("output.mp3"))
        else:
            await ctx.send("ボイスチャンネルに入ってないよ！")

@bot.command()
async def where(ctx):
    await ctx.send(f"このチャンネルの名前は「{ctx.channel.name}」です！")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        with open("read_channel.json", "r") as f:
            data = json.load(f)
        target_channel_id = data.get(str(message.guild.id))
    except:
        target_channel_id = None

    if message.channel.id == target_channel_id:
        if generate_speech(message.content):
            if message.guild.voice_client:
                message.guild.voice_client.play(discord.FFmpegPCMAudio("output.mp3"))

    await bot.process_commands(message)


@bot.command()
async def set_read_channel(ctx):
    guild_id = str(ctx.guild.id)
    channel_id = ctx.channel.id

    try:
        with open("read_channel.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data[guild_id] = channel_id

    with open("read_channel.json", "w") as f:
        json.dump(data, f)

    await ctx.send(f"✅ このチャンネル（{ctx.channel.name}）を読み上げ対象に設定しました！")

@bot.command()
async def status(ctx):
    remaining, limit = get_character_usage()
    if remaining is not None:
        await ctx.send(
            f"📊 ElevenLabs の使用状況\n"
            f"📝 残り文字数: `{remaining:,}` / `{limit:,}`"
        )
    else:
        await ctx.send("❌ ElevenLabsのステータス取得に失敗しました…")

import os

bot.run(os.getenv("DISCORD_TOKEN"))