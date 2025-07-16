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
        "mutually_exclusive_groups": [ # <--- FUNCIONALIDAD AÑADIDA
            {"roles": ["LOCUS", "ENRAIZADO"], "max_slots": 1},
            {"roles": ["TALLADA", "CAZAESPÍRITUS"], "max_slots": 1}
        ],
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
# --- 1. FUNCIÓN PARA CREAR EL EMBED DE ROAMING ---
# ====================================================================

def create_roaming_embed(party_name):
    party = ROAMING_PARTIES.get(party_name)
    if not party:
        return None

    title_map = {
        "kiteo1": "Kiteo 1",
        "kiteo2": "Kiteo 2",
        "pocho": "POCHO",
        "brawl": "Brawl",
        "brawl2": "Brawl 2",
        "brawl_gucci": "Brawl Gucci"
    }

    title = title_map.get(party_name, f"Evento de Roaming: {party_name.capitalize()}")
    color = 0xFF0000 # Rojo
    description = f"**{title}**\n\n"

    total_roles = sum(party["roles"].values())
    current_players = sum(len(players) for players in roaming_events.get(party_name, {}).get("inscripciones", {}).values())
    
    # Calcular el número de jugadores en la lista de espera
    waitlist_count = len(roaming_events.get(party_name, {}).get("waitlist", []))

    description += f"Jugadores inscritos: `{current_players}/{party['max_players']}`\n"
    if waitlist_count > 0:
        description += f"En lista de espera: `{waitlist_count}`\n"
    description += "\n"

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    inscripciones = roaming_events.get(party_name, {}).get("inscripciones", {})
    waitlist = roaming_events.get(party_name, {}).get("waitlist", [])

    # Añadir los campos de roles con jugadores
    for role, max_slots in party["roles"].items():
        players = inscripciones.get(role, [])
        player_names = [player["name"] for player in players]
        
        emoji = party["emojis"].get(role, "❓") # Emoji genérico si no se encuentra uno específico
        
        # Formatear la lista de jugadores inscritos
        if player_names:
            players_str = "\n".join([f"- {name}" for name in player_names])
        else:
            players_str = "Nadie"
            
        embed.add_field(
            name=f"{emoji} {role} (`{len(players)}/{max_slots}`)",
            value=players_str,
            inline=True
        )

    # Añadir la lista de espera si hay jugadores
    if waitlist:
        waitlist_names = [player["name"] for player in waitlist]
        waitlist_str = "\n".join([f"- {name}" for name in waitlist_names])
        embed.add_field(
            name="⌛ Lista de Espera",
            value=waitlist_str,
            inline=False
        )
    
    embed.set_footer(text="Haz clic en un rol para inscribirte o cancelar tu inscripción.")

    return embed

# ====================================================================
# --- 2. VISTAS Y MENÚ DESPLEGABLE ---
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
        await interaction.response.defer(ephemeral=True) # Defer para evitar timeout y ocultar mensaje

        user = interaction.user
        selected_role = self.values[0]
        event = roaming_events.get(self.event_id)
        party_data = ROAMING_PARTIES.get(self.party_name)

        if not event or not party_data:
            await interaction.followup.send("Este evento de roaming ya no existe o es inválido.", ephemeral=True)
            return

        inscripciones = event.get("inscripciones", {})
        waitlist = event.get("waitlist", [])
        
        # Variables para verificar si el usuario ya está en alguna inscripción o lista de espera
        user_already_in_any_role = False
        user_current_role = None

        # Verificar si el usuario ya está inscrito en algún rol
        for role, players in inscripciones.items():
            if any(p["id"] == user.id for p in players):
                user_already_in_any_role = True
                user_current_role = role
                break
        
        # Si el usuario no está inscrito, verificar si está en lista de espera
        if not user_already_in_any_role:
            if any(p["id"] == user.id for p in waitlist):
                user_already_in_any_role = True
                user_current_role = "waitlist" # Marcador para indicar que está en waitlist

        # --- Lógica para roles mutuamente excluyentes ---
        is_mutually_exclusive_role = False
        mutually_exclusive_group = None
        group_max_slots = 0

        if "mutually_exclusive_groups" in party_data:
            for group in party_data["mutually_exclusive_groups"]:
                if selected_role in group["roles"]:
                    is_mutually_exclusive_role = True
                    mutually_exclusive_group = group["roles"]
                    group_max_slots = group["max_slots"]
                    break

        if user_already_in_any_role:
            if user_current_role == selected_role:
                # El usuario quiere cancelar su rol actual
                if selected_role in inscripciones and any(p["id"] == user.id for p in inscripciones[selected_role]):
                    inscripciones[selected_role] = [p for p in inscripciones[selected_role] if p["id"] != user.id]
                    
                    # Intentar mover de la lista de espera si hay un slot disponible
                    if not is_mutually_exclusive_role: # Para roles no exclusivos, solo rellenar si hay espacio
                        while len(inscripciones.get(selected_role, [])) < party_data["roles"][selected_role] and waitlist:
                            next_player_in_waitlist = waitlist.pop(0)
                            inscripciones.setdefault(selected_role, []).append({"id": next_player_in_waitlist["id"], "name": next_player_in_waitlist["name"]})
                            await interaction.followup.send(f"<@{next_player_in_waitlist['id']}>, ¡has sido movido al rol **{selected_role}**!", ephemeral=False)
                    else: # Para roles mutuamente excluyentes
                        # Recalcular ocupación del grupo después de que el usuario se ha salido
                        current_group_occupancy_after_user_cleared = 0
                        for role_in_group in mutually_exclusive_group:
                            if role_in_group in inscripciones:
                                current_group_occupancy_after_user_cleared += len(inscripciones[role_in_group])
                        
                        # Si hay un slot disponible en el grupo, intentar mover a alguien de la lista de espera general
                        if current_group_occupancy_after_user_cleared < group_max_slots:
                            # Buscar a alguien en la waitlist que esté esperando por un rol en este grupo exclusivo
                            moved_from_waitlist = False
                            for i, p in enumerate(waitlist):
                                if p["desired_role"] in mutually_exclusive_group:
                                    inscripciones.setdefault(p["desired_role"], []).append({"id": p["id"], "name": p["name"]})
                                    await interaction.followup.send(f"<@{p['id']}>, ¡has sido movido al rol **{p['desired_role']}**!", ephemeral=False)
                                    waitlist.pop(i) # Eliminar de la lista de espera
                                    moved_from_waitlist = True
                                    break
                            
                            # Si no se movió a nadie específico del grupo, entonces se queda el slot libre
                            # y el siguiente en la waitlist general podría no ser para este slot
                            # Dejar la lógica simple, si se libera slot exclusivo, notificar.
                            if not moved_from_waitlist and current_group_occupancy_after_user_cleared < group_max_slots:
                                pass # El slot exclusivo está libre, pero nadie en waitlist lo pidió específicamente

                    await interaction.followup.send(f"Has cancelado tu inscripción en **{selected_role}**.", ephemeral=True)
                else: # Estaba en lista de espera para el rol actual o no existía su inscripción
                    if user_current_role == "waitlist" and any(p["id"] == user.id and p["desired_role"] == selected_role for p in waitlist):
                        # Remover de la lista de espera si seleccionó su propio rol de espera
                        waitlist[:] = [p for p in waitlist if not (p["id"] == user.id and p["desired_role"] == selected_role)]
                        await interaction.followup.send(f"Has cancelado tu inscripción en la lista de espera para **{selected_role}**.", ephemeral=True)
                    else:
                        await interaction.followup.send(f"Ya estás inscrito en **{user_current_role}** o en lista de espera. Si deseas cambiar de rol, primero cancela tu rol actual usando el menú.", ephemeral=True)
            else:
                # El usuario quiere cambiar de rol (ya está inscrito en otro o en lista de espera por otro)
                await interaction.followup.send(f"Ya estás inscrito en **{user_current_role}**. Para cambiar, primero cancela tu inscripción actual en ese rol.", ephemeral=True)
        else: # El usuario NO está inscrito en ningún rol ni en lista de espera
            max_slots_for_role = party_data["roles"].get(selected_role)
            current_occupancy = len(inscripciones.get(selected_role, []))

            if is_mutually_exclusive_role:
                # Comprobar la ocupación del grupo exclusivo
                current_group_occupancy = 0
                for role_in_group in mutually_exclusive_group:
                    if role_in_group in inscripciones:
                        current_group_occupancy += len(inscripciones[role_in_group])

                if current_group_occupancy < group_max_slots:
                    # Hay espacio en el grupo exclusivo, se puede inscribir
                    inscripciones.setdefault(selected_role, []).append({"id": user.id, "name": user.display_name})
                    await interaction.followup.send(f"¡Te has inscrito en **{selected_role}**!", ephemeral=True)
                else:
                    # El grupo exclusivo está lleno, añadir a lista de espera
                    waitlist.append({"id": user.id, "name": user.display_name, "desired_role": selected_role})
                    await interaction.followup.send(f"**{selected_role}** está lleno (o su rol relacionado). Has sido añadido/a a la lista de espera.", ephemeral=True)
            else: # Rol no mutuamente excluyente, lógica normal
                if current_occupancy < max_slots_for_role:
                    inscripciones.setdefault(selected_role, []).append({"id": user.id, "name": user.display_name})
                    await interaction.followup.send(f"¡Te has inscrito en **{selected_role}**!", ephemeral=True)
                else:
                    waitlist.append({"id": user.id, "name": user.display_name, "desired_role": selected_role})
                    await interaction.followup.send(f"**{selected_role}** está lleno. Has sido añadido/a a la lista de espera.", ephemeral=True)
        
        # Guardar los cambios
        event["inscripciones"] = inscripciones
        event["waitlist"] = waitlist
        roaming_events[self.event_id] = event

        # Actualizar el embed original del mensaje
        original_message = interaction.message
        updated_embed = create_roaming_embed(self.party_name)
        if updated_embed:
            await original_message.edit(embed=updated_embed, view=RoleView(self.party_name, self.event_id))

# ====================================================================
# --- 3. VISTA CON EL MENÚ DESPLEGABLE ---
# ====================================================================

class RoleView(discord.ui.View):
    def __init__(self, party_name: str, event_id: str, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(RoleDropdown(party_name, event_id))

# ====================================================================
# --- 4. COG DE ROAMING ---
# ====================================================================

class RoamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_roaming_events.start()
        print("✅ Módulo Roaming cargado (comandos !roaming, !roster, !cancel, !add, !remove)")

    def cog_unload(self):
        self.cleanup_roaming_events.cancel()

    @commands.command(name='roaming', help='Inicia un evento de roaming. Uso: !roaming <nombre_party> <@rol_a_notificar> [duración_horas (defecto: 1h)]')
    async def start_roaming_event(self, ctx, party_name: str, role_to_notify: discord.Role = None, duration_hours: float = 1.0):
        if party_name not in ROAMING_PARTIES:
            await ctx.send(f"Party '{party_name}' no encontrada. Parties disponibles: {', '.join(ROAMING_PARTIES.keys())}")
            return

        event_id = str(time.time()) # Usar timestamp como ID único para el evento
        
        # Calcular el tiempo de expiración
        expiration_time = datetime.now() + timedelta(hours=duration_hours)
        
        # Crear el embed y la vista
        embed = create_roaming_embed(party_name)
        if not embed:
            await ctx.send("Error al crear el embed del evento.")
            return
        
        view = RoleView(party_name, event_id, timeout=duration_hours * 3600) # El timeout de la vista debe ser en segundos

        # Enviar el mensaje inicial
        message = await ctx.send(embed=embed, view=view)

        # Si se especificó un rol, enviarlo en un mensaje separado para la notificación
        if role_to_notify:
            await ctx.send(f"{role_to_notify.mention} ¡Un evento de roaming ha comenzado! Revisa el mensaje de arriba para inscribirte.", delete_after=30)


        # Guardar el estado del evento
        roaming_events[event_id] = {
            "channel_id": ctx.channel.id,
            "message_id": message.id,
            "thread_id": None, # Se asignará si se crea un hilo
            "party_name": party_name,
            "inscripciones": {},
            "waitlist": [],
            "timestamp": expiration_time.timestamp() # Guardar como timestamp para fácil comparación
        }

        # Crear un hilo para el evento
        try:
            thread = await message.create_thread(name=f"Roaming - {party_name}", auto_archive_duration=60)
            roaming_events[event_id]["thread_id"] = thread.id
            await thread.send(f"¡Bienvenido al hilo del evento de {party_name}! Usa este hilo para coordinar o preguntar.")
        except discord.Forbidden:
            print(f"No tengo permisos para crear hilos en el canal {ctx.channel.name} ({ctx.channel.id}).")
        except Exception as e:
            print(f"Error al crear hilo para evento de roaming: {e}")

        await ctx.send(f"Evento de roaming '{party_name}' creado con éxito. Durará {duration_hours} hora(s).", delete_after=10)


    @commands.command(name='roster', help='Muestra el roster actual de un evento de roaming.')
    async def show_roster(self, ctx, event_id: str):
        event = roaming_events.get(event_id)
        if not event:
            await ctx.send("Evento de roaming no encontrado. Asegúrate de usar el ID correcto.")
            return

        party_name = event["party_name"]
        embed = create_roaming_embed(party_name) # Reutilizar la función para mostrar el estado actual
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error al obtener la información del roster.")

    @commands.command(name='cancelroaming', help='Cancela un evento de roaming activo. Uso: !cancelroaming <event_id>')
    async def cancel_roaming_event(self, ctx, event_id: str):
        if event_id in roaming_events:
            try:
                event_data = roaming_events[event_id]
                channel = self.bot.get_channel(event_data["channel_id"])
                if channel:
                    message = await channel.fetch_message(event_data["message_id"])
                    
                    if message.thread:
                        if not message.thread.archived:
                            await message.thread.edit(archived=True, reason="Evento de Roaming Cancelado")
                        await message.thread.delete() # Eliminar el hilo
                    
                    await message.delete() # Eliminar el mensaje principal
                
                del roaming_events[event_id]
                await ctx.send(f"Evento de roaming `{event_id}` cancelado y eliminado con éxito.")
            except discord.NotFound:
                await ctx.send(f"Mensaje o hilo del evento `{event_id}` no encontrado en Discord, pero el evento ha sido eliminado internamente.")
                del roaming_events[event_id] # Asegurarse de eliminarlo del diccionario
            except discord.Forbidden:
                await ctx.send("No tengo permisos para eliminar mensajes o hilos. Por favor, elimina el mensaje del evento manualmente.")
            except Exception as e:
                await ctx.send(f"Ocurrió un error al intentar cancelar el evento: {e}")
                print(f"Error al cancelar evento de roaming {event_id}: {e}")
        else:
            await ctx.send(f"No se encontró ningún evento de roaming con el ID `{event_id}`.")

    @commands.command(name='addplayer', help='Añade un jugador a un rol de un evento de roaming. Uso: !addplayer <event_id> <@usuario> <rol>')
    @commands.has_permissions(manage_roles=True) # Requiere permisos para gestionar roles
    async def add_player_to_roaming(self, ctx, event_id: str, member: discord.Member, role: str):
        event = roaming_events.get(event_id)
        if not event:
            await ctx.send("Evento de roaming no encontrado.")
            return

        party_data = ROAMING_PARTIES.get(event["party_name"])
        if not party_data or role not in party_data["roles"]:
            await ctx.send(f"El rol '{role}' no es válido para la party '{event['party_name']}'.")
            return

        inscripciones = event["inscripciones"]
        max_slots = party_data["roles"][role]

        # Verificar si el usuario ya está en algún rol
        for r, players in inscripciones.items():
            if any(p["id"] == member.id for p in players):
                await ctx.send(f"{member.display_name} ya está inscrito en el rol {r}.")
                return
        
        # Verificar si el rol ya está lleno (considerando grupos exclusivos)
        is_mutually_exclusive_role = False
        if "mutually_exclusive_groups" in party_data:
            for group in party_data["mutually_exclusive_groups"]:
                if role in group["roles"]:
                    is_mutually_exclusive_role = True
                    group_max_slots = group["max_slots"]
                    
                    current_group_occupancy = 0
                    for role_in_group in group["roles"]:
                        current_group_occupancy += len(inscripciones.get(role_in_group, []))
                    
                    if current_group_occupancy >= group_max_slots:
                        await ctx.send(f"No se puede añadir a {member.display_name} a '{role}'. El grupo de roles mutuamente excluyentes para este rol ya está lleno.")
                        return
                    break

        if not is_mutually_exclusive_role and len(inscripciones.get(role, [])) >= max_slots:
            await ctx.send(f"El rol '{role}' ya está lleno.")
            return

        inscripciones.setdefault(role, []).append({"id": member.id, "name": member.display_name})
        
        # Eliminar de la lista de espera si estaba allí
        event["waitlist"][:] = [p for p in event["waitlist"] if p["id"] != member.id]

        # Actualizar el mensaje
        channel = self.bot.get_channel(event["channel_id"])
        if channel:
            message = await channel.fetch_message(event["message_id"])
            updated_embed = create_roaming_embed(event["party_name"])
            if updated_embed:
                await message.edit(embed=updated_embed, view=RoleView(event["party_name"], event_id))
        
        await ctx.send(f"✅ {member.display_name} ha sido añadido a {role} para el evento `{event_id}`.")


    @commands.command(name='removeplayer', help='Elimina un jugador de un rol de un evento de roaming. Uso: !removeplayer <event_id> <@usuario>')
    @commands.has_permissions(manage_roles=True) # Requiere permisos para gestionar roles
    async def remove_player_from_roaming(self, ctx, event_id: str, member: discord.Member):
        event = roaming_events.get(event_id)
        if not event:
            await ctx.send("Evento de roaming no encontrado.")
            return

        inscripciones = event["inscripciones"]
        user_removed = False
        role_of_removed_user = None

        # Intentar remover de los roles inscritos
        for role, players in inscripciones.items():
            if any(p["id"] == member.id for p in players):
                inscripciones[role] = [p for p in players if p["id"] != member.id]
                user_removed = True
                role_of_removed_user = role
                break
        
        # Si no estaba en un rol, intentar remover de la lista de espera
        if not user_removed:
            if any(p["id"] == member.id for p in event["waitlist"]):
                event["waitlist"][:] = [p for p in event["waitlist"] if p["id"] != member.id]
                user_removed = True
                role_of_removed_user = "la lista de espera"

        if user_removed:
            # Lógica para rellenar el slot si se liberó uno
            if role_of_removed_user and role_of_removed_user != "la lista de espera":
                party_data = ROAMING_PARTIES.get(event["party_name"])
                if party_data:
                    is_mutually_exclusive_role = False
                    mutually_exclusive_group = None
                    group_max_slots = 0

                    if "mutually_exclusive_groups" in party_data:
                        for group in party_data["mutually_exclusive_groups"]:
                            if role_of_removed_user in group["roles"]:
                                is_mutually_exclusive_role = True
                                mutually_exclusive_group = group["roles"]
                                group_max_slots = group["max_slots"]
                                break

                    if is_mutually_exclusive_role:
                        current_group_occupancy_after_removal = 0
                        for r_in_group in mutually_exclusive_group:
                            current_group_occupancy_after_removal += len(inscripciones.get(r_in_group, []))

                        if current_group_occupancy_after_removal < group_max_slots:
                            # Intentar mover de la lista de espera para este grupo exclusivo
                            moved_from_waitlist = False
                            for i, p in enumerate(event["waitlist"]):
                                if p["desired_role"] in mutually_exclusive_group:
                                    inscripciones.setdefault(p["desired_role"], []).append({"id": p["id"], "name": p["name"]})
                                    await ctx.send(f"<@{p['id']}>, ¡has sido movido al rol **{p['desired_role']}**!", ephemeral=False)
                                    event["waitlist"].pop(i)
                                    moved_from_waitlist = True
                                    break
                            if not moved_from_waitlist: # Si nadie específico del grupo, el slot está libre
                                pass # No se necesita acción específica, el slot se mostrará como libre
                    else: # Rol no exclusivo
                        while len(inscripciones.get(role_of_removed_user, [])) < party_data["roles"][role_of_removed_user] and event["waitlist"]:
                            next_player_in_waitlist = event["waitlist"].pop(0)
                            inscripciones.setdefault(role_of_removed_user, []).append({"id": next_player_in_waitlist["id"], "name": next_player_in_waitlist["name"]})
                            await ctx.send(f"<@{next_player_in_waitlist['id']}>, ¡has sido movido al rol **{role_of_removed_user}**!", ephemeral=False)

            # Actualizar el mensaje
            channel = self.bot.get_channel(event["channel_id"])
            if channel:
                message = await channel.fetch_message(event["message_id"])
                updated_embed = create_roaming_embed(event["party_name"])
                if updated_embed:
                    await message.edit(embed=updated_embed, view=RoleView(event["party_name"], event_id))
            
            await ctx.send(f"✅ {member.display_name} ha sido eliminado/a de {role_of_removed_user} para el evento `{event_id}`.")
        else:
            await ctx.send(f"{member.display_name} no se encontró en ningún rol o en la lista de espera para el evento `{event_id}`.")

    # Tarea en segundo plano para limpiar eventos expirados
    @tasks.loop(minutes=5)
    async def cleanup_roaming_events(self):
        print("Ejecutando tarea de limpieza de eventos de roaming...")
        current_time = time.time()
        events_to_remove = []

        for event_id, event_data in list(roaming_events.items()):
            if "timestamp" not in event_data:
                print(f"Evento {event_id} sin timestamp, marcando para eliminación.")
                events_to_remove.append(event_id)
                continue

            if current_time > event_data["timestamp"]:
                print(f"Evento de roaming {event_id} ha expirado. Eliminando...")
                try:
                    channel_id = event_data["channel_id"]
                    message_id = event_data["message_id"]
                    
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        print(f"Canal {channel_id} no encontrado para el evento {event_id}.")
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
