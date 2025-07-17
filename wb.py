import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import time
import random
import re
import traceback

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

wb_events = {}
wb_priority_users = {}
WB_EVENT_TIMEOUT = 7200  # 2 horas

# ====================================================================
# --- FUNCIONES HELPER ---
# ====================================================================

async def log_error(error_message, interaction=None):
    """Registra errores detallados con traceback"""
    error_trace = traceback.format_exc()
    full_error = f"ERROR: {error_message}\n{error_trace}"
    print(full_error)
    
    if interaction:
        try:
            await interaction.followup.send(f"🔴 Error interno: {error_message}", ephemeral=True)
        except:
            pass

async def update_wb_embed(event_id, bot_instance):
    try:
        if event_id not in wb_events:
            return

        event = wb_events[event_id]
        message = event.get("message")
        if not message:
            return

        embed = message.embeds[0].copy() if message.embeds else discord.Embed()
        embed.clear_fields()

        boss = event["boss"]
        is_disabled = False
        footer_text = ""
        embed_color = 0x8B0000

        # Manejo de modo prioridad
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
                is_disabled = True
                footer_text = "🔒 Solo usuarios prioritarios pueden anotarse"
                embed_color = 0xFF4500
            else:
                event["priority_mode"] = False
                footer_text = "🔓 Todos pueden anotarse"
                embed_color = 0x00FF00
                embed.description = event["description"]
                if event_id in wb_priority_users:
                    del wb_priority_users[event_id]
        else:
            footer_text = "🔓 Todos pueden anotarse"
            embed_color = 0x00FF00
            embed.description = event["description"]

        embed.set_footer(text=footer_text)
        embed.color = embed_color

        # Actualizar campos de roles
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

        view = WB_RoleSelectorView(boss, event_id, event["caller_id"], bot_instance, disabled=is_disabled)
        await message.edit(embed=embed, view=view)

    except Exception as e:
        await log_error(f"Error al actualizar embed para evento {event_id}", None)

# ====================================================================
# --- VISTAS Y COMPONENTES DE UI ---
# ====================================================================

class WB_RoleDropdown(discord.ui.Select):
    def __init__(self, boss, event_id, disabled):
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
        try:
            if self.view.event_id not in wb_events:
                await interaction.response.send_message("❌ Este evento WB ya no está activo.", ephemeral=True)
                return

            selected_role = self.values[0]
            user_id = interaction.user.id
            event_data = wb_events[self.view.event_id]
            
            # Remover al usuario de otros roles
            for role_name in WB_BOSS_DATA[self.view.boss]["roles"].keys():
                if user_id in event_data["inscriptions"].get(role_name, []):
                    event_data["inscriptions"][role_name].remove(user_id)
                if user_id in event_data["waitlist"].get(role_name, []):
                    event_data["waitlist"][role_name].remove(user_id)

            # Añadir al rol seleccionado
            role_limit = WB_BOSS_DATA[self.view.boss]["roles"][selected_role]
            inscriptions = event_data["inscriptions"].setdefault(selected_role, [])
            waitlist = event_data["waitlist"].setdefault(selected_role, [])

            if len(inscriptions) < role_limit:
                inscriptions.append(user_id)
                await interaction.response.send_message(f"✅ Te has inscrito como **{selected_role}**.", ephemeral=True)
            else:
                waitlist.append(user_id)
                await interaction.response.send_message(f"⚠️ Rol lleno. Lista de espera para **{selected_role}**.", ephemeral=True)
            
            await update_wb_embed(self.view.event_id, self.view.bot_instance)

        except Exception as e:
            await log_error("Error en RoleDropdown callback", interaction)

class WB_RoleSelectorView(discord.ui.View):
    def __init__(self, boss, event_id, caller_id, bot_instance, disabled=False):
        super().__init__(timeout=None)
        self.boss = boss
        self.event_id = event_id
        self.caller_id = caller_id
        self.bot_instance = bot_instance
        
        self.add_item(WB_RoleDropdown(boss, event_id, disabled))
        self.add_item(discord.ui.Button(label="Salirme", style=discord.ButtonStyle.red, emoji="👋", row=1, custom_id=f"leave_{event_id}"))
        self.add_item(discord.ui.Button(label="Lista Espera", style=discord.ButtonStyle.grey, emoji="⏳", row=1, custom_id=f"waitlist_{event_id}"))
        
        # Botones de administración
        self.add_item(discord.ui.Button(label="Cerrar Evento", style=discord.ButtonStyle.danger, emoji="🚫", row=2, custom_id=f"close_{event_id}"))
        self.add_item(discord.ui.Button(label="Activar Prioridad", style=discord.ButtonStyle.blurple, emoji="🚨", row=2, custom_id=f"priority_{event_id}"))
        self.add_item(discord.ui.Button(label="Resetear", style=discord.ButtonStyle.secondary, emoji="♻️", row=2, custom_id=f"reset_{event_id}"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        try:
            if interaction.data.get("custom_id", "").startswith("close_") and interaction.user.id != self.caller_id:
                await interaction.response.send_message("❌ Solo el organizador puede cerrar el evento.", ephemeral=True)
                return False
            return True
        except Exception as e:
            await log_error("Error en interaction_check", interaction)
            return False

# ====================================================================
# --- COG PRINCIPAL ---
# ====================================================================

class WorldBossCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_task = self.cleanup_wb_events.start()

    def cog_unload(self):
        self.cleanup_task.cancel()

    @app_commands.command(name="wb", description="Inicia un evento de World Boss")
    @app_commands.describe(
        boss_type="Tipo de World Boss (elder o eye)",
        duration="Duración mínima en minutos (default: 60)"
    )
    async def wb_command(self, interaction: discord.Interaction, boss_type: str, duration: int = 60):
        """Manejador principal del comando /wb"""
        await interaction.response.defer()
        
        try:
            boss_type = boss_type.lower()
            if boss_type not in WB_BOSS_DATA:
                await interaction.followup.send(
                    f"❌ Boss '{boss_type}' no válido. Opciones: elder, eye",
                    ephemeral=True
                )
                return

            # Crear ID único para el evento
            event_id = f"wb-{random.randint(1000, 9999)}"
            while event_id in wb_events:
                event_id = f"wb-{random.randint(1000, 9999)}"

            # Configurar datos del evento
            event_data = {
                "boss": boss_type,
                "caller_id": interaction.user.id,
                "channel_id": interaction.channel_id,
                "message": None,
                "inscriptions": {role: [] for role in WB_BOSS_DATA[boss_type]["roles"]},
                "waitlist": {role: [] for role in WB_BOSS_DATA[boss_type]["roles"]},
                "creation_time": datetime.utcnow(),
                "description": WB_BOSS_DATA[boss_type]["default_description"].format(duration=duration),
                "priority_mode": False
            }
            wb_events[event_id] = event_data

            # Crear embed
            embed = discord.Embed(
                title=f"👑 WORLD BOSS - {WB_BOSS_DATA[boss_type]['name']}",
                description=event_data["description"],
                color=0x00FF00
            )
            embed.set_footer(text="🔓 Todos pueden anotarse")
            
            for role in WB_BOSS_DATA[boss_type]["roles"]:
                embed.add_field(
                    name=f"{WB_BOSS_DATA[boss_type]['emojis'].get(role)} {role} (0/{WB_BOSS_DATA[boss_type]['roles'][role]})",
                    value="🚫 Vacío",
                    inline=False
                )

            # Crear y enviar vista
            view = WB_RoleSelectorView(boss_type, event_id, interaction.user.id, self.bot)
            message = await interaction.followup.send(embed=embed, view=view)
            event_data["message"] = message

            # Crear hilo de discusión
            if isinstance(interaction.channel, discord.TextChannel):
                try:
                    thread = await message.create_thread(
                        name=f"WB {WB_BOSS_DATA[boss_type]['name']}",
                        auto_archive_duration=60
                    )
                    event_data["thread_id"] = thread.id
                    await thread.send(f"💬 Hilo de discusión para {interaction.user.mention}", silent=True)
                except discord.Forbidden:
                    await interaction.followup.send(
                        "⚠️ Evento creado pero no pude crear el hilo (falta permiso)",
                        ephemeral=True
                    )

        except Exception as e:
            await log_error(f"Error en comando /wb: {str(e)}", interaction)
            if event_id in wb_events:
                del wb_events[event_id]
            await interaction.followup.send(
                "❌ Error crítico al crear el evento. Contacta al administrador.",
                ephemeral=True
            )

    @tasks.loop(minutes=5)
    async def cleanup_wb_events(self):
        """Limpia eventos antiguos automáticamente"""
        try:
            current_time = datetime.utcnow()
            to_remove = []

            for event_id, event in wb_events.items():
                if (current_time - event["creation_time"]).total_seconds() > WB_EVENT_TIMEOUT:
                    try:
                        if event.get("message"):
                            await event["message"].delete()
                        if event.get("thread_id"):
                            thread = self.bot.get_channel(event["thread_id"])
                            if thread:
                                await thread.delete()
                    except:
                        pass
                    to_remove.append(event_id)

            for event_id in to_remove:
                wb_events.pop(event_id, None)

        except Exception as e:
            print(f"Error en cleanup_wb_events: {str(e)}")

    @cleanup_wb_events.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WorldBossCog(bot))
