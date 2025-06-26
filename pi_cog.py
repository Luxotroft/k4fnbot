import discord
from discord.ext import commands, tasks
import time
from datetime import timedelta
import re

class PiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, 'pi_countdown_data'):
            self.bot.pi_countdown_data = {}
        print("PiCog loaded and initialized.")
        
        # Diccionario de emojis para los objetivos de P.I.
        self.pi_emojis = {
            'verde': '🟢',
            'azul': '🔵',
            'morado': '🟣',
            'dorado': '🟡',
            'mineral': '⛏️',
            'madera': '🌳',
            'piel': '🐾',
            'fibra': '🌿',
            'vortex': '🌪️' # Icono para Vortex
        }

    @commands.hybrid_command(name="ayuda", description="Muestra información sobre todos los comandos del bot")
    async def ayuda(self, ctx: commands.Context):
        """Muestra una guía completa de todos los comandos disponibles"""
        embed = discord.Embed(
            title="📚 Ayuda Completa - Comandos del Bot",
            description="Aquí tienes una guía completa de todos los comandos disponibles:",
            color=discord.Color.blue()
        )
        
        # Sección de comandos de P.I.
        embed.add_field(
            name="⏰ Comandos de Ping de interés (P.I.)",
            value=(
                "**`/pi` o `!pi`** - Crea un temporizador para objetivos de P.I.\n"
                "```/pi <tipo> <minutos> <ubicación>```\n"
                "**Ejemplos:**\n"
                "• `/pi orbe dorado 15 Caerleon`\n"
                "• `/pi mineral 30 Martlock 7.4`\n"
                "• `/pi vortex azul 20 Bridgewatch`\n\n"
                "**Tipos disponibles:**\n"
                "• Orbes: `verde`, `azul`, `morado`, `dorado`\n"
                "• Recursos: `mineral`, `madera`, `piel`, `fibra`\n"
                "• Eventos: `vortex`"
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

    @commands.hybrid_command(name="pi", description="Crea una cuenta regresiva para un objetivo de P.I.")
    async def pi(self, ctx: commands.Context, tipo: str, tiempo: int, ubicacion: str):
        await ctx.defer()
        
        # --- PARSEO DE ARGUMENTOS ---
        # Ejemplo de tipo: "orbe dorado", "mineral 7.4", "vortex azul"
        parts = tipo.lower().split()
        
        main_type = parts[0]
        quality_level = ' '.join(parts[1:]) if len(parts) > 1 else ''
        
        # Obtener el emoji
        emoji = self.pi_emojis.get(main_type, '')
        if not emoji: # Si no encuentra el tipo, busca por la calidad/nivel
            emoji = self.pi_emojis.get(quality_level, '⭐')

        # --- VALIDACIÓN DEL TIEMPO ---
        if tiempo <= 0:
            return await ctx.followup.send("❌ El tiempo debe ser un número entero mayor a cero.", ephemeral=True)
            
        duration_seconds = tiempo * 60 # Tiempo en minutos a segundos
        
        # --- CREACIÓN DEL EMBED ---
        end_time = time.time() + duration_seconds
        
        # Formatear el título y la descripción según la estructura deseada
        title_text = f"{emoji} {main_type.title()} {quality_level.upper()}" if quality_level else f"{emoji} {main_type.title()}"
        
        # Crear la estructura de la descripción
        description_text = f"**Ubicación:** {ubicacion}\n**Aparece en:** **{tiempo} minutos**"

        embed = discord.Embed(
            title=title_text,
            description=description_text,
            color=discord.Color.from_rgb(255, 165, 0) # Naranja
        )
        embed.set_footer(text="El conteo se actualizará cada minuto...")
        
        # --- ENVÍO DEL MENSAJE Y GESTIÓN DE LA TAREA ---
        message = await ctx.send(embed=embed)
        
        countdown_id = str(message.id)
        self.bot.pi_countdown_data[countdown_id] = {
            'main_type': main_type,
            'quality_level': quality_level,
            'location': ubicacion,
            'end_time': end_time,
            'channel_id': ctx.channel.id,
            'message_id': message.id
        }
        
        print(f"DEBUG: Countdown started for ID {countdown_id}. Type: {main_type}, Quality: {quality_level}, Location: {ubicacion}")
        
        if not self.count_down.is_running():
            self.count_down.start()
            print("DEBUG: Countdown task started.")
        else:
            print("DEBUG: Countdown task is already running.")

    @tasks.loop(seconds=60)
    async def count_down(self):
        print(f"DEBUG: count_down loop running. Active tasks: {len(self.bot.pi_countdown_data)}")
        
        tasks_to_remove = []
        current_time = time.time()
        
        for countdown_id, data in self.bot.pi_countdown_data.items():
            remaining_seconds = data['end_time'] - current_time
            
            if remaining_seconds <= 0:
                # El conteo ha terminado
                try:
                    channel = self.bot.get_channel(data['channel_id'])
                    message = await channel.fetch_message(data['message_id'])
                    
                    final_embed = message.embeds[0]
                    final_embed.description = f"**Ubicación:** {data['location']}\n**Aparece en:** **¡Ya pasó el timer!**"
                    final_embed.color = discord.Color.green()
                    final_embed.set_footer(text="El conteo ha finalizado.")
                    await message.edit(embed=final_embed)
                    
                except Exception as e:
                    print(f"DEBUG: Error finalizing message for {countdown_id}: {e}")
                
                tasks_to_remove.append(countdown_id)
                continue
                
            try:
                channel = self.bot.get_channel(data['channel_id'])
                if not channel:
                    print(f"DEBUG: Channel {data['channel_id']} not found. Skipping update for {countdown_id}.")
                    continue

                message = await channel.fetch_message(data['message_id'])
                
                # Obtener el emoji para la actualización
                emoji = self.pi_emojis.get(data['main_type'], '')
                if not emoji:
                    emoji = self.pi_emojis.get(data['quality_level'], '⭐')
                
                remaining_delta = timedelta(seconds=int(remaining_seconds))
                remaining_minutes = int(remaining_seconds / 60)
                
                # --- ACTUALIZACIÓN DEL EMBED ---
                new_embed = discord.Embed(
                    title=f"{emoji} {data['main_type'].title()} {data['quality_level'].upper()}",
                    description=f"**Ubicación:** {data['location']}\n**Aparece en:** **{remaining_minutes} minutos**",
                    color=discord.Color.from_rgb(255, 165, 0)
                )
                new_embed.set_footer(text="El conteo se actualizará cada minuto...")
                
                await message.edit(embed=new_embed)
                print(f"DEBUG: Message edited for {countdown_id}.")

            except discord.NotFound:
                print(f"DEBUG: Message {data['message_id']} not found. Marking for removal.")
                tasks_to_remove.append(countdown_id)
            except Exception as e:
                print(f"DEBUG: Error in countdown loop for {countdown_id}: {e}")
                tasks_to_remove.append(countdown_id)
                
        for countdown_id in tasks_to_remove:
            print(f"DEBUG: Removing countdown task {countdown_id}.")
            del self.bot.pi_countdown_data[countdown_id]

        if not self.bot.pi_countdown_data:
            self.count_down.stop()
            print("DEBUG: Countdown task stopped as there are no active timers.")

    @count_down.before_loop
    async def before_count_down(self):
        print("DEBUG: Waiting for bot to be ready before starting countdown task.")
        await self.bot.wait_until_ready()
    
async def setup(bot):
    await bot.add_cog(PiCog(bot))
    print("PiCog setup complete.")
