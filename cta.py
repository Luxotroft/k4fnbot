import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import random
import time
import re

# ====================================================================
# --- DATOS Y VARIABLES GLOBALES DE CTA ---
# ====================================================================

cta_events = {} # Nuevo diccionario para eventos CTA
CTA_EVENT_TIMEOUT = 7200 # 2 horas (tiempo de vida del evento CTA)

# Combinación de roles y cupos de kiteo1 y kiteo2 de roaming.py
# { "ROL": {"max_count": N, "emoji": "<:emoji_id:>"} }
ALL_CTA_ROLES_CONFIG = {
    "HOJ": {"max_count": 1, "emoji": "<:ManodeJusticia:1290858364129247242>"},
    "PESADA": {"max_count": 1, "emoji": "<:stoper:1290858463135662080>"},
    "LECHO PEEL": {"max_count": 1, "emoji": "<:stoper:1290858463135662080>"},
    "LECHO SUP": {"max_count": 1, "emoji": "<:stoper:1290858463135662080>"},
    "GA": {"max_count": 2, "emoji": "<:GranArcano:1337861969931407411>"},
    "LOCUS": {"max_count": 2, "emoji": "<:Locus:1291467422238249043>"},
    "JURADORES": {"max_count": 2, "emoji": "<:Maracas:1290858583965175828>"},
    "ENRAIZADO": {"max_count": 1, "emoji": "<:Enraizado:1290879541073678397>"},
    "LIFECURSED": {"max_count": 2, "emoji": "<:Maldi:1291467716229730415>"},
    "OCULTO": {"max_count": 2, "emoji": "<:Oculto:1337862058779218026>"},
    "ROMPERREINO": {"max_count": 1, "emoji": "<:RompeReino:1290881352182399017>"},
    "CAZAESPÍRITUS": {"max_count": 1, "emoji": "<:Cazaespiritu:1290881433816137821>"},
    "FISURANTE": {"max_count": 3, "emoji": "<:Fisurante:1337862459008090112>"},
    "PRISMA": {"max_count": 2, "emoji": "<:Prisma:1367151400672559184>"},
    "PUAS": {"max_count": 1, "emoji": "<:Puas:1291468593506029638>"},
    "SANTI": {"max_count": 4, "emoji": "<:Santificador:1290858870260109384>"},
    "FORJACORTEZA": {"max_count": 2, "emoji": "<:Infortunio:1290858784528531537>"},
    "GOLEM": {"max_count": 1, "emoji": "<:Terrunico:1290880192092438540>"},
    "MARTILLO": {"max_count": 1, "emoji": "<:stoper:1290858463135662080>"},
    "1HARCANO": {"max_count": 1, "emoji": "<:Arcano:1297064938531196959>"},
    "LOCUS_OFENSIVO": {"max_count": 1, "emoji": "<:Locus:1291467422238249043>"},
    "CANCION": {"max_count": 1, "emoji": "<:Canciondedespertar:1291635941240213574>"},
    "CARAMBANOS": {"max_count": 1, "emoji": "<:caram:1384931326968463372>"},
    "DAMNATION": {"max_count": 1, "emoji": "<:Maldiciones:1337862954820829294>"},
    "PUTREFACTO": {"max_count": 1, "emoji": "<:Putrefacto:1370577320171016202>"},
    "WITCHWORD": {"max_count": 1, "emoji": "<:witchword:1392942341815533758>"},
    "TORRE_MOVIL": {"max_count": 1, "emoji": "<:MonturaMana:1337863658859925676>"},
}

# ====================================================================
# --- FUNCIONES HELPER DE CTA ---
# ====================================================================

def create_cta_embed(event_data, bot_instance, event_id: str):
    """Genera el mensaje embed para el evento CTA (Pelea Obligatoria)."""
    embed = discord.Embed(
        title=f"🚨 ¡PELEA OBLIGATORIA! - Hora de Masseo: {event_data['mass_time']} UTC 🚨",
        description="¡Pérense para la acción! Anótate en el rol que te corresponda.",
        color=0xFF0000
    )
    embed.set_thumbnail(url="https://assets.albiononline.com/assets/images/icons/faction_standings_martlock.png")

    roles_info = []
    total_inscritos = 0
    total_cupos = 0

    # Procesar roles inscritos
    for role_name, config in event_data["role_config"].items():
        emoji = config["emoji"]
        max_count = config["max_count"]
        inscritos = event_data["inscripciones"].get(role_name, [])
        total_inscritos += len(inscritos)
        total_cupos += max_count

        jugadores_insc = ' '.join(f'<@{uid}>' for uid in inscritos)
        status = f"({len(inscritos)}/{max_count})"
        roles_info.append(f"{emoji} **{role_name.ljust(20)}** {status} → {jugadores_insc or '🚫'}")

    # Dividir los roles en múltiples campos si hay muchos
    for i in range(0, len(roles_info), 10): # Mostrar 10 roles por campo
        embed.add_field(
            name=f"🎮 ROLES DISPONIBLES ({total_inscritos}/{total_cupos})" if i == 0 else "↳ Continuación",
            value="\n".join(roles_info[i:i+10]),
            inline=False
        )

    # Añadir sección de lista de espera
    waitlist_str = []
    for role_name, config in event_data["role_config"].items():
        emoji = config["emoji"]
        waitlist_players = event_data["waitlist"].get(role_name, [])
        if waitlist_players:
            jugadores_wait = ' '.join(f'<@{uid}>' for uid in waitlist_players)
            waitlist_str.append(f"{emoji} **{role_name} (Espera)** → {jugadores_wait}")
    
    if waitlist_str:
        embed.add_field(
            name="⏳ LISTA DE ESPERA POR ROL",
            value="\n".join(waitlist_str),
            inline=False
        )
    
    embed.add_field(
        name="\u200b",
        value="¡Todos los miembros deben presentarse y seguir las indicaciones! @everyone",
        inline=False
    )
    
    caller_user = bot_instance.get_user(event_data['caller_id'])
    caller_display_name = caller_user.display_name if caller_user else 'Desconocido'
    embed.set_footer(text=f"Evento creado por: {caller_display_name} | ID: {event_id}")
    embed.timestamp = datetime.utcnow()
    return embed

async def update_cta_embed(event_id, bot_instance):
    if event_id not in cta_events:
        return
    event = cta_events[event_id]
    message = event.get("message") # Usar .get para manejar caso donde el mensaje no se ha establecido aún

    if not message:
        print(f"Mensaje no encontrado para el evento CTA {event_id}, no se puede actualizar el embed.")
        return
    try:
        embed = create_cta_embed(event, bot_instance, event_id)
        # La vista debe ser instanciada con todos los parámetros necesarios
        view = CTAEventView(event_id, event["caller_id"], bot_instance) 
        await message.edit(embed=embed, view=view)
    except Exception as e:
        print(f"Error actualizando embed para el evento CTA {event_id}: {e}")


# ====================================================================
# --- CLASES DE UI (VIEWS, BUTTONS, SELECTS) PARA CTA ---
# ====================================================================

class CTARoleDropdown(discord.ui.Select):
    def __init__(self, event_id):
        self.event_id = event_id
        options = []
        # Usar ALL_CTA_ROLES_CONFIG para las opciones del dropdown
        for role_name, config in ALL_CTA_ROLES_CONFIG.items():
            options.append(discord.SelectOption(label=role_name, value=role_name, emoji=config["emoji"]))
        
        super().__init__(
            placeholder="Elige tu rol...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in cta_events:
            await interaction.response.send_message("❌ Este evento CTA ya no está activo.", ephemeral=True)
            return

        selected_role = self.values[0]
        user_id = interaction.user.id
        event_data = cta_events[self.event_id]
        
        # Obtener la configuración del rol seleccionado
        role_config = event_data["role_config"].get(selected_role)
        if not role_config:
            await interaction.response.send_message("❌ Rol no válido.", ephemeral=True)
            return

        max_count = role_config["max_count"]

        # Eliminar al usuario de todos los roles (inscripciones y lista de espera)
        # antes de añadirlo al nuevo rol.
        found_in_another_role = False
        for role_name_iter in event_data["role_config"].keys():
            if user_id in event_data["inscripciones"].get(role_name_iter, []):
                event_data["inscripciones"][role_name_iter].remove(user_id)
                found_in_another_role = True
            if user_id in event_data["waitlist"].get(role_name_iter, []):
                event_data["waitlist"][role_name_iter].remove(user_id)
                found_in_another_role = True

        # Añadir al usuario al rol seleccionado
        inscripciones_rol = event_data["inscripciones"].setdefault(selected_role, [])
        waitlist_rol = event_data["waitlist"].setdefault(selected_role, [])

        if len(inscripciones_rol) < max_count:
            if user_id not in inscripciones_rol: # Evitar duplicados
                inscripciones_rol.append(user_id)
                if found_in_another_role:
                    await interaction.response.send_message(f"✅ Te has cambiado e inscrito como **{selected_role}**.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"✅ Te has inscrito como **{selected_role}**.", ephemeral=True)
            else:
                await interaction.response.send_message(f"ℹ️ Ya estás inscrito como **{selected_role}**.", ephemeral=True)
        else: # El rol está lleno, añadir a la lista de espera
            if user_id not in waitlist_rol: # Evitar duplicados
                waitlist_rol.append(user_id)
                if found_in_another_role:
                    await interaction.response.send_message(f"✅ Te has cambiado y añadido a la **lista de espera** para **{selected_role}**.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"✅ Te has añadido a la **lista de espera** para **{selected_role}**.", ephemeral=True)
            else:
                await interaction.response.send_message(f"ℹ️ Ya estás en la lista de espera para **{selected_role}**.", ephemeral=True)
        
        await update_cta_embed(self.event_id, self.view.bot_instance)


class CTALeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salirme", style=discord.ButtonStyle.red, emoji="👋", row=1)
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in cta_events:
            await interaction.response.send_message("❌ Este evento CTA ya no está activo.", ephemeral=True)
            return

        user_id = interaction.user.id
        event_data = cta_events[self.event_id]
        found = False

        # Buscar y eliminar al usuario de inscripciones o lista de espera en cualquier rol
        for role_name in event_data["role_config"].keys():
            if user_id in event_data["inscripciones"].get(role_name, []):
                event_data["inscripciones"][role_name].remove(user_id)
                found = True
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
                found = True
        
        if found:
            await interaction.response.send_message("✅ Te has salido del evento CTA.", ephemeral=True)
            await update_cta_embed(self.event_id, self.view.bot_instance)
        else:
            await interaction.response.send_message("ℹ️ No estabas inscrito en este evento CTA.", ephemeral=True)


class CTAEventView(discord.ui.View):
    def __init__(self, event_id, caller_id, bot_instance):
        super().__init__(timeout=None)
        self.caller_id = caller_id
        self.event_id = event_id
        self.bot_instance = bot_instance
        self.add_item(CTARoleDropdown(event_id))
        self.add_item(CTALeaveButton(event_id))

        # ¡Estas líneas fueron eliminadas para corregir el error de custom_id duplicado!
        # Los botones 'Cerrar Evento' y 'Resetear Inscripciones' se añaden automáticamente
        # a la vista a través de sus decoradores @discord.ui.button.
        # No es necesario llamarlos explícitamente con self.add_item() aquí.

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", row=2)
    async def close_event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)
            return

        if self.event_id not in cta_events:
            await interaction.response.send_message("❌ Este evento CTA ya no está activo.", ephemeral=True)
            return

        thread = interaction.message.thread
        if thread:
            try:
                if thread.archived:
                    await thread.edit(archived=False, reason="Desarchivando para eliminar")
                await thread.delete()
                print(f"Hilo del evento CTA {self.event_id} eliminado correctamente.")
            except discord.NotFound:
                print(f"El hilo del evento CTA {self.event_id} ya no existe.")
            except discord.Forbidden:
                print(f"Error: El bot no tiene el permiso 'Manage Threads' o 'Manage Channels' para eliminar el hilo del evento CTA {self.event_id}.")
            except Exception as e:
                print(f"Error inesperado al eliminar el hilo del evento CTA {self.event_id}: {e}")
        else:
            print("No se encontró un hilo asociado al mensaje del evento CTA.")

        try:
            await interaction.message.delete()
            del cta_events[self.event_id]
            await interaction.response.send_message("✅ Evento CTA cerrado y mensaje eliminado.", ephemeral=True)
        except discord.NotFound:
            print(f"Mensaje del evento CTA {self.event_id} ya eliminado.")
        except Exception as e:
            print(f"Error al eliminar el mensaje del evento CTA {self.event_id}: {e}")

    @discord.ui.button(label="Resetear Inscripciones", style=discord.ButtonStyle.secondary, emoji="♻️", row=2)
    async def reset_inscriptions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede resetear las inscripciones.", ephemeral=True)
            return

        if self.event_id not in cta_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return
        
        event_data = cta_events[self.event_id]
        # Reiniciar inscripciones y listas de espera según la configuración de roles
        event_data["inscripciones"] = {role: [] for role in event_data["role_config"].keys()}
        event_data["waitlist"] = {role: [] for role in event_data["role_config"].keys()}

        await update_cta_embed(self.event_id, self.bot_instance)
        await interaction.response.send_message("✅ Se han reseteado todas las inscripciones y listas de espera del evento.", ephemeral=True)


# ====================================================================
# --- COG DE CTA ---
# ====================================================================

class CTACog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_cta_events.start()

    def cog_unload(self):
        self.cleanup_cta_events.cancel()

    @commands.command(name="cta", aliases=["calltoarms"])
    async def cta(self, ctx, mass_time: str):
        event_id = f"cta-{random.randint(1000, 9999)}"
        while event_id in cta_events:
            event_id = f"cta-{random.randint(1000, 9999)}"

        # Usar la configuración de roles predefinida para este evento
        event_data = {
            "mass_time": mass_time,
            "caller_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "thread_id": None,
            "message_id": None,
            "role_config": ALL_CTA_ROLES_CONFIG, # Aquí se asigna la configuración de roles
            "inscripciones": {role: [] for role in ALL_CTA_ROLES_CONFIG.keys()},
            "waitlist": {role: [] for role in ALL_CTA_ROLES_CONFIG.keys()},
            "creation_time": datetime.utcnow()
        }
        cta_events[event_id] = event_data

        embed = create_cta_embed(event_data, self.bot, event_id)
        view = CTAEventView(event_id, ctx.author.id, self.bot)
        
        try:
            message = await ctx.send(embed=embed, view=view)
            event_data["message_id"] = message.id
            event_data["message"] = message
            
            if isinstance(ctx.channel, discord.TextChannel):
                thread = await message.create_thread(name=f"CTA - {mass_time} UTC", auto_archive_duration=60)
                event_data["thread_id"] = thread.id
                await thread.send(f"¡Hilo de discusión para la Pelea Obligatoria! <@{ctx.author.id}>", silent=True)
        except Exception as e:
            print(f"Error al enviar mensaje o crear hilo para CTA: {e}")
            await ctx.send("❌ Hubo un error al crear el evento CTA. Intenta de nuevo más tarde.")
            if event_id in cta_events:
                del cta_events[event_id]
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("No tengo permisos para borrar el mensaje del comando original.")
        except discord.NotFound:
            pass

    @tasks.loop(seconds=60)
    async def cleanup_cta_events(self):
        events_to_remove = []
        current_time = datetime.utcnow()

        for event_id, event_data in list(cta_events.items()):
            creation_time = event_data.get("creation_time")
            message_id = event_data.get("message_id")
            channel_id = event_data.get("channel_id")

            if not creation_time or not message_id or not channel_id:
                print(f"Evento CTA {event_id} incompleto, marcando para eliminación.")
                events_to_remove.append(event_id)
                continue

            if (current_time - creation_time).total_seconds() > CTA_EVENT_TIMEOUT:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        print(f"Canal {channel_id} no encontrado para el evento CTA {event_id}.")
                        events_to_remove.append(event_id)
                        continue

                    message = await channel.fetch_message(message_id)
                    thread = message.thread
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
                
                events_to_remove.append(event_id)
            else:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.fetch_message(message_id)
                except discord.NotFound:
                    print(f"Mensaje del evento CTA {event_id} no encontrado en el canal, marcando para eliminación.")
                    events_to_remove.append(event_id)
                except Exception as e:
                    print(f"Error verificando mensaje CTA {event_id}: {e}")

        for event_id in events_to_remove:
            if event_id in cta_events:
                del cta_events[event_id]

    @cleanup_cta_events.before_loop
    async def before_cleanup_cta(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(CTACog(bot))
