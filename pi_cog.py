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
            'vortex': '🌪️', 'vortex azul': '🌪️🔵', 'vortex verde': '🌪️🟢'
        }
        print("✅ Módulo P.I. cargado (solo prefijo !pi)")

    @commands.command(name='pi')
    async def pi_command(self, ctx, *, args: str):
        """Crea temporizadores P.I. con !pi (ej: !pi vortex azul 20 Bridgewatch)"""
        try:
            # Parseo inteligente de argumentos
            parts = args.rsplit(' ', 2) # Divide desde la derecha, máximo 2 veces

            if len(parts) < 3:
                # Intenta con menos partes para tipos de un solo nombre
                parts = args.rsplit(' ', 1)
                if len(parts) < 2:
                    await ctx.send("**❌ Formato incorrecto.** Usa: `!pi <tipo> <minutos> <ubicación>`\nEjemplo: `!pi vortex azul 20 Fort Sterling`")
                    return
                tipo = parts[0]
                tiempo_str = parts[1]
                ubicacion = "desconocida" # Valor por defecto si no se da ubicación
            else:
                tipo = parts[0]
                tiempo_str = parts[1]
                ubicacion = parts[2]
            
            # Quitar espacios extra alrededor
            tipo = tipo.strip()
            ubicacion = ubicacion.strip()
            
            tiempo = int(tiempo_str)
            
            # Validación básica
            if tiempo <= 0:
                await ctx.send("**❌ El tiempo debe ser mayor a 0 minutos**")
                return

            # Crear el embed
            emoji = self.pi_emojis.get(tipo.lower(), '⏱️')
            embed = discord.Embed(
                title=f"{emoji} {tipo.title()}",
                description=f"**📍 Ubicación:** {ubicacion}\n**⏳ Aparece en:** **{tiempo} minutos**",
                color=0xFFA500  # Naranja
            )
            embed.set_footer(text="Timer activo - se actualiza cada minuto")
            
            msg = await ctx.send(embed=embed)
            
            # Guardar en memoria
            self.pi_countdown_data[msg.id] = {
                'end_time': time.time() + (tiempo * 60),
                'channel_id': ctx.channel.id,
                'ubicacion': ubicacion,
                'tipo': tipo
            }

            if not self.update_timers.is_running():
                self.update_timers.start()

        except ValueError:
            await ctx.send("**❌ El tiempo debe ser un número entero** (ej: `!pi vortex azul 20 Fort Sterling`)")
        except Exception as e:
            print(f"Error en !pi: {e}")
            await ctx.send("**❌ Error al crear el timer**")

    @tasks.loop(seconds=60)
    async def update_timers(self):
        now = time.time()
        to_remove = []
        
        for msg_id, data in self.pi_countdown_data.items():
            try:
                channel = self.bot.get_channel(data['channel_id'])
                if channel is None:
                    to_remove.append(msg_id)
                    continue

                msg = await channel.fetch_message(msg_id)
                remaining = int((data['end_time'] - now) / 60)
                
                if remaining <= 0:
                    embed = msg.embeds[0]
                    embed.description = f"**📍 Ubicación:** {data['ubicacion']}\n**⏰ Estado:** **¡Ya apareció!**"
                    embed.color = 0x00FF00  # Verde
                    await msg.edit(embed=embed)
                    to_remove.append(msg_id)
                else:
                    embed = msg.embeds[0]
                    embed.description = f"**📍 Ubicación:** {data['ubicacion']}\n**⏳ Aparece en:** **{remaining} minutos**"
                    await msg.edit(embed=embed)
                    
            except (discord.NotFound, discord.Forbidden):
                # El mensaje o el canal ya no existen
                to_remove.append(msg_id)
            except Exception as e:
                print(f"Error actualizando timer (mensaje {msg_id}): {e}")
                to_remove.append(msg_id)
        
        for msg_id in to_remove:
            self.pi_countdown_data.pop(msg_id, None)
        
        if not self.pi_countdown_data:
            self.update_timers.stop()

    @update_timers.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PiCog(bot))
