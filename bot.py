import discord
import os
import gspread
import random
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import CellFormat, color, format_cell_range
from gspread_formatting import TextFormat

load_dotenv()

# Connexion à Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)
sheet = gc.open("Chateau VGS 9").sheet1
inventaire_chateau = {}

# Murs, cases spéciales
murs = ["A6", "A10", "B1", "B3", "B4", "B8", "B12", "B13", "B15", "C3", "C6", "C8", "C10", "C13", "D5", "D11", "E2", "E3", "E7", "E9", "E13", "E14", "F5", "F6", "F10", "F11", "G1", "G2", 
        "G7", "G9", "G14", "G15", "H4", "H5", "H11", "H12", "I1", "I2", "I7", "I9", "I14", "I15", "K2", "K3", "K7", "K9", "K13", "K14", "L5", "L11", "M3", "M6", "M8", "M10", "M13", 
        "N1", "N3", "N4", "N8", "N12", "N13", "N15", "O6", "O10"]

boss_cases = ["A8", "D2", "D14", "F7", "J9", "L2", "L14", "O8"]
evenement_cases = ["A4", "A12", "B6", "B10", "D8", "E1", "E4", "E12", "E15", "G3", "G13",
                   "H6", "H10", "I3", "I13", "K1", "K4", "K12", "K15", "L8", "N6", "N10", "O4", "O12"]
teleporteurs = {"C4": 1, "C12": 2, "F9": 3, "J7": 4, "M4": 5, "M12": 6}

tresors = [
    "1 Fragment d'AR",
    f"{random.choice ([3, 5, 7])} <:maxitomate:834025401646317598>",
    f"{random.choice ([2, 3, 5])} <:ruche:881123143614345247>"
    f"{random.choice([150, 200, 250, 300, 350])} points",
    "1 <:etoile:881111006225502228>",
    "2 <:boo:879445715653394492>",
    "1 <:eclair:880502378971926538>",
    "1 <:clairvoyance:880500461621346366>",
    "1 Parchemin qui dévoile un succès aléatoire"
    f"1 Artéfact qui infligera {random.choice([150, 200, 250, 300, 350])} points de dégats immédiatement au prochain boss que vous affronterez"
]

entites = {
    "Jevil" : "**Jevil** apparaît et mélange les objets entre les équipes !",
    "Cait Sith" : "**Cait Sith** vous surprend en lançant un dé à 6 faces.",
    "Vendeur d'armes" : "Le *Vendeur d'arme** vous approche et vous propose plusieurs objets, faites vos emplettes :",
    "Alphys" : "**Alphys** vous révèle qu'il a piraté le salon des Boss de la VGS et qu'il peut vous révéler un gimmick dans la liste de votre choix.",
    "Ogrim" : "Dans cette salle, **Ogrim** vous donne sa protection : Vous ne subirez **AUCUNE** perte de point durant la prochaine journée !",
    "Simone de Beauvoir" : "**Simone de Beauvoir** se trouve dans cette salle, vous obtenez 50 points supplémentaires par shiny pendant 1h.",
    "Capitaine Eudora" : "Voici la redoutable **Capitaine Eudora**, elle vous propose une quête et vous promets le double de la récompense si vous la terminez en 5jours !",
    "Mr Saturn" : "Oh ? Mr. Saturn ??",
    "Resh'an": "**Resh'an** se présente à vous et vous confronte à un choix crucial :",
    "Ekko" : "**Ekko** vous attend dans cette salle et vous êtes renvoyez au gimmick précédent pendant les 4 prochains jours.",
    "Aphrodite" : "Bienvenue dans la salle de relaxation d' **Aphrodite**, vos shiny valent le double pendant 1h. Tout le monde est au courant.",
    "Némésis" : "**KABOUM !!!** Il s'agit de **Némésis**, il fait perdre 1000 points à l’équipe en tête avec son lance-roquette",
    "Ellie" : "**Ellie** vous vient en aide, votre prochain <:fulgurorbe:834024958006394941> peut se relancer si raté.",
    "Godzilla" : "**ROOOOOOAR !!!** Vous entendez le rugissement de **Godzilla** au loin, cela fait perdre 750/500/250 points aux 3 équipes en tête.",
    "King Ghidorah" : "Vous vous retrouvez face à **King Ghidorah**, tous les Champinocifs du lendemain arriveront chez vous.",
    "Professeur Karl Tastroff" : "Le **Professeur Karl Tastroff** vous accueille et vous offre un **Fragment d'AR**, il vous annonce également que grâce à ses recherches, vous pourrez en fusionner 3 pour obtenir une AR défectueuse qui se transforme en objet doré aléatoire",
    "Malenia" : "**Malenia** se présente à vous et vous offre son pouvoir : vos 10 prochaines attaques vous rapportent 50 points",
    "Alan Grant" : "**Alan Grant** vous demande de l'aide pour ses fouilles archéologiques, il vous promet de doubler les points de vos 3 prochains shiny fossile mais sa machine ne permet pas d'utiliser des objets pour les renforcer",
    "Arsène Lupin" : "**Arsène Lupin** simule une Carapace Bleue et déclenchera des redistributions si un **Klaxon** est utilisé par au moins une des équipes normalement touchée.",
    "Robin des Bois" : "**Robin des Bois** vous vole toutes vos <:maxitomate:834025401646317598> et va les redistribuer à l’équipe en dernière position.",
    "Zero" : "**Zéro** fait ses calculs basés sur la racine numérique... En fonction du résultat, il vous vous offrira un bonus ou un malus sur vos prochains shiny.",
    "Carnibloc" : "Vous entrez dans la salle et faites face au **Carnibloc**, le prochain objet utilisé se lancera 3 fois."
}

boss_data = {
    "A8": {
        "nom": "Mithrix",
        "pv": 2000,
        "effet": "Désactive l’utilisation de **TOUS** vos objets tant que vous êtes en combat, à 50% de sa vie, débloque l’utilisation des <:maxitomate:834025401646317598>. Une fois vaincu, réactive tous les items de votre inventaire.",
        "recompense": "Le <:Recycleur:1387192788109492264> : 1 chance de pouvoir changer l'objet obtenu au tirage par un autre parmi ceux proposés."
    },
    "L14": {
        "nom": "Sora",
        "pv": 1000,
        "effet": "Désactive un salon déclaration (méthode ou FO) pour votre équipe, vous devrez lui infliger des dégâts avec des shiny de l’autre salon.",
        "recompense": "La <:Keyblade:1387192847115096096> : Permet de se déplacer de 2 cases en ligne droite sur le plateau et également de traverser les murs d'une case d'épaisseur."
    },
    "J9": {
        "nom": "Fatalis",
        "pv": 2500,
        "effet": "Vous perdez 10% de vos points toutes les 6h.",
        "recompense": "Le <:FatalisDemolisher:1387192912063889549> : Retire des points quotidiennement aux équipes adjacentes au classement."
    },
    "O8": {
        "nom": "The Company",
        "pv": "???",
        "effet": (
            "Vous choisissez un quota de points à atteindre en 3 jours parmi :\n"
            "- 1000 points | 500 bonus | -5% malus\n"
            "- 1750 points | 875 bonus | -7,5% malus\n"
            "- 2500 points | 1250 bonus | -10% malus\n"
            "Si réussi, vous obtenez les bonus et la récompense.\n"
            "Sinon, vous êtes éjectés et subissez un malus."
        ),
        "recompense": (
            "La <:CaisseEnregistreuse:1387192988450558064> : Stocke 150 points par jour, une fois déséquipé ou à la fin de la compétition, ajoute les points stockés au classement. "
            ":warning: Maximum 1500 points stockables :warning:"
        )
    },
    "F7": {
        "nom": "Gore Magala",
        "pv": 2000,
        "effet": "Tous les jours vous infligez 25% de dégâts en moins. Une fois vaincu, vous avez le choix d’affronter Shagaru Magala.",
        "recompense": (
            "Le <:SetGoreMagala:1387193061615996979> : Après avoir subi une attaque (shiny ou globale), votre prochain shiny voit ses points **doublés**."
        )
    },
    "D14": {
        "nom": "Princes Jumeaux",
        "pv": "1500 PV & 1000",
        "effet": (
            "Le premier Prince vous fait perdre 2% de points toutes les 3 heures. "
            "Le second vous offre un objet aléatoire à chaque fois que vous prenez des dégâts. "
            "Une fois le premier vaincu, plus de dégâts ni objets, mais vous devez battre le second pour obtenir la récompense."
        ),
        "recompense": "L' <:EpeePrincesJumeaux:1387193333784383498> : 1 chance d'obtenir un tirage supplémentaire et immunité aux Champinocifs."
    },
    "L2": {
        "nom": "Gladius",
        "pv": 1000,
        "effet": "Une fois vaincu, il se divise en 3 têtes qui se répandent dans 3 équipes aléatoires.",
        "recompense": "Les <:SouvenirsGladius:1387193412440166430> : Chaque jour, fait apparaître une tête de Gladius chez une équipe adverse."
    },
    "D2": {
        "nom": "La Horde de Freakers (x10)",
        "pv": 250,
        "effet": (
            "Lorsque vous les affrontez, vos chances de toucher diminuent :\n"
            "- ≤7 ennemis : 75%\n"
            "- ≤5 ennemis : 50%\n"
            "- ≤3 ennemis : 25%"
        ),
        "recompense": (
            "<:NapalmMolotov:1387194450937118841> : Vos objets offensifs ciblent 2 shiny de 2 équipes différentes.\n"
        )
    },
    "DRACULA": {
        "nom" : "Dracula",
        "pv" : 1200,
        "effet" : "Vous devrez le vaincre pour obtenir la récompense de Sora",
        "recompense" : "La <:Keyblade:1387192847115096096> : Permet de se déplacer de 2 cases en ligne droite sur le plateau et également de traverser les murs d'une case d'épaisseur.\n"
    },
    "shagaru_magala": {
        "nom": "Shagaru Magala",
        "pv": 2500,
        "effet": "Vous infligez 50% de dégâts en moins chaque jour.",
        "recompense": "<:SetChaoticGore:1387193125591584770> : Vous subissez 150% de dégâts mais votre prochain shiny rapporte x3."
    }
}

# Suivi des messages épinglés d'inventaire
messages_inventaire = {}

# Récompenses des boss (nom => emoji utilisé dans l’inventaire)
recompenses_boss = {
    "mithrix": "<:Recycleur:1387192788109492264>",
    "fatalis": "<:FatalisDemolisher:1387192912063889549>",
    "sora": "",
    "gladius": "<:SouvenirsGladius:1387193412440166430>",
    "princes_jumeaux": "<:EpeePrincesJumeaux:1387193333784383498>",
    "gore_magala": "<:SetGoreMagala:1387193061615996979>",
    "shagaru_magala": "<:SetChaoticGore:1387193125591584770>",
    "dracula": "<:Keyblade:1387192847115096096>",
    "company": "<:CaisseEnregistreuse:1387192988450558064>",
    "freakers": "<:NapalmMolotov:1387194450937118841>"
}

# Équipes
equipes = {
    "mha": {
        "nom": "MHA",
        "channel": "château-mha",
        "format": CellFormat(backgroundColor=color(0.44, 0.55, 0.45))  # vert foncé
    },
    "pkvt": {
        "nom": "PKVT",
        "channel": "château-pkvt",
        "format": CellFormat(backgroundColor=color(1.0, 0.66, 0.66))  # rose
    },
    "patp": {
        "nom": "PATP",
        "channel": "château-patp",
        "format": CellFormat(backgroundColor=color(0.61, 0.35, 0.71))  # violet
    },
    "unk": {
        "nom": "UNK",
        "channel": "château-unk",
        "format": CellFormat(backgroundColor=color(0.27, 0.55, 0.89))  # bleu
    },
    "smc": {
        "nom": "SMC",
        "channel": "château-smc",
        "format": CellFormat(backgroundColor=color(0.85, 0.16, 0.16))  # rouge
    },
    "rclg": {
        "nom": "RCLG",
        "channel": "château-rclg",
        "format": CellFormat(backgroundColor=color(0.14, 0.81, 0.29))  # vert clair
    }
}

evenement_tracker = {
    "mha": {"last_event": None, "since_event": 99},
    "pkvt": {"last_event": None, "since_event": 99},
    "patp": {"last_event": None, "since_event": 99},
    "unk": {"last_event": None, "since_event": 99},
    "smc": {"last_event": None, "since_event": 99},
    "rclg": {"last_event": None, "since_event": 99}
}
affrontement_tracker = {
    team: 99 for team in equipes
}

# Formattings spéciaux
format_blc = CellFormat(backgroundColor=color(1, 1, 1))
format_boss = CellFormat(backgroundColor=color(0.65, 0.11, 0), textFormat=TextFormat(bold=True, fontSize=12, foregroundColor=color(1, 1, 1)))
format_evenement = CellFormat(backgroundColor=color(0.71, 0.84, 0.66), textFormat=TextFormat(bold=True, fontSize=12, foregroundColor=color(1, 1, 1)))
format_tp = CellFormat(backgroundColor=color(0.50, 0.38, 0), textFormat=TextFormat(bold=True, fontSize=12, foregroundColor=color(1, 1, 1)))

# Positions initiales
positions = {
    "mha": "D14",
    "pkvt": "F4",
    "patp": "O1",
    "unk": "F15",
    "smc": "E12",
    "rclg": "K15"
}

def cell_to_coords(cell) :
    col = ord(cell[0].upper()) - ord('A')
    row = int(cell[1:]) - 1
    return (col, row)

def sont_adjacentes(c1: str, c2: str) -> bool:
    x1, y1 = cell_to_coords(c1)
    x2, y2 = cell_to_coords(c2)
    return abs(x1 - x2) + abs(y1 - y2) == 1

def get_team_from_channel(channel_name: str) -> str | None:
    for team, data in equipes.items():
        if data["channel"] == channel_name:
            return team
    return None

async def move_equipe(equipe: str, destination: str, forcer: bool = False, send_to_channel=None, allow_tp: bool = True):
    destination = destination.upper()

    if equipe not in positions:
        return f"🚫 Équipe inconnue : {equipe}."

    ancienne_case = positions[equipe]

    if not forcer and not sont_adjacentes(ancienne_case, destination):
        return f"🚫 {destination} est trop loin. Vous ne pouvez vous déplacer que d'une seule case."

    if destination in murs:
        return f"🚫 {destination} est un mur. Déplacement impossible."

    try:
        # --- Nettoyage de l'ancienne case ---
        equipes_restantes = [eq for eq, pos in positions.items() if pos == ancienne_case and eq != equipe]

        if equipes_restantes:
            contenu = " / ".join(sorted(e.upper() for e in equipes_restantes))
            sheet.update_acell(ancienne_case, contenu)

            if len(equipes_restantes) == 1:
                seule = equipes_restantes[0]
                format_cell_range(sheet, ancienne_case, equipes[seule]["format"])
            else:
                format_multi = CellFormat(backgroundColor=color(1, 1, 0.8))  # jaune pâle
                format_cell_range(sheet, ancienne_case, format_multi)

        else:
            if ancienne_case in boss_cases:
                sheet.update_acell(ancienne_case, "Boss")
                format_cell_range(sheet, ancienne_case, format_boss)
            elif ancienne_case in evenement_cases:
                sheet.update_acell(ancienne_case, "?")
                format_cell_range(sheet, ancienne_case, format_evenement)
            elif ancienne_case in teleporteurs:
                tp_index = teleporteurs[ancienne_case]
                sheet.update_acell(ancienne_case, f"TP{tp_index}")
                format_cell_range(sheet, ancienne_case, format_tp)
            else:
                sheet.update_acell(ancienne_case, "")
                format_cell_range(sheet, ancienne_case, format_blc)

        # --- Mettre à jour position ---
        positions[equipe] = destination

        # Récupère les équipes présentes sur la case
        equipes_sur_case = [eq for eq, pos in positions.items() if pos == destination]

        # Mise à jour de la cellule avec les noms des équipes
        valeur_cellule = "/".join(e.upper() for e in equipes_sur_case)
        sheet.update_acell(destination, valeur_cellule)

        # Applique un fond spécial si plusieurs équipes sur la case
        if len(equipes_sur_case) > 1:
            format_affrontement = CellFormat(backgroundColor=color(0.2, 0.2, 0.2))  # gris foncé
            format_cell_range(sheet, destination, format_affrontement)
        else:
            seul = equipes_sur_case[0]
            format_cell_range(sheet, destination, equipes[seul]["format"])

        # --- Réafficher les équipes présentes sur la nouvelle case ---
        equipes_presentes = [eq.upper() for eq, pos in positions.items() if pos == destination]
        if equipe.upper() not in equipes_presentes:
            equipes_presentes.append(equipe.upper())

        contenu_final = " / ".join(sorted(equipes_presentes))
        sheet.update_acell(destination, contenu_final)

        # Format équipe (ou multi)
        format_equipe = equipes.get(equipe, {}).get("format", format_blc)
        format_multi = CellFormat(backgroundColor=color(1, 1, 0.8))  # jaune pâle si plusieurs
        format_cell_range(sheet, destination, format_multi if len(equipes_presentes) > 1 else format_equipe)

        # Mise à jour des compteurs
        evenement_tracker[equipe]["since_event"] += 1
        affrontement_tracker[equipe] += 1

        # --- Affrontement si une autre équipe est présente ---
        for autre_equipe, pos in positions.items():
            if autre_equipe != equipe and pos == destination:
                other_channel_name = equipes[autre_equipe]["channel"]
                other_channel = discord.utils.get(send_to_channel.guild.text_channels, name=other_channel_name)

                if affrontement_tracker[equipe] >= 5 and affrontement_tracker[autre_equipe] >= 5:
                    await send_to_channel.send(f"⚔️ Affrontement déclenché contre {autre_equipe.upper()} !")
                    await other_channel.send(f"⚔️ {equipe.upper()} vous engage en combat !")
                    affrontement_tracker[equipe] = 0
                    affrontement_tracker[autre_equipe] = 0
                else:
                    await send_to_channel.send(f"🚫 Affrontement non déclenché avec {autre_equipe.upper()}, trop récent.")

        # --- Message selon la case ---
        if destination in boss_cases:
            boss = boss_data.get(destination, {
                "nom": "???",
                "pv": "???",
                "effet": "Effet inconnu...",
                "recompense": "Récompense inconnue."
            })
            msg = (
                f"⚔️ Vous entrez dans la salle du Boss, vous vous retrouvez face à :\n"
                f"**{boss['nom']} : {boss['pv']} PV**\n\n"
                f"**Effet** : {boss['effet']}\n\n"
                f"**Récompense** : {boss['recompense']}"
            )

        elif destination in evenement_cases:
            if evenement_tracker[equipe]["since_event"] < 3:
                msg = f"✅ {equipe.upper()} déplacé vers {destination}. (Zone déjà visitée récemment, aucun événement trouvé.)"
            else:
                type_event = random.choice(["tresor", "entite"])
                if type_event == "tresor":
                    tresor = random.choice(tresors)
                    msg = f"✅ {equipe.upper()} déplacé vers {destination}, vous découvrez un coffre contenant :\n**{tresor}**"

                else:
                    entite = random.choice(list(entites.keys()))
                    msg = f"✅ {equipe.upper()} déplacé vers {destination} et rencontre une entité :\n"

                    if entite == "Cait Sith":
                        roll = random.randint(1, 6)
                        msg += f"**Cait Sith** a lancé un dé et a obtenu : **{roll}**"
                    
                    elif entite == "Mr Saturn":
                        value = random.randint(1, 10)
                        msg += f"Il y'a quelques **Mr. Saturn** dispercés au sol, vous en trouvez **{value}"

                    elif entite == "Zero":
                        number = random.randint(1, 9)
                        msg += f"**Zero** a effectué ses calculs et vous révèle la racine numérique : **{number}**."

                    elif entite == "Vendeur d'armes":
                        msg += (
                            "- 10 <:maxitomate:834025401646317598> → **300 points**\n"
                            "- 10 <:ruche:881123143614345247> → **250 points**\n"
                            "- 3 <:grappin:881116285029728276> → **500 points**\n"
                            "- 2 <:fulgurorbe:834024958006394941> → **100 points**\n"
                            "- 1 <:etoile:881111006225502228> → **250 points**\n"
                            "- 1 <:klaxon:881120726487302174> → **500 points**\n"
                            "- 1 <:timetwister:1119755036847788032> → **1500 points**\n\n"
                        )

                    elif entite == "Resh'an":
                        msg += (
                            "**Resh'an** vous confronte à un choix :\n"
                            "1️⃣ Annuler toutes les attaques sur un shiny déjà validé\n"
                            "2️⃣ Gagner **10 objets aléatoires**\n"
                            "3️⃣ Empêcher toute attaque sur vos shiny pendant **12 heures**\n\n"
                            "Répondez avec la réaction correspondante."
                        )

                        prompt = await send_to_channel.send(msg)
                        await prompt.add_reaction("1️⃣")
                        await prompt.add_reaction("2️⃣")
                        await prompt.add_reaction("3️⃣")

                        def check_reshan(reaction, user):
                            return (
                                reaction.message.id == prompt.id and
                                str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣"] and
                                not user.bot
                            )

                        try:
                            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check_reshan)
                            choice = str(reaction.emoji)

                            if choice == "1️⃣":
                                await send_to_channel.send("✅ Vous avez choisi d’annuler toutes les attaques sur un shiny déjà validé.")

                            elif choice == "2️⃣":
                                objets_possibles = [
                                    "<:maxitomate:834025401646317598>", "<:ruche:881123143614345247>", "<:grappin:881116285029728276>", "<:fulgurorbe:834024958006394941>", "<:etoile:881111006225502228>",
                                    "<:boo:879445715653394492>", "<:picvenin:961550457585696818>", "<:clairvoyance:880500461621346366>", "<:paopou:1245497645561286767>", "<:fleurdegel:1246477202111860857>"
                                ]
                                obtenus = [random.choice(objets_possibles) for _ in range(10)]
                                inventaire_chateau[equipe]["disponibles"].extend(obtenus)

                                msg_id = messages_inventaire.get(equipe)
                                if msg_id:
                                    pinned = await send_to_channel.fetch_message(msg_id)
                                    await pinned.edit(content=afficher_inventaire(equipe))
                                
                                await send_to_channel.send("Vous avez reçu 10 objets :\n" + " ".join(obtenus))

                            elif choice == "3️⃣":
                                await send_to_channel.send("Vos shiny sont protégés pendant 12 heures.")

                        except asyncio.TimeoutError:
                            await send_to_channel.send("⌛ Temps écoulé. Resh'an s’est évaporé dans les airs.")
                        return ""  # Pas besoin de renvoyer un autre message

                    else:
                        msg += entites[entite]

                evenement_tracker[equipe]["since_event"] = 0

        else:
            msg = f"✅ {equipe.upper()} déplacé vers {destination}."

        # --- Téléporteur ---
        if allow_tp and destination in teleporteurs and send_to_channel:
            emoji_mapping = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
            tp_list = list(teleporteurs.keys())
            tp_emojis = dict(zip(emoji_mapping, tp_list))

            tp_msg = await send_to_channel.send("🌀 Vous arrivez sur un téléporteur. Choisissez une destination :")
            for emoji in tp_emojis:
                await tp_msg.add_reaction(emoji)

            def check(reaction, user):
                return (
                    reaction.message.id == tp_msg.id and
                    str(reaction.emoji) in tp_emojis and
                    not user.bot
                )

            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
                destination_tp = tp_emojis[str(reaction.emoji)]
                return await move_equipe(
                    equipe, destination_tp, forcer=True, send_to_channel=send_to_channel, allow_tp=False
                )
            except asyncio.TimeoutError:
                await send_to_channel.send("⌛ Temps écoulé. Téléportation annulée.")

        return msg

    except Exception as e:
        return f"⚠️ Une erreur s'est produite : {e}"
    

async def autocomplete_equipes(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=data["nom"], value=key)
        for key, data in equipes.items()
        if current.lower() in key.lower() or current.lower() in data["nom"].lower()
    ]

async def autocomplete_boss(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=key.capitalize(), value=key)
        for key in recompenses_boss.keys()
        if current.lower() in key.lower()
    ]

async def autocomplete_equipements(interaction: discord.Interaction, current: str):
    if not hasattr(interaction.namespace, "equipe"):
        return []

    equipe = interaction.namespace.equipe.lower()

    if equipe not in inventaire_chateau:
        return []

    disponibles = inventaire_chateau[equipe]["disponibles"]

    return [
        app_commands.Choice(name=emoji, value=emoji)
        for emoji in disponibles
        if current.lower() in emoji.lower()
    ]





# Lancement du bot
print("Lancement du bot...")
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot allumé !")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(e)

from discord import app_commands

@bot.tree.command(name="move", description="Déplace une équipe vers une case (réservé aux administrateurs).")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(equipe="Nom de l'équipe", case="Coordonnées de la case (ex: B3)")
@app_commands.autocomplete(equipe=autocomplete_equipes)
async def move(interaction: discord.Interaction, equipe: str, case: str):
    await interaction.response.defer()

    team = equipe.lower()
    destination = case.upper()

    if team not in equipes:
        await interaction.followup.send(f"🚫 Équipe inconnue : {equipe}")
        return

    # Récupération du salon dédié à l’équipe
    channel_name = equipes[team]["channel"]
    team_channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)

    if not team_channel:
        await interaction.followup.send(f"🚫 Salon introuvable pour l’équipe {team.upper()}.")
        return

    # Déplacement
    resultat = await move_equipe(team, destination, forcer=True, send_to_channel=team_channel)

    # Message dans le salon admin (celui où la commande a été exécutée)
    await interaction.followup.send(f"✅ {team.upper()} déplacé vers {destination} : Ce déplacement a couté 15 PM, n'oublie pas de les enlever de l'inventaire. 25 pour la patpitrouille <:kappa:485902802154029066>")

    # Message dans le salon de l’équipe concernée
    await team_channel.send(resultat)

def afficher_inventaire(team: str) -> str:
    inv = inventaire_chateau.get(team, {"actif": [], "disponibles": []})
    actif = inv["actif"]
    dispo = inv["disponibles"]

    actif_txt = "\n".join(actif) if actif else "_Aucun_"
    dispo_txt = "\n".join(dispo) if dispo else "_Aucun_"

    return (
        f"__**Inventaire {team.upper()}**__\n\n"
        f"**Équipement actif :**\n{actif_txt}\n\n"
        f"**Équipements disponibles :**\n{dispo_txt}"
    )


@bot.tree.command(name="inventory", description="Initialise l'inventaire pour une équipe")
@app_commands.describe(equipe="Nom de l'équipe")
@app_commands.autocomplete(equipe=autocomplete_equipes)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def inventory(interaction: discord.Interaction, equipe: str):
    team = equipe.lower()
    if team not in equipes:
        await interaction.response.send_message("🚫 Équipe inconnue.", ephemeral=True)
        return

    channel_name = equipes[team]["channel"]
    team_channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)

    if not team_channel:
        await interaction.response.send_message("🚫 Salon introuvable.", ephemeral=True)
        return

    inventaire_chateau[team] = {"actif": [], "disponibles": []}
    msg_txt = afficher_inventaire(team)
    msg = await team_channel.send(msg_txt)
    await msg.pin()
    messages_inventaire[team] = msg.id

    await interaction.response.send_message(f"📌 Inventaire initialisé et épinglé pour **{team.upper()}**.")

@bot.tree.command(name="victory", description="Enregistre la victoire contre un boss et ajoute la récompense.")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(equipe="Nom de l'équipe", boss="Nom du boss vaincu")
@app_commands.autocomplete(equipe=autocomplete_equipes, boss=autocomplete_boss)
async def victory(interaction: discord.Interaction, equipe: str, boss: str):
    team = equipe.lower()
    boss_key = boss.lower()

    if team not in equipes:
        await interaction.response.send_message("🚫 Équipe inconnue.", ephemeral=True)
        return

    if boss_key not in recompenses_boss:
        await interaction.response.send_message("🚫 Boss inconnu ou non enregistré.", ephemeral=True)
        return

    # Récupérer le salon d’équipe
    team_channel = discord.utils.get(interaction.guild.text_channels, name=equipes[team]["channel"])

    # ⚠️ Gestion spéciale pour Sora
    if boss_key == "sora":
        # Annonce de Dracula
        dracula_info = boss_data.get("DRACULA")
        if team_channel:
            await team_channel.send(
                f"**Dracula** est sorti de l'ombre de **Sora** !\n"
                f"**PV** : {dracula_info['pv']}\n"
                f"**Effet** : {dracula_info['effet']}\n"
                f"**Récompense** : {dracula_info['recompense']}"
            )
        await interaction.response.send_message("Dracula a été invoqué. Aucune récompense obtenue pour Sora.", ephemeral=True)
        return
    
    # Après avoir envoyé la récompense de Gore Magala
    if boss_key == "gore_magala":
        msg = (
            "Vous avez vaincu **Gore Magala** !\n\n"
            "⚠️ Souhaitez-vous affronter **Shagaru Magala** ?\n"
            "Il a **2500 PV** et vous inflige **-50% de dégâts** par jour.\n\n"
            "**Récompense** : *Set Chaotic Gore* – Subissez 150% de dégâts mais votre prochain shiny rapporte **x3**.\n"
            "✅ pour l'affronter | ❌ pour refuser."
        )
    
        prompt = await team_channel.send(msg)
        await prompt.add_reaction("✅")
        await prompt.add_reaction("❌")

        def check(reaction, user):
            return (
                reaction.message.id == prompt.id and
                str(reaction.emoji) in ["✅", "❌"] and
                not user.bot
            )

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) == "✅":
                shagaru = boss_data.get("shagaru_magala")
                intro = (
                    f"⚔️ **Shagaru Magala** apparaît !\n"
                    f"**PV** : {shagaru['pv']}\n"
                    f"**Effet** : {shagaru['effet']}\n"
                    f"**Récompense** : {shagaru['recompense']}"
                )
                await team_channel.send(intro)
            else:
                await team_channel.send("L’équipe a choisi de ne pas affronter **Shagaru Magala**.")
        except asyncio.TimeoutError:
            await team_channel.send("⌛ Temps écoulé. Le combat contre **Shagaru Magala** est annulé.")


    # Récupération de la récompense
    emoji = recompenses_boss[boss_key]
    if emoji in inventaire_chateau[team]["actif"] or emoji in inventaire_chateau[team]["disponibles"]:
        await interaction.response.send_message("⚠️ Récompense déjà ajoutée.", ephemeral=True)
        return

    # Ajouter à l’inventaire
    inventaire_chateau[team]["disponibles"].append(emoji)

    # Mise à jour du message épinglé
    msg_id = messages_inventaire.get(team)
    if not team_channel or not msg_id:
        await interaction.response.send_message("⚠️ Inventaire non initialisé ou message introuvable.", ephemeral=True)
        return

    try:
        pinned_msg = await team_channel.fetch_message(msg_id)
        await pinned_msg.edit(content=afficher_inventaire(team))
        await team_channel.send(f"🏆 Boss **{boss.capitalize()}** vaincu ! {emoji} ajouté à l'inventaire.")
        await interaction.response.send_message("✅ Récompense enregistrée.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erreur : {e}", ephemeral=True)



@bot.tree.command(name="equip", description="Change l'équipement actif d'une équipe.")
@app_commands.describe(equipe="Nom de l'équipe", objet="Nom de l'équipement (emoji complet)")
@app_commands.autocomplete(equipe=autocomplete_equipes, objet=autocomplete_equipements)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def equip(interaction: discord.Interaction, equipe: str, objet: str):
    team = equipe.lower()

    if team not in inventaire_chateau:
        await interaction.response.send_message("🚫 Équipe inconnue.", ephemeral=True)
        return

    # Vérifie que l’objet est bien dans les équipements disponibles
    if objet not in inventaire_chateau[team]["disponibles"]:
        await interaction.response.send_message(f"🚫 Objet {objet} non disponible dans l'inventaire.", ephemeral=True)
        return

    # Déplacement entre les listes
    ancien = inventaire_chateau[team]["actif"]
    inventaire_chateau[team]["actif"] = [objet]

    if ancien:
        inventaire_chateau[team]["disponibles"].append(ancien[0])
    inventaire_chateau[team]["disponibles"].remove(objet)

    team_channel = discord.utils.get(interaction.guild.text_channels, name=equipes[team]["channel"])
    msg_id = messages_inventaire.get(team)

    if not team_channel or not msg_id:
        await interaction.response.send_message("⚠️ Message d'inventaire introuvable.", ephemeral=True)
        return

    msg = await team_channel.fetch_message(msg_id)
    await msg.edit(content=afficher_inventaire(team))
    await interaction.response.send_message(f"✅ {objet} est maintenant l'équipement actif de **{team.upper()}**.")


bot.run(os.getenv("DISCORD_TOKEN"))