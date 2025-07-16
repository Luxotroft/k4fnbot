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
            "GARZA": "<:Garza:1334558585325228032>",
            "TALLADA": "<:Tallada:1290881286092886172>",
            "CAZAESPÍRITUS": "<:Cazaespiritu:1290881433816137821>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>",
            "ROMPERREINOS": "<:RompeReino:1290881352182399017>",
            "DEMONFANG": "<:Colmillo:1370577697516032031>",
            "GUADAÑA": "<:Guadaa:1291468660917014538>",
            "INFERNALES": "<:Infernales:1334556778465198163>",
            "GRAN BASTON SAGRADO": "<:gransagrado:1395086071275982848>",
            "REDENCION": "<:redencion:1395086294442573957>",
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
            "GOLEM": "<:Terrunico:1290880192092438540>", "MARTILLO 1H": "<:stoper:1290858463135662080>", "MAZA PESADA": "<:stoper:1290858463135662080>", "MONARCA": "<:monarca:1395087126017867836> ", "SAGRADO": "✨",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>", "ENRAIZADO": "<:Enraizado:1290879541073678397>", "JURADORES": "<:Maracas:1290858583965175828>", "LIFECURSED": "<:Maldi:1291467716229730415>", "TALLADA": "<:Tallada:1290881286092886172>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "ROMPERREINO": "<:RompeReino:1290881352182399017>", "DEMONFANG": "<:Colmillo:1370577697516032031>", "GUADAÑA": "<:Guadaa:1291468660917014538>", "PUAS": "<:Puas:1291468593506029638>",
            "ZARPAS": "<:Zarpas:1334560618941911181> ", "ASTRAL": "<:Astral:1334556937328525413>", "HOJA INFINITA": "<:hoja:1395087940417228920>",
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
            "Hoja infinita": "<:hoja:1395087940417228920>",
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

roaming_events = {} # Diccionario para almacenar los eventos activos de roaming

# ====================================================================
# --- FUNCIONES HELPER ---
# ====================================================================

def create_roaming_embed(party_name, event_data):
    """Genera el mensaje embed para el evento de roaming."""
    party = ROAMING_PARTIES.get(party_name)
    if not party:
        return None

    embed = discord.Embed(
        title=f"🚀 ROAMING {party_name.upper()} (Caller: {event_data['caller_display']})",
        color=0x00ff00 if "kiteo" in party_name else 0xFF0000
    )

    # Información básica
    total_inscritos = sum(len(players) for players in event_data["inscripciones"].values())
    embed.description = f"**📍 Salimos de Fort Sterling Portal**\nJugadores: {total_inscritos}/{party['max_players']}"

    # Agregar campos de roles
    roles_info = []
    for role_name, max_slots in party["roles"].items():
        emoji = party["emojis"].get(role_name, "")
        inscritos = event_data["inscripciones"].get(role_name, [])
        waitlist = event_data["waitlist"].get(role_name, [])
        
        players_str = ' '.join(f'<@{uid}>' for uid in inscritos) if inscritos else "🚫"
        waitlist_str = f" | ⏳ Espera: {' '.join(f'<@{uid}>' for uid in waitlist)}" if waitlist else ""
        
        roles_info.append(f"{emoji} **{role_name}** ({len(inscritos)}/{max_slots}) → {players_str}{waitlist_str}")

    # Dividir en campos si hay muchos roles
    for i in range(0, len(roles_info), 8):
        embed.add_field(
            name="🎮 ROLES DISPONIBLES" if i == 0 else "↳ Continuación",
            value="\n".join(roles_info[i:i+8]),
            inline=False
        )

    embed.set_footer(text=f"ID: {event_data['event_id']}")
    return embed

# ====================================================================
# --- VISTAS Y COMPONENTES DE UI ---
# ====================================================================

class RoleDropdown(discord.ui.Select):
    def __init__(self, party_name: str, event_id: str):
        self.party_name = party_name
        self.event_id = event_id
        party_data = ROAMING_PARTIES.get(party_name)
        
        options = []
        if party_data:
            for role_name, _ in party_data["roles"].items():
                emoji = party_data["emojis"].get(role_name, "❓")
                options.append(discord.SelectOption(label=role_name, emoji=emoji))

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
        waitlist = event.get("waitlist", [])
        
        # Verificar si el usuario ya está en algún rol o lista de espera
        user_already_in_any_role = False
        user_current_role = None

        for role, players in inscripciones.items():
            if any(p["id"] == user.id for p in players):
                user_already_in_any_role = True
                user_current_role = role
                break
        
        if not user_already_in_any_role:
            if any(p["id"] == user.id for p in waitlist):
                user_already_in_any_role = True
                user_current_role = "waitlist"

        if user_already_in_any_role:
            if user_current_role == selected_role:
                # Cancelar inscripción
                if selected_role in inscripciones:
                    inscripciones[selected_role] = [p for p in inscripciones[selected_role] if p["id"] != user.id]
                    await interaction.followup.send(f"Has cancelado tu inscripción en {selected_role}.", ephemeral=True)
                else:
                    waitlist[:] = [p for p in waitlist if not (p["id"] == user.id and p["desired_role"] == selected_role)]
                    await interaction.followup.send(f"Has cancelado tu lugar en la lista de espera para {selected_role}.", ephemeral=True)
            else:
                await interaction.followup.send(f"Ya estás inscrito en {user_current_role}. Cancela primero esa inscripción.", ephemeral=True)
        else:
            # Inscribir al nuevo rol
            max_slots = party_data["roles"][selected_role]
            current_players = len(inscripciones.get(selected_role, []))
            
            if current_players < max_slots:
                inscripciones.setdefault(selected_role, []).append({"id": user.id, "name": user.display_name})
                await interaction.followup.send(f"¡Te has inscrito como {selected_role}!", ephemeral=True)
            else:
                waitlist.append({"id": user.id, "name": user.display_name, "desired_role": selected_role})
                await interaction.followup.send(f"{selected_role} está lleno. Has sido añadido a la lista de espera.", ephemeral=True)
        
        # Actualizar el embed
        original_message = interaction.message
        updated_embed = create_roaming_embed(self.party_name, event)
        if updated_embed:
            await original_message.edit(embed=updated_embed, view=RoamingEventView(self.party_name, self.event_id, event["caller_id"], event))

class RoamingEventView(discord.ui.View):
    def __init__(self, party_name: str, event_id: str, caller_id: int, event_data: dict):
        super().__init__(timeout=None)
        self.party_name = party_name
        self.event_id = event_id
        self.caller_id = caller_id
        self.event_data = event_data
        
        self.add_item(RoleDropdown(party_name, event_id))
        
        # Botón para salir del rol
        self.add_item(discord.ui.Button(label="Salir de Rol", style=discord.ButtonStyle.red, emoji="🏃", custom_id=f"leave_{event_id}"))
        
        # Botón para lista de espera
        self.add_item(discord.ui.Button(label="Lista de Espera", style=discord.ButtonStyle.secondary, emoji="👥", custom_id=f"waitlist_{event_id}"))
        
        # Botón para cerrar evento (solo visible para el caller)
        if caller_id:
            self.add_item(discord.ui.Button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", custom_id=f"close_{event_id}"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Verificar botón de cerrar evento
        if interaction.custom_id and interaction.custom_id.startswith("close_"):
            if interaction.user.id != self.caller_id:
                await interaction.response.send_message("❌ Solo el caller puede cerrar el evento.", ephemeral=True)
                return False
        return True

# ====================================================================
# --- COG DE ROAMING ---
# ====================================================================

class RoamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_roaming_events.start()

    def cog_unload(self):
        self.cleanup_roaming_events.cancel()

    @commands.command(name='roaming', aliases=['r'])
    async def start_roaming_event(self, ctx, party_name: str, *args):
        """Inicia un evento de roaming"""
        party_name = party_name.lower()
        if party_name not in ROAMING_PARTIES:
            await ctx.send(f"Party '{party_name}' no encontrada. Parties disponibles: {', '.join(ROAMING_PARTIES.keys())}")
            return

        # Crear ID único para el evento
        event_id = f"roam-{int(time.time())}"
        
        # Configurar datos del evento
        event_data = {
            "event_id": event_id,
            "caller_id": ctx.author.id,
            "caller_display": ctx.author.display_name,
            "channel_id": ctx.channel.id,
            "party_name": party_name,
            "inscripciones": {role: [] for role in ROAMING_PARTIES[party_name]["roles"]},
            "waitlist": {role: [] for role in ROAMING_PARTIES[party_name]["roles"]},
            "start_time": time.time()
        }

        # Crear embed y vista
        embed = create_roaming_embed(party_name, event_data)
        view = RoamingEventView(party_name, event_id, ctx.author.id, event_data)

        # Enviar mensaje
        message = await ctx.send(embed=embed, view=view)
        event_data["message"] = message
        roaming_events[event_id] = event_data

        # Crear hilo de discusión
        try:
            thread = await message.create_thread(name=f"Roaming {party_name.upper()} - {ctx.author.display_name}")
            await thread.send(f"¡Hilo de discusión para el roaming {party_name.upper()}!")
        except Exception as e:
            print(f"Error al crear hilo: {e}")

        # Eliminar mensaje original del comando
        try:
            await ctx.message.delete()
        except:
            pass

    @tasks.loop(minutes=30)
    async def cleanup_roaming_events(self):
        """Limpia eventos de roaming antiguos"""
        current_time = time.time()
        events_to_remove = []

        for event_id, event_data in roaming_events.items():
            if current_time - event_data["start_time"] > 7200:  # 2 horas
                events_to_remove.append(event_id)

        for event_id in events_to_remove:
            event_data = roaming_events.get(event_id)
            if event_data and event_data.get("message"):
                try:
                    await event_data["message"].delete()
                except:
                    pass
            del roaming_events[event_id]

    @cleanup_roaming_events.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RoamingCog(bot))
