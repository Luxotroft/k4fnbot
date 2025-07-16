import discord
import time
import re
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import os
import random
from discord.ui import Button, View, Select
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

# ====================================================================
# --- 1. CONFIGURACIÓN E INSTANCIA DEL BOT ALBION ---
# ====================================================================

# Habilitar intents necesarios para el bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Necesario para obtener miembros del guild

# Crear la única instancia del bot. Soporta prefijo (!) y slash commands.
bot = commands.Bot(command_prefix="!", intents=intents)

# ====================================================================
# --- 2. VARIABLES GLOBALES Y ESTRUCTURAS DE DATOS ---
# ====================================================================

# --- Datos para World Boss (WB) ---
WB_BOSS_DATA = {
    "elder": {
        "name": "Eldersleep",
        "roles": {
            "Main Tank": 1, "Off Tank": 1, "Main Healer": 1, "Gran Arcano": 1,
            "Prisma": 2, "Invocador Oscuro (SC)": 1, "Flamígero": 1,
            "Light Caller (LC)": 1, "Montura Rinoceronte": 1,
            "Scout - Adelante": 1, "Scout - Atrás": 1, "Scout Patrol": 2,
        },
        "emojis": {
            "Main Tank": "<:Incubo:1290858544488386633>", "Off Tank": "<:stoper:1290858463135662080>",
            "Main Healer": "<:Santificador:1290858870260109384>", "Gran Arcano": "<:GranArcano:1337861969931407411>",
            "Prisma": "<:Prisma:1367151400672559184>", "Invocador Oscuro (SC)": "<:InvocadorOscuro:1290880853353955338>",
            "Flamígero": "<:BLAZING:1357789213558439956>", "Light Caller (LC)": "<:LIGHT_CALLER:1357788956137226361>",
            "Montura Rinoceronte": "<:MonturaMana:1337863658859925676>", "Scout - Adelante": "<:Lecho:1337861780780875876>",
            "Scout - Atrás": "<:Lecho:1337861780780875876>", "Scout Patrol": "<:Lecho:1337861780780875876>",
        },
        "default_description": (
            "**💀 Eldersleep — Zona Negra**\n"
            "📢 Prioridad para usuarios mencionados\n\n"
            "📜 **Reglas del contenido:**\n"
            "▸ Todos los roles llevan bastón para revivir\n"
            "▸ Arma t9 / ropa t8 equivalente\n"
            "▸ Armas 4.4 permitidas con el requisito de tener 10% de daño\n"
            "▸ Tiempo mínimo de duración = {duration}\n"
            "▸ Llevar comidas .1\n"
            "@everyone"
        )
    },
    "eye": {
        "name": "Eye of the Forest",
        "roles": {
            "Main Tank": 1, "Off Tank": 1, "Main Healer": 1, "Gran Arcano": 1,
            "Prisma": 2, "Invocador Oscuro (SC)": 1, "Flamígero": 1,
            "Light Caller (LC)": 1, "Montura Rinoceronte": 1,
            "Scout - Adelante": 1, "Scout - Atrás": 1, "Scout Patrol": 2,
        },
        "emojis": {
            "Main Tank": "<:Incubo:1290858544488386633>", "Off Tank": "<:stoper:1290858463135662080>",
            "Main Healer": "<:Santificador:1290858870260109384>", "Gran Arcano": "<:GranArcano:1337861969931407411>",
            "Prisma": "<:Prisma:1367151400672559184>", "Invocador Oscuro (SC)": "<:InvocadorOscuro:1290880853353955338>",
            "Flamígero": "<:BLAZING:1357789213558439956>", "Light Caller (LC)": "<:LIGHT_CALLER:1357788956137226361>",
            "Montura Rinoceronte": "<:MonturaMana:1337863658859925676>", "Scout - Adelante": "<:Lecho:1337861780780875876>",
            "Scout - Atrás": "<:Lecho:1337861780780875876>", "Scout Patrol": "<:Lecho:1337861780780875876>",
        },
        "default_description": (
            "**👁️ Eye of the Forest — Zona Negra**\n"
            "📢 Prioridad para usuarios mencionados\n\n"
            "📜 **Reglas del contenido:**\n"
            "▸ Todos los roles llevan bastón para revivir\n"
            "▸ Arma t9 / ropa t8 equivalente\n"
            "▸ Armas 4.4 permitidas con el requisito de tener 10% de daño\n"
            "▸ Tiempo mínimo de duración = {duration}\n"
            "▸ Llevar comidas .1\n"
            "@everyone"
        )
    }
}
wb_events = {} # {event_id: {data}}
wb_priority_users = {} # {event_id: {"users": [], "expiry": timestamp, "slots": int}}
WB_EVENT_TIMEOUT = 7200 # 2 horas

# --- Datos para Roaming Parties ---
ROAMING_PARTIES = {
    "kiteo1": {
        "max_players": 20,
        "roles": {
            "HOJ": 1, "PESADA": 1, "LECHO PEEL": 1, "LECHO SUP": 1, "GA": 1, "LOCUS": 1,
            "JURADORES": 1, "ENRAIZADO": 1, "LIFECURSED": 1, "OCULTO": 1, "ROMPERREINO": 1,
            "CAZAESPÍRITUS": 1, "FISURANTE": 2, "PRISMA": 1, "PUAS": 1, "SANTI": 3,
            "FORJACORTEZA": 1,
        },
        "emojis": {
            "HOJ": "<:ManodeJusticia:1290858364129247242>", "PESADA": "<:stoper:1290858463135662080>",
            "LECHO PEEL": "<:stoper:1290858463135662080>", "LECHO SUP": "<:stoper:1290858463135662080>",
            "GA": "<:GranArcano:1337861969931407411>", "LOCUS": "<:Locus:1291467422238249043>",
            "JURADORES": "<:Maracas:1290858583965175828>", "ENRAIZADO": "<:Enraizado:1290879541073678397>",
            "LIFECURSED": "<:Maldi:1291467716229730415>", "OCULTO": "<:Oculto:1337862058779218026>",
            "ROMPERREINO": "<:RompeReino:1290881352182399017>", "CAZAESPÍRITUS": "<:Cazaespiritu:1290881433816137821>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "PRISMA": "<:Prisma:1367151400672559184>",
            "PUAS": "<:Puas:1291468593506029638>", "SANTI": "<:Santificador:1290858870260109384>",
            "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
        }
    },
    "kiteo2": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "MARTILLO": 1, "1HARCANO": 1, "GA": 1, "LOCUS": 1, "JURADORES": 1, "LOCUS_OFENSIVO": 1,
            "CANCION": 1, "CARAMBANOS": 1, "DAMNATION": 1, "LIFECURSED": 1, "PUTREFACTO": 1,
            "OCULTO": 1, "WITCHWORD": 1, "FISURANTE": 1, "PRISMA": 1, "FORJACORTEZA": 1, "SANTI": 3, "TORRE_MOVIL": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "MARTILLO": "<:stoper:1290858463135662080>", "1HARCANO": "<:Arcano:1297064938531196959>",
            "GA": "<:GranArcano:1337861969931407411>", "LOCUS": "<:Locus:1291467422238249043>",
            "JURADORES": "<:Maracas:1290858583965175828>", "LOCUS_OFENSIVO": "<:Locus:1291467422238249043>",
            "CANCION": "<:Canciondedespertar:1291635941240213574>", "CARAMBANOS": "<:caram:1384931326968463372>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "LIFECURSED": "<:Maldi:1291467716229730415>",
            "PUTREFACTO": "<:Putrefacto:1370577320171016202>", "OCULTO": "<:Oculto:1337862058779218026>",   "WITCHWORD": "<:witchword:1392942341815533758>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "PRISMA": "<:Prisma:1367151400672559184>", "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
            "SANTI": "<:Santificador:1290858870260109384>", "TORRE_MOVIL": "<:MonturaMana:1337863658859925676>",
        }
    },
    "brawl": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1,
            "PESADA": 1,
            "MONARCA": 1,
            "MARTILLO 1 H / EQUILIBRIO": 1,
            "JURADORES": 1,
            "LIFECURSED": 1,
            "LOCUS": 1,
            "GARZA / PUTREFACTO": 1,
            "TALLADA / CAZAESPIRITUS": 1,
            "DAMNATION": 1,
            "ROMPERREINOS": 1,
            "ASTRAL": 1,
            "DEMONFANG": 1,
            "FALCE/ GUADAÑA": 1,
            "HOJA INFINITA": 2,
            "SANTI": 3,
            "INFORTUNIO": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>",
            "PESADA": "<:stoper:1290858463135662080>",
            "MONARCA": "😈",
            "MARTILLO 1 H / EQUILIBRIO": "🔨",
            "JURADORES": "<:Maracas:1290858583965175828>",
            "LIFECURSED": "<:Maldi:1291467716229730415>",
            "LOCUS": "<:Locus:1291467422238249043>",
            "GARZA / PUTREFACTO": "<:Putrefacto:1370577320171016202>",
            "TALLADA / CAZAESPIRITUS": "<:Cazaespiritu:1290881433816137821>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>",
            "ROMPERREINOS": "<:RompeReino:1290881352182399017>",
            "ASTRAL": "<:Astral:1334556937328525413>",
            "DEMONFANG": "👹",
            "FALCE/ GUADAÑA": "<:Guadaa:1291468660917014538>",
            "HOJA INFINITA": "⚔️",
            "SANTI": "<:Santificador:1290858870260109384>",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>",
        }
    },
    "brawl2": {
        "max_players": 20,
        "roles": {
            "Maza pesada": 1,
            "Martillo de una mano": 1,
            "Baston de equilibrio": 1,
            "Santificador": 3,
            "Infortunio": 1,
            "Juradores": 1,
            "Silvano": 1,
            "Romperreinos": 1,
            "Putrefacto": 1,
            "Tallada": 1,
            "Astral": 1,
            "Patas de oso": 1,
            "Hoja infinita": 3,
            "Colmillo": 1,
            "Guadaña": 1,
            "Puas": 1
        },
        "emojis": {
            "Maza pesada": "<:stoper:1290858463135662080>",
            "Martillo de una mano": "<:CALLER:1367141230596853761>",
            "Baston de equilibrio": "<:Equilibrado:1291466491803471933>",
            "Santificador": "<:Hallowfall:1361429140460539973>",
            "Infortunio": "<:Infortunio:1290858784528531537>",
            "Juradores": "<:Maracas:1290858583965175828>",
            "Silvano": "<:Enraizado:1290879541073678397>",
            "Romperreinos": "<:RompeReino:1290881352182399017>",
            "Putrefacto": "<:Putrefacto:1370577320171016202>",
            "Tallada": "<:Tallada:1290881286092886172>",
            "Astral": "<:Astral:1334556937328525413>",
            "Patas de oso": "<:PatasDeOso:1272599457778630737>",
            "Hoja infinita": "⚔️",
            "Colmillo": "<:Colmillo:1370577697516032031>",
            "Guadaña": "<:Guadaa:1291468660917014538>",
            "Puas": "<:Puas:1291468593506029638>"
        }
    },
    "brawl_gucci": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "PESADA": 1, "PESADA PEEL": 1, "GA": 1, "LOCUS": 1, "JURADORES": 1,
            "ENRAIZADO": 1, "DAMNATION": 1, "LIFECURSED": 1, "PUTREFACTO": 1, "ROMPERREINO": 1,
            "CAZAESPÍRITUS": 1, "HOJA INFINITA": 1, "ASTRAL": 1, "ZARPAS": 1, "INFERNALES": 1,
            "INFORTUNIO": 1, "SANTI": 3,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "PESADA": "<:stoper:1290858463135662080>",
            "PESADA PEEL": "<:stoper:1290858463135662080>", "GA": "<:GranArcano:1337861969931407411>",
            "LOCUS": "<:Locus:1291467422238249043>", "JURADORES": "<:Maracas:1290858583965175828>",
            "ENRAIZADO": "<:Enraizado:1290879541073678397>", "DAMNATION": "<:Maldiciones:1337862954820829294>",
            "LIFECURSED": "<:Maldi:1291467716229730415>", "PUTREFACTO": "<:Putrefacto:1370577320171016202>",
            "ROMPERREINO": "<:RompeReino:1290881352182399017>", "CAZAESPÍRITUS": "<:Cazaespiritu:1290881433816137821>",
            "HOJA INFINITA": "<:Guadaa:1291468660917014538>", "ASTRAL": "<:Astral:1334556937328525413>",
            "ZARPAS": "<:Zarpas:1334560618941911181>", "INFERNALES": "<:Infernales:1338344041598812180>",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>", "SANTI": "<:Santificador:1290858870260109384>",
        }
    },
    "pocho": { # New roaming composition
        "max_players": 20,
        "roles": {
            "GOLEM": 1,
            "PESADA": 2,
            "MARTILLO 1 H": 1,
            "JURADORES": 1,
            "LIFECURSED": 1,
            "LOCUS / ENRAIZADO": 1,
            "GARZA": 1,
            "TALLADA / CAZAESPIRITUS": 1,
            "DAMNATION": 1,
            "ROMPERREINOS": 1,
            "DEMONFANG": 2,
            "GUADAÑA": 1,
            "INFERNALES": 2,
            "GRAN BASTON SAGRADO": 2,
            "REDENCION": 1,
            "INFORTUNIO": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>",
            "PESADA": "<:stoper:1290858463135662080>",
            "MARTILLO 1 H": "🔨",
            "JURADORES": "<:Maracas:1290858583965175828>",
            "LIFECURSED": "<:Maldi:1291467716229730415>",
            "LOCUS / ENRAIZADO": "<:Locus:1291467422238249043>",
            "GARZA": "🐦",
            "TALLADA / CAZAESPIRITUS": "<:Cazaespiritu:1290881433816137821>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>",
            "ROMPERREINOS": "<:RompeReino:1290881352182399017>",
            "DEMONFANG": "👹",
            "GUADAÑA": "<:Guadaa:1291468660917014538>",
            "INFERNALES": "<:Infernales:1338344041598812180>",
            "GRAN BASTON SAGRADO": "✨",
            "REDENCION": "✨",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>",
        }
    }
}

roaming_events = {} # {event_id: {data}}
roaming_generic_counter = 0
ROAMING_EVENT_TIMEOUT = 7200 # 2 horas

cta_events = {} # Nuevo diccionario para eventos CTA
CTA_EVENT_TIMEOUT = 7200 # 2 horas

# ====================================================================
# --- 3. FUNCIONES HELPER ---
# ====================================================================

# --- Helper de Roaming ---
def get_roaming_caller_info(ctx, args):
    """
    Determina el nombre del caller a mostrar en el embed de forma flexible.
    Asume que el último argumento de *args es el nombre del caller.
    """
    if args:
        # Si el último argumento no es un número ni 'si'/'no', lo considera el caller.
        last_arg = args[-1].lower()
        if not last_arg.isdigit() and last_arg not in ('si', 'sí', 'no', 'n', 'y', 'yes'):
            return args[-1]
    return ctx.author.display_name # Asume que el caller es el que envía el comando

def create_roaming_embed(party, event_data):
    """Genera el mensaje embed para el evento de roaming."""
    embed = discord.Embed(
        title=f"🚀 ROAMING {party.upper()} (Caller: {event_data['caller_display']})",
        description=f"**📍 Salimos de Fort Sterling Portal**\nTier: {event_data['tier_min']} | IP: {event_data['ip_min']}+",
        color=0x00ff00 if "kiteo" in party else 0xFF0000
    )

    total_inscritos = sum(len(players) for players in event_data["inscripciones"].values())
    embed.set_footer(text=f"📊 {total_inscritos}/{ROAMING_PARTIES[party]['max_players']} jugadores | ID: {event_data['event_id']}")

    # Agrega la hora si está presente
    if event_data.get("time"):
        # Agregamos 'UTC' al final de la hora si no lo tiene.
        display_time = event_data["time"]
        if not display_time.upper().endswith('UTC'):
            display_time += ' UTC'
        embed.add_field(name="⏰ Hora de Salida", value=display_time, inline=True)
    
    # Agrega la información de swap de gank
    swap_status = "✅ **Sí**" if event_data.get("swap_gank") else "❌ **No**"
    embed.add_field(name="⚔️ Swap de Gank", value=swap_status, inline=True)
    
    # Lista de roles
    lineas_roles = []
    for rol, limite in ROAMING_PARTIES[party]["roles"].items():
        inscritos = event_data["inscripciones"].get(rol, [])
        waitlist_players = event_data["waitlist"].get(rol, []) # Obtiene la lista de espera
        emoji = ROAMING_PARTIES[party]["emojis"].get(rol, "")
        slots = f"{len(inscritos)}/{limite}"
        jugadores = ' '.join(f'<@{uid}>' for uid in inscritos[:3])
        if len(inscritos) > 3:
            jugadores += f" (+{len(inscritos)-3} más)"

        linea = f"{emoji} **{rol.ljust(15)}** {slots.rjust(5)} → {jugadores or '🚫'}"
        if waitlist_players:
            jugadores_espera = ' '.join(f'<@{uid}>' for uid in waitlist_players)
            linea += f" | ⏳ Espera: {jugadores_espera}"

        lineas_roles.append(linea)

    # Dividir en campos
    for i in range(0, len(lineas_roles), 8):
        embed.add_field(
            name="🎮 ROLES DISPONIBLES" if i == 0 else "↳ Continuación",
            value="\n".join(lineas_roles[i:i+8]),
            inline=False
        )

    reglas = (
        f"▸ Tier mínimo: **{event_data['tier_min']}**\n"
        f"▸ IP mínima: **{event_data['ip_min']}+**\n"
        "▸ Traer **embotelladas y comida**\n"
        "▸ **Escuchar calls** y no flamear\n"
        f"▸ {'🔔 @everyone' if total_inscritos < 15 else '🚨 SOBRECUPO!'}"
    )

    embed.add_field(name="📜 REGLAS DEL ROAMING", value=reglas, inline=False)
    return embed

async def update_wb_embed(event_id):
    if event_id not in wb_events:
        return

    event = wb_events[event_id]
    boss = event["boss"]
    message = event["message"]

    if not message:
        return

    try:
        embed = message.embeds[0].copy()
        embed.clear_fields()

        is_disabled = False
        footer_text = ""
        embed_color = 0x8B0000

        if event.get("priority_mode", False):
            priority_data = wb_priority_users.get(event_id)
            if priority_data and time.time() < priority_data["expiry"]:
                time_left = int(priority_data["expiry"] - time.time())
                minutes_left = max(0, time_left // 60)
                seconds_left = max(0, time_left % 60)

                embed.description = (
                    f"{event['description']}\n\n"
                    f"🎯 **Sistema de Prioridad Activo**\n"
                    f"⏳ **Tiempo restante:** {minutes_left}m {seconds_left}s\n"
                    f"👥 **Usuarios prioritarios:** {', '.join([f'<@{uid}>' for uid in priority_data['users']])}\n"
                    f"📊 **Slots usados:** {len(priority_data['users'])}/{priority_data['slots']}"
                )
                is_disabled = True # Se deshabilita para no-prioritarios
                footer_text = "🔒 Solo usuarios prioritarios pueden anotarse"
                embed_color = 0xFF4500
            else:
                event["priority_mode"] = False
                is_disabled = False
                footer_text = "🔓 Todos pueden anotarse"
                embed.description = event["description"]
                if event_id in wb_priority_users:
                    del wb_priority_users[event_id]
        else:
            is_disabled = False
            footer_text = "🔓 Todos pueden anotarse"
            embed_color = 0x00FF00
            embed.description = event["description"]

        embed.set_footer(text=footer_text)
        embed.color = embed_color

        for role in WB_BOSS_DATA[boss]["roles"]:
            players = ", ".join([f"<@{uid}>" for uid in event["inscriptions"][role]])
            waitlist_players = ", ".join([f"<@{uid}>" for uid in event["waitlist"][role]])

            role_status = ""
            if players:
                role_status += f"👥 {players}"
            if waitlist_players:
                role_status += f"\n⏳ Espera: {waitlist_players}"

            if not role_status:
                role_status = "🚫 Vacío"

            embed.add_field(
                name=f"{WB_BOSS_DATA[boss]['emojis'].get(role)} {role} ({len(event['inscriptions'][role])}/{WB_BOSS_DATA[boss]['roles'][role]} +{len(event['waitlist'][role])} en espera)",
                value=role_status,
                inline=False
            )

        view = WB_RoleSelectorView(boss, event_id, event["caller_id"], disabled=is_disabled) # NOTA: Se crea una nueva vista en cada actualización
        await message.edit(embed=embed, view=view)

    except Exception as e:
        print(f"Error actualizando embed para el evento {event_id}: {e}")

# --- Helper de CTA ---
def create_cta_embed(event_data):
    """Genera el mensaje embed para el evento CTA (Pelea Obligatoria)."""
    embed = discord.Embed(
        title=f"🚨 ¡PELEA OBLIGATORIA! - Hora de Masseo: {event_data['mass_time']} UTC 🚨",
        description="¡Pense en ello como el preaviso para la proxima gran aventura. Anotate en el rol que te corresponda.",
        color=0xFF0000
    )
    embed.set_thumbnail(url="https://assets.albiononline.com/assets/images/icons/faction_standings_martlock.png")

    # Información de Kiteo Onda 1
    party1_name = "kiteo1"
    if party1_name in ROAMING_PARTIES:
        party1_data = ROAMING_PARTIES[party1_name]
        roles_str_1 = []
        current_insc_1 = event_data["inscripciones"].get(party1_name, {})
        current_wait_1 = event_data["waitlist"].get(party1_name, {})
        
        for rol, limite in party1_data["roles"].items():
            emoji = party1_data["emojis"].get(rol, "")
            inscritos = current_insc_1.get(rol, [])
            waitlist_players = current_wait_1.get(rol, [])
            
            jugadores_insc = ' '.join(f'<@{uid}>' for uid in inscritos)
            jugadores_wait = ' '.join(f'<@{uid}>' for uid in waitlist_players)

            linea = f"{emoji} **{rol}** ({len(inscritos)}/{limite})"
            if jugadores_insc:
                linea += f" → {jugadores_insc}"
            if jugadores_wait:
                linea += f" | ⏳ Espera: {jugadores_wait}"
            roles_str_1.append(linea)
        
        embed.add_field(
            name=f"🚀 COMPOSICIÓN KITE ONDA 1 ({sum(len(current_insc_1.get(r,[])) for r in party1_data['roles'])}/{party1_data['max_players']})",
            value="\n".join(roles_str_1) or "Roles no definidos.",
            inline=False # Para que ocupe toda la línea y se vea mejor
        )
    else:
        embed.add_field(name="🚀 COMPOSICIÓN KITE ONDA 1", value="Datos no disponibles.", inline=False)

    # Información de Kiteo Onda 2
    party2_name = "kiteo2"
    if party2_name in ROAMING_PARTIES:
        party2_data = ROAMING_PARTIES[party2_name]
        roles_str_2 = []
        current_insc_2 = event_data["inscripciones"].get(party2_name, {})
        current_wait_2 = event_data["waitlist"].get(party2_name, {})

        for rol, limite in party2_data["roles"].items():
            emoji = party2_data["emojis"].get(rol, "")
            inscritos = current_insc_2.get(rol, [])
            waitlist_players = current_wait_2.get(rol, [])

            jugadores_insc = ' '.join(f'<@{uid}>' for uid in inscritos)
            jugadores_wait = ' '.join(f'<@{uid}>' for uid in waitlist_players)

            linea = f"{emoji} **{rol}** ({len(inscritos)}/{limite})"
            if jugadores_insc:
                linea += f" → {jugadores_insc}"
            if jugadores_wait:
                linea += f" | ⏳ Espera: {jugadores_wait}"
            roles_str_2.append(linea)
        
        embed.add_field(
            name=f"🌪️ COMPOSICIÓN KITE ONDA 2 ({sum(len(current_insc_2.get(r,[])) for r in party2_data['roles'])}/{party2_data['max_players']})",
            value="\n".join(roles_str_2) or "Roles no definidos.",
            inline=False # Para que ocupe toda la línea
        )
    else:
        embed.add_field(name="🌪️ COMPOSICIÓN KITE ONDA 2", value="Datos no disponibles.", inline=False)
    
    embed.add_field(
        name="\u200b", 
        value="¡Todos los miembros deben presentarse y seguir las indicaciones! @everyone",
        inline=False
    )
    
    embed.set_footer(text=f"Evento creado por: {bot.get_user(event_data['caller_id']).display_name if bot.get_user(event_data['caller_id']) else 'Desconocido'} | ID: {event_data['event_id']}")
    embed.timestamp = datetime.utcnow()
    return embed

async def update_cta_embed(event_id):
    if event_id not in cta_events:
        return

    event = cta_events[event_id]
    message = event["message"]

    if not message:
        return

    try:
        embed = create_cta_embed(event)
        view = CTAEventView(event_id, event["caller_id"], event)
        await message.edit(embed=embed, view=view)
    except Exception as e:
        print(f"Error actualizando embed para el evento CTA {event_id}: {e}")

# ====================================================================
# --- 4. CLASES DE UI (VIEWS, BUTTONS, SELECTS) ---
# ====================================================================

# --- Clases para World Boss (WB) ---
class WB_RoleSelectorView(discord.ui.View):
    def __init__(self, boss, event_id, caller_id, disabled=False):
        super().__init__(timeout=None)
        self.caller_id = caller_id
        self.event_id = event_id
        self.add_item(WB_RoleDropdown(boss, event_id, disabled))
        self.add_item(WB_LeaveButton(event_id))
        self.add_item(WB_JoinWaitlistMainButton(boss, event_id))

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", row=1)
    async def close_event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Verificar si el usuario que presiona el botón es el caller original
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)

        # 2. Verificar si el evento sigue activo
        if self.event_id not in wb_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        # 3. Obtener el hilo asociado
        thread = interaction.message.thread
        
        # 4. MODIFICACIÓN CLAVE: Eliminar el hilo de forma segura
        if thread:
            try:
                # Paso 1: Desarchivar el hilo si está archivado.
                if thread.archived:
                    await thread.edit(archived=False, reason="Desarchivando para eliminar")
                
                # Paso 2: Eliminar el hilo.
                await thread.delete()
                print(f"Hilo del evento WB {self.event_id} eliminado correctamente.")
            except discord.NotFound:
                print(f"El hilo del evento WB {self.event_id} ya no existe.")
            except discord.Forbidden:
                print(f"Error: El bot no tiene el permiso 'Manage Threads' o 'Manage Channels' para eliminar el hilo del evento WB {self.event_id}.")
            except Exception as e:
                print(f"Error inesperado al eliminar el hilo del evento WB {self.event_id}: {e}")
        else:
            print("No se encontró un hilo asociado al mensaje del evento WB.")

        # 5. Eliminar el mensaje principal
        try:
            # Usa interaction.message.delete() para borrar el mensaje que contiene el embed y los botones.
            await interaction.message.delete()
            print(f"Mensaje del evento WB {self.event_id} eliminado correctamente.")
        except discord.Forbidden:
            print(f"Error: El bot no tiene el permiso 'Manage Messages' para eliminar el mensaje del evento WB {self.event_id}.")
            # Si no puede borrar el mensaje, desactiva la vista y notifica.
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("✅ Evento cerrado, pero no pude borrar el mensaje (permisos faltantes).", ephemeral=True)
        except Exception as e:
            print(f"Error inesperado al eliminar el mensaje del evento WB {self.event_id}: {e}")
            # Si no puede borrar el mensaje, desactiva la vista y notifica.
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("❌ Ocurrió un error al intentar eliminar el mensaje.", ephemeral=True)
            
        # 6. Eliminar el evento del diccionario global
        del wb_events[self.event_id]

        # 7. Responde a la interacción. Como ya borraste el mensaje,
        # solo puedes enviar una respuesta de seguimiento.
        await interaction.response.send_message(f"✅ Evento de World Boss cerrado y eliminado.", ephemeral=True)

class WB_RoleDropdown(discord.ui.Select):
    def __init__(self, boss, event_id, disabled=False):
        self.boss = boss
        self.event_id = event_id
        options = [
            discord.SelectOption(
                label=role,
                emoji=WB_BOSS_DATA[boss]["emojis"].get(role),
                description=f"0/{WB_BOSS_DATA[boss]["roles"][role]}"
            ) for role in WB_BOSS_DATA[boss]["roles"]
        ]
        super().__init__(
            placeholder="Elige tu rol",
            options=options,
            max_values=1,
            disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        # MODIFICACIÓN: Defer la respuesta para evitar el timeout
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in wb_events:
            return await interaction.followup.send("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]
        role = self.values[0]

        # Check if user is already in any role or waitlist for this event
        for existing_role, users in event["inscriptions"].items():
            if interaction.user.id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás inscrito como **{existing_role}**. Usa el botón 'Salir de Rol' primero.",
                    ephemeral=True
                )
        for existing_role, users in event["waitlist"].items():
            if interaction.user.id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás en la lista de espera para **{existing_role}**. Usa el botón 'Salir de Rol' primero.",
                    ephemeral=True
                )

        # Priority check
        if event["priority_mode"]:
            priority_data = wb_priority_users.get(self.event_id)
            is_caller = (interaction.user.id == event["caller_id"])

            if (priority_data and time.time() < priority_data["expiry"] and 
                interaction.user.id not in priority_data["users"] and not is_caller):
                expiry_time = priority_data["expiry"] if priority_data else 0
                return await interaction.followup.send(
                    f"🔒 **Solo usuarios prioritarios pueden anotarse ahora.**\n"
                    f"⏳ El bloqueo termina: <t:{int(expiry_time)}:R>",
                    ephemeral=True
                )

            if priority_data and time.time() >= priority_data["expiry"]:
                event["priority_mode"] = False
                await update_wb_embed(self.event_id)

        # Check if role is full for main inscription
        if len(event["inscriptions"][role]) >= WB_BOSS_DATA[self.boss]["roles"][role]:
            return await interaction.followup.send("❌ Este rol ya está lleno. Usa el botón 'Unirse a Lista de Espera' si deseas esperar un slot.", ephemeral=True)

        # Inscribe user
        event["inscriptions"][role].append(interaction.user.id)
        await interaction.followup.send(f"✅ Te has unido como **{role}**", ephemeral=True)
        await update_wb_embed(self.event_id)

class WB_LeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salir de Rol", style=discord.ButtonStyle.red, custom_id=f"leave_role_{event_id}")
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        # MODIFICACIÓN: Defer la respuesta
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in wb_events:
            return await interaction.followup.send("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]
        user_removed = False
        removed_role = None

        # Check main inscriptions
        for role, users in event["inscriptions"].items():
            if interaction.user.id in users:
                users.remove(interaction.user.id)
                user_removed = True
                removed_role = role
                break

        # Check waitlist if not removed from main
        if not user_removed:
            for role, users in event["waitlist"].items():
                if interaction.user.id in users:
                    users.remove(interaction.user.id)
                    user_removed = True
                    removed_role = role
                    break

        if user_removed:
            if removed_role and len(event["inscriptions"][removed_role]) < WB_BOSS_DATA[event["boss"]]["roles"][removed_role]:
                # Promote from waitlist if a slot opened
                if event["waitlist"][removed_role]:
                    promoted_user_id = event["waitlist"][removed_role].pop(0)
                    promoted_member = interaction.guild.get_member(promoted_user_id)
                    event["inscriptions"][removed_role].append(promoted_user_id)
                    if promoted_member:
                        try:
                            await promoted_member.send(f"🎉 ¡Has sido movido de la lista de espera al rol **{removed_role}** en el evento de World Boss {WB_BOSS_DATA[event['boss']]['name']}!")
                        except discord.Forbidden:
                            print(f"No se pudo enviar DM a {promoted_member.name}. Probablemente tiene los DMs cerrados.")
            await interaction.followup.send("✅ Has salido del rol (o de la lista de espera).", ephemeral=True)
            await update_wb_embed(self.event_id)
        else:
            await interaction.followup.send("❌ No estás inscrito en ningún rol ni en lista de espera en este evento.", ephemeral=True)

class WB_JoinWaitlistMainButton(discord.ui.Button):
    def __init__(self, boss, event_id):
        super().__init__(label="Unirse a Lista de Espera", style=discord.ButtonStyle.blurple, custom_id=f"join_waitlist_main_{event_id}")
        self.boss = boss
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        # MODIFICACIÓN: Defer la respuesta
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in wb_events:
            return await interaction.followup.send("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]

        # Check if user is already in any role or waitlist for this event
        for existing_role, users in event["inscriptions"].items():
            if interaction.user.id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás inscrito como **{existing_role}**. No puedes unirte a la lista de espera.",
                    ephemeral=True
                )
        for existing_role, users in event["waitlist"].items():
            if interaction.user.id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás en la lista de espera para **{existing_role}**. No puedes unirte a otra.",
                    ephemeral=True
                )

        # Get roles that are currently full
        full_roles = [
            role for role in WB_BOSS_DATA[self.boss]["roles"]
            if len(event["inscriptions"][role]) >= WB_BOSS_DATA[self.boss]["roles"][role]
        ]

        if not full_roles:
            return await interaction.followup.send("✅ ¡No hay roles llenos en este momento! Puedes unirte directamente usando el menú desplegable de roles.", ephemeral=True)

        # Present a new dropdown for selecting the waitlist role
        view = discord.ui.View(timeout=60)
        view.add_item(WB_WaitlistRoleDropdown(self.boss, self.event_id, full_roles))
        await interaction.followup.send("Por favor, selecciona el rol al que deseas unirte en la lista de espera:", view=view, ephemeral=True)

class WB_WaitlistRoleDropdown(discord.ui.Select):
    def __init__(self, boss, event_id, full_roles):
        self.boss = boss
        self.event_id = event_id
        options = [
            discord.SelectOption(
                label=role,
                emoji=WB_BOSS_DATA[boss]["emojis"].get(role),
                description="Rol lleno - Unirse a lista de espera"
            ) for role in full_roles
        ]
        super().__init__(
            placeholder="Elige el rol para la lista de espera",
            options=options,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        # MODIFICACIÓN: Defer la respuesta
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in wb_events:
            return await interaction.followup.send("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]
        role = self.values[0]

        # Re-check if user is already in any role or waitlist (race condition)
        user_id = interaction.user.id
        for existing_role, users in event["inscriptions"].items():
            if user_id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás inscrito como **{existing_role}**. No puedes unirte a la lista de espera.",
                    ephemeral=True
                )
        for existing_role, users in event["waitlist"].items():
            if user_id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás en la lista de espera para **{existing_role}**. No puedes unirte a otra.",
                    ephemeral=True
                )

        # Add to waitlist
        event["waitlist"][role].append(user_id)
        await interaction.followup.send(f"✅ Te has unido a la lista de espera para **{role}**.", ephemeral=True)
        await update_wb_embed(self.event_id)


# --- Clases para Roaming Parties ---

class RoamingRoleSelectorView(discord.ui.View):
    def __init__(self, party_type, event_id, caller_id):
        super().__init__(timeout=None)
        self.party_type = party_type
        self.event_id = event_id
        self.caller_id = caller_id
        self.add_item(RoamingRoleDropdown(party_type, event_id))
        self.add_item(RoamingLeaveButton(event_id))

    @discord.ui.button(label="Cerrar Roaming", style=discord.ButtonStyle.danger, emoji="🚫", row=1)
    async def close_roaming_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)

        if self.event_id not in roaming_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        # Eliminar el mensaje principal
        try:
            await interaction.message.delete()
            print(f"Mensaje del evento roaming {self.event_id} eliminado correctamente.")
        except discord.Forbidden:
            print(f"Error: El bot no tiene el permiso 'Manage Messages' para eliminar el mensaje del evento roaming {self.event_id}.")
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("✅ Evento cerrado, pero no pude borrar el mensaje (permisos faltantes).", ephemeral=True)
        except Exception as e:
            print(f"Error inesperado al eliminar el mensaje del evento roaming {self.event_id}: {e}")
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("❌ Ocurrió un error al intentar eliminar el mensaje.", ephemeral=True)
        
        del roaming_events[self.event_id]
        await interaction.response.send_message(f"✅ Evento de roaming cerrado y eliminado.", ephemeral=True)

class RoamingRoleDropdown(discord.ui.Select):
    def __init__(self, party_type, event_id):
        self.party_type = party_type
        self.event_id = event_id
        options = [
            discord.SelectOption(
                label=role,
                emoji=ROAMING_PARTIES[party_type]["emojis"].get(role),
                description=f"0/{ROAMING_PARTIES[party_type]["roles"][role]}"
            ) for role in ROAMING_PARTIES[party_type]["roles"]
        ]
        super().__init__(
            placeholder="Elige tu rol",
            options=options,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in roaming_events:
            return await interaction.followup.send("❌ Este evento ya no está activo.", ephemeral=True)

        event = roaming_events[self.event_id]
        party_data = ROAMING_PARTIES[self.party_type]
        selected_role = self.values[0]

        # Check if user is already in any role or waitlist
        for role, users in event["inscripciones"].items():
            if interaction.user.id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás inscrito como **{role}**. Usa el botón 'Salir de Rol' primero.",
                    ephemeral=True
                )
        for role, users in event["waitlist"].items():
            if interaction.user.id in users:
                return await interaction.followup.send(
                    f"❌ Ya estás en la lista de espera para **{role}**. Usa el botón 'Salir de Rol' primero.",
                    ephemeral=True
                )

        # Check if party is full
        current_total_players = sum(len(players) for players in event["inscripciones"].values())
        if current_total_players >= party_data["max_players"]:
            # If party is full, add to waitlist
            if selected_role not in event["waitlist"]:
                event["waitlist"][selected_role] = []
            event["waitlist"][selected_role].append(interaction.user.id)
            await interaction.followup.send(f"✅ La party está llena. Te has unido a la lista de espera para **{selected_role}**.", ephemeral=True)
        else:
            # Check if selected role is full
            if len(event["inscripciones"].get(selected_role, [])) >= party_data["roles"][selected_role]:
                if selected_role not in event["waitlist"]:
                    event["waitlist"][selected_role] = []
                event["waitlist"][selected_role].append(interaction.user.id)
                await interaction.followup.send(f"✅ El rol **{selected_role}** está lleno. Te has unido a la lista de espera.", ephemeral=True)
            else:
                event["inscripciones"].setdefault(selected_role, []).append(interaction.user.id)
                await interaction.followup.send(f"✅ Te has unido como **{selected_role}**", ephemeral=True)
        
        await interaction.message.edit(embed=create_roaming_embed(self.party_type, event), view=self.view)

class RoamingLeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salir de Rol", style=discord.ButtonStyle.red, custom_id=f"roaming_leave_role_{event_id}")
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in roaming_events:
            return await interaction.followup.send("❌ Este evento ya no está activo.", ephemeral=True)

        event = roaming_events[self.event_id]
        party_type = event["party"]
        user_removed = False
        removed_role = None

        # Try to remove from inscriptions
        for role, users in event["inscripciones"].items():
            if interaction.user.id in users:
                users.remove(interaction.user.id)
                user_removed = True
                removed_role = role
                break

        # If not found in inscriptions, try to remove from waitlist
        if not user_removed:
            for role, users in event["waitlist"].items():
                if interaction.user.id in users:
                    users.remove(interaction.user.id)
                    user_removed = True
                    removed_role = role
                    break

        if user_removed:
            # Promote from waitlist if a slot opened in the main inscription
            if removed_role and len(event["inscripciones"].get(removed_role, [])) < ROAMING_PARTIES[party_type]["roles"][removed_role]:
                if event["waitlist"].get(removed_role):
                    promoted_user_id = event["waitlist"][removed_role].pop(0)
                    event["inscripciones"][removed_role].append(promoted_user_id)
                    promoted_member = interaction.guild.get_member(promoted_user_id)
                    if promoted_member:
                        try:
                            await promoted_member.send(f"🎉 ¡Has sido movido de la lista de espera al rol **{removed_role}** en el evento de roaming!")
                        except discord.Forbidden:
                            print(f"No se pudo enviar DM a {promoted_member.name}. Probablemente tiene los DMs cerrados.")

            await interaction.followup.send("✅ Has salido del rol (o de la lista de espera).", ephemeral=True)
            await interaction.message.edit(embed=create_roaming_embed(party_type, event), view=self.view)
        else:
            await interaction.followup.send("❌ No estás inscrito en ningún rol ni en lista de espera en este evento.", ephemeral=True)


# --- Clases para CTA (Call To Arms) ---

class CTAEventView(discord.ui.View):
    def __init__(self, event_id, caller_id, event_data):
        super().__init__(timeout=None)
        self.event_id = event_id
        self.caller_id = caller_id
        self.event_data = event_data
        self.add_item(CTARoleDropdown(event_id, event_data))
        self.add_item(CTALeaveButton(event_id))
        self.add_item(CTASwapGankButton(event_id)) # Nuevo botón de swap de gank

    @discord.ui.button(label="Cerrar CTA", style=discord.ButtonStyle.danger, emoji="🚫", row=1)
    async def close_cta_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)

        if self.event_id not in cta_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        thread = interaction.message.thread
        if thread:
            try:
                if thread.archived:
                    await thread.edit(archived=False, reason="Desarchivando para eliminar CTA")
                await thread.delete()
                print(f"Hilo del evento CTA {self.event_id} eliminado.")
            except discord.NotFound:
                print(f"Hilo del evento CTA {self.event_id} ya no existe.")
            except discord.Forbidden:
                print(f"Fallo al eliminar el hilo del evento CTA {self.event_id}. Permisos faltantes.")
            except Exception as e:
                print(f"Error inesperado al eliminar el hilo del evento CTA {self.event_id}: {e}")

        try:
            await interaction.message.delete()
            print(f"Mensaje del evento CTA {self.event_id} eliminado.")
        except discord.Forbidden:
            print(f"Fallo al eliminar el mensaje del evento CTA {self.event_id}. Permisos faltantes.")
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("✅ Evento cerrado, pero no pude borrar el mensaje (permisos faltantes).", ephemeral=True)
        except Exception as e:
            print(f"Error inesperado al eliminar el mensaje del evento CTA {self.event_id}: {e}")
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("❌ Ocurrió un error al intentar eliminar el mensaje.", ephemeral=True)

        del cta_events[self.event_id]
        await interaction.response.send_message(f"✅ Evento CTA cerrado y eliminado.", ephemeral=True)

class CTARoleDropdown(discord.ui.Select):
    def __init__(self, event_id, event_data):
        self.event_id = event_id
        self.event_data = event_data
        
        options = []
        for party_name in ["kiteo1", "kiteo2", "roaming_pocho"]: # Added "roaming_pocho"
            if party_name in ROAMING_PARTIES:
                party_data = ROAMING_PARTIES[party_name]
                for role_name in party_data["roles"]:
                    options.append(
                        discord.SelectOption(
                            label=f"{party_name.upper()} - {role_name}",
                            value=f"{party_name}-{role_name}",
                            emoji=party_data["emojis"].get(role_name, "❔")
                        )
                    )
        
        super().__init__(
            placeholder="Elige tu rol para el CTA",
            options=options,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in cta_events:
            return await interaction.followup.send("❌ Este evento CTA ya no está activo.", ephemeral=True)

        event = cta_events[self.event_id]
        party_name, selected_role = self.values[0].split('-', 1)

        # Check if user is already in any role across all CTA parties
        for p_name in ["kiteo1", "kiteo2", "roaming_pocho"]: # Added "roaming_pocho"
            for r_name, users in event["inscripciones"].get(p_name, {}).items():
                if interaction.user.id in users:
                    return await interaction.followup.send(
                        f"❌ Ya estás inscrito como **{p_name.upper()} - {r_name}**. Usa el botón 'Salir de Rol' primero.",
                        ephemeral=True
                    )
            for r_name, users in event["waitlist"].get(p_name, {}).items():
                if interaction.user.id in users:
                    return await interaction.followup.send(
                        f"❌ Ya estás en la lista de espera para **{p_name.upper()} - {r_name}**. Usa el botón 'Salir de Rol' primero.",
                        ephemeral=True
                    )

        party_data = ROAMING_PARTIES[party_name]
        
        # Ensure the nested dictionaries exist
        event["inscripciones"].setdefault(party_name, {})
        event["waitlist"].setdefault(party_name, {})

        # Check if the specific role is full
        if len(event["inscripciones"][party_name].get(selected_role, [])) >= party_data["roles"].get(selected_role, 1):
            event["waitlist"][party_name].setdefault(selected_role, []).append(interaction.user.id)
            await interaction.followup.send(f"✅ El rol **{party_name.upper()} - {selected_role}** está lleno. Te has unido a la lista de espera.", ephemeral=True)
        else:
            event["inscripciones"][party_name].setdefault(selected_role, []).append(interaction.user.id)
            await interaction.followup.send(f"✅ Te has unido como **{party_name.upper()} - {selected_role}**", ephemeral=True)
        
        await update_cta_embed(self.event_id)

class CTALeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salir de Rol", style=discord.ButtonStyle.red, custom_id=f"cta_leave_role_{event_id}")
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in cta_events:
            return await interaction.followup.send("❌ Este evento CTA ya no está activo.", ephemeral=True)

        event = cta_events[self.event_id]
        user_removed = False
        removed_party = None
        removed_role = None

        # Try to remove from inscriptions
        for p_name, roles_data in event["inscripciones"].items():
            for r_name, users in roles_data.items():
                if interaction.user.id in users:
                    users.remove(interaction.user.id)
                    user_removed = True
                    removed_party = p_name
                    removed_role = r_name
                    break
            if user_removed:
                break

        # If not found in inscriptions, try to remove from waitlist
        if not user_removed:
            for p_name, roles_data in event["waitlist"].items():
                for r_name, users in roles_data.items():
                    if interaction.user.id in users:
                        users.remove(interaction.user.id)
                        user_removed = True
                        removed_party = p_name
                        removed_role = r_name
                        break
                if user_removed:
                    break

        if user_removed:
            # Promote from waitlist if a slot opened in the main inscription
            if removed_party and removed_role:
                party_data = ROAMING_PARTIES[removed_party]
                if len(event["inscripciones"][removed_party].get(removed_role, [])) < party_data["roles"].get(removed_role, 1):
                    if event["waitlist"][removed_party].get(removed_role):
                        promoted_user_id = event["waitlist"][removed_party][removed_role].pop(0)
                        event["inscripciones"][removed_party][removed_role].append(promoted_user_id)
                        promoted_member = interaction.guild.get_member(promoted_user_id)
                        if promoted_member:
                            try:
                                await promoted_member.send(f"🎉 ¡Has sido movido de la lista de espera al rol **{removed_party.upper()} - {removed_role}** en el evento CTA!")
                            except discord.Forbidden:
                                print(f"No se pudo enviar DM a {promoted_member.name}. Probablemente tiene los DMs cerrados.")

            await interaction.followup.send("✅ Has salido del rol (o de la lista de espera) del CTA.", ephemeral=True)
            await update_cta_embed(self.event_id)
        else:
            await interaction.followup.send("❌ No estás inscrito en ningún rol ni en lista de espera en este evento CTA.", ephemeral=True)

class CTASwapGankButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Swap de Gank", style=discord.ButtonStyle.blurple, custom_id=f"cta_swap_gank_{event_id}")
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.event_id not in cta_events:
            return await interaction.followup.send("❌ Este evento CTA ya no está activo.", ephemeral=True)

        event = cta_events[self.event_id]
        
        # Toggle swap_gank status
        event["swap_gank"] = not event.get("swap_gank", False)
        
        status_text = "activado" if event["swap_gank"] else "desactivado"
        await interaction.followup.send(f"✅ Swap de Gank ha sido {status_text} para este CTA.", ephemeral=True)
        await update_cta_embed(self.event_id)

# ====================================================================
# --- 5. COMANDOS DEL BOT ---
# ====================================================================

# --- Comandos para World Boss (WB) ---
@bot.command(name="wb")
async def wb_event(ctx, boss_name: str, duration: str = "2h", priority_slots: int = 0, *priority_users: discord.Member):
    if boss_name.lower() not in WB_BOSS_DATA:
        return await ctx.send(f"❌ Jefe '{boss_name}' no reconocido. Jefes disponibles: {', '.join(WB_BOSS_DATA.keys())}")

    boss_info = WB_BOSS_DATA[boss_name.lower()]
    event_id = int(time.time()) # Usar timestamp como ID único

    # Inicializar inscripciones y lista de espera
    inscriptions = {role: [] for role in boss_info["roles"]}
    waitlist = {role: [] for role in boss_info["roles"]}

    description = boss_info["default_description"].format(duration=duration)
    
    # Crear el embed
    embed = discord.Embed(
        title=f"💀 WORLD BOSS {boss_info['name'].upper()}",
        description=description,
        color=0x00FF00 # Verde por defecto
    )
    embed.set_footer(text="🔓 Todos pueden anotarse")

    for role in boss_info["roles"]:
        embed.add_field(
            name=f"{boss_info['emojis'].get(role)} {role} (0/{boss_info['roles'][role]})",
            value="🚫 Vacío",
            inline=False
        )
    
    # Enviar el mensaje y guardar la referencia
    message = await ctx.send(embed=embed)

    # Crear el hilo
    thread = await message.create_thread(
        name=f"WB {boss_name.upper()} - {datetime.now().strftime('%H:%M')}",
        auto_archive_duration=1440 # 24 horas
    )
    # Ping al caller en el hilo
    await thread.send(f"<@{ctx.author.id}> ¡Tu evento de World Boss ha sido creado! Usa este hilo para la coordinación.")

    # Guardar el evento
    wb_events[event_id] = {
        "boss": boss_name.lower(),
        "message": message,
        "thread": thread,
        "caller_id": ctx.author.id,
        "inscriptions": inscriptions,
        "waitlist": waitlist,
        "description": description,
        "priority_mode": False
    }

    # Configurar modo de prioridad si aplica
    if priority_slots > 0 and priority_users:
        priority_user_ids = [user.id for user in priority_users]
        wb_priority_users[event_id] = {
            "users": priority_user_ids,
            "expiry": time.time() + WB_EVENT_TIMEOUT, # Duración de la prioridad
            "slots": priority_slots
        }
        wb_events[event_id]["priority_mode"] = True
        await update_wb_embed(event_id) # Actualizar embed para reflejar prioridad

    # Enviar la vista con botones
    view = WB_RoleSelectorView(boss_name.lower(), event_id, ctx.author.id, disabled=wb_events[event_id]["priority_mode"])
    await message.edit(view=view)
    await ctx.send(f"✅ Evento de World Boss '{boss_info['name']}' creado. ID: {event_id}", ephemeral=True)


@bot.command(name="prioritywb")
async def priority_wb(ctx, event_id: int, slots: int, *users: discord.Member):
    if event_id not in wb_events:
        return await ctx.send("❌ ID de evento WB no encontrado.", ephemeral=True)

    event = wb_events[event_id]
    if ctx.author.id != event["caller_id"]:
        return await ctx.send("❌ Solo el creador del evento puede usar este comando.", ephemeral=True)

    if not users:
        return await ctx.send("❌ Debes mencionar al menos un usuario para darle prioridad.", ephemeral=True)

    user_ids = [user.id for user in users]
    wb_priority_users[event_id] = {
        "users": user_ids,
        "expiry": time.time() + WB_EVENT_TIMEOUT, # 2 horas de prioridad
        "slots": slots
    }
    event["priority_mode"] = True
    await update_wb_embed(event_id)
    await ctx.send(f"✅ Prioridad de {slots} slots activada para {len(users)} usuarios en el evento WB ID: {event_id}. Expira en 2 horas.", ephemeral=True)

@bot.command(name="clearprioritywb")
async def clear_priority_wb(ctx, event_id: int):
    if event_id not in wb_events:
        return await ctx.send("❌ ID de evento WB no encontrado.", ephemeral=True)

    event = wb_events[event_id]
    if ctx.author.id != event["caller_id"]:
        return await ctx.send("❌ Solo el creador del evento puede usar este comando.", ephemeral=True)

    if event_id in wb_priority_users:
        del wb_priority_users[event_id]
        event["priority_mode"] = False
        await update_wb_embed(event_id)
        await ctx.send(f"✅ Prioridad desactivada para el evento WB ID: {event_id}.", ephemeral=True)
    else:
        await ctx.send(f"ℹ️ El evento WB ID: {event_id} no tenía prioridad activa.", ephemeral=True)

# --- Comandos para Roaming Parties ---
@bot.command(name="roaming")
async def roaming_party(ctx, party_type: str, tier_min: str, ip_min: int, time_val: str = None, swap_gank: str = "no", *caller_name_args):
    party_type = party_type.lower()
    if party_type not in ROAMING_PARTIES:
        return await ctx.send(f"❌ Tipo de roaming '{party_type}' no reconocido. Tipos disponibles: {', '.join(ROAMING_PARTIES.keys())}", ephemeral=True)
    
    caller_display = get_roaming_caller_info(ctx, caller_name_args)
    swap_gank_bool = swap_gank.lower() in ('si', 'sí', 'y', 'yes')

    event_id = int(time.time()) # Unique ID based on timestamp
    
    # Initialize inscriptions and waitlist for each role in the selected party type
    inscriptions = {role: [] for role in ROAMING_PARTIES[party_type]["roles"]}
    waitlist = {role: [] for role in ROAMING_PARTIES[party_type]["roles"]}

    event_data = {
        "party": party_type,
        "caller_id": ctx.author.id,
        "caller_display": caller_display,
        "tier_min": tier_min,
        "ip_min": ip_min,
        "time": time_val,
        "swap_gank": swap_gank_bool,
        "inscripciones": inscriptions,
        "waitlist": waitlist,
        "event_id": event_id
    }
    
    embed = create_roaming_embed(party_type, event_data)
    message = await ctx.send(embed=embed)

    roaming_events[event_id] = {
        "message": message,
        "caller_id": ctx.author.id,
        "party": party_type,
        "event_data": event_data # Store the full event data
    }
    
    view = RoamingRoleSelectorView(party_type, event_id, ctx.author.id)
    await message.edit(view=view)
    await ctx.send(f"✅ Evento de roaming '{party_type}' creado. ID: {event_id}", ephemeral=True)

# --- Comandos para CTA (Call to Arms) ---
@bot.command(name="cta")
async def cta_event(ctx, mass_time: str):
    event_id = int(time.time())
    
    # Inicializar inscripciones y listas de espera para cada party dentro del CTA
    inscripciones = {
        "kiteo1": {role: [] for role in ROAMING_PARTIES["kiteo1"]["roles"]},
        "kiteo2": {role: [] for role in ROAMING_PARTIES["kiteo2"]["roles"]},
        "roaming_pocho": {role: [] for role in ROAMING_PARTIES["roaming_pocho"]["roles"]}, # Added "roaming_pocho"
        # Agrega aquí otras parties que quieras incluir en el CTA
    }
    waitlist = {
        "kiteo1": {role: [] for role in ROAMING_PARTIES["kiteo1"]["roles"]},
        "kiteo2": {role: [] for role in ROAMING_PARTIES["kiteo2"]["roles"]},
        "roaming_pocho": {role: [] for role in ROAMING_PARTIES["roaming_pocho"]["roles"]}, # Added "roaming_pocho"
        # Agrega aquí otras parties que quieras incluir en el CTA
    }

    event_data = {
        "event_id": event_id,
        "caller_id": ctx.author.id,
        "mass_time": mass_time,
        "inscripciones": inscripciones,
        "waitlist": waitlist,
        "swap_gank": False # Por defecto, swap de gank desactivado para CTA
    }

    embed = create_cta_embed(event_data)
    message = await ctx.send(embed=embed)

    # Crear el hilo para el CTA
    thread = await message.create_thread(
        name=f"CTA - {mass_time} UTC",
        auto_archive_duration=1440 # 24 horas
    )
    await thread.send(f"<@{ctx.author.id}> ¡Tu evento CTA ha sido creado! Coordina a tus equipos aquí.")

    cta_events[event_id] = {
        "message": message,
        "thread": thread,
        "caller_id": ctx.author.id,
        "mass_time": mass_time,
        "inscripciones": inscripciones,
        "waitlist": waitlist,
        "swap_gank": False # Asegurarse que se guarde el estado inicial
    }

    view = CTAEventView(event_id, ctx.author.id, event_data)
    await message.edit(view=view)
    await ctx.send(f"✅ Evento CTA creado para las {mass_time} UTC. ID: {event_id}", ephemeral=True)


# ====================================================================
# --- 6. TAREAS EN BUCLE (LIMPIEZA) ---
# ====================================================================

@tasks.loop(minutes=5)
async def cleanup_wb_events():
    current_time = time.time()
    events_to_remove = []
    for event_id, event_data in list(wb_events.items()): # Iterate over a copy
        if current_time - event_data["message"].created_at.timestamp() > WB_EVENT_TIMEOUT:
            events_to_remove.append(event_id)
            try:
                # Intenta eliminar el mensaje si aún existe
                if event_data["message"]:
                    await event_data["message"].delete()
                    print(f"Mensaje del evento WB expirado {event_id} eliminado.")
            except discord.NotFound:
                print(f"Mensaje del evento WB expirado {event_id} ya no existe.")
            except discord.Forbidden:
                print(f"Fallo al eliminar el mensaje del evento WB expirado {event_id}. Permisos faltantes.")
            except Exception as e:
                print(f"Error inesperado al eliminar el mensaje del evento WB expirado {event_id}: {e}")
            
            # Intenta eliminar el hilo asociado
            if event_data.get("thread"):
                try:
                    if event_data["thread"].archived:
                        await event_data["thread"].edit(archived=False, reason="Desarchivando para eliminar por expiración WB")
                    await event_data["thread"].delete()
                    print(f"Hilo del evento WB expirado {event_id} eliminado.")
                except discord.NotFound:
                    print(f"Hilo del evento WB expirado {event_id} ya no existe.")
                except discord.Forbidden:
                    print(f"Fallo al eliminar el hilo del evento WB expirado {event_id}. Permisos faltantes.")
                except Exception as e:
                    print(f"Error inesperado al eliminar el hilo del evento WB expirado {event_id}: {e}")

    for event_id in events_to_remove:
        if event_id in wb_events:
            del wb_events[event_id]
        if event_id in wb_priority_users:
            del wb_priority_users[event_id]

@tasks.loop(minutes=5)
async def cleanup_roaming_events():
    current_time = time.time()
    events_to_remove = []
    for event_id, event_data in list(roaming_events.items()): # Iterate over a copy
        # Asegúrate de que event_data["message"] existe y tiene created_at
        if event_data.get("message") and hasattr(event_data["message"], "created_at"):
            if current_time - event_data["message"].created_at.timestamp() > ROAMING_EVENT_TIMEOUT:
                events_to_remove.append(event_id)
                try:
                    await event_data["message"].delete()
                    print(f"Mensaje del evento roaming expirado {event_id} eliminado.")
                except discord.NotFound:
                    print(f"Mensaje del evento roaming expirado {event_id} ya no existe.")
                except discord.Forbidden:
                    print(f"Fallo al eliminar el mensaje del evento roaming expirado {event_id}. Permisos faltantes.")
                except Exception as e:
                    print(f"Error inesperado al eliminar el mensaje del evento roaming expirado {event_id}: {e}")
        else: # Si el mensaje no existe o no tiene created_at, también lo consideramos para eliminar
            print(f"Evento roaming {event_id} sin mensaje o sin timestamp, marcando para eliminación.")
            events_to_remove.append(event_id)

    for event_id in events_to_remove:
        if event_id in roaming_events:
            del roaming_events[event_id]

@tasks.loop(minutes=5)
async def cleanup_cta_events():
    current_time = time.time()
    events_to_remove = []
    for event_id, event_data in list(cta_events.items()):
        if event_data.get("message") and hasattr(event_data["message"], "created_at"):
            if current_time - event_data["message"].created_at.timestamp() > CTA_EVENT_TIMEOUT:
                events_to_remove.append(event_id)
                try:
                    message = event_data["message"]
                    thread = event_data.get("thread")
                    if thread:
                        if thread.archived:
                            await thread.edit(archived=False, reason="Desarchivando para eliminar por expiración CTA")
                        await thread.delete()
                        print(f"Hilo del evento CTA expirado {event_id} eliminado.")
                    await message.delete()
                    print(f"Mensaje del evento CTA expirado {event_id} eliminado.")
                except discord.NotFound:
                    print(f"Mensaje o hilo del evento CTA expirado {event_id} ya no existe.")
                except discord.Forbidden:
                    print(f"Fallo al eliminar el mensaje/hilo del evento CTA expirado {event_id}. Permisos faltantes.")
                except Exception as e:
                    print(f"Error inesperado al eliminar el mensaje del evento CTA expirado {event_id}: {e}")
            else:
                print(f"Evento CTA {event_id} sin mensaje o sin timestamp, marcando para eliminación.")
                events_to_remove.append(event_id)

    for event_id in events_to_remove:
        if event_id in cta_events:
            del cta_events[event_id]


# La función before_loop se mantiene igual, ya que es la forma correcta de esperar.
@cleanup_roaming_events.before_loop
async def before_cleanup_roaming():
    await bot.wait_until_ready()
    await bot.load_extension('builds')

@cleanup_cta_events.before_loop
async def before_cleanup_cta():
    await bot.wait_until_ready()

# ====================================================================
# --- 8. EJECUCIÓN DEL BOT ---
# ====================================================================
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
