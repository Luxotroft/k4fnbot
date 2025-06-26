import discord
from discord.ext import commands, tasks
import time

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
        print("✅ Módulo P.I. cargado (formato horizontal activo)")

    @commands.command(name='pi')
    async def pi_command(self, ctx, *, args: str):
        """Crea un temporizador P.I. con formato horizontal"""
        parts = args.split()
        tiempo = None
        tiempo_index = -1

        for i, part in enumerate(parts):
            if part.isdigit():
                tiempo = int(part)
                tiempo_index = i
                break

        if tiempo is None:
            return await ctx.send("**❌ El tiempo debe ser un número entero**\nEjemplo: `!pi mineral 7.4 30 Martlock`")
        if tiempo <= 0:
            return await ctx.send("**❌ El tiempo debe ser mayor a cero**")
        if tiempo > 1440:
            return await ctx.send("**❌ El tiempo máximo es 1440 minutos (24 horas)**")

        tipo = ' '.join(parts[:tiempo_index])
        ubicacion = ' '.join(parts[tiempo_index + 1:])

        if not tipo or not ubicacion:
            return await ctx.send("**❌ Formato incorrecto.** Usa: `!pi <tipo> <minutos> <ubicación>`")

        try:
            base_tipo = tipo.lower().split()[0]  # e.g., "mineral", "vortex"
            emoji = self.pi_emojis.get(tipo.lower(), self.pi_emojis.get(base_tipo, '⏱️'))

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
            await ctx.send("**❌ Error al crear el timer**\nVerifica el formato del comando.")

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
                base_tipo = timer['tipo'].lower().split()[0]
                emoji = self.pi_emojis.get(timer['tipo'].lower(), self.pi_emojis.get(base_tipo, '⏱️'))
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



