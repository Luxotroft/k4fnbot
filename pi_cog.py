import discord
from discord.ext import commands, tasks
import time
import re
from datetime import datetime, timedelta

class PiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Asegúrate de que esta variable exista en el objeto del bot
        if not hasattr(self.bot, 'pi_countdown_data'):
            self.bot.pi_countdown_data = {}
        print("PiCog loaded and initialized.") # DEBUG

    @commands.hybrid_command(name="pi", description="Crea una cuenta regresiva para un boss de P.I.")
    async def pi(self, interaction: discord.Interaction, hours: int, minutes: int):
        await interaction.response.defer() # Deja la respuesta en espera
        
        duration_seconds = (hours * 3600) + (minutes * 60)
        
        if duration_seconds <= 0:
            return await interaction.followup.send("❌ El tiempo debe ser mayor a cero.", ephemeral=True)
            
        countdown_id = str(interaction.id)
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # Guardar los datos del conteo en una variable del bot para que el loop los pueda acceder
        self.bot.pi_countdown_data[countdown_id] = {
            'end_time': end_time,
            'channel_id': interaction.channel_id,
            'message_id': None # Se actualizará más adelante
        }

        # Crear el embed inicial
        embed = discord.Embed(
            title="⏰ Conteo Regresivo de Boss de P.I.",
            description=f"El boss aparecerá en: **{hours}h {minutes}m**",
            color=0xffa500 # Naranja
        )
        embed.set_footer(text="Actualizando cada minuto...")

        # Enviar el mensaje inicial y guardar su ID
        message = await interaction.followup.send(embed=embed)
        self.bot.pi_countdown_data[countdown_id]['message_id'] = message.id
        
        print(f"DEBUG: Countdown started for ID {countdown_id}. Message ID: {message.id}") # DEBUG
        
        # Iniciar la tarea en bucle si no está corriendo
        if not self.count_down.is_running():
            self.count_down.start()
            print("DEBUG: Countdown task started.") # DEBUG
        else:
            print("DEBUG: Countdown task is already running.") # DEBUG

    @tasks.loop(seconds=60) # Actualizar cada 60 segundos
    async def count_down(self):
        print(f"DEBUG: count_down loop running. Active tasks: {len(self.bot.pi_countdown_data)}") # DEBUG
        
        # Crear una lista de IDs de conteo para eliminar
        tasks_to_remove = []
        current_time = time.time()
        
        for countdown_id, data in self.bot.pi_countdown_data.items():
            remaining_seconds = data['end_time'] - current_time
            
            if remaining_seconds <= 0:
                tasks_to_remove.append(countdown_id)
                continue
                
            try:
                # Obtener el canal y el mensaje
                channel = self.bot.get_channel(data['channel_id'])
                if not channel:
                    print(f"DEBUG: Channel {data['channel_id']} not found. Skipping update for {countdown_id}.") # DEBUG
                    continue

                message = await channel.fetch_message(data['message_id'])
                print(f"DEBUG: Fetched message for {countdown_id}.") # DEBUG

                # Calcular el tiempo restante
                remaining_delta = timedelta(seconds=int(remaining_seconds))
                
                # Crear el nuevo embed con el tiempo actualizado
                new_embed = discord.Embed(
                    title="⏰ Conteo Regresivo de Boss de P.I.",
                    description=f"El boss aparecerá en: **{remaining_delta}**",
                    color=0xffa500 # Naranja
                )
                new_embed.set_footer(text="Actualizando cada minuto...")
                
                # Editar el mensaje
                await message.edit(embed=new_embed)
                print(f"DEBUG: Message edited for {countdown_id}.") # DEBUG

            except discord.NotFound:
                print(f"DEBUG: Message {data['message_id']} not found. Marking for removal.") # DEBUG
                tasks_to_remove.append(countdown_id)
            except Exception as e:
                print(f"DEBUG: Error in countdown loop for {countdown_id}: {e}") # DEBUG
                tasks_to_remove.append(countdown_id)
                
        # Limpiar los conteos que han terminado o fallado
        for countdown_id in tasks_to_remove:
            print(f"DEBUG: Removing countdown task {countdown_id}.") # DEBUG
            del self.bot.pi_countdown_data[countdown_id]

        # Si no hay más conteos, detener la tarea
        if not self.bot.pi_countdown_data:
            self.count_down.stop()
            print("DEBUG: Countdown task stopped as there are no active timers.") # DEBUG

    @count_down.before_loop
    async def before_count_down(self):
        print("DEBUG: Waiting for bot to be ready before starting countdown task.") # DEBUG
        await self.bot.wait_until_ready()
    
async def setup(bot):
    await bot.add_cog(PiCog(bot))
    print("PiCog setup complete.") # DEBUG
