import discord
from discord.ext import commands, tasks
import time
import re
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
            'orbe verde': '🟢',
            'orbe azul': '🔵',
            'orbe morado': '🟣',
            'orbe dorado': '🟡'
        }
        print("✅ Módulo P.I. cargado (comandos !pi y !ayuda)")

    def parse_time(self, time_str):
        """Parsea tiempo en formato como '1h30', '30m', '2h', '90' (minutos)"""
        time_str = time_str.lower().strip()
        
        # Patrón para capturar horas y minutos
        pattern = r'(?:(\d+)h)?(?:(\d+)m?)?$'
        match = re.match(pattern, time_str)
        
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            
            # Si no hay 'h' o 'm', asumimos que son minutos
            if not re.search(r'[hm]', time_str):
                minutes = int(time_str) if time_str.isdigit() else 0
                hours = 0
            
            total_minutes = hours * 60 + minutes
            return total_minutes if total_minutes > 0 else None
        
        # Si no coincide con el patrón, intentar como número simple (minutos)
        if time_str.isdigit():
            return int(time_str)
        
        return None

    def format_time_remaining(self, minutes):
        """Formatea el tiempo restante en horas y minutos o solo minutos"""
        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours}h"
            else:
                return f"{hours}h{mins:02d}"
        else:
            return f"{minutes}m"

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
                "```!pi <tipo> <tiempo> <ubicación>```\n"
                "**Ejemplos:**\n"
                "• `!pi vortex azul 20 Fort Sterling` (20 minutos)\n"
                "• `!pi mineral 7.4 1h30 Fort Sterling` (tier 7.4, 1h30)\n"
                "• `!pi vortex azul 2h \"Thetford Portal\"` (2 horas)\n\n"
                "**Formatos de tiempo:**\n"
                "• `30` o `30m` = 30 minutos\n"
                "• `1h` = 1 hora\n"
                "• `1h30` = 1 hora 30 minutos\n\n"
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
        """Crea un temporizador P.I. (ej: !pi vortex azul 1h30 Fort Sterling)"""
        parts = args.split()
        tiempo_minutos = None
        tiempo_index = -1

        # Buscar el tiempo en los argumentos - priorizar formatos con h/m
        for i, part in enumerate(parts):
            # Primero buscar formatos con 'h' o 'm'
            if 'h' in part.lower() or 'm' in part.lower():
                tiempo_parsed = self.parse_time(part)
                if tiempo_parsed is not None:
                    tiempo_minutos = tiempo_parsed
                    tiempo_index = i
                    break
        
        # Si no encontró formato h/m, buscar números simples
        if tiempo_minutos is None:
            for i, part in enumerate(parts):
                if part.isdigit():
                    tiempo_minutos = int(part)
                    tiempo_index = i
                    break

        if tiempo_minutos is None:
            return await ctx.send("**❌ Formato de tiempo inválido**\nEjemplos: `30`, `1h`, `1h30`, `2h15`\nUso: `!pi <tipo> <tiempo> <ubicación>`")
        
        if tiempo_minutos <= 0:
            return await ctx.send("**❌ El tiempo debe ser mayor a cero**")
        
        if tiempo_minutos > 1440:  # 24 horas
            return await ctx.send("**❌ El tiempo máximo es 24 horas**")

        tipo_completo = ' '.join(parts[:tiempo_index])
        ubicacion = ' '.join(parts[tiempo_index + 1:])

        if not tipo_completo or not ubicacion:
            return await ctx.send("**❌ Formato incorrecto.** Usa: `!pi <tipo> [tier] <tiempo> <ubicación>`\nEjemplo: `!pi mineral 7.4 1h30 Fort Sterling`")

        try:
            # Extraer el tipo base para el emoji (primera palabra)
            tipo_base = parts[0].lower()
            emoji = self.pi_emojis.get(tipo_base, '⏱️')
            
            tipo_formateado = tipo_completo.upper()
            tiempo_formateado = self.format_time_remaining(tiempo_minutos)
            
            mensaje = f"{emoji} **{tipo_formateado}** en **{ubicacion}** — ⏳ *{tiempo_formateado} restantes*"

            msg = await ctx.send(mensaje)

            self.pi_countdown_data[msg.id] = {
                'end_time': time.time() + (tiempo_minutos * 60),
                'channel_id': ctx.channel.id,
                'message_id': msg.id,
                'ubicacion': ubicacion,
                'tipo_completo': tipo_completo,
                'tipo_base': tipo_base
            }

            if not self.update_timers.is_running():
                self.update_timers.start()

        except Exception as e:
            print(f"[ERROR] !pi: {str(e)}")
            await ctx.send("**❌ Error al crear el timer**\nUsa: `!pi <tipo> <tiempo> <ubicación>`")

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

                try:
                    msg = await channel.fetch_message(timer['message_id'])
                except discord.NotFound:
                    expired.append(msg_id)
                    continue
                
                remaining_seconds = max(0, timer['end_time'] - current_time)
                remaining_minutes = int(remaining_seconds / 60)
                
                emoji = self.pi_emojis.get(timer['tipo_base'], '⏱️')
                tipo_formateado = timer['tipo_completo'].upper()

                if remaining_minutes <= 0:
                    mensaje = f"{emoji} **{tipo_formateado}** en **{timer['ubicacion']}** — ✅ *¡Ya pasó el timer!*"
                    expired.append(msg_id)
                else:
                    tiempo_formateado = self.format_time_remaining(remaining_minutes)
                    mensaje = f"{emoji} **{tipo_formateado}** en **{timer['ubicacion']}** — ⏳ *{tiempo_formateado} restantes*"

                await msg.edit(content=mensaje)

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
    
    @commands.command(name='borra')
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int):
        """Elimina un número especificado de mensajes."""
        # Asegúrate de que el bot tenga el permiso 'Administrar mensajes' en el servidor.
        if amount <= 0:
            return await ctx.send("El número de mensajes a eliminar debe ser mayor que 0.", delete_after=5)
        
        # +1 para eliminar también el mensaje de invocación del comando
        # Se elimina el mensaje de la persona que lo pidió y los que le siguen.
        await ctx.channel.purge(limit=amount + 1)
        
        # Envía un mensaje de confirmación que se eliminará automáticamente después de 5 segundos
        await ctx.send(f"✅ Se han eliminado {amount} mensajes.", delete_after=5)

async def setup(bot):
    await bot.add_cog(PiCog(bot))
