import discord
import time
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import os
import random
from discord.ui import Button, View, Select
from dotenv import load_dotenv
import os
from keep_alive import keep_alive
load_dotenv()

# ====================================================================
# --- 1. CONFIGURACIÓN E INSTANCIA DEL BOT ---
# ====================================================================

# Habilitar intents necesarios para el bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necesario para obtener miembros del guild
# Para versiones más recientes de discord.py (2.0+)
intents.guilds = True  # Necesario para manejar hilos
intents.messages = True  # Necesario para manejar mensajes en hilos

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

# --- Datos para Roaming Parties ---
ROAMING_PARTIES = {
    "kiteo1": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "PESADA": 1, "LECHO PEEL": 1, "LECHO SUP": 1, "GA": 1, "LOCUS": 1,
            "JURADORES": 1, "ENRAIZADO": 1, "LIFECURSED": 1, "OCULTO": 1, "ROMPERREINO": 1,
            "CAZAESPÍRITUS": 1, "FISURANTE": 3, "PRISMA": 1, "PUAS": 1, "SANTI": 3,
            "FORJACORTEZA": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "PESADA": "<:stoper:1290858463135662080>",
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
            "GOLEM": 1, "MARTILLO": 1, "GA": 1, "LOCUS": 1, "JURADORES": 1, "ENRAIZADO": 1,
            "CANCION": 1, "CARAM": 1, "DAMNATION": 1, "LIFECURSED": 1, "PUTREFACTO": 1,
            "OCULTO": 1, "FISURANTE": 3, "FORJACORTEZA": 1, "SANTI": 3, "TORRE_MOVIL": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "MARTILLO": "<:stoper:1290858463135662080>",
            "GA": "<:GranArcano:1337861969931407411>", "LOCUS": "<:Locus:1291467422238249043>",
            "JURADORES": "<:Maracas:1290858583965175828>", "ENRAIZADO": "<:Enraizado:1290879541073678397>",
            "CANCION": "<:Canciondedespertar:1291635941240213574>", "CARAMBANOS": "<:caram:1384931326968463372>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "LIFECURSED": "<:Maldi:1291467716229730415>",
            "PUTREFACTO": "<:Putrefacto:1370577320171016202>", "OCULTO": "<:Oculto:1337862058779218026>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
            "SANTI": "<:Santificador:1290858870260109384>", "TORRE_MOVIL": "<:MonturaMana:1337863658859925676>",
        }
    },
    "brawl": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "MARTILLO 1H": 1, "MAZA PESADA": 1, "MONARCA": 1, "SAGRADO": 3, "INFORTUNIO": 1,
            "ENRAIZADO": 1, "JURADORES": 1, "LIFECURSED": 1, "TALLADA": 1, "DAMNATION": 1,
            "ROMPERREINO": 1, "DEMONFANG": 1, "GUADAÑA": 1, "PUAS": 1, "ZARPAS": 1, "ASTRAL": 1,
            "HOJA INFINITA": 1,
        },
        "emojis": {
            "GOLEM": "🪨", "MARTILLO 1H": "🔨", "MAZA PESADA": "⚔️", "MONARCA": "😈", "SAGRADO": "✨",
            "INFORTUNIO": "🌿", "ENRAIZADO": "🌱", "JURADORES": "⚖️", "LIFECURSED": "💀", "TALLADA": "🗡️",
            "DAMNATION": "😈", "ROMPERREINO": "💥", "DEMONFANG": "👹", "GUADAÑA": "💀", "PUAS": "🌵",
            "ZARPAS": "🐾", "ASTRAL": "✨", "HOJA INFINITA": "🗡️",
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
            "Patas de oso": 3,
            "Hoja infinita": 1,
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
    }
}

wb_events = {} # {event_id: {data}}
wb_priority_users = {} # {event_id: {"users": [], "expiry": timestamp, "slots": int}}

# --- Datos para Roaming Parties ---
roaming_events = {} # {event_id: {data}}
roaming_generic_counter = 0
ROAMING_EVENT_TIMEOUT = 7200 # 2 horas en segundos

# ====================================================================
# --- 3. FUNCIONES HELPER ---
# ====================================================================

# --- Helper de Roaming ---
def get_roaming_caller_info(ctx, args):
    """
    Determina el nombre del caller a mostrar en el embed.
    Si el último argumento no es un número (IP/Tier) o si no hay args,
    asume que el caller es el usuario que ejecutó el comando.
    Si el último argumento es una palabra, lo usa como nombre del caller.
    """
    if not args or args[-1].upper().startswith(('T', 'IP')) or args[-1].isdigit():
        return ctx.author.display_name # Asume que el caller es el que envía el comando
    else:
        return args[-1] # Usa el nombre que fue proporcionado

def create_roaming_embed(party, event_data):
    """Genera el mensaje embed para el evento de roaming."""
    embed = discord.Embed(
        title=f"🚀 ROAMING {party.upper()} (Caller: {event_data['caller_display']})",
        description=f"**📍 Salimos de Fort Sterling Portal**\nTier: {event_data['tier_min']} | IP: {event_data['ip_min']}+",
        color=0x00ff00 if "kiteo" in party else 0xFF0000
    )

    total_inscritos = sum(len(players) for players in event_data["inscripciones"].values())
    embed.set_footer(text=f"📊 {total_inscritos}/{ROAMING_PARTIES[party]['max_players']} jugadores | ID: {event_data['event_id']}")

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

# --- Helper de World Boss ---
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
                is_disabled = False
                footer_text = "🔒 Solo usuarios prioritarios pueden anotarse"
                embed_color = 0xFF4500
            else:
                event["priority_mode"] = False
                is_disabled = False
                footer_text = "🔓 Todos pueden anotarse"
                embed_color = 0x00FF00
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

        view = WB_RoleSelectorView(boss, event_id, event["caller_id"], disabled=is_disabled)
        await message.edit(embed=embed, view=view)

    except Exception as e:
        print(f"Error actualizando embed para el evento {event_id}: {e}")

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
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)

        if self.event_id not in wb_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        event_data = wb_events[self.event_id]
        embed = interaction.message.embeds[0]
        embed.title = f"🚫 WORLD BOSS: {event_data['boss'].upper()} (CERRADO)"
        embed.description = f"**Este evento ha sido cerrado por: {interaction.user.display_name}**"
        embed.color = discord.Color.red()

        # Deshabilitar componentes
        for item in self.children:
            item.disabled = True

        # Eliminar el hilo asociado si existe
        if interaction.message.thread:
            try:
                await interaction.message.thread.delete()
            except Exception as e:
                print(f"Error al eliminar hilo de WB: {e}")

        # Eliminar del diccionario y actualizar mensaje
        del wb_events[self.event_id]
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send("✅ Evento de World Boss cerrado correctamente.", ephemeral=True)

class WB_RoleDropdown(discord.ui.Select):
    def __init__(self, boss, event_id, disabled=False):
        self.boss = boss
        self.event_id = event_id
        options = [
            discord.SelectOption(
                label=role,
                emoji=WB_BOSS_DATA[boss]["emojis"].get(role),
                description=f"0/{WB_BOSS_DATA[boss]['roles'][role]}"
            ) for role in WB_BOSS_DATA[boss]["roles"]
        ]
        super().__init__(
            placeholder="Elige tu rol",
            options=options,
            max_values=1,
            disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in wb_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]
        role = self.values[0]

        # Check if user is already in any role or waitlist for this event
        for existing_role, users in event["inscriptions"].items():
            if interaction.user.id in users:
                return await interaction.response.send_message(
                    f"❌ Ya estás inscrito como **{existing_role}**. Usa el botón 'Salir de Rol' primero.",
                    ephemeral=True
                )
        for existing_role, users in event["waitlist"].items():
            if interaction.user.id in users:
                return await interaction.response.send_message(
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
                return await interaction.response.send_message(
                    f"🔒 **Solo usuarios prioritarios pueden anotarse ahora.**\n"
                    f"⏳ El bloqueo termina: <t:{int(expiry_time)}:R>",
                    ephemeral=True
                )

            if priority_data and time.time() >= priority_data["expiry"]:
                event["priority_mode"] = False
                await update_wb_embed(self.event_id)

        # Check if role is full for main inscription
        if len(event["inscriptions"][role]) >= WB_BOSS_DATA[self.boss]["roles"][role]:
            return await interaction.response.send_message("❌ Este rol ya está lleno. Usa el botón 'Unirse a Lista de Espera' si deseas esperar un slot.", ephemeral=True)

        # Inscribe user
        event["inscriptions"][role].append(interaction.user.id)
        await interaction.response.send_message(f"✅ Te has unido como **{role}**", ephemeral=True)
        await update_wb_embed(self.event_id)

class WB_LeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salir de Rol", style=discord.ButtonStyle.red, custom_id=f"leave_role_{event_id}")
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in wb_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

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
                    event["inscriptions"][removed_role].append(promoted_user_id)
                    promoted_member = interaction.guild.get_member(promoted_user_id)
                    if promoted_member:
                        try:
                            await promoted_member.send(f"🎉 ¡Has sido movido de la lista de espera al rol **{removed_role}** en el evento de World Boss {WB_BOSS_DATA[event['boss']]['name']}!")
                        except discord.Forbidden:
                            print(f"No se pudo enviar DM a {promoted_member.name}. Probablemente tiene los DMs cerrados.")

            await interaction.response.send_message("✅ Has salido del rol (o de la lista de espera).", ephemeral=True)
            await update_wb_embed(self.event_id)
        else:
            await interaction.response.send_message("❌ No estás inscrito en ningún rol ni en lista de espera en este evento.", ephemeral=True)

class WB_JoinWaitlistMainButton(discord.ui.Button):
    def __init__(self, boss, event_id):
        super().__init__(label="Unirse a Lista de Espera", style=discord.ButtonStyle.blurple, custom_id=f"join_waitlist_main_{event_id}")
        self.boss = boss
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in wb_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]

        # Check if user is already in any role or waitlist for this event
        for existing_role, users in event["inscriptions"].items():
            if interaction.user.id in users:
                return await interaction.response.send_message(
                    f"❌ Ya estás inscrito como **{existing_role}**. No puedes unirte a la lista de espera.",
                    ephemeral=True
                )
        for existing_role, users in event["waitlist"].items():
            if interaction.user.id in users:
                return await interaction.response.send_message(
                    f"❌ Ya estás en la lista de espera para **{existing_role}**. No puedes unirte a otra.",
                    ephemeral=True
                )

        # Get roles that are currently full
        full_roles = [
            role for role in WB_BOSS_DATA[self.boss]["roles"]
            if len(event["inscriptions"][role]) >= WB_BOSS_DATA[self.boss]["roles"][role]
        ]

        if not full_roles:
            return await interaction.response.send_message("✅ ¡No hay roles llenos en este momento! Puedes unirte directamente usando el menú desplegable de roles.", ephemeral=True)

        # Present a new dropdown for selecting the waitlist role
        view = discord.ui.View(timeout=60)
        view.add_item(WB_WaitlistRoleDropdown(self.boss, self.event_id, full_roles))
        await interaction.response.send_message("Por favor, selecciona el rol al que deseas unirte en la lista de espera:", view=view, ephemeral=True)

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
        if self.event_id not in wb_events:
            return await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)

        event = wb_events[self.event_id]
        role = self.values[0]

        # Re-check if user is already in any role or waitlist (race condition)
        partial_user_id = interaction.user.id
        for existing_role, users in event["inscriptions"].items():
            if partial_user_id in users:
                return await interaction.response.send_message(
                    f"❌ Ya estás inscrito como **{existing_role}**. No puedes unirte a la lista de espera.",
                    ephemeral=True
                )
        for existing_role, users in event["waitlist"].items():
            if partial_user_id in users:
                return await interaction.response.send_message(
                    f"❌ Ya estás en la lista de espera para **{existing_role}**. No puedes unirte a otra.",
                    ephemeral=True
                )

        # Re-check if role is still full
        if len(event["inscriptions"][role]) < WB_BOSS_DATA[self.boss]["roles"][role]:
            await interaction.response.send_message(f"✅ ¡Un slot se abrió en **{role}**! Por favor, usa el menú desplegable principal para unirte directamente.", ephemeral=True)
            await update_wb_embed(self.event_id) # Update embed to reflect open slot
            return

        # Add to waitlist
        event["waitlist"][role].append(partial_user_id)
        await interaction.response.send_message(f"✅ Te has unido a la lista de espera para **{role}**.", ephemeral=True)
        await update_wb_embed(self.event_id)

# --- Clases para Roaming Parties ---
class RoamingEventView(discord.ui.View):
    def __init__(self, party, event_id, caller_id, event_data):
        super().__init__(timeout=None)
        self.party = party
        self.event_id = event_id
        self.caller_id = caller_id
        self.event_data = event_data # Referencia a la entrada en roaming_events

        # Agrega el menú desplegable de roles
        self.add_item(self.create_role_selector())

    def create_role_selector(self):
        opciones = [
            discord.SelectOption(
                label=rol,
                emoji=ROAMING_PARTIES[self.party]["emojis"].get(rol),
                description=f"Slots: {len(self.event_data['inscripciones'][rol])}/{ROAMING_PARTIES[self.party]['roles'][rol]}"
            ) for rol in ROAMING_PARTIES[self.party]["roles"]
        ]

        select_menu = discord.ui.Select(
            placeholder="Elige tu rol",
            min_values=1,
            max_values=1,
            options=opciones
        )

        async def callback(interaction: discord.Interaction):
            user_id = interaction.user.id
            rol_elegido = select_menu.values[0]

            # Remover de cualquier rol previo en ESTE evento (principal o espera)
            for rol in self.event_data["inscripciones"]:
                if user_id in self.event_data["inscripciones"][rol]:
                    self.event_data["inscripciones"][rol].remove(user_id)
            for rol in self.event_data["waitlist"]:
                if user_id in self.event_data["waitlist"][rol]:
                    self.event_data["waitlist"][rol].remove(user_id)

            # Verificar slot disponible
            if len(self.event_data["inscripciones"][rol_elegido]) >= ROAMING_PARTIES[self.party]["roles"][rol_elegido]:
                await interaction.response.send_message("❌ Este rol ya está lleno. Por favor, usa el botón 'Lista de Espera'.", ephemeral=True)
                return

            # Inscribir al jugador
            self.event_data["inscripciones"][rol_elegido].append(user_id)

            # Actualizar embed
            embed = create_roaming_embed(self.party, self.event_data)
            await self.event_data["message"].edit(embed=embed, view=RoamingEventView(self.party, self.event_id, self.caller_id, self.event_data))
            await interaction.response.send_message(
                f"✅ Te has unido como **{rol_elegido}** en el evento de {self.event_data['caller_display']}",
                ephemeral=True
            )

        select_menu.callback = callback
        return select_menu

    # --- Botón para SALIR de rol ---
    @discord.ui.button(label="Salir de Rol", style=discord.ButtonStyle.red, emoji="🏃")
    async def leave_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        user_removed = False

        # Buscar en inscripciones (party principal)
        for rol, usuarios in self.event_data["inscripciones"].items():
            if user_id in usuarios:
                usuarios.remove(user_id)
                user_removed = True
                break

        # Si no está en el party principal, buscar en la lista de espera
        if not user_removed:
            for rol, usuarios in self.event_data["waitlist"].items():
                if user_id in usuarios:
                    usuarios.remove(user_id)
                    user_removed = True
                    break

        if user_removed:
            embed = create_roaming_embed(self.party, self.event_data)
            await self.event_data["message"].edit(embed=embed)
            await interaction.response.send_message("✅ Has salido del rol (o de la lista de espera).", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No estás inscrito en ningún rol ni en lista de espera en este evento.", ephemeral=True)

    # --- Botón para UNIRSE a la lista de espera ---
    @discord.ui.button(label="Lista de Espera", style=discord.ButtonStyle.secondary, emoji="👥")
    async def join_waitlist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        # Remover de cualquier rol previo en ESTE evento
        for rol in self.event_data["inscripciones"]:
            if user_id in self.event_data["inscripciones"][rol]:
                await interaction.response.send_message("❌ Ya estás en un rol principal. Usa 'Salir de Rol' para moverte a la lista de espera.", ephemeral=True)
                return
        for rol in self.event_data["waitlist"]:
            if user_id in self.event_data["waitlist"][rol]:
                await interaction.response.send_message("❌ Ya estás en la lista de espera para un rol. Usa 'Salir de Rol' para cambiar.", ephemeral=True)
                return

        # Crear un select para que elija el rol en la lista de espera
        full_roles = [rol for rol, limite in ROAMING_PARTIES[self.party]["roles"].items() if len(self.event_data["inscripciones"][rol]) >= limite]

        if not full_roles:
            return await interaction.response.send_message("✅ ¡No hay roles llenos en este momento! Usa el menú desplegable principal para unirte.", ephemeral=True)

        options = [
            discord.SelectOption(
                label=rol,
                emoji=ROAMING_PARTIES[self.party]["emojis"].get(rol),
                description=f"Jugadores en espera: {len(self.event_data['waitlist'][rol])}"
            ) for rol in full_roles
        ]

        select_waitlist = discord.ui.Select(
            placeholder="Elige rol para la lista de espera",
            min_values=1,
            max_values=1,
            options=options
        )

        async def waitlist_callback(interact: discord.Interaction):
            rol_elegido = select_waitlist.values[0]
            # Verifica si el rol sigue lleno (puede haber cambiado en el intertanto)
            if len(self.event_data["inscripciones"][rol_elegido]) < ROAMING_PARTIES[self.party]["roles"][rol_elegido]:
                await interact.response.send_message(f"🎉 ¡Un slot se abrió en **{rol_elegido}**! Por favor, usa el menú desplegable principal para unirte directamente.", ephemeral=True)
                return

            self.event_data["waitlist"][rol_elegido].append(user_id)

            embed = create_roaming_embed(self.party, self.event_data)
            await self.event_data["message"].edit(embed=embed)
            await interact.response.send_message(f"✅ Te has unido a la lista de espera para **{rol_elegido}**.", ephemeral=True)

        select_waitlist.callback = waitlist_callback

        temp_view = discord.ui.View(timeout=60)
        temp_view.add_item(select_waitlist)

        await interaction.response.send_message("Selecciona el rol para la lista de espera:", view=temp_view, ephemeral=True)

    # --- Botón para CERRAR el evento (Solo el caller) ---
    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫")
    async def close_event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Verificar si el usuario es el caller original
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)

        # 2. Actualizar el embed para mostrar que el evento está cerrado
        embed = interaction.message.embeds[0]
        embed.title = f"🚫 ROAMING {self.event_data['party'].upper()} (CERRADO)"
        embed.description = f"**Este evento ha sido cerrado por: {interaction.user.display_name}**"
        embed.color = discord.Color.red()

        # Deshabilitar todos los componentes de la vista
        for item in self.children:
            item.disabled = True

        # 3. Eliminar el hilo asociado si existe
        if interaction.message.thread:
            try:
                await interaction.message.thread.delete()
            except Exception as e:
                print(f"Error al eliminar hilo de Roaming: {e}")

        # 4. Eliminar el evento del diccionario global
        if self.event_id in roaming_events:
            del roaming_events[self.event_id]

        # 5. Actualizar el mensaje
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"✅ Evento de roaming `{self.event_id}` cerrado correctamente.", ephemeral=True)

# ====================================================================
# --- 5. COMANDOS (SLASH Y PREFIX) ---
# ====================================================================

# --- Comando Slash para cerrar cualquier evento ---
@bot.tree.command(name="close", description="Cierra un evento de World Boss o Roaming que hayas creado.")
@discord.app_commands.describe(event_id="ID del evento a cerrar (opcional, si tienes varios activos).")
async def close_event_slash(interaction: discord.Interaction, event_id: str = None):
    """
    Cierra un evento de WB o Roaming.
    Si no se especifica un ID, cerrará el evento más reciente que haya creado el usuario.
    """
    user_id = interaction.user.id
    event_found = False

    # --- Intentar cerrar un evento de World Boss ---
    for eid, data in list(wb_events.items()): # Usamos list() para poder borrar elementos mientras iteramos
        if data["caller_id"] == user_id and (event_id is None or eid == event_id):
            event_found = True

            # Editar el mensaje original para mostrar que ha sido cerrado
            channel = bot.get_channel(data["channel_id"])
            if channel and data["message"]:
                try:
                    message_to_edit = await channel.fetch_message(data["message"].id)
                    embed = message_to_edit.embeds[0]
                    embed.title = f"🚫 WORLD BOSS: {data['boss'].upper()} (CERRADO)"
                    embed.description = "**Este evento ha sido cerrado por el caller.**"
                    embed.color = discord.Color.red()

                    # Deshabilitar todos los botones y menús de la vista
                    view = discord.ui.View()
                    for item in message_to_edit.components:
                        view.add_item(item)
                    for item in view.children:
                        item.disabled = True

                    await message_to_edit.edit(embed=embed, view=view)

                    # Eliminar el hilo asociado si existe
                    if message_to_edit.thread:
                        try:
                            await message_to_edit.thread.delete()
                        except Exception as e:
                            print(f"Error al eliminar hilo de WB: {e}")

                except discord.NotFound:
                    print(f"Mensaje para el evento WB {eid} no encontrado. No se puede editar.")
                except Exception as e:
                    print(f"Error al editar el mensaje del evento WB {eid}: {e}")

            # Eliminar el evento del diccionario global
            del wb_events[eid]
            if event_id: break # Si se especificó un ID, cerramos uno y salimos del bucle

    # --- Intentar cerrar un evento de Roaming si no se encontró uno de WB ---
    if not event_found:
        for eid, data in list(roaming_events.items()):
            if data["caller_id"] == user_id and (event_id is None or eid == event_id):
                event_found = True

                # Editar el mensaje original
                channel = bot.get_channel(data["channel_id"])
                if channel and data["message"]:
                    try:
                        message_to_edit = await channel.fetch_message(data["message"].id)
                        embed = message_to_edit.embeds[0]
                        embed.title = f"🚫 ROAMING {data['party'].upper()} (CERRADO)"
                        embed.description = "**Este evento ha sido cerrado por el caller.**"
                        embed.color = discord.Color.red()

                        # Deshabilitar todos los componentes de la vista
                        view = discord.ui.View()
                        for item in message_to_edit.components:
                            view.add_item(item)
                        for item in view.children:
                            item.disabled = True

                        await message_to_edit.edit(embed=embed, view=view)

                        # Eliminar el hilo asociado si existe
                        if message_to_edit.thread:
                            try:
                                await message_to_edit.thread.delete()
                            except Exception as e:
                                print(f"Error al eliminar hilo de Roaming: {e}")

                    except discord.NotFound:
                        print(f"Mensaje para el evento Roaming {eid} no encontrado. No se puede editar.")
                    except Exception as e:
                        print(f"Error al editar el mensaje del evento Roaming {eid}: {e}")

                # Eliminar el evento del diccionario global
                del roaming_events[eid]
                if event_id: break

    # --- Enviar respuesta al usuario ---
    if event_found:
        await interaction.response.send_message(f"✅ Evento(s) cerrado(s) correctamente.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No se encontró ningún evento activo que hayas creado.", ephemeral=True)

# --- Comando Slash para World Boss ---
@bot.tree.command(name="wb", description="Crea un evento de World Boss con o sin prioridad.")
@discord.app_commands.describe(
    caller="El nombre del caller del World Boss.",
    boss="El World Boss (elder o eye).",
    duracion="La duración del evento (ej: '2 horas', '90 minutos').",
    prios="Número de slots prioritarios (opcional, 1-20).",
    tiempo_prios="Duración del modo prioridad en minutos (opcional, 1-60).",
    miembros_prio="Menciona los usuarios prioritarios (ej: '@User1 @User2')."
)
async def wb_slash(
    interaction: discord.Interaction,
    caller: str,
    boss: str,
    duracion: str,
    prios: int = 0,
    tiempo_prios: int = 0,
    miembros_prio: str = None
):
    """
    Crea un evento de World Boss.
    """
    boss_lower = boss.lower()
    if boss_lower not in WB_BOSS_DATA:
        return await interaction.response.send_message("❌ Boss inválido. Usa `elder` o `eye`.", ephemeral=True)

    # Verificar si el usuario ya tiene un evento activo
    for event_id, event_data in wb_events.items():
        if event_data["caller_id"] == interaction.user.id:
            return await interaction.response.send_message("❌ Ya tienes un evento activo. Usa `/close` para cerrarlo primero.", ephemeral=True)

    has_priority = (prios > 0 and tiempo_prios > 0)

    # Parsear los miembros prioritarios si se proporcionaron
    mentioned_users = []
    if miembros_prio:
        for mention in miembros_prio.split():
            try:
                user_id = int(mention.replace('<@', '').replace('!', '').replace('>', ''))
                user = interaction.guild.get_member(user_id) 
                if user:
                    mentioned_users.append(user)
            except ValueError:
                pass

    if has_priority:
        if interaction.user not in mentioned_users:
            mentioned_users.insert(0, interaction.user)

        if len(mentioned_users) > prios:
            return await interaction.response.send_message(f"❌ Solo puedes asignar {prios} usuarios prioritarios. Has mencionado {len(mentioned_users)} (incluyéndote).", ephemeral=True)

    event_id = f"WB-{int(time.time())}"
    description_content = WB_BOSS_DATA[boss_lower]["default_description"].format(duration=duracion)

    # Creamos la entrada del evento en el diccionario global
    wb_events[event_id] = {
        "caller": caller,
        "caller_id": interaction.user.id,
        "boss": boss_lower,
        "inscriptions": {role: [] for role in WB_BOSS_DATA[boss_lower]["roles"]},
        "waitlist": {role: [] for role in WB_BOSS_DATA[boss_lower]["roles"]},
        "priority_mode": has_priority,
        "priority_slots": prios if has_priority else 0,
        "priority_minutes": tiempo_prios if has_priority else 0,
        "message": None,
        "channel_id": interaction.channel.id,
        "description": description_content
    }

    # Asignamos el evento a una variable local para evitar el UnboundLocalError
    event = wb_events[event_id]

    embed_description = description_content
    footer_text = ""
    embed_color = 0x8B0000
    view_disabled = False

    if has_priority:
        priority_expiry_time = time.time() + (tiempo_prios * 60)
        wb_priority_users[event_id] = {
            "users": [user.id for user in mentioned_users],
            "expiry": priority_expiry_time,
            "slots": prios,
            "minutes": tiempo_prios
        }
        embed_description += (
            f"\n\n🎯 **Sistema de Prioridad Activado**\n"
            f"⏳ **Usuarios prioritarios:** {', '.join([f'<@{uid}>' for uid in wb_priority_users[event_id]['users']])}\n"
            f"🕒 **Bloqueo termina en:** <t:{int(priority_expiry_time)}:R>\n"
            f"📊 **Slots usados:** {len(mentioned_users)}/{prios}"
        )
        footer_text = "🔒 Solo usuarios prioritarios pueden anotarse"
        embed_color = 0xFF4500
        view_disabled = False
    else:
        footer_text = "🔓 Todos pueden anotarse"
        embed_color = 0x00FF00

    embed = discord.Embed(
        title=f"🌍 WORLD BOSS: {WB_BOSS_DATA[boss_lower]['name']} (Caller: {caller})",
        description=embed_description,
        color=embed_color
    )
    embed.set_footer(text=footer_text)

    for role in WB_BOSS_DATA[boss_lower]["roles"]:
        players_in_role = ", ".join([f"<@{uid}>" for uid in event["inscriptions"][role]])
        waitlist_players = ", ".join([f"<@{uid}>" for uid in event["waitlist"][role]])

        role_status = ""
        if players_in_role:
            role_status += f"👥 {players_in_role}"
        if waitlist_players:
            role_status += f"\n⏳ Espera: {waitlist_players}"

        if not role_status:
            role_status = "🚫 Vacío"

        embed.add_field(
            name=f"{WB_BOSS_DATA[boss_lower]['emojis'].get(role)} {role} ({len(event['inscriptions'][role])}/{WB_BOSS_DATA[boss_lower]['roles'][role]} +{len(event['waitlist'][role])} en espera)",
            value=role_status,
            inline=False
        )

    # --- MODIFICACIÓN: Pasamos el caller_id a la vista ---
    view = WB_RoleSelectorView(boss_lower, event_id, interaction.user.id, disabled=view_disabled)

    await interaction.response.send_message(embed=embed, view=view)
    message = await interaction.original_response()
    event["message"] = message

    # --- DIAGNÓSTICO: Verificamos si llegamos a esta parte del código y si el mensaje es válido ---
    print("\n--- Intentando crear el hilo para /wb...")
    print(f"Objeto del mensaje: {message}")

    try:
        thread = await message.create_thread(name=f"💬 Discusión sobre WB {WB_BOSS_DATA[boss_lower]['name']}")
        print(f"Hilo creado con éxito: {thread.name}")
    except discord.Forbidden:
        print("ERROR: No se pudo crear el hilo. A pesar de los permisos de Administrador, algo está impidiendo la creación. Revisa los permisos del canal.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al crear el hilo: {e}")

# --- Comandos de Prefijo para Roaming ---
@bot.command(name='roaming', aliases=['r'])
async def roaming(ctx, party: str, tier: str = "T8", ip: int = 1400, *args):
    """
    Crea un evento de roaming con la opción de asignar un caller.
    Ej: !r kiteo1 8 1400 (caller es el que envía el comando)
    Ej: !r kiteo1 8 1400 Pepito (caller es Pepito)
    """
    party_lower = party.lower()
    if party_lower not in ROAMING_PARTIES:
        return await ctx.send("❌ Party inválido. Opciones disponibles: " + ", ".join(ROAMING_PARTIES.keys()))

    # Determina el nombre del caller a mostrar en el embed usando la nueva lógica
    caller_display = get_roaming_caller_info(ctx, args)

    event_id = f"{ctx.author.id}-{int(time.time())}"

    # Inicializa el diccionario de inscripciones y la lista de espera
    inscripciones_dict = {rol: [] for rol in ROAMING_PARTIES[party_lower]["roles"]}
    waitlist_dict = {rol: [] for rol in ROAMING_PARTIES[party_lower]["roles"]}

    # Crea la entrada en el diccionario global
    roaming_events[event_id] = {
        "event_id": event_id,
        "caller_id": ctx.author.id,  # Este ID siempre será el del usuario que lanzó el comando (para permisos)
        "caller_display": caller_display, # Este es el nombre a mostrar en el embed
        "channel_id": ctx.channel.id,
        "party": party_lower,
        "tier_min": tier.upper(),
        "ip_min": ip,
        "start_time": time.time(),
        "message": None,
        "inscripciones": inscripciones_dict,
        "waitlist": waitlist_dict # Campo necesario para la lista de espera
    }

    # Crea el embed y la vista con el menú desplegable y los botones
    embed = create_roaming_embed(party_lower, roaming_events[event_id])

    # Usa la clase de vista con los botones
    vista_botones = RoamingEventView(
        party=party_lower,
        event_id=event_id,
        caller_id=ctx.author.id,
        event_data=roaming_events[event_id]
    )

    # Envía el mensaje con la mención de rol y la vista
    mensaje_mencion = f"**¡Roaming de {party_lower.upper()} ha sido lanzado por {ctx.author.mention}!** "
    mensaje = await ctx.send(content=mensaje_mencion, embed=embed, view=vista_botones)

    # Guarda el objeto del mensaje para poder editarlo después
    roaming_events[event_id]["message"] = mensaje

    # --- DIAGNÓSTICO: Verificamos si llegamos a esta parte del código y si el mensaje es válido ---
    print("\n--- Intentando crear el hilo para !roaming...")
    print(f"Objeto del mensaje: {mensaje}")

    try:
        thread = await mensaje.create_thread(name=f"💬 Discusión sobre Roaming {party_lower.upper()}")
        print(f"Hilo creado con éxito: {thread.name}")
    except discord.Forbidden:
        print("ERROR: No se pudo crear el hilo. A pesar de los permisos de Administrador, algo está impidiendo la creación. Revisa los permisos del canal.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al crear el hilo: {e}")

# ====================================================================
# --- 6. EVENTOS DEL BOT ---
# ====================================================================

@bot.event
async def on_ready():
    """Se ejecuta cuando el bot está listo y conectado a Discord."""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    # --- 1. Sincronizar comandos slash ---
    try:
        # Sincroniza los comandos de la aplicación con Discord
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    # --- 2. Reanudar vistas persistentes ---
    try:
        # Re-añade las vistas para cualquier evento activo
        for event_id, event_data in roaming_events.items():
            if event_data.get("message"):
                # Obtenemos el canal y el mensaje por sus IDs
                channel = bot.get_channel(event_data["channel_id"])
                if channel:
                    try:
                        message = await channel.fetch_message(event_data["message"].id)
                        # Creamos y añadimos la vista de nuevo para que sea persistente
                        view = RoamingEventView(
                            party=event_data["party"],
                            event_id=event_id,
                            caller_id=event_data["caller_id"],
                            event_data=event_data
                        )
                        bot.add_view(view, message_id=message.id)
                        print(f"Re-added view for event {event_id}")
                    except discord.NotFound:
                        print(f"Message for event {event_id} not found. Skipping.")
                else:
                    print(f"Channel for event {event_id} not found. Skipping.")

    except Exception as e:
        print(f"Failed to re-add views: {e}")

    # --- 3. Iniciar tareas en bucle ---
    # Es crucial iniciar las tareas *dentro* de on_ready, donde el event loop ya está corriendo.
    if not cleanup_roaming_events.is_running():
        cleanup_roaming_events.start()
        print("Started cleanup_roaming_events task.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# ====================================================================
# --- 7. TAREAS EN BUCLE (LOOP TASKS) ---
# ====================================================================

# Tarea para limpiar eventos de roaming antiguos
@tasks.loop(minutes=30)
async def cleanup_roaming_events():
    now = time.time()
    events_to_remove = []
    for event_id, event_data in roaming_events.items():
        # Clean up roaming events older than the timeout
        if (now - event_data["start_time"]) > ROAMING_EVENT_TIMEOUT:
            events_to_remove.append(event_id)

    for event_id in events_to_remove:
        event_data = roaming_events.get(event_id)
        if event_data:
            print(f"Cleaning up roaming event {event_id} due to timeout.")
            # Optional: Edit message to show it's expired
            message = event_data.get("message")
            if message:
                try:
                    embed = message.embeds[0]
                    embed.title = f"⚠️ ROAMING {event_data['party'].upper()} (EXPIRADO)"
                    embed.description = "**Este evento ha expirado y se ha cerrado automáticamente.**"
                    embed.color = discord.Color.dark_gray()
                    view = RoamingEventView(event_data['party'], event_id, event_data['caller_id'], event_data)
                    for item in view.children:
                        item.disabled = True
                    await message.edit(embed=embed, view=view)
                except Exception as e:
                    print(f"Error editing expired roaming message: {e}")
            del roaming_events[event_id]

# La función before_loop se mantiene igual, ya que es la forma correcta de esperar.
@cleanup_roaming_events.before_loop
async def before_cleanup_roaming():
    await bot.wait_until_ready()

# ====================================================================
# --- 8. EJECUCIÓN DEL BOT ---
# ====================================================================
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
