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
        # Format attendu : YYYY-MM-DD
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        await ctx.send("❌ Format de date invalide. Utilise AAAA-MM-JJ.")
        return

    data = charger_devoirs()
    data["devoirs"].append({
        "matière": matière,
        "date": date,  # déjà au bon format
        "description": description
    })

    sauvegarder_devoirs(data)
    await ctx.send(f"📌 Devoir ajouté : **{date_obj.strftime('%d-%m-%Y')}** en **{matière}** – {description}")

@bot.command()
async def calendrier(ctx):
    data = charger_devoirs()

    try:
        devoirs_triés = sorted(
            data["devoirs"],
            key=lambda d: datetime.strptime(d["date"], "%Y-%m-%d")
        )
    except Exception as e:
        await ctx.send("❌ Erreur lors du tri des devoirs.")
        return

    if not devoirs_triés:
        await ctx.send("📭 Aucun devoir enregistré.")
        return

    msg = "**📅 Voici les prochains devoirs :**\n"
    for i, d in enumerate(devoirs_triés, start=1):
        date_affichée = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        msg += f"{i}. **{d['matière']}** le **{date_affichée}** : {d['description']}\n"

    await ctx.send(msg)

bot.run(os.getenv("TOKEN"))
