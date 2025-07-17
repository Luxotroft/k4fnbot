import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive # Asumiendo que ya tiene este archivo

load_dotenv()

# ====================================================================
# --- 1. CONFIGURACIÓN E INSTANCIA DEL BOT ALBION ---
# ====================================================================

# Habilitar intents necesarios para el bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Necesario para obtener miembros del guild

# Crear la única instancia del bot. Soporta prefijo (!) y slash commands.
bot = commands.Bot(command_prefix="!", intents=intents)

# ====================================================================
# --- 2. EVENTOS DEL BOT ---
# ====================================================================

@bot.event
async def on_ready():
    print(f'¡Bot conectado como {bot.user}!')
    print(f'ID: {bot.user.id}')
    print('------')

    # Cargar extensiones (cogs)
    initial_extensions = [
        'roaming', # Nuevo módulo para roaming
        'wb',      # Nuevo módulo para World Boss
        'cta',     # Nuevo módulo para CTA
        'builds',  # Ya existente, asumido en carpeta 'builds.py'
        'pi_cog'   # Nuevo módulo P.I.
    ]

    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Cargada extensión: {extension}")
        except commands.ExtensionAlreadyLoaded:
            print(f"Extensión {extension} ya cargada.")
        except commands.ExtensionNotFound:
            print(f"Error: Extensión {extension} no encontrada. Asegúrate de que el archivo exista.")
        except Exception as e:
            print(f"Error al cargar la extensión {extension}: {e}")
    
    # --- ¡IMPORTANTE! Sincronizar comandos de barra ---
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comando(s) de barra.")
    except Exception as e:
        print(f"Error al sincronizar comandos de barra: {e}")


# ====================================================================
# --- 3. EJECUCIÓN DEL BOT ---
# ====================================================================
keep_alive() # Para mantener el bot online, si usa Replit u similar
bot.run(os.getenv("DISCORD_TOKEN"))
