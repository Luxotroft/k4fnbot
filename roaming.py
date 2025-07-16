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
            "PUTREFACTO": "<:Putrefacto:1370577320171016202>", "OCULTO": "<:Oculto:1337862058779218026>", "WITCHWORD": "<:witchword:1392942341815533758>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "PRISMA": "<:Prisma:1367151400672559184>", "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
            "SANTI": "<:Santificador:1290858870260109384>", "TORRE_MOVIL": "<:MonturaMana:1337863658859925676>",
        }
    },
    "pocho": {
        "max_players": 22,
        "roles": {
            "GOLEM": 1,
            "PESADA": 2,
            "MARTILLO 1 H": 1,
            "JURADORES": 1,
            "LIFECURSED": 1,
            "LOCUS": 1,
            "ENRAIZADO": 1,
            "GARZA": 1,
            "TALLADA": 1,
            "CAZAESPÍRITUS": 1,
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
            "MARTILLO 1 H": "<:stoper:1290858463135662080>",
            "JURADORES": "<:Maracas:1290858583965175828>",
            "LIFECURSED": "<:Maldi:1291467716229730415>",
            "LOCUS": "<:Locus:1291467422238249043>",
            "ENRAIZADO": "<:Enraizado:1290879541073678397>",
            "GARZA": "🕊️",
            "TALLADA": "🪵",
            "CAZAESPÍRITUS": "<:Cazaespiritu:1290881433816137821>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>",
            "ROMPERREINOS": "<:RompeReino:1290881352182399017>",
            "DEMONFANG": "👹",
            "GUADAÑA": "💀",
            "INFERNALES": "🔥",
            "GRAN BASTON SAGRADO": "✨",
            "REDENCION": "💖",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>",
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

roaming_events = {} # Diccionario para almacenar los eventos de roaming activos
ROAMING_EVENT_TIMEOUT = 7200 # 2 horas


# ====================================================================
# --- FUNCIONES HELPER DE ROAMING ---
# ====================================================================

def create_roaming_embed(party, event_data):
    """Genera el mensaje embed para el evento de roaming."""
    embed = discord.Embed(
        title=f"⚔️ ¡ROAMING DE {party.upper()} ABIERTO! ⚔️",
        description="¡Anótate en el rol que mejor se adapte a ti!",
        color=0x00ff00
    )
    embed.set_thumbnail(url="https://assets.albiononline.com/assets/images/icons/faction_standings_lymhurst.png") # Ejemplo

    # Campos para Roles y sus inscripciones
    roles_str = []
    total_inscritos = 0

    # Asegurarse de que party es una clave válida en ROAMING_PARTIES
    if party not in ROAMING_PARTIES:
        return embed # O manejar el error de otra forma

    for rol, max_count in ROAMING_PARTIES[party]["roles"].items():
        inscritos = event_data["inscripciones"].get(rol, [])
        waitlist_players = event_data["waitlist"].get(rol, [])
        total_inscritos += len(inscritos)

        emoji = ROAMING_PARTIES[party]["emojis"].get(rol, "❓") # Emoji predeterminado si no se encuentra
        
        jugadores_insc = ' '.join(f'<@{uid}>' for uid in inscritos)
        if jugadores_insc:
            linea = f"{emoji} **{rol.ljust(20)}** ({len(inscritos)}/{max_count}) → {jugadores_insc}"
        else:
            linea = f"{emoji} **{rol.ljust(20)}** ({len(inscritos)}/{max_count}) → 🚫"
        
        if waitlist_players:
            jugadores_wait = ' '.join(f'<@{uid}>' for uid in waitlist_players)
            linea += f" | ⏳ Espera: {jugadores_wait}"
        
        roles_str.append(linea)

    # Dividir los roles en múltiples campos si hay muchos
    for i in range(0, len(roles_str), 10): # Mostrar 10 roles por campo
        embed.add_field(
            name=f"🎮 ROLES DISPONIBLES ({total_inscritos}/{ROAMING_PARTIES[party]['max_players']} jugadores)" if i == 0 else "↳ Continuación",
            value="\n".join(roles_str[i:i+10]),
            inline=False
        )
    
    # Campo para la lista de "Otros" si existe
    otros_inscritos = event_data["inscripciones"].get("Otros", [])
    if otros_inscritos:
        embed.add_field(
            name="👥 Otros Inscritos",
            value=' '.join(f'<@{uid}>' for uid in otros_inscritos),
            inline=False
        )

    embed.set_footer(text=f"📊 {total_inscritos}/{ROAMING_PARTIES[party]['max_players']} jugadores | ID: {event_data['event_id']}")
    embed.timestamp = datetime.utcnow()
    return embed

async def update_roaming_embed(event_id, bot_instance):
    """Actualiza el mensaje embed de un evento de roaming."""
    if event_id not in roaming_events:
        return
    event = roaming_events[event_id]
    message = event["message"]

    if not message:
        return
    try:
        embed = create_roaming_embed(event["party"], event)
        view = RoamingEventView(event_id, event["caller_id"], bot_instance) # Pasa la instancia del bot
        await message.edit(embed=embed, view=view)
    except Exception as e:
        print(f"Error actualizando embed para el evento {event_id}: {e}")


# ====================================================================
# --- CLASES DE UI (VIEWS, BUTTONS, SELECTS) PARA ROAMING ---
# ====================================================================

class RoleDropdown(discord.ui.Select):
    def __init__(self, party, event_id):
        self.party = party
        self.event_id = event_id
        options = []
        for role_name, _ in ROAMING_PARTIES[party]["roles"].items():
            emoji_str = ROAMING_PARTIES[party]["emojis"].get(role_name, "❓")
            options.append(discord.SelectOption(label=role_name, value=role_name, emoji=emoji_str))
        
        # Añadir la opción "Otros" para roles no listados específicamente
        options.append(discord.SelectOption(label="Otros", value="Otros", emoji="👤"))

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
        for role_name in list(ROAMING_PARTIES[self.party]["roles"].keys()) + ["Otros"]:
            if user_id in event_data["inscripciones"].get(role_name, []):
                event_data["inscripciones"][role_name].remove(user_id)
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
        
        # Añadir al usuario al rol seleccionado o a la lista de espera
        inscripciones_rol = event_data["inscripciones"].setdefault(selected_role, [])
        max_players_for_role = ROAMING_PARTIES[self.party]["roles"].get(selected_role, 999) # 999 si es "Otros" o no tiene límite definido
        
        if user_id not in inscripciones_rol:
            if len(inscripciones_rol) < max_players_for_role:
                inscripciones_rol.append(user_id)
                await interaction.response.send_message(f"✅ Te has inscrito como **{selected_role}**.", ephemeral=True)
            else:
                # Si el rol está lleno, añadir a la lista de espera
                waitlist_rol = event_data["waitlist"].setdefault(selected_role, [])
                if user_id not in waitlist_rol:
                    waitlist_rol.append(user_id)
                    await interaction.response.send_message(f"⚠️ El rol de **{selected_role}** está lleno. Te hemos añadido a la lista de espera.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"ℹ️ Ya estás en la lista de espera para **{selected_role}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ Ya estás inscrito como **{selected_role}**.", ephemeral=True)
        
        await update_roaming_embed(self.event_id, self.view.bot_instance) # Pasa la instancia del bot desde la vista


class LeaveButton(discord.ui.Button):
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
        for role_name in list(ROAMING_PARTIES[event_data["party"]]["roles"].keys()) + ["Otros"]:
            if user_id in event_data["inscripciones"].get(role_name, []):
                event_data["inscripciones"][role_name].remove(user_id)
                found = True
                break
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
                found = True
                break
        
        if found:
            await interaction.response.send_message("✅ Te has salido del evento de roaming.", ephemeral=True)
            await update_roaming_embed(self.event_id, self.view.bot_instance) # Pasa la instancia del bot
        else:
            await interaction.response.send_message("ℹ️ No estabas inscrito en este evento de roaming.", ephemeral=True)


class RoamingEventView(discord.ui.View):
    def __init__(self, event_id, caller_id, bot_instance):
        super().__init__(timeout=None)
        self.caller_id = caller_id
        self.event_id = event_id
        self.bot_instance = bot_instance # Guardar la instancia del bot
        
        # Asegurarse de que el party existe en roaming_events antes de intentar acceder a él
        if event_id in roaming_events:
            party_type = roaming_events[event_id]["party"]
            self.add_item(RoleDropdown(party_type, event_id))
        else:
            # Si el evento no existe, no añadir el dropdown o manejar el error
            print(f"Error: No se encontró el evento {event_id} al crear la vista.")

        self.add_item(LeaveButton(event_id))

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", row=2)
    async def close_event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)
            return

        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento de roaming ya no está activo.", ephemeral=True)
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
            print(f"Mensaje del evento Roaming {self.event_id} ya eliminado.")
        except Exception as e:
            print(f"Error al eliminar el mensaje del evento Roaming {self.event_id}: {e}")

    @discord.ui.button(label="Resetear Inscripciones", style=discord.ButtonStyle.secondary, emoji="♻️", row=2)
    async def reset_inscriptions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede resetear las inscripciones.", ephemeral=True)
            return

        if self.event_id not in roaming_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return
        
        event_data = roaming_events[self.event_id]
        party_type = event_data["party"]
        event_data["inscripciones"] = {rol: [] for rol in ROAMING_PARTIES[party_type]["roles"].keys()}
        event_data["inscripciones"]["Otros"] = [] # Asegurarse de resetear también "Otros"
        event_data["waitlist"] = {rol: [] for rol in ROAMING_PARTIES[party_type]["roles"].keys()}
        event_data["waitlist"]["Otros"] = []

        await update_roaming_embed(self.event_id, self.bot_instance)
        await interaction.response.send_message("✅ Se han reseteado todas las inscripciones y listas de espera del evento.", ephemeral=True)


# ====================================================================
# --- COG DE ROAMING ---
# ====================================================================

class RoamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_roaming_events.start()

    def cog_unload(self):
        self.cleanup_roaming_events.cancel()

    @commands.command(name="roaming")
    async def roaming(self, ctx, party: str):
        party_lower = party.lower()
        if party_lower not in ROAMING_PARTIES:
            available_parties = ", ".join(ROAMING_PARTIES.keys())
            await ctx.send(f"❌ Tipo de roaming inválido. Opciones disponibles: {available_parties}")
            return

        # Generar un ID único para el evento de roaming
        event_id = f"{party_lower}-{random.randint(1000, 9999)}"
        while event_id in roaming_events: # Asegurarse de que el ID no esté ya en uso
            event_id = f"{party_lower}-{random.randint(1000, 9999)}"

        # Inicializar los datos del evento
        event_data = {
            "caller_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "thread_id": None, # Se llenará si se crea un hilo
            "message_id": None, # Se llenará después de enviar el mensaje
            "party": party_lower,
            "inscripciones": {rol: [] for rol in ROAMING_PARTIES[party_lower]["roles"].keys()},
            "waitlist": {rol: [] for rol in ROAMING_PARTIES[party_lower]["roles"].keys()},
            "creation_time": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        event_data["event_id"] = event_id # AÑADIDO: Asegura que event_id esté en event_data
        roaming_events[event_id] = event_data # Almacenar el evento


        embed = create_roaming_embed(party_lower, event_data) # Pasa los datos del evento
        view = RoamingEventView(event_id, ctx.author.id, self.bot) # Pasa la instancia del bot
        
        try:
            message = await ctx.send(embed=embed, view=view)
            event_data["message_id"] = message.id
            event_data["message"] = message # Almacenar el objeto mensaje para futuras ediciones
            
            # Crear un hilo asociado al mensaje si el canal lo permite
            if isinstance(ctx.channel, discord.TextChannel):
                thread = await message.create_thread(name=f"Roaming - {party.upper()}", auto_archive_duration=60)
                event_data["thread_id"] = thread.id
                await thread.send(f"¡Hilo de discusión para el roaming de {party.upper()}! <@{ctx.author.id}>", silent=True)
        except Exception as e:
            print(f"Error al enviar mensaje o crear hilo para Roaming: {e}")
            await ctx.send("❌ Hubo un error al crear el evento de roaming. Intenta de nuevo más tarde.")
            if event_id in roaming_events: # Si falló al enviar el mensaje, limpiar el evento
                del roaming_events[event_id]
            return

        # Intentar borrar el mensaje de invocación del comando para mantener el canal limpio
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("No tengo permisos para borrar el mensaje del comando original.")
        except discord.NotFound:
            pass # El mensaje ya fue borrado

    @tasks.loop(seconds=60)
    async def cleanup_roaming_events(self):
        """Tarea para limpiar eventos de roaming caducados."""
        events_to_remove = []
        current_time = datetime.utcnow()

        for event_id, event_data in list(roaming_events.items()): # Usar list() para permitir la eliminación durante la iteración
            creation_time = event_data.get("creation_time")
            message_id = event_data.get("message_id")
            channel_id = event_data.get("channel_id")

            # Si faltan datos críticos, marcar para eliminación
            if not creation_time or not message_id or not channel_id:
                print(f"Evento Roaming {event_id} incompleto, marcando para eliminación.")
                events_to_remove.append(event_id)
                continue

            # Si el evento ha excedido el tiempo de vida
            if (current_time - creation_time).total_seconds() > ROAMING_EVENT_TIMEOUT:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        print(f"Canal {channel_id} no encontrado para el evento Roaming {event_id}.")
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
                
                events_to_remove.append(event_id) # Marcar para eliminación después de intentar limpiar
            else:
                # Si el evento no ha expirado, pero el mensaje/thread no existe (quizás borrado manualmente), también limpiarlo
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.fetch_message(message_id) # Intenta obtener el mensaje para verificar si existe
                except discord.NotFound:
                    print(f"Mensaje del evento Roaming {event_id} no encontrado en el canal, marcando para eliminación.")
                    events_to_remove.append(event_id)
                except Exception as e:
                    print(f"Error verificando mensaje Roaming {event_id}: {e}")

        # Eliminar los eventos marcados después de la iteración
        for event_id in events_to_remove:
            if event_id in roaming_events:
                del roaming_events[event_id]

    @cleanup_roaming_events.before_loop
    async def before_cleanup_roaming(self):
        """Espera a que el bot esté listo antes de iniciar la tarea de limpieza."""
        await self.bot.wait_until_ready()


async def setup(bot):
    """Función de configuración para añadir el cog al bot."""
    await bot.add_cog(RoamingCog(bot))
