import discord
from discord.ext import commands
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FICHIER = "devoirs.json"

def charger_devoirs():
    try:
        with open(FICHIER, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"devoirs": []}

def sauvegarder_devoirs(data):
    with open(FICHIER, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.command()
async def ajouter(ctx, matière: str, date: str, *, description: str = None):
    try:
        date_obj = datetime.strptime(date.strip(), "%Y-%m-%d")
    except ValueError:
        await ctx.send("❌ Format de date invalide. Utilise AAAA-MM-JJ.")
        return

    data = charger_devoirs()
    data["devoirs"].append({
        "matière": matière,
        "date": date,
        "description": description
    })

    sauvegarder_devoirs(data)
    await ctx.send(f"📌 Devoir ajouté : **{date_obj.strftime('%d-%m-%Y')}** en **{matière}** – {description}")

@bot.command()
async def calendrier(ctx):
    data = charger_devoirs()
    aujourd_hui = datetime.now().date()

    devoirs = [
        d for d in data["devoirs"]
        if datetime.strptime(d["date"], "%Y-%m-%d").date() >= aujourd_hui
    ]
    devoirs = sorted(devoirs, key=lambda d: d["date"])

    if not devoirs:
        await ctx.send("📭 Aucun devoir à venir.")
        return

    msg = "**📅 Devoirs à venir :**\n"
    for i, d in enumerate(devoirs, start=1):
        date_affichée = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        msg += f"{i}. **{d['matière']}** le **{date_affichée}** : {d['description']}\n"

    await ctx.send(msg)

bot.run(os.getenv("TOKEN"))
