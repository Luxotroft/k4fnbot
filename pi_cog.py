import discord
from discord.ext import commands, tasks
import time
import re
from datetime import datetime, timedelta

# ====================================================================
# --- COG PARA EL COMANDO !PI ---
# ====================================================================

# --- 1. VARIABLES GLOBALES Y HELPERS ---
PI_NODES_DATA = {
    "mineral": {"name": "Mineral", "emoji": "💎"},
    "madera": {"name": "Madera", "emoji": "🌳"},
    "fibra": {"name": "Fibra", "emoji": "🌿"},
    "piel": {"name": "Piel", "emoji": "🐾"},
    "vortex verde": {"name": "Vortex Verde", "emoji": "🟢"},
    "vortex morado": {"name": "Vortex Morado", "emoji": "🟣"},
    "vortex azul": {"name": "Vortex Azul", "emoji": "🔵"},
    "vortex dorado": {"name": "Vortex Dorado", "emoji": "🟡"},
    "orbe verde": {"name": "Orbe Verde", "emoji": "🟢"},
    "orbe morado": {"name": "Orbe Morado", "emoji": "🟣"},
    "orbe azul": {"name": "Orbe Azul", "emoji": "🔵"},
    "orbe dorado": {"name": "Orbe Dorado", "emoji": "🟡"},
}

pi_events = {} # {event_id: {data}}

def parse_time_string(time_str: str):
    """
    Parsea una cadena de tiempo 'H.MM' a segundos.
    Ej: '7.45' -> 7 horas y 45 minutos.
    """
    try:
        if '.' in time_str:
            parts = time_str.split('.')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                hours = int(parts[0])
                minutes = int(parts[1])
                return (hours * 3600) + (minutes * 60)
        # Si no tiene el formato H.MM, se asume que es solo una cantidad de minutos
        if time_str.isdigit():
            return int(time_str) * 60
    except (ValueError, IndexError):
        return None
    return None

def create_pi_embed(event_data):
    """Genera el mensaje embed para el evento de nodo/vortex/orbe."""
    remaining_seconds = max(0, event_data['end_time'] - time.time())
    
    hours = int(remaining_seconds // 3600)
    minutes = int((remaining_seconds % 3600) // 60)
    seconds = int(remaining_seconds % 60)
    
    time_str = ""
    if hours > 0:
        time_str += f"{hours}h "
    if minutes > 0:
        time_str += f"{minutes}m "
    time_str += f"{seconds}s"
    
    node_info = PI_NODES_DATA.get(event_data['type'], {"name": "Desconocido", "emoji": "❓"})
    emoji = node_info["emoji"]
    
    title_parts = [f"{emoji} **{node_info['name']}**"]
    if event_data.get('tier'):
        title_parts.append(f"**{event_data['tier']}**")
    title_str = ' '.join(title_parts)

    embed = discord.Embed(
        title=f"{title_str} en **{event_data['map_name']}**",
        description=f"⏳ **Tiempo restante:** `{time_str}`",
        color=0x2ecc71
    )
    
    if remaining_seconds <= 900:
        embed.color = 0xe74c3c
    elif remaining_seconds <= 1800:
        embed.color = 0xf1c40f
        
    embed.set_footer(text=f"ID del evento: {event_data['event_id']}")
    
    return embed

# --- 2. CLASE DEL COG Y COMANDOS ---
class PiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pi_events = pi_events

    @commands.Cog.listener()
    async def on_ready(self):
        """Se ejecuta cuando el bot está listo y este cog se ha cargado."""
        print("Cargando PiCog...")
        if not self.update_pi_timers.is_running():
            self.update_pi_timers.start()
            print("Tarea 'update_pi_timers' iniciada.")

    @commands.command(name='pi', help='<nombre_nodo> <mapa> <h.mm>')
    async def pi_command(self, ctx, node_type: str, map_name: str, time_str: str, tier: str = None):
        await ctx.message.delete()
        
        node_type_lower = node_type.lower()
        if node_type_lower not in PI_NODES_DATA:
            valid_nodes = ", ".join([f"`{n}`" for n in PI_NODES_DATA.keys()])
            return await ctx.send(f"❌ Tipo de nodo inválido. Nodos válidos: {valid_nodes}", delete_after=10)

        parsed_seconds = parse_time_string(time_str)
        if parsed_seconds is None or parsed_seconds <= 0:
            return await ctx.send("❌ Tiempo inválido. Usa el formato 'H.MM' (ej. 1.30 para 1h 30m) o solo minutos (ej. 90 para 90m).", delete_after=10)

        event_id = f"pi-{int(time.time())}"
        end_time = time.time() + parsed_seconds
        
        event_data = {
            'event_id': event_id,
            'type': node_type_lower,
            'map_name': map_name,
            'start_time': time.time(),
            'end_time': end_time,
            'channel_id': ctx.channel.id,
            'message_id': None,
            'tier': tier
        }
        
        embed = create_pi_embed(event_data)
        message = await ctx.send(embed=embed)
        
        event_data['message_id'] = message.id
        self.pi_events[event_id] = event_data
        
        print(f"PI event created: {event_id} in {map_name} for {parsed_seconds} seconds.")

    # --- 3. TAREA EN BUCLE PARA ACTUALIZAR TEMPORIZADORES ---
    @tasks.loop(seconds=5)
    async def update_pi_timers(self):
        """
        Esta tarea en bucle actualiza cada 5 segundos los mensajes de los eventos de PI
        y elimina los que han expirado, enviando una alerta de finalización.
        """
        print("Tarea en bucle update_pi_timers se está ejecutando...") # <-- Nuevo print para verificar
        events_to_remove = []
        for event_id, event_data in list(self.pi_events.items()):
            remaining_seconds = event_data['end_time'] - time.time()
            
            # Nuevo print para ver el tiempo restante calculado
            print(f"  > Evento {event_id}: Tiempo restante = {remaining_seconds:.2f}s") 
            
            # Obtener el objeto Message
            try:
                channel = self.bot.get_channel(event_data['channel_id'])
                if not channel:
                    print(f"  > Canal para el evento {event_id} no encontrado. Eliminando evento.")
                    events_to_remove.append(event_id)
                    continue
                
                message = await channel.fetch_message(event_data['message_id'])
                
                # Actualizar el embed con el tiempo restante
                embed = create_pi_embed(event_data)
                await message.edit(embed=embed)
                
                # Comprobar si el temporizador ha llegado a 0
                if remaining_seconds <= 0:
                    events_to_remove.append(event_id)
                    
                    # Enviar alerta de finalización
                    node_info = PI_NODES_DATA.get(event_data['type'], {"name": "Desconocido"})
                    await channel.send(f"🚨 **¡ATENCIÓN!** El **{node_info['name']}** en **{event_data['map_name']}** ha expirado.", delete_after=300)
                    
                    # Borrar el mensaje del temporizador (opcional)
                    await message.delete()

            except (discord.NotFound, discord.Forbidden):
                print(f"  > Mensaje para el evento {event_id} no encontrado o inaccesible. Eliminando evento.")
                events_to_remove.append(event_id)
                continue
            except Exception as e:
                # Captura cualquier otro error inesperado y lo imprime
                print(f"  > ¡Error inesperado en el evento {event_id}! Detalle: {e}")
                events_to_remove.append(event_id) # Opcional: Quitar el evento con error

        # Eliminar eventos expirados del diccionario
        for event_id in events_to_remove:
            if event_id in self.pi_events:
                del self.pi_events[event_id]

    @update_pi_timers.before_loop
    async def before_update_pi_timers(self):
        await self.bot.wait_until_ready()

# --- 4. FUNCIÓN DE SETUP (REQUERIDA) ---
async def setup(bot):
    """Función de setup requerida para cargar el cog."""
    await bot.add_cog(PiCog(bot))
