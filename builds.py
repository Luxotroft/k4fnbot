import discord
from discord.ext import commands

class BuildsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Diccionario con las builds organizadas por nombre de arma/rol y luego por tipo
        self.build_data = {
            # --- Builds de COMPO BRAWL ---
            'golem': {
                'brawl': {
                    'description': 'Casco: Cap. Mercenario / Juez / Asesino | Armadura: Caballero / Valor | Botas: Valor / Z. Real / Acechador | Off Hand: N/A | Capa: Morgana / Contrabandista | Comida: Omelette .2',
                    'emojis': '🛡️'
                }
            },
            'maza pesada': {
                'brawl': {
                    'description': 'Casco: Tenacidad / Cap. Mercenario | Armadura: Crepuscular / Guardian | Botas: Acechador / Valor / Cazador | Off Hand: N/A | Capa: Contrabandista / Martlock / Bridge | Comida: Bocadillo Locha .2',
                    'emojis': '🛡️'
                }
            },
            'gran arcano': {
                'brawl': {
                    'description': 'Casco: Asesino / Vándalo / Valor | Armadura: Caballero / Crepuscular | Botas: Acechador / Valor / Clérigo | Off Hand: N/A | Capa: Contrabandista / Martlock / Bridge | Comida: Tortilla .2',
                    'emojis': '🛡️'
                }
            },
            'locus': {
                'brawl': {
                    'description': 'Casco: Asesino | Armadura: Judi / Demon | Botas: Z.Reales / Clérigo / Mercenario | Off Hand: N/A | Capa: Morgana / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Demon | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'damnation': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino | Armadura: Arm. Real / Erudito | Botas: Z.Reales / Clérigo / Mercenario | Off Hand: N/A | Capa: Morgana | Comida: Tortilla .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Erudito | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'lifecurse': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino | Armadura: Judi / Demon / Caballero | Botas: Z.Reales / Clérigo / Mercenario | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Tortilla .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Demon / Crepuscular / Caballero | Botas: Valor / Z.Reales / Acechador | Off Hand: Invocanieblas / Aegis | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'enraizado': {
                'brawl': {
                    'description': 'Casco: Asesino | Armadura: Judi | Botas: Z.Reales / Clérigo / Mercenario | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Tortilla .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Judi | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'juradores': {
                'brawl': {
                    'description': 'Casco: Asesino | Armadura: Demon / Judi | Botas: Z.Reales / Clérigo / Mercenario | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Tortilla .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Demon | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'romperreino': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / Clérigo | Armadura: Vándalo / Juez | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Caballero | Armadura: Ch. Real / Caminanieblas | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/a | Capa: Bracilien / Lym | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'cazaespiritus': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / Clérigo | Armadura: Vándalo / Tenacidad / Caminanieblas | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Ch. Real / Caminanieblas | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/a | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'hoja infinita': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / C. Acechador | Armadura: Armadura Guardian / Vándalo / Acechador | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                },
                 'kiteo': {
                    'description': 'Casco: Asesino / Caminanieblas | Armadura: Escamas / Pureza | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/a | Capa: Bracilien / Lym | Comida: Guiso .3',
                    'emojis': '🌬️'
                }
            },
            'guadaña': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / C. Acechador | Armadura: Armadura Guardian / Vándalo / Acechador | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                }
            },
            'zarpas': {
                'brawl': {
                    'description': 'Casco: Asesino / Soldado / Acechador | Armadura: Vándalo / Mercenario / Tenacidad | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                }
            },
            'manos infernales': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / Clérigo | Armadura: Vándalo / Acechador | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Guiso .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Soldado / Asesino / Clérigo | Armadura: Vándalo / Acechador | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Guiso .2',
                    'emojis': '🌬️'
                }
            },
            'santi': {
                'brawl': {
                    'description': 'Casco: Guardian / C. Caballero | Armadura: Pureza | Botas: Acechador / Mercenario | Off Hand: Invocanieblas | Capa: Contrabandista / Lym | Comida: Omelette .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Caballero / Guardian / H. Real | Armadura: Escamas / Pureza | Botas: Acechador / Z. Reales / Mercenario | Off Hand: Invocanieblas | Capa: Caerleon / Lym | Comida: Omelette .2',
                    'emojis': '🌬️'
                }
            },
            'forjacorteza': {
                'brawl': {
                    'description': 'Casco: Caminanieblas / Caballero / C. de Juez | Armadura: Pureza | Botas: Acechador / Mercenario | Off Hand: N/a | Capa: Contrabandista / Lym | Comida: Omelette .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino / Caballero | Armadura: Escamas / Pureza | Botas: Acechador / Z. Reales / Mercenario | Off Hand: N/a | Capa: Lym / Contrabandista | Comida: Omelette .2',
                    'emojis': '🌬️'
                }
            },
            'infortunio': {
                'brawl': {
                    'description': 'Casco: Caminanieblas / Caballero / C. de Juez | Armadura: Pureza | Botas: Acechador / Mercenario | Off Hand: N/a | Capa: Contrabandista / Lym | Comida: Omelette .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino / Caballero | Armadura: Escamas / Pureza | Botas: Acechador / Z. Reales / Mercenario | Off Hand: N/a | Capa: Lym / Contrabandista | Comida: Omelette .2',
                    'emojis': '🌬️'
                }
            },
            'equilibrio': {
                'brawl': {
                    'description': 'Casco: Soldado / Clérigo / Vándalo | Armadura: Caballero / Crepuscular | Botas: Escamas / Valor / Acechador | Off Hand: N/A | Capa: Bridwatch / Martlock | Comida: Bocadillo Locha .2',
                    'emojis': '🛡️'
                }
            },
            'martillo 1m': {
                'brawl': {
                    'description': 'Casco: Vándalo / Juez / Cap. Mercenario | Armadura: Caballero / Crepuscular | Botas: Valor | Off Hand: Malicioso | Capa: Contrabandista / Martlock / Bridge | Comida: Bocadillo Locha .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Vándalo | Armadura: Crepuscular / Caballero | Botas: Valor / Z.Reales / Acechador | Off Hand: Malicioso | Capa: Lym / Contrabandista | Comida: Bocadillo de locha',
                    'emojis': '🌬️'
                }
            },
            'carambanos': {
                'brawl': {
                    'description': 'Casco: Asesino | Armadura: Caballero / Crepuscular | Botas: Acechador / Valor / Clérigo | Off Hand: N/A | Capa: Contrabandista / Martlock / Bridge | Comida: Tortilla .2',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Caballero | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'incubo': {
                'brawl': {
                    'description': 'Casco: Asesino | Armadura: Guardian / Crepuscular / Caballero | Botas: Acechador / Valor | Off Hand: Invocanieblas / Aegis | Capa: Contrabandista / Lym | Comida: Bocadillo Locha',
                    'emojis': '🛡️'
                }
            },
            'puas': {
                'brawl': {
                    'description': 'Casco: Soldado / Caminanieblas / Asesino | Armadura: Vándalo / Mercenario / Caminanieblas | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Asesino / Caminanieblas | Armadura: Cazador | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/a | Capa: Bracilien / Lym | Comida: Guiso .3',
                    'emojis': '🌬️'
                }
            },
            'colmillos': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / Clérigo | Armadura: Vándalo / Mercenario / Caminanieblas | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Soldado / Asesino / Clérigo | Armadura: Vándalo / Mercenario / Caminanieblas | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🌬️'
                }
            },
            'falce': {
                'brawl': {
                    'description': 'Casco: Soldado / Asesino / C. Acechador | Armadura: Vándalo / Mercenario / Caminanieblas | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🛡️'
                },
                'kiteo': {
                    'description': 'Casco: Soldado / Asesino / C. Acechador | Armadura: Vándalo / Mercenario / Caminanieblas | Botas: Guardatumba / Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Pargo / Cerdo asado',
                    'emojis': '🌬️'
                }
            },
            'fisurante': {
                'kiteo': {
                    'description': 'Casco: Caminanieblas | Armadura: Escamas / Pureza | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/a | Capa: Bracilien / Lym | Comida: Guiso .3',
                    'emojis': '🌬️'
                }
            },
            'prisma': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Erudito | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/a | Capa: Bracilien / Lym | Comida: Omelette .2',
                    'emojis': '🌬️'
                }
            },
            'torre movil': {
                'brawl': {
                    'description': 'SET DE ESCAPE',
                    'emojis': '🏃'
                },
                'kiteo': {
                    'description': 'SET DE ESCAPE',
                    'emojis': '🏃'
                }
            },
            'behemot': {
                'brawl': {
                    'description': 'SET DE ESCAPE',
                    'emojis': '🏃'
                },
                'kiteo': {
                    'description': 'SET DE ESCAPE',
                    'emojis': '🏃'
                }
            },
            'aguila': {
                'brawl': {
                    'description': 'SET DE ESCAPE',
                    'emojis': '🏃'
                },
                'kiteo': {
                    'description': 'SET DE ESCAPE',
                    'emojis': '🏃'
                }
            },
            'exaltado': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Judi | Botas: Z.Reales / Clérigo / Mercenario | Off Hand: N/A | Capa: Contrabandista / Lym | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'cancion': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Escamas / Pureza | Botas: Guardatumba / Z. Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'arcano 1 h': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Judi | Botas: Valor / Z.Reales / Acechador | Off Hand: Aegis / Malicioso | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'oculto': {
                'kiteo': {
                    'description': 'Casco: Caballero | Armadura: Ch. Real | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            },
            'hoj': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Demon | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Omelette .3',
                    'emojis': '🌬️'
                }
            },
            'pesada': {
                 'brawl': {
                    'description': 'Casco: Vándalo | Armadura: Guardian / Caballero | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Bocadillo de locha',
                    'emojis': '🛡️'
                 },
                 'kiteo': {
                    'description': 'Casco: Vándalo | Armadura: Guardian / Caballero | Botas: Valor / Z.Reales / Acechador | Off Hand: N/A | Capa: Lym / Contrabandista | Comida: Bocadillo de locha',
                    'emojis': '🌬️'
                 }
            },
            'lecho peel': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Caballero / Crepuscular | Botas: Valor / Z.Reales / Acechador | Off Hand: Aegis | Capa: Lym / Contrabandista | Comida: Bocadillo de locha',
                    'emojis': '🌬️'
                }
            },
            'lecho sup': {
                'kiteo': {
                    'description': 'Casco: Asesino | Armadura: Demon | Botas: Valor / Z.Reales / Acechador | Off Hand: Aegis | Capa: Lym / Contrabandista | Comida: Tortilla .2',
                    'emojis': '🌬️'
                }
            }
        }
        print("✅ Módulo de Builds cargado (comandos !build)")

    @commands.command(name='build')
    async def build_command(self, ctx, *, build_name: str):
        """
        Muestra la información de una build específica o una imagen para composiciones.
        Ejemplo: !build santi, !build brawl, !build kiteo
        """
        build_name_clean = build_name.lower().strip()
        
        # --- PASO DE DEPURACIÓN: MIRA QUÉ RECIBE EL COMANDO ---
        print(f"DEBUG: Comando !build recibido. build_name_clean: '{build_name_clean}'")
        # ----------------------------------------------------

        # Condición especial para el comando !build brawl
        if build_name_clean == 'brawl':
            embed = discord.Embed(
                title="🛡️ Builds para Composición **BRAWL**",
                color=discord.Color.red()
            )
            # URL de la imagen que quieres mostrar para brawl
            image_url = "https://media.discordapp.net/attachments/1387864307378819202/1387864321404567602/image.png?ex=685ee4df&is=685d935f&hm=884cf944b954c7925e98f3ffc41d20d316eb6ddc9e10ce2a50f96392a6ae05df&=&format=webp&quality=lossless&width=864&height=442" # CAMBIA ESTE LINK POR LA IMAGEN DE BRAWL
            embed.set_image(url=image_url)
            embed.set_footer(text="Fuente: Composiciones de Gremio")
            await ctx.send(embed=embed)
            return  # Termina la ejecución para no continuar con la búsqueda en el diccionario
        
        # Condición especial para el comando !build kiteo
        if build_name_clean == 'kiteo':
            embed = discord.Embed(
                title="🌬️ Builds para Composición **KITEO**",
                color=discord.Color.blue()
            )
            # URL de la imagen que quieres mostrar para kiteo
            image_url = "https://cdn.discordapp.com/attachments/1387864307378819202/1387864874427744386/image.png?ex=685ee563&is=685d93e3&hm=1041c35cd7a17235f7fd9accf45f1c31ec2f07f96eafae92544e5b896a3cde35&" # CAMBIA ESTE LINK POR LA IMAGEN DE KITEO
            embed.set_image(url=image_url)
            embed.set_footer(text="Fuente: Composiciones de Gremio")
            await ctx.send(embed=embed)
            return # Termina la ejecución

        # Busca la build principal en el diccionario si no es una de las excepciones
        build_options = self.build_data.get(build_name_clean)
        
        if build_options:
            # Crea un Embed principal
            embed = discord.Embed(
                title=f"🛠️ Builds para **{build_name_clean.upper()}**",
                color=discord.Color.blue()
            )
            
            # Itera sobre los tipos de composición disponibles para esta build (brawl, kiteo, etc.)
            for build_type, details in build_options.items():
                embed.add_field(
                    name=f"**{build_type.capitalize()}** {details['emojis']}",
                    value=details['description'],
                    inline=False  # Para que cada build esté en una línea separada
                )
            
            embed.set_footer(text="¡Buena suerte en el PvP!")
            await ctx.send(embed=embed)
        else:
            # Si la build no se encuentra, envía un mensaje de error y sugiere las disponibles.
            available_builds = sorted(list(self.build_data.keys()))
            available_str = ", ".join([f"`{name}`" for name in available_builds])
            await ctx.send(f"❌ **Build no encontrada.** Las builds disponibles son: {available_str}")

# Esta función es necesaria para que el bot pueda cargar el cog
async def setup(bot):
    await bot.add_cog(BuildsCog(bot))
