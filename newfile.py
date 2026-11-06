
import discord
from discord.ext import commands
import requests
import asyncio
import getpass

# SECRET TOKENS
BOT_TOKEN = getpass.getpass("Discord Bot Token: ")
COPS_TOKEN = getpass.getpass("Critical Ops API Token: ")

# DISCORD SETTINGS
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="-",
    intents=intents
)

API_URL = "https://latest.prod.copsapi.criticalforce.fi/api/public/v2"

def get_player(username):

    headers = {
        "Authorization": f"Bearer {COPS_TOKEN}"
    }

    response = requests.get(
        API_URL + "/profile",
        headers=headers,
        params={"usernames": username},
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    if not data:
        return None

    return data[0] if isinstance(data, list) else data


def kd(stats):
    kills = stats.get("k", 0)
    deaths = stats.get("d", 0)

    if deaths == 0:
        return "N/A"

    return f"{kills / deaths:.2f}"


@bot.event
async def on_ready():
    print(f"CLUTCH AI ONLINE: {bot.user}")
    print("Command: -search PlayerName")


@bot.command(name="search")
async def search_player(ctx, *, username):

    await ctx.send(f"🔎 Searching {username}...")

    try:
        player = await asyncio.to_thread(
            get_player, username
        )

        if not player:
            await ctx.send("❌ Player not found!")
            return

        info = player.get("basic_info", {})
        level = info.get("player_level", {})
        stats = player.get("stats", {})
        seasons = stats.get("seasonal_stats", [])

        latest = seasons[-1] if seasons else {}

        ranked = latest.get("ranked", {})
        casual = latest.get("casual", {})

        clan = player.get("clan") or {}
        clan_name = clan.get("name", "Unknown")

        embed = discord.Embed(
            title="⚡ CLUTCH AI | PLAYER PROFILE",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="👤 Player",
            value=info.get("name", username),
            inline=True
        )

        embed.add_field(
            name="⭐ Level",
            value=str(level.get("level", "N/A")),
            inline=True
        )

        embed.add_field(
            name="🏆 Ranked KD",
            value=kd(ranked),
            inline=True
        )

        embed.add_field(
            name="🎮 Casual KD",
            value=kd(casual),
            inline=True
        )

        embed.add_field(
            name="🏷️ Clan",
            value=clan_name,
            inline=True
        )

        embed.set_footer(
            text="Critical Ops | CLUTCH AI"
        )

        await ctx.send(embed=embed)

    except requests.HTTPError as e:
        await ctx.send(
            f"❌ API Error: {e.response.status_code}"
        )

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


bot.run(BOT_TOKEN)
