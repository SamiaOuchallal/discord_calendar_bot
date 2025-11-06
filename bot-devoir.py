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
        date_obj = datetime.strptime(date, "%d-%m-%Y")
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
    await ctx.send(f"📌 Devoir ajouté : **{date}** en **{matière}** – {description}")

@bot.command()
async def calendrier(ctx):
    data = charger_devoirs()
    #devoirs = sorted(data["devoirs"], key=lambda d: d["date"])

    devoirs = sorted(data["devoirs"], key=lambda date: datetime.strptime(data["date"], "%d-%m-%Y"))

    if not devoirs:
        await ctx.send("📭 Aucun devoir enregistré.")
        return

    msg = "**📅 Voici les prochains devoirs :**\n"
    for d in devoirs:
        msg += f"- **{d['matière']}** le **{d['date']}** : {d['description']}\n"
    await ctx.send(msg)

bot.run(os.getenv("TOKEN"))
