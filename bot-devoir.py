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
            data = json.load(f)
    except FileNotFoundError:
        return {"devoirs": []}

    # Migration automatique des anciennes dates
    modifié = False
    for d in data["devoirs"]:
        try:
            # Si la date est au format JJ-MM-AAAA, on la convertit
            if "-" in d["date"] and len(d["date"].split("-")[0]) == 2:
                date_obj = datetime.strptime(d["date"], "%Y-%m-%d")
                d["date"] = date_obj.strftime("%Y-%m-%d")
                modifié = True
        except Exception:
            continue

    if modifié:
        sauvegarder_devoirs(data)

    return data

def sauvegarder_devoirs(data):
    with open(FICHIER, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.command()
async def ajouter(ctx, matière: str, date: str, *, description: str = None):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        await ctx.send("❌ Format de date invalide. Utilise JJ-MM-AAAA.")
        return

    data = charger_devoirs()
    data["devoirs"].append({
        "matière": matière,
        "date": date_obj.strftime("%Y-%m-%d"),
        "description": description
    })

    sauvegarder_devoirs(data)
    await ctx.send(f"📌 Devoir ajouté : **{date_obj.strftime('%Y-%m-%d')}** en **{matière}** – {description}")

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
        date_affichée = datetime.strptime(d["date"], "%Y-%m-%d")
        msg += f"{i}. **{d['matière']}** le **{date_affichée}** : {d['description']}\n"

    await ctx.send(msg)

bot.run(os.getenv("TOKEN"))
