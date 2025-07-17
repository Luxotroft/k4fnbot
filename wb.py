import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import random
import time
import traceback

# ====================================================================
# --- CONFIGURACIÓN DE WORLD BOSS ---
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
            "Main Tank": "<:Incubo:1290858544488386633>",
            "Off Tank": "<:stoper:1290858463135662080>",
            "Main Healer": "<:Santificador:1290858870260109384>",
            "Gran Arcano": "<:GranArcano:1337861969931407411>",
            "Prisma": "<:Prisma:1367151400672559184>",
            "Invocador Oscuro (SC)": "<:InvocadorOscuro:1290880853353955338>",
            "Flamígero": "<:BLAZING:1357789213558439956>",
            "Light Caller (LC)": "<:LIGHT_CALLER:1357788956137226361>",
            "Montura Rinoceronte": "<:MonturaMana:1337863658859925676>",
            "Scout - Adelante": "<:Lecho:1337861780780875876>",
            "Scout - Atrás": "<:Lecho:1337861780780875876>",
            "Scout Patrol": "<:Lecho:1337861780780875876>",
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
    }
}

wb_events = {}
WB_EVENT_TIMEOUT = 7200  # 2 horas

# ====================================================================
# --- VISTAS INTERACTIVAS ---
# ====================================================================

class WB_RoleDropdown(discord.ui.Select):
    def __init__(self, boss, event_id):
        options = [
            discord.SelectOption(
                label=role,
                emoji=WB_BOSS_DATA[boss]["emojis"].get(role),
                description=f"Slots: {WB_BOSS_DATA[boss]['roles'][role]}"
            ) for role in WB_BOSS_DATA[boss]["roles"]
        ]
        super().__init__(
            placeholder="Selecciona tu rol",
            options=options,
            min_values=1,
            max_values=1
        )
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if self.event_id not in wb_events:
            return await interaction.followup.send("❌ Este evento ya no está activo", ephemeral=True)

        event = wb_events[self.event_id]
        selected_role = self.values[0]
        user_id = interaction.user.id

        # Remover de otros roles
        for role in event["inscriptions"]:
            if user_id in event["inscriptions"][role]:
                event["inscriptions"][role].remove(user_id)
            if user_id in event["waitlist"][role]:
                event["waitlist"][role].remove(user_id)

        # Añadir al rol seleccionado
        role_limit = WB_BOSS_DATA[event["boss"]]["roles"][selected_role]
        if len(event["inscriptions"][selected_role]) < role_limit:
            event["inscriptions"][selected_role].append(user_id)
            await interaction.followup.send(f"✅ Te has unido como **{selected_role}**", ephemeral=True)
        else:
            event["waitlist"][selected_role].append(user_id)
            await interaction.followup.send(f"⏳ Lista de espera para **{selected_role}**", ephemeral=True)

        await update_wb_embed(self.event_id, interaction.client)

class WB_RoleSelectorView(discord.ui.View):
    def __init__(self, boss, event_id, caller_id):
        super().__init__(timeout=None)
        self.add_item(WB_RoleDropdown(boss, event_id))
        
        @discord.ui.button(label="Salir", style=discord.ButtonStyle.red, emoji="🚪")
        async def leave_button(interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer(ephemeral=True)
            if event_id not in wb_events:
                return await interaction.followup.send("❌ Evento no encontrado", ephemeral=True)

            event = wb_events[event_id]
            user_id = interaction.user.id
            removed = False

            for role in event["inscriptions"]:
                if user_id in event["inscriptions"][role]:
                    event["inscriptions"][role].remove(user_id)
                    removed = True
                    # Mover siguiente de lista de espera
                    if event["waitlist"][role]:
                        next_user = event["waitlist"][role].pop(0)
                        event["inscriptions"][role].append(next_user)
                        try:
                            user = await interaction.guild.fetch_member(next_user)
                            await user.send(f"🎉 Has sido movido al rol {role}!")
                        except:
                            pass

            if not removed:
                for role in event["waitlist"]:
                    if user_id in event["waitlist"][role]:
                        event["waitlist"][role].remove(user_id)
                        removed = True

            if removed:
                await interaction.followup.send("✅ Has salido del evento", ephemeral=True)
                await update_wb_embed(event_id, interaction.client)
            else:
                await interaction.followup.send("❌ No estabas inscrito", ephemeral=True)

# ====================================================================
# --- FUNCIONES AUXILIARES ---
# ====================================================================

async def update_wb_embed(event_id, bot):
    if event_id not in wb_events:
        return

    event = wb_events[event_id]
    message = event.get("message")
    if not message:
        return

    try:
        embed = discord.Embed(
            title=f"👑 WORLD BOSS - {WB_BOSS_DATA[event['boss']]['name']}",
            description=event["description"],
            color=0x00FF00
        )

        for role in WB_BOSS_DATA[event['boss']]["roles"]:
            players = ", ".join([f"<@{p}>" for p in event["inscriptions"][role]])
            waitlist = ", ".join([f"<@{w}>" for w in event["waitlist"][role]])

            value = "🚫 Vacío"
            if players:
                value = f"👥 {players}"
            if waitlist:
                value += f"\n⏳ {waitlist}"

            embed.add_field(
                name=f"{WB_BOSS_DATA[event['boss']]['emojis'].get(role)} {role} ({len(event['inscriptions'][role])}/{WB_BOSS_DATA[event['boss']]['roles'][role]})",
                value=value,
                inline=False
            )

        view = WB_RoleSelectorView(event['boss'], event_id, event['caller_id'])
        await message.edit(embed=embed, view=view)

    except Exception as e:
        print(f"Error actualizando embed: {e}")
        traceback.print_exc()

# ====================================================================
# --- COG PRINCIPAL ---
# ====================================================================

class WorldBossCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_task = self.cleanup_wb_events.start()

    def cog_unload(self):
        self.cleanup_task.cancel()

    @app_commands.command(name="wb", description="Crea un evento de World Boss")
    @app_commands.describe(
        boss_type="Tipo de World Boss (elder o eye)",
        duration="Duración mínima en minutos (default: 60)"
    )
    @app_commands.guild_only()
    async def wb_command(self, interaction: discord.Interaction, boss_type: str, duration: int = 60):
        """Manejador del comando /wb"""
        try:
            # Verificar que estamos en un servidor
            if not interaction.guild:
                return await interaction.response.send_message(
                    "❌ Este comando solo puede usarse en servidores",
                    ephemeral=True
                )

            await interaction.response.defer()

            boss_type = boss_type.lower()
            if boss_type not in WB_BOSS_DATA:
                return await interaction.followup.send(
                    f"❌ Boss inválido. Opciones: elder, eye",
                    ephemeral=True
                )

            # Crear ID único
            event_id = f"wb-{random.randint(1000, 9999)}"
            while event_id in wb_events:
                event_id = f"wb-{random.randint(1000, 9999)}"

            # Configurar evento
            event_data = {
                "boss": boss_type,
                "caller_id": interaction.user.id,
                "channel_id": interaction.channel_id,
                "message": None,
                "inscriptions": {role: [] for role in WB_BOSS_DATA[boss_type]["roles"]},
                "waitlist": {role: [] for role in WB_BOSS_DATA[boss_type]["roles"]},
                "creation_time": datetime.utcnow(),
                "description": WB_BOSS_DATA[boss_type]["default_description"].format(duration=duration)
            }
            wb_events[event_id] = event_data

            # Crear embed
            embed = discord.Embed(
                title=f"👑 WORLD BOSS - {WB_BOSS_DATA[boss_type]['name']}",
                description=event_data["description"],
                color=0x00FF00
            )
            embed.set_footer(text="🔓 Todos pueden unirse")

            for role in WB_BOSS_DATA[boss_type]["roles"]:
                embed.add_field(
                    name=f"{WB_BOSS_DATA[boss_type]['emojis'].get(role)} {role} (0/{WB_BOSS_DATA[boss_type]['roles'][role]})",
                    value="🚫 Vacío",
                    inline=False
                )

            # Enviar mensaje
            message = await interaction.followup.send(embed=embed, view=WB_RoleSelectorView(boss_type, event_id, interaction.user.id))
            event_data["message"] = message

            # Crear hilo solo si es un TextChannel
            if isinstance(interaction.channel, discord.TextChannel):
                try:
                    thread = await message.create_thread(
                        name=f"WB {WB_BOSS_DATA[boss_type]['name']}",
                        auto_archive_duration=60,
                        reason=f"Hilo para WB creado por {interaction.user}"
                    )
                    event_data["thread_id"] = thread.id
                    await thread.send(f"💬 Hilo creado por {interaction.user.mention}")
                except Exception as e:
                    print(f"Error creando hilo: {e}")
                    await interaction.followup.send(
                        "⚠️ No pude crear el hilo de discusión",
                        ephemeral=True
                    )

        except Exception as e:
            print(f"Error en /wb: {e}")
            traceback.print_exc()
            
            if event_id in wb_events:
                del wb_events[event_id]
                
            await interaction.followup.send(
                "❌ Error al crear el evento",
                ephemeral=True
            )

    @tasks.loop(minutes=5)
    async def cleanup_wb_events(self):
        """Limpia eventos WB antiguos"""
        current_time = datetime.utcnow()
        to_remove = []

        for event_id, event in wb_events.items():
            if (current_time - event["creation_time"]) > timedelta(seconds=WB_EVENT_TIMEOUT):
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

    @cleanup_wb_events.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WorldBossCog(bot))
