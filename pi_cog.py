import discord
from discord.ext import commands, tasks
import time
import re

class PiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Inicializa pi_countdown_data si no existe en el bot
        if not hasattr(self.bot, 'pi_countdown_data'):
            self.bot.pi_countdown_data = {}
        print("✅ Módulo P.I. cargado (solo prefijo !pi)")

        # Diccionario de emojis para los objetivos de P.I.
        self.pi_emojis = {
            'verde': '🟢', 'azul': '🔵', 'morado': '🟣', 'dorado': '🟡',
            'mineral': '⛏️', 'madera': '🌳', 'piel': '🐾', 'fibra': '🌿',
            'vortex': '🌪️', 'vortex azul': '🌪️🔵', 'vortex verde': '🌪️🟢',
            'vortex morado': '🌪️🟣', 'vortex dorado': '🌪️🟡',
            'orbe verde': '🟢', 'orbe azul': '🔵', 'orbe morado': '🟣', 'orbe dorado': '🟡'
        }
        
        # Inicia el bucle de actualización si ya hay temporizadores guardados
        if self.bot.pi_countdown_data and not self.update_timers.is_running():
            self.update_timers.start()

    @commands.command(name='ayuda')
    async def ayuda(self, ctx: commands.Context):
        """Muestra una guía completa de todos los comandos disponibles"""
        embed = discord.Embed(
            title="📚 Ayuda Completa - Comandos del Bot",
            description="Aquí tienes una guía completa de todos los comandos disponibles:",
            color=discord.Color.blue()
        )
        
        # Sección de comandos de P.I. (corregida para !pi)
        embed.add_field(
            name="⏰ Comandos de Puntos de Interés (P.I.)",
            value=(
                "**`!pi`** - Crea un temporizador para objetivos de P.I.\n"
                "```!pi <tipo> <minutos> <ubicación>```\n"
                "**Ejemplos:**\n"
                "• `!pi orbe dorado 15 Caerleon`\n"
                "• `!pi mineral 30 Martlock 7.4`\n"
                "• `!pi vortex azul 20 Bridgewatch`\n"
                "• `!pi madera 45 Fort Sterling`\n\n"
                "**Tipos disponibles:**\n"
                "• Orbes: `verde`, `azul`, `morado`, `dorado`, `orbe verde`, etc.\n"
                "• Recursos: `mineral`, `madera`, `piel`, `fibra`\n"
                "• Eventos: `vortex`, `vortex azul`, `vortex verde`, etc."
            ),
            inline=False
        )
        
        # Sección de World Boss
        embed.add_field(
            name="🌍 Comandos de World Boss (`/wb`)",
            value=(
                "**`/wb`** - Crea un evento de World Boss con sistema de prioridad\n"
                "```/wb <caller> <boss> <duración> [prios] [tiempo_prios] [miembros_prio]```\n"
                "**Ejemplos:**\n"
                "• `/wb Pancho elder \"2 horas\"`\n"
                "• `/wb Maria eye \"90 minutos\" 5 30 @Jugador1 @Jugador2`\n\n"
                "**Parámetros opcionales:**\n"
                "• `prios`: Número de slots prioritarios (1-20)\n"
                "• `tiempo_prios`: Duración de prioridad en minutos (1-60)\n"
                "• `miembros_prio`: Menciona a los usuarios con prioridad"
            ),
            inline=False
        )
        
        # Sección de Roaming
        embed.add_field(
            name="🚀 Comandos de Roaming (`!roaming` o `!r`)",
            value=(
                "**`!roaming` o `!r`** - Crea un evento de roaming party\n"
                "```!roaming <tipo> <tier> <ip> [hora] [swap] [caller]```\n"
                "**Ejemplos:**\n"
                "• `!roaming kiteo1 T8 1400`\n"
                "• `!r kiteo2 T8 1450 3.30 si Pancho`\n"
                "• `!roaming brawl T8 1500 no Maria`\n\n"
                "**Parámetros opcionales:**\n"
                "• `hora`: Hora de salida (ej: 3.30)\n"
                "• `swap`: 'si' o 'no' para swap de gank\n"
                "• `caller`: Nombre del caller (si no se especifica, usa tu nombre)"
            ),
            inline=False
        )
        
        # Sección de cierre de eventos
        embed.add_field(
            name="🚫 Comando para cerrar eventos (`/close`)",
            value=(
                "**`/close`** - Cierra un evento que hayas creado\n"
                "```/close [event_id]```\n"
                "**Ejemplos:**\n"
                "• `/close` (cierra el evento más reciente que creaste)\n"
                "• `/close WB-123456789` (cierra un evento específico por ID)\n\n"
                "**Nota:** El ID del evento aparece en el pie del mensaje del evento"
            ),
            inline=False
        )
        
        embed.set_footer(text="Para más ayuda, contacta a los administradores.")
        await ctx.send(embed=embed)

    @commands.command(name='pi')
    async def pi_command(self, ctx: commands.Context, *, args: str):
        """
        Crea un temporizador de P.I. y puede manejar nombres de ciudades con espacios.
        Ej: !pi vortex azul 20 Fort Sterling
        """
        # Expresión regular para encontrar el tipo, el tiempo y la ubicación.
        # Captura cualquier cosa al inicio (tipo), un número (minutos) y cualquier cosa al final (ubicación).
        match = re.search(r'(.+)\s+(\d+)\s+(.+)', args)
        
        if not match:
            # Si el patrón principal no coincide, intenta un patrón más simple (sin ubicación).
            match = re.search(r'(.+)\s+(\d+)', args)
            if not match:
                await ctx.send("**❌ Formato incorrecto.** Usa: `!pi <tipo> <minutos> <ubicación>`\nEjemplo: `!pi vortex azul 20 Fort Sterling`")
                return
            
            tipo = match.group(1).strip().lower()
            tiempo = int(match.group(2))
            ubicacion = "Ubicación desconocida" # Valor por defecto
        
        else:
            # Si el patrón completo coincide, extrae los tres grupos.
            tipo = match.group(1).strip().lower()
            tiempo = int(match.group(2))
            ubicacion = match.group(3).strip()
            
        try:
            if tiempo <= 0:
                await ctx.send("**❌ El tiempo debe ser mayor a 0 minutos.**")
                return

            await self.create_pi_timer(ctx, tipo, tiempo, ubicacion)

        except ValueError:
            await ctx.send("**❌ El tiempo debe ser un número entero.** (Ej: `!pi vortex azul 20 Bridgewatch`)")
        except Exception as e:
            print(f"Error en el comando !pi: {e}")
            await ctx.send("**❌ Ocurrió un error al procesar el comando.**")

    async def create_pi_timer(self, ctx, tipo: str, tiempo: int, ubicacion: str):
        """Función compartida para crear timers"""
        
        emoji = self.pi_emojis.get(tipo, '⏱️')
        
        end_time = time.time() + (tiempo * 60)
        
        embed = discord.Embed(
            title=f"{emoji} {tipo.title()}",
            description=f"**📍 Ubicación:** {ubicacion}\n**⏳ Aparece en:** **{tiempo} minutos**",
            color=0xFFA500
        )
        embed.set_footer(text="Timer activo - se actualiza cada minuto")
        
        message = await ctx.send(embed=embed)
        
        countdown_id = str(message.id)
        self.bot.pi_countdown_data[countdown_id] = {
            'tipo': tipo,
            'ubicacion': ubicacion,
            'end_time': end_time,
            'channel_id': ctx.channel.id,
            'message_id': message.id
        }
        
        # Asegúrate de que el bucle de tareas se esté ejecutando.
        if not self.update_timers.is_running():
            self.update_timers.start()

    @tasks.loop(seconds=60)
    async def update_timers(self):
        print(f"DEBUG: Bucle de actualización en ejecución. Tareas activas: {len(self.bot.pi_countdown_data)}")
        
        tasks_to_remove = []
        current_time = time.time()
        
        for msg_id, data in self.bot.pi_countdown_data.items():
            remaining_seconds = data['end_time'] - current_time
            
            if remaining_seconds <= 0:
                # El temporizador ha terminado.
                try:
                    channel = self.bot.get_channel(data['channel_id'])
                    if channel:
                        message = await channel.fetch_message(data['message_id'])
                        
                        final_embed = message.embeds[0]
                        final_embed.description = f"**📍 Ubicación:** {data['ubicacion']}\n**⏰ Estado:** **¡Ya apareció!**"
                        final_embed.color = discord.Color.green()
                        final_embed.set_footer(text="El conteo ha finalizado.")
                        await message.edit(embed=final_embed)
                except (discord.NotFound, discord.Forbidden):
                    print(f"DEBUG: Mensaje o canal {msg_id} no encontrado. Marcando para eliminar.")
                except Exception as e:
                    print(f"DEBUG: Error al finalizar el temporizador {msg_id}: {e}")
                
                tasks_to_remove.append(msg_id)
                continue
            
            try:
                channel = self.bot.get_channel(data['channel_id'])
                if not channel:
                    print(f"DEBUG: Canal {data['channel_id']} no encontrado. Saltando actualización para {msg_id}.")
                    continue
                
                message = await channel.fetch_message(data['message_id'])
                
                emoji = self.pi_emojis.get(data['tipo'], '⏱️')
                
                remaining_minutes = int(remaining_seconds / 60)
                
                # Actualizar el embed con el tiempo restante.
                new_embed = discord.Embed(
                    title=f"{emoji} {data['tipo'].title()}",
                    description=f"**📍 Ubicación:** {data['ubicacion']}\n**⏳ Aparece en:** **{remaining_minutes} minutos**",
                    color=0xFFA500
                )
                new_embed.set_footer(text="Timer activo - se actualiza cada minuto")
                
                await message.edit(embed=new_embed)
                
            except (discord.NotFound, discord.Forbidden):
                print(f"DEBUG: Mensaje o canal {data['message_id']} no encontrado. Marcando para eliminar.")
                tasks_to_remove.append(msg_id)
            except Exception as e:
                print(f"DEBUG: Error en el bucle de actualización para {msg_id}: {e}")
                tasks_to_remove.append(msg_id)
                
        for msg_id in tasks_to_remove:
            print(f"DEBUG: Eliminando tarea de temporizador {msg_id}.")
            self.bot.pi_countdown_data.pop(msg_id, None)

        if not self.bot.pi_countdown_data and self.update_timers.is_running():
            self.update_timers.stop()
            print("DEBUG: Tarea de cuenta regresiva detenida ya que no hay temporizadores activos.")

    @update_timers.before_loop
    async def before_update_timers(self):
        print("DEBUG: Esperando a que el bot esté listo antes de iniciar la tarea de actualización.")
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(PiCog(bot))
    print("Setup de PiCog completado.")
