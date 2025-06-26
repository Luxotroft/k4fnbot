import discord
from discord.ext import commands, tasks
import time
import re
from datetime import datetime, timedelta

class PiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, 'pi_countdown_data'):
            self.bot.pi_countdown_data = {}
        print("PiCog loaded and initialized.")

    @commands.hybrid_command(name="pi", description="Crea una cuenta regresiva para un boss de P.I.")
    async def pi(self, ctx: commands.Context, hours: int, minutes: int):
        await ctx.defer()
        
        duration_seconds = (hours * 3600) + (minutes * 60)
        
        if duration_seconds <= 0:
            return await ctx.followup.send("❌ El tiempo debe ser mayor a cero.", ephemeral=True)
            
        countdown_id = str(ctx.interaction.id) if ctx.interaction else str(int(time.time()))
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        self.bot.pi_countdown_data[countdown_id] = {
            'end_time': end_time,
            'channel_id': ctx.channel.id,
            'message_id': None
        }

        embed = discord.Embed(
            title="⏰ Conteo Regresivo de Boss de P.I.",
            description=f"El boss aparecerá en: **{hours}h {minutes}m**",
            color=0xffa500
        )
        embed.set_footer(text="Actualizando cada minuto...")

        message = await ctx.send(embed=embed)
        self.bot.pi_countdown_data[countdown_id]['message_id'] = message.id
        
        print(f"DEBUG: Countdown started for ID {countdown_id}. Message ID: {message.id}")
        
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
                tasks_to_remove.append(countdown_id)
                continue
                
            try:
                channel = self.bot.get_channel(data['channel_id'])
                if not channel:
                    print(f"DEBUG: Channel {data['channel_id']} not found. Skipping update for {countdown_id}.")
                    continue

                message = await channel.fetch_message(data['message_id'])
                print(f"DEBUG: Fetched message for {countdown_id}.")

                remaining_delta = timedelta(seconds=int(remaining_seconds))
                
                new_embed = discord.Embed(
                    title="⏰ Conteo Regresivo de Boss de P.I.",
                    description=f"El boss aparecerá en: **{remaining_delta}**",
                    color=0xffa500
                )
                new_embed.set_footer(text="Actualizando cada minuto...")
                
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
