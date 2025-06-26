import discord
from discord.ext import commands, tasks
import time
from datetime import timedelta

class PiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pi_countdown_data = {}
        self.pi_emojis = {
            'verde': '🟢', 'azul': '🔵', 'morado': '🟣', 'dorado': '🟡',
            'mineral': '⛏️', 'madera': '🌳', 'piel': '🐾', 'fibra': '🌿',
            'vortex': '🌪️', 'vortex azul': '🌪️🔵', 'vortex verde': '🌪️🟢',
            'vortex dorado': '🌪️🟡', 'vortex morado': '🌪️🟣'
        }
        print("✅ Módulo P.I. cargado (comandos !pi y !ayuda)")

    @commands.command(name='ayuda')
    async def ayuda(self, ctx):
        embed = discord.Embed(
            title="📚 **AYUDA COMPLETA**",
            description="Comandos disponibles para World Boss, Roaming y P.I.:",
            color=0x00FF00
        )
        embed.add_field(
            name="⏰ **COMANDOS P.I. (!pi)**",
            value=(
                "```!pi <tipo> <minutos> <ubicación>```\n"
                "**Ejemplos:**\n"
                "• `!pi vortex azul 20 Fort Sterling`\n"
                "• `!pi mineral 30 \"Thetford Portal\"`\n\n"
                "**Tipos válidos:**\n"
                "• Orbes: `verde`, `azul`, `morado`, `dorado`\n"
                "• Recursos: `mineral`, `madera`, `piel`, `fibra`\n"
                "• Vortex: `vortex [color]`"
            ),
            inline=False
        )
        embed.add_field(
            name="🌍 **WORLD BOSS (/wb)**",
            value=(
                "```/wb <caller> <boss> <duración> [prios] [tiempo_prios] [@miembros]```\n"
                "**Ejemplos:**\n"
                "• `/wb Pancho elder \"90 minutos\"`\n"
                "• `/wb Maria eye \"2 horas\" 5 30 @User1 @User2`\n\n"
                "**Bosses disponibles:** `elder`, `eye`"
            ),
            inline=False
        )
        embed.add_field(
            name="🚀 **ROAMING (!roaming o !r)**",
            value=(
                "```!roaming <tipo> <tier> <ip> [hora] [swap] [caller]```\n"
                "**Ejemplos:**\n"
                "• `!roaming kiteo1 T8 1400`\n"
                "• `!r kiteo2 T8 1450 3.30 si Pancho`\n\n"
                "**Tipos:** `kiteo1`, `kiteo2`, `brawl`, `brawl2`"
            ),
            inline=False
        )
        embed.add_field(
            name="🚫 **CERRAR EVENTOS (/close)**",
            value=(
                "```/close [event_id]```\n"
                "**Ejemplos:**\n"
                "• `/close` (cierra tu último evento)\n"
                "• `/close WB-123456789` (cierra por ID)\n\n"
                "**Nota:** El ID aparece en el pie del mensaje del evento"
            ),
            inline=False
        )
        embed.set_footer(text="📍 Usa comillas para nombres con espacios (ej: \"Fort Sterling\")")
        await ctx.send(embed=embed)

    @commands.command(name='pi')
    async def pi_command(self, ctx, *, args: str):
        """Crea un temporizador P.I. (ej: !pi vortex azul 20 Fort Sterling)"""
        parts = args.split()
        tiempo = None
        tiempo_index = -1

        for i, part in enumerate(parts):
            if part.isdigit():
                tiempo = int(part)
                tiempo_index = i
                break

        if tiempo is None:
            return await ctx.send("**❌ El tiempo debe ser un número entero**\nEjemplo: `!pi mineral 30 Martlock`")
        if tiempo <= 0:
            return await ctx.send("**❌ El tiempo debe ser mayor a cero**")
        if tiempo > 1440:
            return await ctx.send("**❌ El tiempo máximo es 1440 minutos (24 horas)**")

        tipo = ' '.join(parts[:tiempo_index])
        ubicacion = ' '.join(parts[tiempo_index + 1:])

        if not tipo or not ubicacion:
            return await ctx.send("**❌ Formato incorrecto.** Usa: `!pi <tipo> <minutos> <ubicación>`\nEjemplo: `!pi vortex azul 20 Fort Sterling`")

        try:
            emoji = self.pi_emojis.get(tipo.lower(), '⏱️')
            tipo_formateado = tipo.upper()
            mensaje = f"{emoji} **{tipo_formateado}** en **{ubicacion}** — ⏳ *{tiempo}m restantes*"

            msg = await ctx.send(mensaje)

            self.pi_countdown_data[msg.id] = {
                'end_time': time.time() + (tiempo * 60),
                'channel_id': ctx.channel.id,
                'message_id': msg.id,
                'ubicacion': ubicacion,
                'tipo': tipo
            }

            if not self.update_timers.is_running():
                self.update_timers.start()

        except Exception as e:
            print(f"[ERROR] !pi: {str(e)}")
            await ctx.send("**❌ Error al crear el timer**\nUsa: `!pi <tipo> <minutos> <ubicación>`")

    @tasks.loop(seconds=60.0)
    async def update_timers(self):
        current_time = time.time()
        expired = []

        for msg_id, timer in list(self.pi_countdown_data.items()):
            try:
                channel = self.bot.get_channel(timer['channel_id'])
                if not channel:
                    expired.append(msg_id)
                    continue

                msg = await channel.fetch_message(timer['message_id'])
                remaining = max(0, int((timer['end_time'] - current_time) / 60))
                emoji = self.pi_emojis.get(timer['tipo'].lower(), '⏱️')
                tipo_formateado = timer['tipo'].upper()

                if remaining <= 0:
                    mensaje = f"{emoji} **{tipo_formateado}** en **{timer['ubicacion']}** — ✅ *¡Ya pasó el timer!*"
                    await msg.edit(content=mensaje)
                    expired.append(msg_id)
                else:
                    mensaje = f"{emoji} **{tipo_formateado}** en **{timer['ubicacion']}** — ⏳ *{remaining}m restantes*"
                    await msg.edit(content=mensaje)

            except discord.NotFound:
                expired.append(msg_id)
            except Exception as e:
                print(f"[ERROR] Actualizando timer {msg_id}: {str(e)}")
                expired.append(msg_id)

        for msg_id in expired:
            self.pi_countdown_data.pop(msg_id, None)

        if not self.pi_countdown_data:
            self.update_timers.stop()

    @update_timers.before_loop
    async def before_updater(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PiCog(bot))


