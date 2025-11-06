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
        await ctx.send("❌ Format de date invalide. Utilise JJ-MM-AAAA.")
        return

    data = charger_devoirs()
    data["devoirs"].append({
        "matière": matière,
        "date": date_obj.strftime("%d-%m-%Y"),
        "description": description
    })

    sauvegarder_devoirs(data)
    await ctx.send(f"📌 Devoir ajouté : **{date_obj.strftime('%d-%m-%Y')}** en **{matière}** – {description}")

@bot.command()
async def calendrier(ctx):
    data = charger_devoirs()

    devoirs_valides = []
    erreurs = []

    # Conversion sécurisée des dates
    for d in data["devoirs"]:
        try:
            d["date_obj"] = datetime.strptime(d["date"], "%d-%m-%Y")
            devoirs_valides.append(d)
        except ValueError:
            erreurs.append(d)

    # Tri par date réelle
    devoirs_triés = sorted(devoirs_valides, key=lambda d: d["date_obj"])

    if not devoirs_triés:
        await ctx.send("📭 Aucun devoir valide enregistré.")
        return

    msg = "**📅 Voici les prochains devoirs :**\n"
    for i, d in enumerate(devoirs_triés, start=1):
        msg += f"{i}. **{d['matière']}** le **{d['date']}** : {d['description']}\n"

    if erreurs:
        msg += f"\n⚠️ {len(erreurs)} devoir(s) ignoré(s) à cause d’un format de date invalide."

    await ctx.send(msg)

bot.run(os.getenv("TOKEN"))
