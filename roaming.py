import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import time
import random

# ====================================================================
# --- DATOS Y VARIABLES GLOBALES DE ROAMING ---
# ====================================================================

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
    }
}

roaming_events = {} # {event_id: {data}}
roaming_generic_counter = 0
ROAMING_EVENT_TIMEOUT = 7200 # 2 horas

# ====================================================================
# --- FUNCIONES HELPER DE ROAMING ---
# ====================================================================

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


async def update_roaming_embed(event_id):
    """Actualiza el mensaje de embed del evento de roaming con los datos más recientes."""
    if event_id not in roaming_events:
        print(f"Evento de roaming {event_id} no encontrado para actualización.")
        return

    event = roaming_events[event_id]
    party = event["party"]
    message = event["message"]

    if not message:
        print(f"Mensaje no encontrado para el evento de roaming {event_id}.")
        return

    try:
        updated_embed = create_roaming_embed(party, event)
        view = RoamingEventView(event_id, event["caller_id"], party)
        await message.edit(embed=updated_embed, view=view)
    except Exception as e:
        print(f"Error actualizando embed para el evento de roaming {event_id}: {e}")


# ====================================================================
# --- CLASES DE UI (VIEWS, BUTTONS, SELECTS) PARA ROAMING ---
# ====================================================================

class RoamingRoleDropdown(discord.ui.Select):
    def __init__(self, party, event_id):
        self.party = party
        self.event_id = event_id

        # Asegúrate de que los roles y emojis existan en ROAMING_PARTIES
        if party not in ROAMING_PARTIES:
            options = [discord.SelectOption(label="Error: Party no encontrada", value="error")]
        else:
            options = []
            for role_name in ROAMING_PARTIES[party]["roles"].keys():
                emoji_str = ROAMING_PARTIES[party]["emojis"].get(role_name)
                options.append(discord.SelectOption(label=role_name, value=role_name, emoji=emoji_str))

        super().__init__(
            placeholder="Elige tu rol...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento de roaming ya no está activo.", ephemeral=True)
            return

        selected_role = self.values[0]
        user_id = interaction.user.id
        event_data = roaming_events[self.event_id]

        # Eliminar al usuario de todos los roles de este evento antes de añadirlo
        for role_name in ROAMING_PARTIES[self.party]["roles"].keys():
            if user_id in event_data["inscripciones"].get(role_name, []):
                event_data["inscripciones"][role_name].remove(user_id)
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)

        # Añadir al usuario al rol seleccionado
        inscripciones_rol = event_data["inscripciones"].setdefault(selected_role, [])
        limite_rol = ROAMING_PARTIES[self.party]["roles"][selected_role]

        if len(inscripciones_rol) < limite_rol:
            if user_id not in inscripciones_rol:
                inscripciones_rol.append(user_id)
                await interaction.response.send_message(f"✅ Te has inscrito como **{selected_role}**.", ephemeral=True)
            else:
                await interaction.response.send_message(f"ℹ️ Ya estás inscrito como **{selected_role}**.", ephemeral=True)
        else:
            # Si el rol está lleno, añadir a la lista de espera
            waitlist_rol = event_data["waitlist"].setdefault(selected_role, [])
            if user_id not in waitlist_rol:
                waitlist_rol.append(user_id)
                await interaction.response.send_message(f"⚠️ El rol de **{selected_role}** está lleno. Te hemos añadido a la lista de espera.", ephemeral=True)
            else:
                await interaction.response.send_message(f"ℹ️ Ya estás en la lista de espera de **{selected_role}**.", ephemeral=True)
        
        await update_roaming_embed(self.event_id)


class RoamingLeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salirme", style=discord.ButtonStyle.red, emoji="👋", row=1)
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento de roaming ya no está activo.", ephemeral=True)
            return

        user_id = interaction.user.id
        event_data = roaming_events[self.event_id]
        found = False

        # Buscar y eliminar al usuario de inscripciones o lista de espera
        for role_name in ROAMING_PARTIES[event_data["party"]]["roles"].keys():
            if user_id in event_data["inscripciones"].get(role_name, []):
                event_data["inscripciones"][role_name].remove(user_id)
                found = True
                # Si se desinscribió de un rol, verificar la lista de espera y mover a alguien
                if event_data["waitlist"].get(role_name):
                    next_player_id = event_data["waitlist"][role_name].pop(0)
                    event_data["inscripciones"][role_name].append(next_player_id)
                    await interaction.followup.send(f"<@{next_player_id}>, ¡has sido movido de la lista de espera al rol de **{role_name}**!", ephemeral=False)
                break
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
                found = True
                break
        
        if found:
            await interaction.response.send_message("✅ Te has salido del evento.", ephemeral=True)
            await update_roaming_embed(self.event_id)
        else:
            await interaction.response.send_message("ℹ️ No estabas inscrito en este evento.", ephemeral=True)


class RoamingJoinWaitlistMainButton(discord.ui.Button):
    def __init__(self, party, event_id):
        super().__init__(label="Lista de Espera General", style=discord.ButtonStyle.grey, emoji="⏳", row=1)
        self.party = party
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento de roaming ya no está activo.", ephemeral=True)
            return

        user_id = interaction.user.id
        event_data = roaming_events[self.event_id]

        # Quitar al usuario de cualquier rol en el que esté inscrito
        for role_name in ROAMING_PARTIES[self.party]["roles"].keys():
            if user_id in event_data["inscripciones"].get(role_name, []):
                event_data["inscripciones"][role_name].remove(user_id)
                break
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
                break

        # Añadir a la lista de espera general (si no está ya)
        general_waitlist = event_data.setdefault("general_waitlist", [])
        if user_id not in general_waitlist:
            general_waitlist.append(user_id)
            await interaction.response.send_message("✅ Te has añadido a la lista de espera general.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Ya estás en la lista de espera general.", ephemeral=True)
        
        await update_roaming_embed(self.event_id)


class RoamingEventView(discord.ui.View):
    def __init__(self, event_id, caller_id, party):
        super().__init__(timeout=None)
        self.caller_id = caller_id
        self.event_id = event_id
        self.party = party
        self.add_item(RoamingRoleDropdown(party, event_id))
        self.add_item(RoamingLeaveButton(event_id))
        self.add_item(RoamingJoinWaitlistMainButton(party, event_id))

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", row=2)
    async def close_event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)
            return

        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return

        thread = interaction.message.thread
        if thread:
            try:
                if thread.archived:
                    await thread.edit(archived=False, reason="Desarchivando para eliminar")
                await thread.delete()
                print(f"Hilo del evento Roaming {self.event_id} eliminado correctamente.")
            except discord.NotFound:
                print(f"El hilo del evento Roaming {self.event_id} ya no existe.")
            except discord.Forbidden:
                print(f"Error: El bot no tiene el permiso 'Manage Threads' o 'Manage Channels' para eliminar el hilo del evento Roaming {self.event_id}.")
            except Exception as e:
                print(f"Error inesperado al eliminar el hilo del evento Roaming {self.event_id}: {e}")
        else:
            print("No se encontró un hilo asociado al mensaje del evento Roaming.")

        try:
            await interaction.message.delete()
            del roaming_events[self.event_id]
            await interaction.response.send_message("✅ Evento de roaming cerrado y mensaje eliminado.", ephemeral=True)
        except discord.NotFound:
            print(f"Mensaje del evento de roaming {self.event_id} ya eliminado.")
        except Exception as e:
            print(f"Error al eliminar el mensaje del evento de roaming {self.event_id}: {e}")

    @discord.ui.button(label="Resetear Inscripciones", style=discord.ButtonStyle.secondary, emoji="♻️", row=2)
    async def reset_inscriptions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede resetear las inscripciones.", ephemeral=True)
            return

        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return
        
        event_data = roaming_events[self.event_id]
        event_data["inscripciones"] = {rol: [] for rol in ROAMING_PARTIES[event_data["party"]]["roles"].keys()}
        event_data["waitlist"] = {rol: [] for rol in ROAMING_PARTIES[event_data["party"]]["roles"].keys()}
        event_data["general_waitlist"] = []

        await update_roaming_embed(self.event_id)
        await interaction.response.send_message("✅ Se han reseteado todas las inscripciones y listas de espera del evento.", ephemeral=True)


# ====================================================================
# --- COG DE ROAMING ---
# ====================================================================

class RoamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_roaming_events.start() # Inicia la tarea de limpieza

    def cog_unload(self):
        self.cleanup_roaming_events.cancel() # Detiene la tarea cuando el cog se descarga

    @commands.command(name="roaming", aliases=["roam", "r"])
    async def roaming(self, ctx, party: str, tier_min: int = 0, ip_min: int = 0, time: str = None, swap_gank: str = None, *args):
        party_lower = party.lower()
        if party_lower not in ROAMING_PARTIES:
            await ctx.send(f"❌ La composición de roaming '{party}' no existe. Composiciones disponibles: {', '.join(ROAMING_PARTIES.keys())}")
            return

        # Validar tier e IP mínimas
        if tier_min == 0:
            tier_min = 8 # Default a T8
        if ip_min == 0:
            ip_min = 1400 # Default a 1400 IP

        # Determinar el nombre del caller (último argumento de *args si es un string)
        caller_display = get_roaming_caller_info(ctx, args)

        # Manejar 'swap_gank' de forma flexible
        swap_gank_bool = False
        if swap_gank:
            swap_gank_lower = swap_gank.lower()
            if swap_gank_lower in ['si', 'sí', 's', 'y', 'yes', 'true']:
                swap_gank_bool = True
            elif swap_gank_lower in ['no', 'n', 'false']:
                swap_gank_bool = False
            else:
                await ctx.send("⚠️ Valor inválido para `swap_gank`. Usa 'si' o 'no'. Se asumirá 'no'.", ephemeral=True)
                swap_gank_bool = False


        event_id = f"roaming-{random.randint(1000, 9999)}"
        # Asegurarse de que el ID sea único
        while event_id in roaming_events:
            event_id = f"roaming-{random.randint(1000, 9999)}"

        event_data = {
            "party": party_lower,
            "caller_id": ctx.author.id,
            "caller_display": caller_display,
            "channel_id": ctx.channel.id,
            "thread_id": None, # Se llenará si se crea un hilo
            "message_id": None, # Se llenará con el ID del mensaje del embed
            "inscripciones": {rol: [] for rol in ROAMING_PARTIES[party_lower]["roles"].keys()},
            "waitlist": {rol: [] for rol in ROAMING_PARTIES[party_lower]["roles"].keys()},
            "general_waitlist": [], # Nueva lista de espera general
            "creation_time": datetime.utcnow(),
            "tier_min": tier_min,
            "ip_min": ip_min,
            "time": time,
            "swap_gank": swap_gank_bool
        }
        roaming_events[event_id] = event_data

        embed = create_roaming_embed(party_lower, event_data)
        view = RoamingEventView(event_id, ctx.author.id, party_lower)
        
        try:
            # Enviar el mensaje inicial y guardar su ID
            message = await ctx.send(embed=embed, view=view)
            event_data["message_id"] = message.id
            event_data["message"] = message # Guardar el objeto mensaje para futuras actualizaciones

            # Crear un hilo si es un canal de texto
            if isinstance(ctx.channel, discord.TextChannel):
                thread = await message.create_thread(name=f"Roaming {party.upper()} - {caller_display}", auto_archive_duration=60)
                event_data["thread_id"] = thread.id
                await thread.send(f"¡Hilo de discusión para el roaming '{party.upper()}'! <@{ctx.author.id}>", silent=True)
        except Exception as e:
            print(f"Error al enviar mensaje o crear hilo para roaming: {e}")
            await ctx.send("❌ Hubo un error al crear el evento de roaming. Intenta de nuevo más tarde.")
            if event_id in roaming_events:
                del roaming_events[event_id] # Limpiar evento si falla la creación del mensaje/hilo
            return

        # Limpiar el comando original
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("No tengo permisos para borrar el mensaje del comando original.")
        except discord.NotFound:
            pass # Mensaje ya borrado

    @tasks.loop(seconds=60) # Ejecutar cada 60 segundos
    async def cleanup_roaming_events(self):
        events_to_remove = []
        current_time = datetime.utcnow()

        for event_id, event_data in list(roaming_events.items()):
            creation_time = event_data.get("creation_time")
            message_id = event_data.get("message_id")
            thread_id = event_data.get("thread_id")
            channel_id = event_data.get("channel_id")

            if not creation_time or not message_id or not channel_id:
                print(f"Evento de roaming {event_id} incompleto, marcando para eliminación.")
                events_to_remove.append(event_id)
                continue

            # Convertir creation_time a datetime si es necesario (ya debería serlo)
            if not isinstance(creation_time, datetime):
                creation_time = datetime.fromisoformat(creation_time.isoformat()) # Asegura que sea datetime

            if (current_time - creation_time).total_seconds() > ROAMING_EVENT_TIMEOUT:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        print(f"Canal {channel_id} no encontrado para el evento roaming {event_id}.")
                        events_to_remove.append(event_id)
                        continue

                    message = await channel.fetch_message(message_id)
                    thread = message.thread
                    if thread:
                        if thread.archived:
                            await thread.edit(archived=False, reason="Desarchivando para eliminar por expiración Roaming")
                        await thread.delete()
                        print(f"Hilo del evento Roaming expirado {event_id} eliminado.")
                    await message.delete()
                    print(f"Mensaje del evento Roaming expirado {event_id} eliminado.")
                except discord.NotFound:
                    print(f"Mensaje o hilo del evento Roaming expirado {event_id} ya no existe.")
                except discord.Forbidden:
                    print(f"Fallo al eliminar el mensaje/hilo del evento Roaming expirado {event_id}. Permisos faltantes.")
                except Exception as e:
                    print(f"Error inesperado al eliminar el mensaje del evento Roaming expirado {event_id}: {e}")
                
                events_to_remove.append(event_id)
        
        for event_id in events_to_remove:
            if event_id in roaming_events:
                del roaming_events[event_id]

    @cleanup_roaming_events.before_loop
    async def before_cleanup_roaming(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(RoamingCog(bot))
