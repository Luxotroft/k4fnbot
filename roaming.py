import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import time
import random
import re

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
            "GA": "<:GranArcano:1337861969931407411>", "LOCUS": "<:Locus:12914674222238249043>",
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
            "PUTREFACTO": "<:Putrefacto:1370577320171016202>", "OCULTO": "<:Oculto:1337862058779218026>", "WITCHWORD": "<:witchword:1392942341815533758>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "PRISMA": "<:Prisma:1367151400672559184>", "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
            "SANTI": "<:Santificador:1290858870260109384>", "TORRE_MOVIL": "<:MonturaMana:1337863658859925676>",
        }
    },
    "pocho": {
        "max_players": 22,
        "roles": {
            "GOLEM": 1, "PESADA": 2, "MARTILLO 1 H": 1, "JURADORES": 1, "LIFECURSED": 1, "LOCUS": 1,
            "ENRAIZADO": 1, "GARZA": 1, "TALLADA": 1, "CAZAESPÍRITUS": 1, "DAMNATION": 1,
            "ROMPERREINOS": 1, "DEMONFANG": 2, "GUADAÑA": 1, "INFERNALES": 2, "GRAN BASTON SAGRADO": 2,
            "REDENCION": 1, "INFORTUNIO": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "PESADA": "<:stoper:1290858463135662080>",
            "MARTILLO 1 H": "<:stoper:1290858463135662080>", "JURADORES": "<:Maracas:1290858583965175828>",
            "LIFECURSED": "<:Maldi:1291467716229730415>", "LOCUS": "<:Locus:1291467422238249043>",
            "ENRAIZADO": "<:Enraizado:1290879541073678397>", "GARZA": "<:Garza:1334558585325228032>",
            "TALLADA": "<:Tallada:1290881286092886172>", "CAZAESPÍRITUS": "<:Cazaespiritu:1290881433816137821>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "ROMPERREINOS": "<:RompeReino:1290881352182399017>",
            "DEMONFANG": "<:Colmillo:1370577697516032031>", "GUADAÑA": "<:Guadaa:1291468660917014538>",
            "INFERNALES": "<:Infernales:1334556778465198163>", "GRAN BASTON SAGRADO": "<:gransagrado:1395086071275982848>",
            "REDENCION": "<:redencion:1395086294442573957>", "INFORTUNIO": "<:Infortunio:1290858784528531537>",
        },
        "mutually_exclusive_groups": [
            {"roles": ["MARTILLO 1 H", "PESADA"], "max_total": 2}, # Max 2 entre estos 2 roles
            {"roles": ["GOLEM", "PESADA"], "max_total": 2}, # Max 2 entre estos 2 roles
            {"roles": ["INFERNALES", "GRAN BASTON SAGRADO"], "max_total": 2}, # Max 2 entre estos 2 roles
        ]
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
            "GOLEM": "<:Terrunico:1290880192092438540>", "MARTILLO 1H": "<:stoper:1290858463135662080>", "MAZA PESADA": "<:stoper:1290858463135662080>", "MONARCA": "<:monarca:1395087126017867836>", "SAGRADO": "✨",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>", "ENRAIZADO": "<:Enraizado:1290879541073678397>", "JURADORES": "<:Maracas:1290858583965175828>", "LIFECURSED": "<:Maldi:1291467716229730415>", "TALLADA": "<:Tallada:1290881286092886172>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "ROMPERREINO": "<:RompeReino:1290881352182399017>", "DEMONFANG": "<:Colmillo:1370577697516032031>", "GUADAÑA": "<:Guadaa:1291468660917014538>", "PUAS": "<:Puas:1291468593506029638>",
            "ZARPAS": "<:Zarpas:1334560618941911181>", "ASTRAL": "<:Astral:1334556937328525413>", "HOJA INFINITA": "<:hoja:1395087940417228920>",
        }
    },
    "brawl2": {
        "max_players": 20,
        "roles": {
            "Maza pesada": 1, "Martillo de una mano": 1, "Baston de equilibrio": 1, "Santificador": 3, "Infortunio": 1,
            "Juradores": 1, "Silvano": 1, "Romperreinos": 1, "Putrefacto": 1, "Tallada": 1,
            "Astral": 1, "Patas de oso": 1, "Hoja infinita": 3, "Colmillo": 1, "Guadaña": 1, "Puas": 1
        },
        "emojis": {
            "Maza pesada": "<:stoper:1290858463135662080>", "Martillo de una mano": "<:CALLER:1367141230596853761>",
            "Baston de equilibrio": "<:Equilibrado:1291466491803471933>", "Santificador": "<:Hallowfall:1361429140460539973>",
            "Infortunio": "<:Infortunio:1290858784528531537>", "Juradores": "<:Maracas:1290858583965175828>",
            "Silvano": "<:Enraizado:1290879541073678397>", "Romperreinos": "<:RompeReino:1290881352182399017>",
            "Putrefacto": "<:Putrefacto:1370577320171016202>", "Tallada": "<:Tallada:1290881286092886172>",
            "Astral": "<:Astral:1334556937328525413>", "Patas de oso": "<:PatasDeOso:1272599457778630737>",
            "Hoja infinita": "<:hoja:1395087940417228920>", "Colmillo": "<:Colmillo:1370577697516032031>",
            "Guadaña": "<:Guadaa:1291468660917014538>", "Puas": "<:Puas:1291468593506029638>"
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

roaming_events = {} # Diccionario para almacenar los eventos de roaming activos
ROAMING_EVENT_TIMEOUT = 7200 # 2 horas

# ====================================================================
# --- FUNCIONES HELPER ---
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

        linea = f"{emoji} **{rol.ljust(15)}** {slots.rjust(5)} → {jugadores or '-'}"
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
    )
    # El @everyone se envía fuera del embed. Aquí solo se indica un estado.
    if total_inscritos < 15:
        reglas += "▸ 🔔 **Se necesita más gente!**"
    else:
        reglas += "▸ ✅ **Listo para salir!**"

    embed.add_field(name="📜 REGLAS DEL ROAMING", value=reglas, inline=False)
    return embed

# ====================================================================
# --- VISTAS Y COMPONENTES DE UI ---
# ====================================================================

class RoamingRoleDropdown(discord.ui.Select):
    def __init__(self, event_id: str, party_name: str):
        self.event_id = event_id
        self.party_name = party_name
        
        party_data = ROAMING_PARTIES.get(party_name)
        options = []
        if party_data:
            for role_name, _ in party_data["roles"].items():
                emoji = party_data["emojis"].get(role_name, "❓")
                options.append(discord.SelectOption(label=role_name, emoji=emoji, value=role_name))

        super().__init__(placeholder="Selecciona tu rol...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        selected_role = self.values[0]
        event = roaming_events.get(self.event_id)
        party_data = ROAMING_PARTIES.get(self.party_name)

        if not event or not party_data:
            await interaction.followup.send("Este evento de roaming ya no existe o es inválido.", ephemeral=True)
            return

        inscripciones = event.get("inscripciones", {})
        waitlist = event.get("waitlist", {})
        
        # 1. Eliminar al usuario de CUALQUIER rol o lista de espera
        user_id_str = str(user.id)
        user_removed_from_old_spot = False

        # Check inscripciones
        for role_name_in_insc, players_in_role in inscripciones.items():
            if user_id_str in players_in_role:
                inscripciones[role_name_in_insc].remove(user_id_str)
                user_removed_from_old_spot = True
                # Si el rol liberado tiene lista de espera, mover al primero de la espera al rol
                if waitlist.get(role_name_in_insc):
                    next_player_id = waitlist[role_name_in_insc].pop(0)
                    inscripciones[role_name_in_insc].append(next_player_id)
                    next_player_obj = interaction.guild.get_member(int(next_player_id)) # Intenta obtener el miembro
                    if next_player_obj:
                         await interaction.followup.send(f"<@{next_player_id}>, has sido movido a **{role_name_in_insc}**.", ephemeral=False)
                    else:
                        print(f"No se pudo encontrar el miembro con ID {next_player_id} para notificación.")
                break # Solo puede estar en un rol a la vez

        # Check waitlist (si no fue removido de inscripciones)
        if not user_removed_from_old_spot:
            for role_name_in_wl, players_in_wl in waitlist.items():
                if user_id_str in players_in_wl:
                    waitlist[role_name_in_wl].remove(user_id_str)
                    user_removed_from_old_spot = True
                    break

        # 2. Procesar nueva inscripción
        max_slots = party_data["roles"][selected_role]
        
        # Asegurarse de que las estructuras estén inicializadas
        if selected_role not in inscripciones:
            inscripciones[selected_role] = []
        if selected_role not in waitlist:
            waitlist[selected_role] = []

        current_players_in_role = len(inscripciones[selected_role])
        
        if current_players_in_role < max_slots:
            if user_id_str not in inscripciones[selected_role]: # Evitar duplicados
                inscripciones[selected_role].append(user_id_str)
                msg = f"¡Te has inscrito como **{selected_role}**!"
                if user_removed_from_old_spot:
                    msg += "\n(Tu inscripción anterior ha sido eliminada.)"
                await interaction.followup.send(msg, ephemeral=True)
            else:
                msg = f"ℹ️ Ya estás inscrito como **{selected_role}**."
                await interaction.followup.send(msg, ephemeral=True)
        else:
            # Añadir a la lista de espera
            if user_id_str not in waitlist[selected_role]: # Evitar duplicados
                waitlist[selected_role].append(user_id_str)
                msg = f"**{selected_role}** está lleno. Has sido añadido a la lista de espera para este rol."
                if user_removed_from_old_spot:
                    msg += "\n(Tu inscripción anterior ha sido eliminada.)"
                await interaction.followup.send(msg, ephemeral=True)
            else:
                msg = f"ℹ️ Ya estás en la lista de espera para **{selected_role}**."
                await interaction.followup.send(msg, ephemeral=True)
        
        # Actualizar el mensaje del embed
        if event.get("message"):
            updated_embed = create_roaming_embed(self.party_name, event)
            if updated_embed:
                await event["message"].edit(embed=updated_embed, view=RoamingView(self.event_id, self.party_name, event.get("caller_id")))

class RoamingView(discord.ui.View):
    def __init__(self, event_id: str, party_name: str, caller_id: int):
        super().__init__(timeout=None) # La vista persiste indefinidamente
        self.event_id = event_id
        self.party_name = party_name
        self.caller_id = caller_id
        
        # Añadir el dropdown de roles
        self.add_item(RoamingRoleDropdown(event_id, party_name))

    @discord.ui.button(label="Salir de Roaming", style=discord.ButtonStyle.red, emoji="🏃", custom_id="roaming_leave_button")
    async def leave_roaming(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        event = roaming_events.get(self.event_id)
        
        if not event:
            await interaction.followup.send("Este evento de roaming ya no existe.", ephemeral=True)
            return

        user_id_str = str(user.id)
        user_found_and_removed = False

        # Eliminar de inscripciones
        for role_name, players in event["inscripciones"].items():
            if user_id_str in players:
                event["inscripciones"][role_name].remove(user_id_str)
                user_found_and_removed = True
                # Mover de la lista de espera al rol si hay espacio
                if event["waitlist"].get(role_name):
                    next_player_id = event["waitlist"][role_name].pop(0)
                    event["inscripciones"][role_name].append(next_player_id)
                    next_player_obj = interaction.guild.get_member(int(next_player_id))
                    if next_player_obj:
                         await interaction.followup.send(f"<@{next_player_id}>, has sido movido a **{role_name}**.", ephemeral=False)
                break
        
        # Eliminar de lista de espera si no estaba en inscripciones
        if not user_found_and_removed:
            for role_name, players in event["waitlist"].items():
                if user_id_str in players:
                    event["waitlist"][role_name].remove(user_id_str)
                    user_found_and_removed = True
                    break

        if user_found_and_removed:
            await interaction.followup.send("Has abandonado tu rol/lugar en la lista de espera para este roaming.", ephemeral=True)
            if event.get("message"):
                updated_embed = create_roaming_embed(self.party_name, event)
                await event["message"].edit(embed=updated_embed, view=RoamingView(self.event_id, self.party_name, self.caller_id))
        else:
            await interaction.followup.send("No estabas inscrito en ningún rol o lista de espera para este roaming.", ephemeral=True)

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="-", custom_id="roaming_close_button")
    async def close_roaming(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el creador del evento puede cerrarlo.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        event_data = roaming_events.get(self.event_id)

        if not event_data:
            await interaction.followup.send("Este evento de roaming ya no existe.", ephemeral=True)
            return

        # Eliminar el hilo si existe
        if event_data.get("thread_id") and event_data.get("channel_id"):
            try:
                guild = interaction.guild
                if guild:
                    channel = guild.get_channel(event_data["channel_id"])
                    if channel:
                        thread = None
                        try:
                            thread = await channel.fetch_thread(event_data["thread_id"])
                        except discord.NotFound:
                            pass
                        
                        if thread:
                            if thread.archived:
                                await thread.edit(archived=False, reason="Desarchivando para eliminar roaming")
                            await thread.delete()
                            print(f"Hilo de Roaming {self.event_id} eliminado.")
                    else:
                        print(f"Canal principal {event_data['channel_id']} no encontrado para el hilo del Roaming {self.event_id}.")
            except (discord.NotFound, discord.Forbidden) as e:
                print(f"Error al eliminar hilo de Roaming {self.event_id}: {e}. Puede que ya no exista o permisos insuficientes.")
            except Exception as e:
                print(f"Error inesperado al eliminar hilo de Roaming {self.event_id}: {e}")

        # Eliminar el mensaje principal
        if event_data.get("message_id") and event_data.get("channel_id"):
            try:
                guild = interaction.guild
                if guild:
                    channel = guild.get_channel(event_data["channel_id"])
                    if channel:
                        message_to_delete = await channel.fetch_message(event_data["message_id"])
                        await message_to_delete.delete()
                        print(f"Mensaje de Roaming {self.event_id} eliminado.")
            except (discord.NotFound, discord.Forbidden) as e:
                print(f"Error al eliminar mensaje de Roaming {self.event_id}: {e}. Puede que ya no exista o permisos insuficientes.")
            except Exception as e:
                print(f"Error inesperado al eliminar mensaje de Roaming {self.event_id}: {e}")

        # Eliminar el evento del diccionario global
        if self.event_id in roaming_events:
            del roaming_events[self.event_id]

        await interaction.followup.send("✅ Evento de Roaming cerrado y eliminado.", ephemeral=True)


# ====================================================================
# --- COG DE ROAMING ---
# ====================================================================

class RoamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_roaming_events.start()

    def cog_unload(self):
        self.cleanup_roaming_events.cancel()

    @commands.command(name='roaming')
    async def start_roaming_event(self, ctx, party_name: str, tier_min: int, ip_min: int, swap_gank_str: str, *, caller_display_name_or_none: str = None):
        """
        Inicia un evento de Roaming con party, tier, IP, swap de gank y caller opcional.
        Uso: !roaming <party> <tier_min> <ip_min> <swap_gank (si/no)> [caller_display_name]
        Ej: !roaming pocho 8 1300 si MiCaller
        """
        party_name_lower = party_name.lower()
        if party_name_lower not in ROAMING_PARTIES:
            await ctx.send(f"Party '{party_name}' no encontrada. Parties disponibles: {', '.join(ROAMING_PARTIES.keys())}")
            return

        party_data = ROAMING_PARTIES[party_name_lower]

        if not (1 <= tier_min <= 8):
            await ctx.send("El tier mínimo debe ser un número entre 1 y 8.")
            return
        
        try:
            ip_min = int(ip_min)
            if ip_min < 0: # O algún mínimo razonable, ej: 1000
                raise ValueError
        except ValueError:
            await ctx.send("La IP mínima debe ser un número válido.")
            return

        swap_gank = False
        if swap_gank_str.lower() in ('si', 'sí', 'y', 'yes'):
            swap_gank = True
        elif swap_gank_str.lower() in ('no', 'n'):
            swap_gank = False
        else:
            await ctx.send("El valor para 'swap de gank' debe ser 'si' o 'no'.")
            return
        
        caller_display = caller_display_name_or_none if caller_display_name_or_none else ctx.author.display_name

        event_id = f"roaming-{int(time.time())}-{random.randint(1000, 9999)}"

        event_data = {
            "event_id": event_id,
            "caller_id": ctx.author.id,
            "caller_display": caller_display,
            "channel_id": ctx.channel.id,
            "party_name": party_name_lower,
            "tier_min": tier_min,
            "ip_min": ip_min,
            "swap_gank": swap_gank,
            "inscripciones": {rol: [] for rol in party_data["roles"]},
            "waitlist": {rol: [] for rol in party_data["roles"]}, # Lista de espera por rol
            "start_time": time.time(),
            "message_id": None,
            "thread_id": None,
            "thread_channel_id": None,
            "time": datetime.now().strftime("%H:%M") # Hora actual para 'Hora de Salida' si no se especifica
        }

        # Enviar el @everyone primero
        try:
            await ctx.send(f"¡Atención @everyone! Se ha iniciado un nuevo Roaming: **{party_name.upper()}**!")
        except Exception as e:
            print(f"Error al enviar el @everyone para Roaming {event_id}: {e}")

        embed = create_roaming_embed(party_name_lower, event_data)
        view = RoamingView(event_id, party_name_lower, ctx.author.id)

        message = await ctx.send(embed=embed, view=view)
        event_data["message_id"] = message.id
        event_data["message"] = message # Guardar la referencia al objeto mensaje

        roaming_events[event_id] = event_data # Almacenar el evento después de obtener el message_id

        # Crear hilo de discusión
        try:
            thread_name = f"Roaming {party_name.upper()} - {caller_display}"
            thread = await message.create_thread(name=thread_name)
            await thread.send(f"¡Hilo de discusión para el roaming {party_name.upper()}!")
            event_data["thread_id"] = thread.id
            event_data["thread_channel_id"] = thread.id
        except Exception as e:
            print(f"Error al crear hilo para Roaming {event_id}: {e}")

        # Eliminar mensaje original del comando
        try:
            await ctx.message.delete()
        except:
            pass

    @tasks.loop(minutes=30)
    async def cleanup_roaming_events(self):
        """Limpia eventos de roaming antiguos que hayan superado un umbral de tiempo."""
        current_time = time.time()
        events_to_remove = []

        for event_id, event_data in roaming_events.items():
            if current_time - event_data["start_time"] > ROAMING_EVENT_TIMEOUT:
                events_to_remove.append(event_id)
        
        for event_id in events_to_remove:
            event_data = roaming_events.get(event_id)
            if event_data:
                # Intentar eliminar el mensaje principal del evento
                if event_data.get("message_id") and event_data.get("channel_id"):
                    try:
                        channel = self.bot.get_channel(event_data["channel_id"])
                        if channel:
                            message_to_delete = await channel.fetch_message(event_data["message_id"])
                            await message_to_delete.delete()
                            print(f"Mensaje de Roaming {event_id} eliminado durante la limpieza.")
                    except (discord.NotFound, discord.Forbidden):
                        print(f"Mensaje de Roaming {event_id} ya no existe o no se pudo acceder durante la limpieza.")
                    except Exception as e:
                        print(f"Error inesperado al eliminar mensaje de Roaming {event_id} durante la limpieza: {e}")

                # Intentar eliminar el hilo del evento
                if event_data.get("thread_id") and event_data.get("channel_id"):
                    try:
                        channel = self.bot.get_channel(event_data["channel_id"])
                        if channel:
                            thread_to_delete = await channel.fetch_thread(event_data["thread_id"])
                            if thread_to_delete.archived:
                                await thread_to_delete.edit(archived=False, reason="Desarchivando para eliminar en limpieza de Roaming")
                            await thread_to_delete.delete()
                            print(f"Hilo de Roaming {event_id} eliminado durante la limpieza.")
                    except (discord.NotFound, discord.Forbidden):
                        print(f"Hilo de Roaming {event_id} ya no existe o no se pudo acceder durante la limpieza.")
                    except Exception as e:
                        print(f"Error inesperado al eliminar hilo de Roaming {event_id} durante la limpieza: {e}")
                
                del roaming_events[event_id]

    @cleanup_roaming_events.before_loop
    async def before_cleanup_roaming(self):
        """Espera a que el bot esté listo antes de iniciar la tarea de limpieza."""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RoamingCog(bot))
