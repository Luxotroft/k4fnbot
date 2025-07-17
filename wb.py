import discord
from discord.ext import commands, tasks
from discord import app_commands # Importar app_commands para comandos de barra
from datetime import datetime, timedelta
import asyncio
import time
import random
import re # ¡IMPORTANTE! Necesario para re.search

# ====================================================================
# --- DATOS Y VARIABLES GLOBALES DE WORLD BOSS ---
# ====================================================================

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

# ====================================================================
# --- FUNCIONES HELPER DE WORLD BOSS ---
# ====================================================================

async def update_wb_embed(event_id, bot_instance):
    if event_id not in wb_events:
        print(f"[DEBUG update_wb_embed] Event ID {event_id} not found in wb_events during update attempt.")
        return

    event = wb_events[event_id]
    boss = event["boss"]
    message = event["message"]

    if not message:
        print(f"[DEBUG update_wb_embed] Message object is None for event ID {event_id}.")
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
                embed_color = 0x00FF00
                embed.description = event["description"]
                if event_id in wb_priority_users:
                    del wb_priority_users[event_id]
        else:
            is_disabled = False
            footer_text = "🔓 Todos pueden anotarse"
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

        view = WB_RoleSelectorView(boss, event_id, event["caller_id"], bot_instance, disabled=is_disabled) # Pasa la instancia del bot
        await message.edit(embed=embed, view=view)

    except Exception as e:
        print(f"Error actualizando embed para el evento {event_id}: {e}")

# ====================================================================
# --- CLASES DE UI (VIEWS, BUTTONS, SELECTS) PARA WORLD BOSS ---
# ====================================================================

class WB_RoleDropdown(discord.ui.Select):
    def __init__(self, boss, event_id, disabled):
        self.boss = boss
        self.event_id = event_id
        options = []
        for role_name in WB_BOSS_DATA[boss]["roles"].keys():
            emoji_str = WB_BOSS_DATA[boss]["emojis"].get(role_name)
            options.append(discord.SelectOption(label=role_name, value=role_name, emoji=emoji_str))
        
        super().__init__(
            placeholder="Elige tu rol...",
            min_values=1,
            max_values=1,
            options=options,
            disabled=disabled,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in wb_events:
            await interaction.response.send_message("❌ Este evento WB ya no está activo.", ephemeral=True)
            return

        selected_role = self.values[0]
        user_id = interaction.user.id
        event_data = wb_events[self.event_id]
        
        # Remover al usuario de cualquier otro rol o lista de espera en este evento
        for role_name in WB_BOSS_DATA[self.boss]["roles"].keys():
            if user_id in event_data["inscriptions"].get(role_name, []):
                event_data["inscriptions"][role_name].remove(user_id)
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)

        # Añadir al usuario al rol seleccionado
        inscriptions_for_role = event_data["inscriptions"].setdefault(selected_role, [])
        role_limit = WB_BOSS_DATA[self.boss]["roles"][selected_role]

        if len(inscriptions_for_role) < role_limit:
            if user_id not in inscriptions_for_role:
                inscriptions_for_role.append(user_id)
                await interaction.response.send_message(f"✅ Te has inscrito como **{selected_role}**.", ephemeral=True)
            else:
                await interaction.response.send_message(f"ℹ️ Ya estás inscrito como **{selected_role}**.", ephemeral=True)
        else:
            # Rol lleno, añadir a lista de espera
            waitlist_for_role = event_data["waitlist"].setdefault(selected_role, [])
            if user_id not in waitlist_for_role:
                waitlist_for_role.append(user_id)
                await interaction.response.send_message(f"⚠️ El rol de **{selected_role}** está lleno. Te hemos añadido a la lista de espera.", ephemeral=True)
            else:
                await interaction.response.send_message(f"ℹ️ Ya estás en la lista de espera de **{selected_role}**.", ephemeral=True)
        
        await update_wb_embed(self.event_id, self.view.bot_instance) # Pasa la instancia del bot desde la vista


class WB_LeaveButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="Salirme", style=discord.ButtonStyle.red, emoji="👋", row=1)
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in wb_events:
            await interaction.response.send_message("❌ Este evento WB ya no está activo.", ephemeral=True)
            return

        user_id = interaction.user.id
        event_data = wb_events[self.event_id]
        found = False

        # Buscar y eliminar al usuario de cualquier rol o lista de espera
        for role_name in WB_BOSS_DATA[event_data["boss"]]["roles"].keys():
            if user_id in event_data["inscriptions"].get(role_name, []):
                event_data["inscriptions"][role_name].remove(user_id)
                found = True
                # Mover al siguiente de la lista de espera si hay espacio
                if event_data["waitlist"].get(role_name):
                    next_player_id = event_data["waitlist"][role_name].pop(0)
                    event_data["inscriptions"][role_name].append(next_player_id)
                    # Usar followup.send después de la respuesta inicial (ephemeral)
                    await interaction.followup.send(f"<@{next_player_id}>, ¡has sido movido de la lista de espera al rol de **{role_name}**!", ephemeral=False)
                break
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
                found = True
                break
        
        if found:
            await interaction.response.send_message("✅ Te has salido del evento.", ephemeral=True)
            await update_wb_embed(self.event_id, self.view.bot_instance) # Pasa la instancia del bot
        else:
            await interaction.response.send_message("ℹ️ No estabas inscrito en este evento.", ephemeral=True)


class WB_JoinWaitlistMainButton(discord.ui.Button):
    def __init__(self, boss, event_id):
        super().__init__(label="Lista de Espera General", style=discord.ButtonStyle.grey, emoji="⏳", row=1)
        self.boss = boss
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        if self.event_id not in wb_events:
            await interaction.response.send_message("❌ Este evento WB ya no está activo.", ephemeral=True)
            return

        user_id = interaction.user.id
        event_data = wb_events[self.event_id]

        # Quitar al usuario de cualquier rol en el que esté inscrito
        for role_name in WB_BOSS_DATA[self.boss]["roles"].keys():
            if user_id in event_data["inscriptions"].get(role_name, []):
                event_data["inscriptions"][role_name].remove(user_id)
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
        
        await update_wb_embed(self.event_id, self.view.bot_instance)


class WB_RoleSelectorView(discord.ui.View):
    def __init__(self, boss, event_id, caller_id, bot_instance, disabled=False):
        super().__init__(timeout=None)
        self.caller_id = caller_id
        self.event_id = event_id
        self.boss = boss
        self.bot_instance = bot_instance # Guardar la instancia del bot
        self.add_item(WB_RoleDropdown(boss, event_id, disabled))
        self.add_item(WB_LeaveButton(event_id))
        self.add_item(WB_JoinWaitlistMainButton(boss, event_id))

    @discord.ui.button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", row=2)
    async def close_event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede cerrarlo.", ephemeral=True)
            return

        if self.event_id not in wb_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True) # Defer para evitar timeout si el hilo tarda en borrar

        thread = interaction.message.thread
        if thread:
            try:
                if thread.archived:
                    await thread.edit(archived=False, reason="Desarchivando para eliminar")
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

        try:
            await interaction.message.delete()
            del wb_events[self.event_id]
            await interaction.followup.send("✅ Evento WB cerrado y mensaje eliminado.", ephemeral=True)
        except discord.NotFound:
            print(f"Mensaje del evento WB {self.event_id} ya eliminado.")
            await interaction.followup.send("✅ Evento WB cerrado (el mensaje ya había sido eliminado).", ephemeral=True)
        except Exception as e:
            print(f"Error al eliminar el mensaje del evento WB {self.event_id}: {e}")
            await interaction.followup.send(f"❌ Hubo un error al eliminar el mensaje del evento: {e}", ephemeral=True)


    @discord.ui.button(label="Activar Prioridad", style=discord.ButtonStyle.blurple, emoji="🚨", row=2)
    async def activate_priority_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # --- LÍNEAS DE DEPURACIÓN AÑADIDAS ---
        print(f"[DEBUG Prioridad] Botón 'Activar Prioridad' clicado para event_id: {self.event_id}")
        print(f"[DEBUG Prioridad] Keys actuales en wb_events: {list(wb_events.keys())}")
        # -------------------------------------

        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede activar la prioridad.", ephemeral=True)
            return

        if self.event_id not in wb_events:
            print(f"[DEBUG Prioridad] ERROR: Event ID {self.event_id} no encontrado en wb_events al activar prioridad.")
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return

        event_data = wb_events[self.event_id]

        if event_data.get("priority_mode", False):
            await interaction.response.send_message("ℹ️ El modo prioridad ya está activo para este evento.", ephemeral=True)
            return

        # Pedir slots y duración
        class PriorityConfigModal(discord.ui.Modal, title="Configurar Prioridad"):
            slots_input = discord.ui.TextInput(label="Número de slots de prioridad", placeholder="Ej: 5", required=True)
            duration_input = discord.ui.TextInput(label="Duración de la prioridad (minutos)", placeholder="Ej: 15", required=True)

            # Referencia a la vista para acceder a event_id y bot_instance
            def __init__(self, parent_view):
                super().__init__()
                self.parent_view = parent_view

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    slots = int(self.slots_input.value)
                    duration_minutes = int(self.duration_input.value)
                    if slots <= 0 or duration_minutes <= 0:
                        await modal_interaction.response.send_message("❌ Los valores de slots y duración deben ser mayores a 0.", ephemeral=True)
                        return

                    wb_priority_users[self.parent_view.event_id] = { # Usar parent_view
                        "users": [],
                        "expiry": time.time() + (duration_minutes * 60),
                        "slots": slots
                    }
                    event_data["priority_mode"] = True
                    await update_wb_embed(self.parent_view.event_id, self.parent_view.bot_instance) # Usar parent_view
                    await modal_interaction.response.send_message(f"✅ Modo prioridad activado para {slots} slots durante {duration_minutes} minutos.", ephemeral=True)

                except ValueError:
                    await modal_interaction.response.send_message("❌ Por favor, introduce números válidos para slots y duración.", ephemeral=True)

        # Crear una instancia del modal y mostrarla
        modal = PriorityConfigModal(self) # Pasa la vista actual al modal
        await interaction.response.send_modal(modal)


    @discord.ui.button(label="Desactivar Prioridad", style=discord.ButtonStyle.secondary, emoji="🔓", row=2)
    async def deactivate_priority_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede desactivar la prioridad.", ephemeral=True)
            return

        if self.event_id not in wb_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return
        
        event_data = wb_events[self.event_id]
        if not event_data.get("priority_mode", False):
            await interaction.response.send_message("ℹ️ El modo prioridad no está activo para este evento.", ephemeral=True)
            return
        
        event_data["priority_mode"] = False
        if self.event_id in wb_priority_users:
            del wb_priority_users[self.event_id]

        await update_wb_embed(self.event_id, self.bot_instance)
        await interaction.response.send_message("✅ Modo prioridad desactivado.", ephemeral=True)


    @discord.ui.button(label="Agregar Prioritario", style=discord.ButtonStyle.green, emoji="➕", row=3)
    async def add_priority_user_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede agregar usuarios prioritarios.", ephemeral=True)
            return

        if self.event_id not in wb_events or not wb_events[self.event_id].get("priority_mode", False):
            await interaction.response.send_message("❌ El modo prioridad no está activo para este evento.", ephemeral=True)
            return

        priority_data = wb_priority_users.get(self.event_id)
        if not priority_data:
            await interaction.response.send_message("❌ No hay datos de prioridad para este evento. Activa la prioridad primero.", ephemeral=True)
            return

        class AddPriorityUserModal(discord.ui.Modal, title="Agregar Usuario Prioritario"):
            user_input = discord.ui.TextInput(label="Menciona al usuario", placeholder="Ej: @Usuario#1234", required=True)

            def __init__(self, parent_view):
                super().__init__()
                self.parent_view = parent_view # Guardar referencia a la vista

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    user_mention = self.user_input.value.strip()
                    user_id_match = re.search(r'<@!?(\d+)>', user_mention)
                    
                    if not user_id_match:
                        await modal_interaction.response.send_message("❌ Formato de usuario inválido. Por favor, menciona al usuario.", ephemeral=True)
                        return
                    
                    user_id = int(user_id_match.group(1))

                    if user_id in priority_data["users"]:
                        await modal_interaction.response.send_message("ℹ️ Ese usuario ya es prioritario para este evento.", ephemeral=True)
                        return

                    if len(priority_data["users"]) >= priority_data["slots"]:
                        await modal_interaction.response.send_message("❌ No hay slots de prioridad disponibles.", ephemeral=True)
                        return
                    
                    priority_data["users"].append(user_id)
                    await update_wb_embed(self.parent_view.event_id, self.parent_view.bot_instance) # Usar parent_view
                    await modal_interaction.response.send_message(f"✅ <@{user_id}> ha sido añadido a la lista de prioritarios.", ephemeral=True)

                except Exception as e:
                    await modal_interaction.response.send_message(f"❌ Error al agregar usuario: {e}", ephemeral=True)

        modal = AddPriorityUserModal(self) # Pasa la vista actual al modal
        await interaction.response.send_modal(modal)


    @discord.ui.button(label="Remover Prioritario", style=discord.ButtonStyle.red, emoji="➖", row=3)
    async def remove_priority_user_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede remover usuarios prioritarios.", ephemeral=True)
            return

        if self.event_id not in wb_events or not wb_events[self.event_id].get("priority_mode", False):
            await interaction.response.send_message("❌ El modo prioridad no está activo para este evento.", ephemeral=True)
            return

        priority_data = wb_priority_users.get(self.event_id)
        if not priority_data or not priority_data["users"]:
            await interaction.response.send_message("ℹ️ No hay usuarios prioritarios para remover en este evento.", ephemeral=True)
            return

        class RemovePriorityUserModal(discord.ui.Modal, title="Remover Usuario Prioritario"):
            user_input = discord.ui.TextInput(label="Menciona al usuario", placeholder="Ej: @Usuario#1234", required=True)

            def __init__(self, parent_view):
                super().__init__()
                self.parent_view = parent_view # Guardar referencia a la vista

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    user_mention = self.user_input.value.strip()
                    user_id_match = re.search(r'<@!?(\d+)>', user_mention)
                    
                    if not user_id_match:
                        await modal_interaction.response.send_message("❌ Formato de usuario inválido. Por favor, menciona al usuario.", ephemeral=True)
                        return
                    
                    user_id = int(user_id_match.group(1))

                    if user_id not in priority_data["users"]:
                        await modal_interaction.response.send_message("ℹ️ Ese usuario no es prioritario para este evento.", ephemeral=True)
                        return
                    
                    priority_data["users"].remove(user_id)
                    await update_wb_embed(self.parent_view.event_id, self.parent_view.bot_instance) # Usar parent_view
                    await modal_interaction.response.send_message(f"✅ <@{user_id}> ha sido removido de la lista de prioritarios.", ephemeral=True)

                except Exception as e:
                    await modal_interaction.response.send_message(f"❌ Error al remover usuario: {e}", ephemeral=True)

        modal = RemovePriorityUserModal(self) # Pasa la vista actual al modal
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Resetear Inscripciones", style=discord.ButtonStyle.secondary, emoji="♻️", row=3)
    async def reset_inscriptions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            await interaction.response.send_message("❌ Solo el que lanzó el evento puede resetear las inscripciones.", ephemeral=True)
            return

        if self.event_id not in wb_events:
            await interaction.response.send_message("❌ Este evento ya no está activo.", ephemeral=True)
            return
        
        event_data = wb_events[self.event_id]
        event_data["inscriptions"] = {rol: [] for rol in WB_BOSS_DATA[event_data["boss"]]["roles"].keys()}
        event_data["waitlist"] = {rol: [] for rol in WB_BOSS_DATA[event_data["boss"]]["roles"].keys()}
        event_data["general_waitlist"] = [] # Asumiendo que también hay una general_waitlist para WB

        await update_wb_embed(self.event_id, self.bot_instance)
        await interaction.response.send_message("✅ Se han reseteado todas las inscripciones y listas de espera del evento.", ephemeral=True)

# ====================================================================
# --- COG DE WORLD BOSS ---
# ====================================================================

class WorldBossCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_wb_events.start()

    def cog_unload(self):
        self.cleanup_wb_events.cancel()

    @app_commands.command(name="wb", description="Inicia un evento de World Boss.")
    @app_commands.describe(
        boss_type="Tipo de World Boss (elder o eye)",
        duration="Tiempo mínimo de duración en minutos (default: 60)"
    )
    async def wb(self, interaction: discord.Interaction, boss_type: str, duration: app_commands.Range[int, 1, None] = 60):
        # Es crucial deferir la respuesta para que Discord no dé timeout
        await interaction.response.defer() 

        boss_type_lower = boss_type.lower()
        if boss_type_lower not in WB_BOSS_DATA:
            await interaction.followup.send(f"❌ El tipo de World Boss '{boss_type}' no existe. Opciones: {', '.join(WB_BOSS_DATA.keys())}", ephemeral=True)
            return

        event_id = f"wb-{random.randint(1000, 9999)}"
        while event_id in wb_events:
            event_id = f"wb-{random.randint(1000, 9999)}"

        event_description = WB_BOSS_DATA[boss_type_lower]["default_description"].format(duration=duration)

        event_data = {
            "boss": boss_type_lower,
            "caller_id": interaction.user.id, # Usar interaction.user.id
            "channel_id": interaction.channel_id, # Usar interaction.channel_id
            "thread_id": None,
            "message_id": None,
            "inscriptions": {role: [] for role in WB_BOSS_DATA[boss_type_lower]["roles"].keys()},
            "waitlist": {role: [] for role in WB_BOSS_DATA[boss_type_lower]["roles"].keys()},
            "creation_time": datetime.utcnow(),
            "description": event_description,
            "priority_mode": False
        }
        wb_events[event_id] = event_data
        
        # --- LÍNEAS DE DEPURACIÓN AÑADIDAS ---
        print(f"[DEBUG WB] Evento creado con ID: {event_id}")
        print(f"[DEBUG WB] wb_events contiene {len(wb_events)} eventos. Keys: {list(wb_events.keys())}")
        # -------------------------------------

        embed = discord.Embed(
            title=f"👑 WORLD BOSS - {WB_BOSS_DATA[boss_type_lower]['name']}",
            description=event_description,
            color=0x00FF00
        )
        embed.set_footer(text="🔓 Todos pueden anotarse")
        embed.timestamp = datetime.utcnow()

        for role in WB_BOSS_DATA[boss_type_lower]["roles"]:
            embed.add_field(
                name=f"{WB_BOSS_DATA[boss_type_lower]['emojis'].get(role)} {role} ({len(event_data['inscriptions'][role])}/{WB_BOSS_DATA[boss_type_lower]['roles'][role]})",
                value="🚫 Vacío",
                inline=False
            )

        view = WB_RoleSelectorView(boss_type_lower, event_id, interaction.user.id, self.bot) # Pasa la instancia del bot
        
        try:
            # En comandos de barra, usa followup.send() después de defer()
            message = await interaction.followup.send(embed=embed, view=view)
            event_data["message_id"] = message.id
            event_data["message"] = message

            if isinstance(interaction.channel, discord.TextChannel): # Usar interaction.channel
                thread = await message.create_thread(name=f"WB {WB_BOSS_DATA[boss_type_lower]['name']}", auto_archive_duration=60)
                event_data["thread_id"] = thread.id
                await thread.send(f"¡Hilo de discusión para el World Boss '{WB_BOSS_DATA[boss_type_lower]['name']}'! <@{interaction.user.id}>", silent=True)
        except Exception as e:
            # --- LÍNEA DE DEPURACIÓN CLAVE ---
            print(f"Error al enviar mensaje o crear hilo para WB: {e}")
            # ---------------------------------
            await interaction.followup.send("❌ Hubo un error al crear el evento de World Boss. Intenta de nuevo más tarde.", ephemeral=True)
            if event_id in wb_events:
                del wb_events[event_id]
            return

    @app_commands.command(name="wbadd", description="Añade un usuario a un rol específico de un evento WB.")
    @app_commands.describe(
        event_id="ID del evento WB (ej. wb-1234)",
        role_name="Nombre del rol al que añadir (ej. Main Tank)",
        user="Usuario a añadir"
    )
    async def wb_add_user(self, interaction: discord.Interaction, event_id: str, user: discord.Member, role_name: str):
        # Asegurarse de que role_name es la última variable en la definición si no es de tipo discord.Member
        # o reorganizar el orden de los argumentos en el decorador @app_commands.describe
        # según cómo se definen en la función.
        # Por convención, discord.Member/discord.Channel/etc. suelen ir al final.
        # Si role_name es un String, debe ser el último si hay un discord.Member antes.
        # Corregido a role_name al final en @app_commands.describe para coincidir.

        await interaction.response.defer(ephemeral=True) # Deferir la respuesta

        if event_id not in wb_events:
            await interaction.followup.send("❌ ID de evento WB no encontrado.", ephemeral=True)
            return
        
        event_data = wb_events[event_id]
        boss_type = event_data["boss"]
        
        if role_name not in WB_BOSS_DATA[boss_type]["roles"]:
            await interaction.followup.send(f"❌ Rol '{role_name}' no existe para este WB.", ephemeral=True)
            return

        user_id = user.id

        # Remover al usuario de cualquier otro rol o lista de espera en este evento
        for r_name in WB_BOSS_DATA[boss_type]["roles"].keys():
            if user_id in event_data["inscriptions"].get(r_name, []):
                event_data["inscriptions"][r_name].remove(user_id)
            if user_id in event_data["waitlist"].get(r_name, []):
                event_data["waitlist"][r_name].remove(user_id)

        # Añadir al usuario al rol especificado
        inscriptions_for_role = event_data["inscriptions"].setdefault(role_name, [])
        role_limit = WB_BOSS_DATA[boss_type]["roles"][role_name]

        if len(inscriptions_for_role) < role_limit:
            if user_id not in inscriptions_for_role:
                inscriptions_for_role.append(user_id)
                await interaction.followup.send(f"✅ <@{user_id}> ha sido añadido como **{role_name}**.", ephemeral=True)
            else:
                await interaction.followup.send(f"ℹ️ <@{user_id}> ya está inscrito como **{role_name}**.", ephemeral=True)
        else:
            # Rol lleno, añadir a lista de espera
            waitlist_for_role = event_data["waitlist"].setdefault(role_name, [])
            if user_id not in waitlist_for_role:
                waitlist_for_role.append(user_id)
                await interaction.followup.send(f"⚠️ El rol de **{role_name}** está lleno. <@{user_id}> ha sido añadido a la lista de espera.", ephemeral=True)
            else:
                await interaction.followup.send(f"ℹ️ <@{user_id}> ya está en la lista de espera de **{role_name}**.", ephemeral=True)
        
        await update_wb_embed(event_id, self.bot) # Pasa la instancia del bot


    @app_commands.command(name="wbremove", description="Remueve un usuario de un evento WB.")
    @app_commands.describe(
        event_id="ID del evento WB (ej. wb-1234)",
        user="Usuario a remover"
    )
    async def wb_remove_user(self, interaction: discord.Interaction, event_id: str, user: discord.Member):
        await interaction.response.defer(ephemeral=True) # Deferir la respuesta

        if event_id not in wb_events:
            await interaction.followup.send("❌ ID de evento WB no encontrado.", ephemeral=True)
            return
        
        event_data = wb_events[event_id]
        user_id = user.id
        found = False

        # Buscar y eliminar al usuario de cualquier rol o lista de espera
        for role_name in WB_BOSS_DATA[event_data["boss"]]["roles"].keys():
            if user_id in event_data["inscriptions"].get(role_name, []):
                event_data["inscriptions"][role_name].remove(user_id)
                found = True
                # Mover al siguiente de la lista de espera si hay espacio
                if event_data["waitlist"].get(role_name):
                    next_player_id = event_data["waitlist"][role_name].pop(0)
                    event_data["inscriptions"][role_name].append(next_player_id)
                    await interaction.followup.send(f"<@{next_player_id}>, ¡has sido movido de la lista de espera al rol de **{role_name}**!", ephemeral=False)
                break
            if user_id in event_data["waitlist"].get(role_name, []):
                event_data["waitlist"][role_name].remove(user_id)
                found = True
                break
        
        if found:
            await interaction.followup.send(f"✅ <@{user_id}> ha sido removido del evento WB.", ephemeral=True)
            await update_wb_embed(event_id, self.bot)
        else:
            await interaction.followup.send(f"ℹ️ <@{user_id}> no estaba inscrito en este evento WB.", ephemeral=True)

    @tasks.loop(seconds=60)
    async def cleanup_wb_events(self):
        events_to_remove = []
        current_time = datetime.utcnow()

        for event_id, event_data in list(wb_events.items()):
            creation_time = event_data.get("creation_time")
            message_id = event_data.get("message_id")
            channel_id = event_data.get("channel_id")

            if not creation_time or not message_id or not channel_id:
                print(f"[DEBUG Cleanup] Evento WB {event_id} incompleto, marcando para eliminación.")
                events_to_remove.append(event_id)
                continue

            if (current_time - creation_time).total_seconds() > WB_EVENT_TIMEOUT:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        print(f"[DEBUG Cleanup] Canal {channel_id} no encontrado para el evento WB {event_id}.")
                        events_to_remove.append(event_id)
                        continue
                    
                    message = await channel.fetch_message(message_id)
                    thread = message.thread
                    if thread:
                        if thread.archived:
                            await thread.edit(archived=False, reason="Desarchivando para eliminar por expiración WB")
                        await thread.delete()
                        print(f"[DEBUG Cleanup] Hilo del evento WB expirado {event_id} eliminado.")
                    await message.delete()
                    print(f"[DEBUG Cleanup] Mensaje del evento WB expirado {event_id} eliminado.")
                except discord.NotFound:
                    print(f"[DEBUG Cleanup] Mensaje o hilo del evento WB expirado {event_id} ya no existe.")
                except discord.Forbidden:
                    print(f"[DEBUG Cleanup] Fallo al eliminar el mensaje/hilo del evento WB expirado {event_id}. Permisos faltantes.")
                except Exception as e:
                    print(f"[DEBUG Cleanup] Error inesperado al eliminar el mensaje del evento WB expirado {event_id}: {e}")
                
                events_to_remove.append(event_id)
        
        for event_id in events_to_remove:
            if event_id in wb_events:
                del wb_events[event_id]

    @cleanup_wb_events.before_loop
    async def before_cleanup_wb(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(WorldBossCog(bot))
