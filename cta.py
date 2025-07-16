import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import random
import time
import re

# ====================================================================
# --- IMPORTAR ROAMING_PARTIES desde roaming.py (Asume que roaming.py está en la misma carpeta o accesible) ---
# Si roaming.py no está directamente importable, deberás copiar ROAMING_PARTIES aquí.
# Por simplicidad y modularidad, es mejor que ROAMING_PARTIES sea una variable global accesible.
# Si tienes ROAMING_PARTIES en roaming.py, asegúrate de que sea accesible o cópialo aquí.
# Para este ejemplo, lo duplicaré para que cta.py sea autocontenido si lo ejecutas solo.
# EN UN ENTORNO REAL, SI YA LO TIENES EN roaming.py, NO LO DUPLIQUES, IMPORTA:
# from roaming import ROAMING_PARTIES

# --- COPIA DE ROAMING_PARTIES (PARA QUE CTA.PY SEA INDEPENDIENTE EN ESTE EJEMPLO) ---
# --- DEBES USAR LA VERSIÓN COMPLETA Y FINAL DE ROAMING_PARTIES DE TU ARCHIVO ROAMING.PY ---
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
# --- FIN COPIA DE ROAMING_PARTIES ---

cta_events = {} # Diccionario para almacenar los eventos CTA activos
CTA_EVENT_TIMEOUT = 7200 # 2 horas para limpieza

# ====================================================================
# --- FUNCIONES HELPER ---
# ====================================================================

def create_cta_embed(event_data):
    """Genera el mensaje embed para el evento CTA."""
    embed = discord.Embed(
        title=f"🚨 ¡CTA Activo! (Caller: {event_data['caller_display']}) 🚨",
        color=0xFF4500 # Naranja rojizo para CTA
    )

    embed.description = f"**⏰ Hora de Masseo: {event_data['masseo_hour']:02d}:00 (Hora Chile)**\n"
    embed.description += f"**Composiciones:** {', '.join([c.upper() for c in event_data['selected_parties']])}\n\n"

    total_inscritos_cta = 0
    total_max_players_cta = 0

    for party_name in event_data['selected_parties']:
        party_data = ROAMING_PARTIES.get(party_name)
        if not party_data:
            continue

        inscripciones_party = event_data['inscripciones'].get(party_name, {})
        
        # Calcular inscritos y cupo total para esta party
        current_party_inscritos = sum(len(players) for players in inscripciones_party.values())
        total_inscritos_cta += current_party_inscritos
        total_max_players_cta += party_data['max_players']

        # Sección para cada composición
        embed.add_field(
            name=f"⚔️ **{party_name.upper()}** ({current_party_inscritos}/{party_data['max_players']} Jugadores)",
            value="-------------------------------------",
            inline=False
        )

        roles_info = []
        for role_name, max_slots in party_data["roles"].items():
            emoji = party_data["emojis"].get(role_name, "")
            inscritos = inscripciones_party.get(role_name, [])
            waitlist_for_role_and_party = [
                p for p in event_data["waitlist"] 
                if p["desired_role"] == role_name and p["desired_party"] == party_name
            ]
            
            players_str = ' '.join(f'<@{p_data["id"]}>' for p_data in inscritos) if inscritos else "🚫"
            waitlist_str = f" | ⏳ Espera: {' '.join(f'<@{p_data["id"]}>' for p_data in waitlist_for_role_and_party)}" if waitlist_for_role_and_party else ""
            
            roles_info.append(f"{emoji} **{role_name}** ({len(inscritos)}/{max_slots}) → {players_str}{waitlist_str}")

        # Dividir roles en campos si hay muchos
        for i in range(0, len(roles_info), 5): # Ajusta el número para mejor visualización
            embed.add_field(
                name="Roles" if i == 0 else " ", # Nombre del campo vacío para continuación
                value="\n".join(roles_info[i:i+5]),
                inline=True # Puedes ponerlo en True para que se muestren en columnas si caben
            )
        # Añadir un campo vacío si el último inline fue True y no hay más composiciones para forzar una nueva línea
        if (len(roles_info) % 5 != 0 or len(roles_info) == 0) and embed.fields[-1].inline:
             embed.add_field(name="\u200b", value="\u200b", inline=False) # Espacio en blanco para nueva línea

    embed.set_footer(text=f"ID del CTA: {event_data['event_id']} | Total de Inscritos: {total_inscritos_cta}/{total_max_players_cta}")
    return embed

# ====================================================================
# --- VISTAS Y COMPONENTES DE UI ---
# ====================================================================

class CTARoleDropdown(discord.ui.Select):
    def __init__(self, cta_event_id: str, party_name: str, main_view: discord.ui.View):
        self.cta_event_id = cta_event_id
        self.party_name = party_name
        self.main_view = main_view # Referencia a la vista principal para volver
        party_data = ROAMING_PARTIES.get(party_name)
        
        options = []
        if party_data:
            for role_name, _ in party_data["roles"].items():
                emoji = party_data["emojis"].get(role_name, "❓")
                options.append(discord.SelectOption(label=role_name, emoji=emoji))

        super().__init__(placeholder=f"Selecciona tu rol en {party_name.upper()}...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        selected_role = self.values[0]
        event = cta_events.get(self.cta_event_id)
        party_data = ROAMING_PARTIES.get(self.party_name)

        if not event or not party_data:
            await interaction.followup.send("Este evento CTA ya no existe o es inválido.", ephemeral=True)
            # Volver a la vista principal si el evento no existe
            if interaction.message:
                main_cta_view = CTAEventView(event.get("selected_parties", []), self.cta_event_id, event["caller_id"], event)
                await interaction.message.edit(view=main_cta_view)
            return

        inscripciones = event.get("inscripciones", {})
        waitlist = event.get("waitlist", [])
        
        # 1. Eliminar al usuario de CUALQUIER rol o lista de espera en CUALQUIER COMPOSICIÓN del CTA
        user_removed_from_old_spot = False
        
        # De inscripciones (roles principales en cualquier party)
        for p_name, roles_in_party in inscripciones.items():
            for role_n, players in roles_in_party.items():
                initial_len = len(players)
                inscripciones[p_name][role_n] = [p for p in players if p["id"] != user.id]
                if len(inscripciones[p_name][role_n]) < initial_len:
                    user_removed_from_old_spot = True
                    break
            if user_removed_from_old_spot:
                break
        
        # De la lista de espera (de cualquier party)
        initial_waitlist_len = len(waitlist)
        waitlist[:] = [p for p in waitlist if p["id"] != user.id]
        if len(waitlist) < initial_waitlist_len:
            user_removed_from_old_spot = True

        # 2. Procesar nueva inscripción para el rol y la party seleccionados
        max_slots = party_data["roles"][selected_role]
        
        # Asegurarse de que la estructura de inscripciones esté inicializada para la party y el rol
        inscripciones.setdefault(self.party_name, {})
        inscripciones[self.party_name].setdefault(selected_role, [])

        current_players_in_role = len(inscripciones[self.party_name][selected_role])
        
        if current_players_in_role < max_slots:
            inscripciones[self.party_name][selected_role].append({"id": user.id, "name": user.display_name})
            msg = f"¡Te has inscrito como **{selected_role}** en **{self.party_name.upper()}**!"
            if user_removed_from_old_spot:
                msg += "\n(Tu inscripción anterior ha sido eliminada.)"
            await interaction.followup.send(msg, ephemeral=True)
        else:
            # Añadir a la lista de espera para el rol y la party específica
            waitlist.append({"id": user.id, "name": user.display_name, "desired_role": selected_role, "desired_party": self.party_name})
            msg = f"**{selected_role}** en **{self.party_name.upper()}** está lleno. Has sido añadido a la lista de espera para este rol."
            if user_removed_from_old_spot:
                msg += "\n(Tu inscripción anterior ha sido eliminada.)"
            await interaction.followup.send(msg, ephemeral=True)
        
        # Volver a la vista principal y actualizar el embed
        if interaction.message:
            updated_embed = create_cta_embed(event)
            if updated_embed:
                main_cta_view = CTAEventView(event["selected_parties"], self.cta_event_id, event["caller_id"], event)
                await interaction.message.edit(embed=updated_embed, view=main_cta_view)

class CTASignUpView(discord.ui.View):
    def __init__(self, cta_event_id: str, party_name: str, caller_id: int, event_data: dict):
        super().__init__(timeout=300) # Timeout para esta vista temporal
        self.cta_event_id = cta_event_id
        self.party_name = party_name
        self.caller_id = caller_id
        self.event_data = event_data
        
        # Añadir el dropdown de roles específico para la party
        self.add_item(CTARoleDropdown(cta_event_id, party_name, self))

    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, emoji="↩️", custom_id="cta_back_to_main_view")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        event = cta_events.get(self.cta_event_id)
        if event:
            updated_embed = create_cta_embed(event)
            if updated_embed:
                main_cta_view = CTAEventView(event["selected_parties"], self.cta_event_id, self.caller_id, event)
                await interaction.message.edit(embed=updated_embed, view=main_cta_view)
        else:
            await interaction.followup.send("El evento CTA ya no existe.", ephemeral=True)
            if interaction.message:
                await interaction.message.delete() # Limpiar si el evento ya no está

class CTAEventView(discord.ui.View):
    def __init__(self, selected_parties: list, cta_event_id: str, caller_id: int, event_data: dict):
        super().__init__(timeout=None) # Vista principal sin timeout
        self.selected_parties = selected_parties
        self.cta_event_id = cta_event_id
        self.caller_id = caller_id
        self.event_data = event_data

        # Añadir botones para cada composición
        for i, party_name in enumerate(selected_parties):
            # Asegurarse de que el custom_id sea único y no exceda 100 caracteres
            custom_id = f"cta_signup_party_{party_name}_{self.cta_event_id[:10]}_{i}" 
            self.add_item(discord.ui.Button(label=f"Inscribirse en {party_name.upper()}", 
                                            style=discord.ButtonStyle.primary, 
                                            custom_id=custom_id))

        # Botones generales
        self.add_item(discord.ui.Button(label="Salir de CTA", style=discord.ButtonStyle.red, emoji="🏃", custom_id="cta_leave_event_button"))
        self.add_item(discord.ui.Button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", custom_id="cta_close_event_button"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Si es un botón de inscripción por party, manejarlo dinámicamente
        if interaction.custom_id and interaction.custom_id.startswith("cta_signup_party_"):
            parts = interaction.custom_id.split('_')
            party_name_from_id = parts[3] # extrae el nombre de la party
            
            # Enviar la nueva vista de selección de rol
            await interaction.response.defer(ephemeral=True)
            new_view = CTASignUpView(self.cta_event_id, party_name_from_id, self.caller_id, self.event_data)
            # Editar el mensaje original con la nueva vista
            await interaction.message.edit(view=new_view)
            return False # Ya respondimos a la interacción, no procesar más en este check

        # Verificar permisos para el botón de cerrar evento
        if interaction.custom_id == "cta_close_event_button":
            if interaction.user.id != self.caller_id:
                await interaction.response.send_message("❌ Solo el creador del evento puede cerrarlo.", ephemeral=True)
                return False
        return True # Permitir el resto de interacciones

    @discord.ui.button(label="Salir de CTA", style=discord.ButtonStyle.red, emoji="🏃", custom_id="cta_leave_event_button")
    async def leave_cta_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        event = cta_events.get(self.cta_event_id)
        
        if not event:
            await interaction.followup.send("Este evento CTA ya no existe.", ephemeral=True)
            return

        user_found_and_removed = False
        # De inscripciones (roles principales en cualquier party)
        for p_name, roles_in_party in event["inscripciones"].items():
            for role_n, players in roles_in_party.items():
                initial_len = len(players)
                event["inscripciones"][p_name][role_n] = [p for p in players if p["id"] != user.id]
                if len(event["inscripciones"][p_name][role_n]) < initial_len:
                    user_found_and_removed = True
                    break
            if user_found_and_removed:
                break
        
        # De la lista de espera (de cualquier party)
        initial_waitlist_len = len(event["waitlist"])
        event["waitlist"][:] = [p for p in event["waitlist"] if p["id"] != user.id]
        if len(event["waitlist"]) < initial_waitlist_len:
            user_found_and_removed = True

        if user_found_and_removed:
            await interaction.followup.send("Has abandonado tu rol/lugar en la lista de espera para este CTA.", ephemeral=True)
            # Actualizar el embed
            updated_embed = create_cta_embed(event)
            if updated_embed:
                await interaction.message.edit(embed=updated_embed, view=CTAEventView(self.selected_parties, self.cta_event_id, self.caller_id, event))
        else:
            await interaction.followup.send("No estabas inscrito en ningún rol o lista de espera para este CTA.", ephemeral=True)

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", custom_id="cta_close_event_button")
    async def close_cta_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Permiso ya verificado en interaction_check, pero lo reconfirmo por seguridad.
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el creador del evento puede cerrarlo.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True) 
        
        event_data = cta_events.get(self.cta_event_id)
        if not event_data:
            await interaction.followup.send("Este evento CTA ya no existe.", ephemeral=True)
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
                                await thread.edit(archived=False, reason="Desarchivando para eliminar CTA")
                            await thread.delete()
                            print(f"Hilo de CTA {self.cta_event_id} eliminado.")
                    else:
                        print(f"Canal principal {event_data['channel_id']} no encontrado para el hilo del CTA {self.cta_event_id}.")
            except (discord.NotFound, discord.Forbidden) as e:
                print(f"Error al eliminar hilo de CTA {self.cta_event_id}: {e}. Puede que ya no exista o permisos insuficientes.")
            except Exception as e:
                print(f"Error inesperado al eliminar hilo de CTA {self.cta_event_id}: {e}")

        # Eliminar el mensaje principal
        if event_data.get("message_id") and event_data.get("channel_id"):
            try:
                guild = interaction.guild
                if guild:
                    channel = guild.get_channel(event_data["channel_id"])
                    if channel:
                        message_to_delete = await channel.fetch_message(event_data["message_id"])
                        await message_to_delete.delete()
                        print(f"Mensaje de CTA {self.cta_event_id} eliminado.")
            except (discord.NotFound, discord.Forbidden) as e:
                print(f"Error al eliminar mensaje de CTA {self.cta_event_id}: {e}. Puede que ya no exista o permisos insuficientes.")
            except Exception as e:
                print(f"Error inesperado al eliminar mensaje de CTA {self.cta_event_id}: {e}")

        # Eliminar el evento del diccionario global
        if self.cta_event_id in cta_events:
            del cta_events[self.cta_event_id]

        await interaction.followup.send("✅ Evento CTA cerrado y eliminado.", ephemeral=True)


# ====================================================================
# --- COG DE CTA ---
# ====================================================================

class CTACog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_cta_events.start()

    def cog_unload(self):
        self.cleanup_cta_events.cancel()

    @commands.command(name='cta')
    async def start_cta_event(self, ctx, *args):
        """
        Inicia un evento CTA con una o más composiciones y una hora de masseo.
        Uso: !cta <comp1> [comp2...] <hora_masseo_HH>
        Ej: !cta kiteo1 pocho 20
        """
        if len(args) < 2:
            await ctx.send("Uso incorrecto. Formato: `!cta <comp1> [comp2...] <hora_masseo_HH>`")
            return

        masseo_hour_str = args[-1]
        try:
            masseo_hour = int(masseo_hour_str)
            if not (0 <= masseo_hour <= 23):
                raise ValueError
        except ValueError:
            await ctx.send("La hora de masseo debe ser un número entero entre 0 y 23 (ej: `20` para 20:00).")
            return
        
        selected_parties_input = args[:-1]
        selected_parties = []
        invalid_parties = []

        for p_name in selected_parties_input:
            p_name_lower = p_name.lower()
            if p_name_lower in ROAMING_PARTIES:
                selected_parties.append(p_name_lower)
            else:
                invalid_parties.append(p_name)
        
        if not selected_parties:
            await ctx.send(f"No se seleccionaron composiciones válidas. Composiciones disponibles: {', '.join(ROAMING_PARTIES.keys())}")
            return
        if invalid_parties:
            await ctx.send(f"Las siguientes composiciones no son válidas y fueron ignoradas: {', '.join(invalid_parties)}")
        
        # Crear ID único para el evento CTA
        event_id = f"cta-{int(time.time())}-{random.randint(1000, 9999)}"

        # Inicializar inscripciones para cada composición seleccionada
        initial_inscripciones = {}
        for party_name in selected_parties:
            initial_inscripciones[party_name] = {role: [] for role in ROAMING_PARTIES[party_name]["roles"]}

        event_data = {
            "event_id": event_id,
            "caller_id": ctx.author.id,
            "caller_display": ctx.author.display_name,
            "channel_id": ctx.channel.id,
            "masseo_hour": masseo_hour,
            "selected_parties": selected_parties,
            "inscripciones": initial_inscripciones,
            "waitlist": [],
            "start_time": time.time(),
            "message_id": None,
            "thread_id": None,
            "thread_channel_id": None
        }

        embed = create_cta_embed(event_data)
        view = CTAEventView(selected_parties, event_id, ctx.author.id, event_data)

        message = await ctx.send(embed=embed, view=view)
        event_data["message_id"] = message.id

        cta_events[event_id] = event_data # Almacenar el evento después de obtener el message_id

        # Crear hilo de discusión
        try:
            thread_name = f"CTA {'-'.join([p.upper() for p in selected_parties])} - {masseo_hour:02d}H"
            thread = await message.create_thread(name=thread_name)
            await thread.send(f"¡Hilo de discusión para el CTA! Hora de masseo: {masseo_hour:02d}:00")
            event_data["thread_id"] = thread.id
            event_data["thread_channel_id"] = thread.id
        except Exception as e:
            print(f"Error al crear hilo para CTA {event_id}: {e}")

        # Eliminar mensaje original del comando
        try:
            await ctx.message.delete()
        except:
            pass

    @tasks.loop(minutes=30)
    async def cleanup_cta_events(self):
        """Limpia eventos CTA antiguos que hayan superado un umbral de tiempo."""
        current_time = time.time()
        events_to_remove = []

        for event_id, event_data in cta_events.items():
            if current_time - event_data["start_time"] > CTA_EVENT_TIMEOUT:
                events_to_remove.append(event_id)
        
        for event_id in events_to_remove:
            event_data = cta_events.get(event_id)
            if event_data:
                # Intentar eliminar el mensaje principal del evento
                if event_data.get("message_id") and event_data.get("channel_id"):
                    try:
                        channel = self.bot.get_channel(event_data["channel_id"])
                        if channel:
                            message_to_delete = await channel.fetch_message(event_data["message_id"])
                            await message_to_delete.delete()
                            print(f"Mensaje de CTA {event_id} eliminado durante la limpieza.")
                    except (discord.NotFound, discord.Forbidden):
                        print(f"Mensaje de CTA {event_id} ya no existe o no se pudo acceder durante la limpieza.")
                    except Exception as e:
                        print(f"Error inesperado al eliminar mensaje de CTA {event_id} durante la limpieza: {e}")

                # Intentar eliminar el hilo del evento
                if event_data.get("thread_id") and event_data.get("channel_id"):
                    try:
                        channel = self.bot.get_channel(event_data["channel_id"])
                        if channel:
                            thread_to_delete = await channel.fetch_thread(event_data["thread_id"])
                            if thread_to_delete.archived:
                                await thread_to_delete.edit(archived=False, reason="Desarchivando para eliminar en limpieza de CTA")
                            await thread_to_delete.delete()
                            print(f"Hilo de CTA {event_id} eliminado durante la limpieza.")
                    except (discord.NotFound, discord.Forbidden):
                        print(f"Hilo de CTA {event_id} ya no existe o no se pudo acceder durante la limpieza.")
                    except Exception as e:
                        print(f"Error inesperado al eliminar hilo de CTA {event_id} durante la limpieza: {e}")
                
                del cta_events[event_id]

    @cleanup_cta_events.before_loop
    async def before_cleanup_cta(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(CTACog(bot))
