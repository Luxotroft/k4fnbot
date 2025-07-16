import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

# --- Configuración de las composiciones de Roaming (mantener como está) ---
ROAMING_PARTIES = {
    "kiteo1": {
        "max_players": 20,
        "roles": {
            "HOJ": 1, "PESADA": 1, "LECHO PEEL": 1, "LECHO SUP": 1, "GA": 1, "LOCUS": 1,
            "JURADORES": 1, "ENRAIZADO": 1, "LIFECURSED": 1, "OCULTO": 1, "ROMPERREINO": 1,
            "CAZAESPÍRITUS": 1, "FISURANTE": 2, "PRISMA": 1, "PUAS": 1, "SANTI": 3,
            "FORJACORTEZA": 1,
        },
        "emojis": {
            "HOJ": "<:ManodeJusticia:1290858364129247242>", "PESADA": "<:stoper:1290858463135662080>",
            "LECHO PEEL": "<:Lecho:1337861780780875876>", "LECHO SUP": "<:Lecho:1337861780780875876>",
            "GA": "<:GREAT_ARCANE:1357788071470301273>", "LOCUS": "<:Locus:1291467422238249043>",
            "JURADORES": "<:Maracas:1290858583965175828>", "ENRAIZADO": "<:Enraizado:1290879541073678397>",
            "LIFECURSED": "<:Maldi:1291467716229730415>", "OCULTO": "<:Oculto:1337862058779218026>",
            "ROMPERREINO": "<:RompeReino:1290881352182399017>", "CAZAESPIRITUS": "<:Cazaespiritu:1290881433816137821>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "PRISMA": "<:Prisma:1367151400672559184>",
            "PUAS": "<:Puas:1291468593506029638>", "SANTI": "<:Santificador:1290858870260109384>",
            "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
        },
        "default_params": {"tier": "8", "ip": "1450", "time_offset_minutes": 15, "gank_swap": "No", "caller": None}
    },
    "kiteo2": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "MARTILLO": 1, "1HARCANO": 1, "GA": 1, "LOCUS": 1, "JURADORES": 1, "LOCUS_OFENSIVO": 1,
            "CANCION": 1, "CARAMBANOS": 1, "DAMNATION": 1, "LIFECURSED": 1, "PUTREFACTO": 1,
            "OCULTO": 1, "WITCHWORD": 1, "FISURANTE": 1, "PRISMA": 1, "FORJACORTEZA": 1, "SANTI": 3, "TORRE_MOVIL": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "MARTILLO": "<:stoper:1290858463135662080>", "1HARCANO": "<:Arcano:1297064938531196959>",
            "GA": "<:GranArcano:1337861969931407411>", "LOCUS": "<:Locus:1291467422238249043>",
            "JURADORES": "<:Maracas:1290858583965175828>", "LOCUS_OFENSIVO": "<:Locus:1291467422238249043>",
            "CANCION": "<:Canciondedespertar:1291635941240213574>", "CARAMBANOS": "<:caram:1384931326968463372>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "LIFECURSED": "<:Maldi:1291467716229730415>",
            "PUTREFACTO": "<:Putrefacto:1370577320171016202>", "OCULTO": "<:Oculto:1337862058779218026>", "WITCHWORD": "<:witchword:1392942341815533758>",
            "FISURANTE": "<:Fisurante:1337862459008090112>", "PRISMA": "<:Prisma:1367151400672559184>", "FORJACORTEZA": "<:Infortunio:1290858784528531537>",
            "SANTI": "<:Santificador:1290858870260109384>", "TORRE_MOVIL": "<:MonturaMana:1337863658859925676>",
        },
        "default_params": {"tier": "8", "ip": "1450", "time_offset_minutes": 15, "gank_swap": "No", "caller": None}
    },
    "pocho": {
        "max_players": 22,
        "roles": {
            "GOLEM": 1, "PESADA": 2, "MARTILLO 1 H": 1, "JURADORES": 1, "LIFECURSED": 1,
            "LOCUS": 1, "ENRAIZADO": 1, # Estos dos son mutuamente excluyentes, el código lo manejará
            "GARZA": 1,
            "TALLADA": 1, "CAZAESPÍRITUS": 1, # Estos dos son mutuamente excluyentes, el código lo manejará
            "DAMNATION": 1, "ROMPERREINOS": 1, "DEMONFANG": 2, "GUADAÑA": 1, "INFERNALES": 2,
            "GRAN BASTON SAGRADO": 2, "REDENCION": 1, "INFORTUNIO": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "PESADA": "<:stoper:1290858463135662080>",
            "MARTILLO 1 H": "<:stoper:1290858463135662080>", "JURADORES": "<:Maracas:1290858583965175828>",
            "LIFECURSED": "<:Maldi:1291467716229730415>", "LOCUS": "<:Locus:1291467422238249043>",
            "ENRAIZADO": "<:Enraizado:1290879541073678397>", "GARZA": "<:Garza:1334558585325228032>",
            "TALLADA": "<:Tallada:1290881286092886172>", "CAZAESPIRITUS": "<:Cazaespiritu:1290881433816137821>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "ROMPERREINOS": "<:RompeReino:1290881352182399017>",
            "DEMONFANG": "<:Colmillo:1370577697516032031>", "GUADAÑA": "<:Guadaa:1291468660917014538>",
            "INFERNALES": "<:Infernales:1334556778465198163>", "GRAN BASTON SAGRADO": "<:gransagrado:1395086071275982848>",
            "REDENCION": "<:redencion:1395086294442573957>", "INFORTUNIO": "<:Infortunio:1290858784528531537>",
        },
        "mutually_exclusive_groups": [
            {"roles": ["LOCUS", "ENRAIZADO"], "max_total": 1}, # Añadido max_total
            {"roles": ["TALLADA", "CAZAESPÍRITUS"], "max_total": 1} # Añadido max_total
        ],
        "default_params": {"tier": "4.2", "ip": "1200", "time_offset_minutes": 15, "gank_swap": "No", "caller": None}
    },
    "brawl": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "MARTILLO 1H": 1, "MAZA PESADA": 1, "MONARCA": 1, "SAGRADO": 3, "INFORTUNIO": 1,
            "ENRAIZADO": 1, "JURADORES": 1, "LIFECURSED": 1, "TALLADA": 1, "DAMNATION": 1,
            "ROMPERREINO": 1, "DEMONFANG": 1, "GUADAÑA": 1, "PUAS": 1, "ZARPAS": 1, "ASTRAL": 1,
            "HOJA INFINITA": 1,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "MARTILLO 1H": "<:stoper:1290858463135662080>", "MAZA PESADA": "<:stoper:1290858463135662080>", "MONARCA": "<:monarca:1395087126017867836>", "SAGRADO": "✨",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>", "ENRAIZADO": "<:Enraizado:1290879541073678397>", "JURADORES": "<:Maracas:1290858583965175828>", "LIFECURSED": "<:Maldi:1291467716229730415>", "TALLADA": "<:Tallada:1290881286092886172>",
            "DAMNATION": "<:Maldiciones:1337862954820829294>", "ROMPERREINO": "<:RompeReino:1290881352182399017>", "DEMONFANG": "<:Colmillo:1370577697516032031>", "GUADAÑA": "<:Guadaa:1291468660917014538>", "PUAS": "<:Puas:1291468593506029638>",
            "ZARPAS": "<:Zarpas:1334560618941911181>", "ASTRAL": "<:Astral:1334556937328525413>", "HOJA INFINITA": "<:hoja:1395087940417228920>",
        },
        "default_params": {"tier": "8", "ip": "1450", "time_offset_minutes": 15, "gank_swap": "No", "caller": None}
    },
    "brawl2": {
        "max_players": 20,
        "roles": {
            "Maza pesada": 1, "Martillo de una mano": 1, "Baston de equilibrio": 1, "Santificador": 3, "Infortunio": 1,
            "Juradores": 1, "Silvano": 1, "Romperreinos": 1, "Putrefacto": 1, "Tallada": 1,
            "Astral": 1, "Patas de oso": 1, "Hoja infinita": 3, "Colmillo": 1, "Guadaña": 1, "Puas": 1
        },
        "emojis": {
            "Maza pesada": "<:stoper:1290858463135662080>", "Martillo de una mano": "<:CALLER:1367141230596853761>",
            "Baston de equilibrio": "<:Equilibrado:1291466491803471933>", "Santificador": "<:Hallowfall:1361429140460539973>",
            "Infortunio": "<:Infortunio:1290858784528531537>", "Juradores": "<:Maracas:1290858583965175828>",
            "Silvano": "<:Enraizado:1290879541073678397>", "Romperreinos": "<:RompeReino:1290881352182399017>",
            "Putrefacto": "<:Putrefacto:1370577320171016202>", "Tallada": "<:Tallada:1290881286092886172>",
            "Astral": "<:Astral:1334556937328525413>", "Patas de oso": "<:PatasDeOso:1272599457778630737>",
            "Hoja infinita": "<:hoja:1395087940417228920>", "Colmillo": "<:Colmillo:1370577697516032031>",
            "Guadaña": "<:Guadaa:1291468660917014538>", "Puas": "<:Puas:1291468593506029638>"
        },
        "default_params": {"tier": "8", "ip": "1450", "time_offset_minutes": 15, "gank_swap": "No", "caller": None}
    },
    "brawl_gucci": {
        "max_players": 20,
        "roles": {
            "GOLEM": 1, "PESADA": 1, "PESADA PEEL": 1, "GA": 1, "LOCUS": 1, "JURADORES": 1,
            "ENRAIZADO": 1, "DAMNATION": 1, "LIFECURSED": 1, "PUTREFACTO": 1, "ROMPERREINO": 1,
            "CAZAESPÍRITUS": 1, "HOJA INFINITA": 1, "ASTRAL": 1, "ZARPAS": 1, "INFERNALES": 1,
            "INFORTUNIO": 1, "SANTI": 3,
        },
        "emojis": {
            "GOLEM": "<:Terrunico:1290880192092438540>", "PESADA": "<:stoper:1290858463135662080>",
            "PESADA PEEL": "<:stoper:1290858463135662080>", "GA": "<:GranArcano:1337861969931407411>",
            "LOCUS": "<:Locus:1291467422238249043>", "JURADORES": "<:Maracas:1290858583965175828>",
            "ENRAIZADO": "<:Enraizado:1290879541073678397>", "DAMNATION": "<:Maldiciones:1337862954820829294>",
            "LIFECURSED": "<:Maldi:1291467716229730415>", "PUTREFACTO": "<:Putrefacto:1370577320171016202>",
            "ROMPERREINO": "<:RompeReino:1290881352182399017>", "CAZAESPÍRITUS": "<:Cazaespiritu:1290881433816137821>",
            "HOJA INFINITA": "<:hoja:1395087940417228920>", "ASTRAL": "<:Astral:1334556937328525413>",
            "ZARPAS": "<:Zarpas:1334560618941911181>", "INFERNALES": "<:Infernales:1338344041598812180>",
            "INFORTUNIO": "<:Infortunio:1290858784528531537>", "SANTI": "<:Santificador:1290858870260109384>",
        },
        "default_params": {"tier": "8", "ip": "1450", "time_offset_minutes": 15, "gank_swap": "No", "caller": None}
    }
}

# Diccionario para almacenar eventos de roaming activos
active_roaming_events = {}
event_counter = 0

class RoamingView(discord.ui.View):
    def __init__(self, event_id, composition_name, initial_roles_needed, max_players, mutual_exclusive_groups, caller_name):
        super().__init__(timeout=None)
        self.event_id = event_id
        self.composition_name = composition_name
        self.roles_needed = initial_roles_needed.copy()
        self.current_players = {}  # {user_id: role_name}
        self.max_players = max_players
        self.mutual_exclusive_groups = mutual_exclusive_groups
        self.caller_name = caller_name
        self.update_select_menu()

    def update_select_menu(self):
        # Limpiar los ítems existentes en la vista para recrearlos
        self.clear_items()

        options = []
        # Asegúrate de generar las opciones solo para roles NO excluyentes
        # y para los roles excluyentes, generar una única opción por grupo.
        processed_exclusive_groups = set()
        for role, count in self.roles_needed.items():
            emoji_str = ROAMING_PARTIES[self.composition_name]["emojis"].get(role, "❓")
            
            is_exclusive_role = False
            for group in self.mutual_exclusive_groups:
                if role in group["roles"]:
                    is_exclusive_role = True
                    group_key = tuple(sorted(group["roles"])) # Usar una tupla para identificar el grupo
                    if group_key not in processed_exclusive_groups:
                        # Solo añadir una opción por grupo excluyente
                        combined_label = " / ".join(group["roles"])
                        # Contar cuántos slots quedan en el grupo. Asumimos max_total es 1 para estos grupos.
                        # Si es 1, y ya hay alguien en el grupo, no hay slots.
                        current_players_in_group = sum(1 for uid, r in self.current_players.items() if r in group["roles"])
                        if current_players_in_group < group.get("max_total", 1): # Default max_total to 1
                            options.append(discord.SelectOption(label=f"{combined_label} (Disponible)", value=f"exclusive_{group['roles'][0]}", emoji="❓")) # Usa el primer rol como valor para el callback
                        processed_exclusive_groups.add(group_key)
                    break # Ya procesamos este rol como parte de un grupo excluyente

            if not is_exclusive_role and count > 0:
                options.append(discord.SelectOption(label=f"{role} ({count} dispo.)", value=role, emoji=emoji_str))

        if not options:
            options.append(discord.SelectOption(label="Todos los roles tomados", value="none", default=True))
            self.add_item(discord.ui.Select(placeholder="No hay roles disponibles", options=options, disabled=True))
        else:
            self.add_item(self.RoleSelect(options=options, custom_id=f"role_select_{self.event_id}"))

        self.add_item(self.LeaveRoleButton(custom_id=f"leave_role_{self.event_id}"))
        self.add_item(self.BenchButton(custom_id=f"bench_player_{self.event_id}"))
        self.add_item(self.CloseEventButton(custom_id=f"close_event_{self.event_id}"))

    def get_current_composition_string(self):
        composition_str = "**Roles Necesarios:**\n"
        
        # Primero, roles normales
        normal_roles_info = []
        for role, count in self.roles_needed.items():
            is_exclusive = False
            for group in self.mutual_exclusive_groups:
                if role in group["roles"]:
                    is_exclusive = True
                    break
            if not is_exclusive:
                emoji_str = ROAMING_PARTIES[self.composition_name]["emojis"].get(role, "")
                normal_roles_info.append(f"{emoji_str} **{role}**: {count} dispo.")

        if normal_roles_info:
            composition_str += "\n".join(normal_roles_info)
        
        # Luego, roles excluyentes
        exclusive_roles_info = []
        processed_exclusive_groups = set()
        for group in self.mutual_exclusive_groups:
            group_key = tuple(sorted(group["roles"]))
            if group_key not in processed_exclusive_groups:
                combined_roles_display = " / ".join(group["roles"])
                current_players_in_group = sum(1 for uid, r in self.current_players.items() if r in group["roles"])
                max_total = group.get("max_total", 1) # Default max_total to 1
                
                status_text = f"{max_total - current_players_in_group} dispo." if max_total - current_players_in_group > 0 else "ocupado"
                exclusive_roles_info.append(f"❓ **{combined_roles_display}**: {status_text}")
                processed_exclusive_groups.add(group_key)
        
        if exclusive_roles_info:
            if normal_roles_info:
                composition_str += "\n\n"
            composition_str += "**Roles Excluyentes:**\n" + "\n".join(exclusive_roles_info)


        if self.current_players:
            composition_str += "\n\n**Jugadores en la composición:**\n"
            players_by_role = {}
            for user_id, role in self.current_players.items():
                if role not in players_by_role:
                    players_by_role[role] = []
                players_by_role[role].append(f"<@{user_id}>")

            for role, players_list in players_by_role.items():
                emoji_str = ROAMING_PARTIES[self.composition_name]["emojis"].get(role, "")
                composition_str += f"{emoji_str} **{role}**: {', '.join(players_list)}\n"
        
        return composition_str

    def check_mutual_exclusion(self, user_id, new_role):
        current_role = self.current_players.get(user_id)
        if not self.mutual_exclusive_groups:
            return True

        for group in self.mutual_exclusive_groups:
            if new_role in group["roles"]:
                # Si el usuario ya tiene un rol de este grupo, no puede tomar otro rol del mismo grupo
                if current_role and current_role in group["roles"] and current_role != new_role:
                    return False 
                
                # Contar cuántos roles del grupo están tomados por otros jugadores
                count_in_group = sum(1 for uid, r in self.current_players.items() if r in group["roles"] and uid != user_id)
                
                # Si añadir este rol excede el max_total del grupo
                if count_in_group + 1 > group.get("max_total", len(group["roles"])): # Default max_total to the number of roles in group
                    return False
        return True

    async def update_embed(self, message):
        embed = message.embeds[0]
        # Asegúrate de que la descripción no exceda los 4096 caracteres
        embed.description = self.get_current_composition_string()
        if len(embed.description) > 4096:
            embed.description = "Descripción demasiado larga para mostrar. Roles y jugadores detallados a continuación." # Fallback message
            # O podrías intentar truncar el string, o dividirlo en múltiples campos si es posible.

        # Re-crear el campo de roles, o actualizar su valor
        # Para simplificar y evitar el error 1024, eliminaremos el campo y pondremos todo en la descripción
        # o si realmente queremos un campo, asegurarnos de que el contenido sea corto.
        # Por ahora, moveré todo a la descripción principal del embed para el formato actualizado
        # y eliminaremos el add_field específico para "Roles Necesarios".
        # En el `roaming_command` tendremos que ajustar esto también.

        # Actualizar el footer
        embed.set_footer(text=f"Jugadores: {len(self.current_players)}/{self.max_players}")
        await message.edit(embed=embed, view=self)

    class RoleSelect(discord.ui.Select):
        def __init__(self, options, custom_id):
            super().__init__(placeholder="Selecciona tu rol...", options=options, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            view: RoamingView = self.view
            selected_value = self.values[0]
            user_id = interaction.user.id
            current_role = view.current_players.get(user_id)

            if selected_value == "none":
                await interaction.response.send_message("No hay roles disponibles en este momento.", ephemeral=True)
                return
            
            selected_role = selected_value
            is_exclusive_selection = False
            if selected_value.startswith("exclusive_"):
                is_exclusive_selection = True
                selected_role = selected_value.replace("exclusive_", "") # Obtener el nombre del rol real
                # En este punto, `selected_role` es uno de los roles dentro del grupo excluyente.
                # Tendremos que determinar si es el correcto o si el usuario quiere otro de ese grupo.
                # Para simplificar, asumiremos que si elige "exclusive_LOCUS", se quiere LOCUS.
                # Si el usuario hace clic en una opción de grupo, asignamos el primer rol del grupo
                # que está disponible y no rompe la exclusividad. Esto requiere un ajuste.
                
                # Para hacerlo más robusto, el valor del SelectOption para un grupo exclusivo
                # debería ser el nombre específico del rol que el usuario está eligiendo *dentro* de ese grupo.
                # Por ahora, lo dejaré con `exclusive_ROLENAME` y en el callback
                # asumimos que `selected_role` es el rol que el usuario realmente quiere.

                # Si el usuario ya está en un rol del mismo grupo excluyente y elige la misma opción del select,
                # no hacemos nada.
                if current_role and any(role in view.mutual_exclusive_groups for group in view.mutual_exclusive_groups if current_role in group["roles"] and selected_role in group["roles"]):
                     await interaction.response.send_message(f"Ya estás en un rol de este grupo exclusivo o es el mismo rol.", ephemeral=True)
                     return


            # Manejar roles mutuamente excluyentes ANTES de asignar.
            # `check_mutual_exclusion` ya lo hace, pero aquí el manejo de la lógica de asignación.
            if not view.check_mutual_exclusion(user_id, selected_role):
                await interaction.response.send_message(f"No puedes tomar el rol de **{selected_role}** porque ya estás en un rol mutuamente excluyente o el límite del grupo se ha alcanzado.", ephemeral=True)
                return

            if current_role: # El usuario está cambiando de rol
                # Si el rol actual es parte de un grupo excluyente, liberarlo correctamente
                found_current_in_exclusive_group = False
                for group in view.mutual_exclusive_groups:
                    if current_role in group["roles"]:
                        # Para roles excluyentes, no incrementamos el contador de roles individuales,
                        # sino que marcamos que el slot del grupo está libre.
                        # La lógica de `roles_needed` es para roles no-excluyentes.
                        found_current_in_exclusive_group = True
                        break
                
                if not found_current_in_exclusive_group:
                    view.roles_needed[current_role] += 1 # Liberar el rol antiguo (si no era exclusivo)
                view.current_players.pop(user_id) # Eliminar del usuario de los jugadores actuales

            # Asignar el nuevo rol
            found_new_in_exclusive_group = False
            for group in view.mutual_exclusive_groups:
                if selected_role in group["roles"]:
                    # Para roles excluyentes, no decrementamos el contador de roles individuales.
                    # Simplemente asignamos el rol. La comprobación `check_mutual_exclusion` ya maneja los límites.
                    found_new_in_exclusive_group = True
                    break

            if not found_new_in_exclusive_group:
                if view.roles_needed.get(selected_role, 0) > 0: # Check if normal role is available
                    view.roles_needed[selected_role] -= 1
                    view.current_players[user_id] = selected_role
                    view.update_select_menu()
                    await view.update_embed(interaction.message)
                    await interaction.response.send_message(f"Te has unido a la composición como **{selected_role}**.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"No hay más espacios para el rol de **{selected_role}**.", ephemeral=True)
            else: # Es un rol exclusivo, ya hemos comprobado disponibilidad
                view.current_players[user_id] = selected_role
                view.update_select_menu()
                await view.update_embed(interaction.message)
                await interaction.response.send_message(f"Te has unido a la composición como **{selected_role}**.", ephemeral=True)

    class LeaveRoleButton(discord.ui.Button):
        def __init__(self, custom_id):
            super().__init__(label="Salir de Rol", style=discord.ButtonStyle.red, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            view: RoamingView = self.view
            user_id = interaction.user.id
            current_role = view.current_players.get(user_id)

            if current_role:
                # Si el rol es parte de un grupo excluyente, solo quitar al jugador sin afectar los contadores de `roles_needed`
                is_exclusive_role = False
                for group in view.mutual_exclusive_groups:
                    if current_role in group["roles"]:
                        is_exclusive_role = True
                        break
                
                if not is_exclusive_role:
                    view.roles_needed[current_role] += 1 # Liberar el rol antiguo (si no era exclusivo)
                
                view.current_players.pop(user_id)
                view.update_select_menu()
                await view.update_embed(interaction.message)
                await interaction.response.send_message(f"Has salido del rol de **{current_role}**.", ephemeral=True)
            else:
                await interaction.response.send_message("No estás asignado a ningún rol en esta composición.", ephemeral=True)

    class BenchButton(discord.ui.Button):
        def __init__(self, custom_id):
            super().__init__(label="Banca", style=discord.ButtonStyle.grey, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            view: RoamingView = self.view
            caller_id = int(view.caller_name.split('<@')[1][:-1]) # Extract ID from <@ID> or <@!ID>
            if interaction.user.id != caller_id:
                await interaction.response.send_message("Solo el caller puede usar este botón.", ephemeral=True)
                return
            await interaction.response.send_message("Funcionalidad de banca (próximamente).", ephemeral=True)

    class CloseEventButton(discord.ui.Button):
        def __init__(self, custom_id):
            super().__init__(label="Cerrar Evento", style=discord.ButtonStyle.danger, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            view: RoamingView = self.view
            caller_id = int(view.caller_name.split('<@')[1][:-1]) # Extract ID from <@ID> or <@!ID>
            if interaction.user.id != caller_id:
                await interaction.response.send_message("Solo el caller puede cerrar este evento.", ephemeral=True)
                return

            del active_roaming_events[view.event_id]
            for item in view.children:
                item.disabled = True
            
            # --- CAMBIO AQUÍ PARA ELIMINAR EL RATE LIMIT ---
            # En lugar de followup.send después de edit_message, 
            # combina la acción o envía el mensaje de confirmación primero.
            # Opción 1: Simplemente edita el mensaje para decir que está cerrado y la vista deshabilitada.
            await interaction.response.edit_message(content=f"El evento de roaming '{view.event_id}' ha sido cerrado por {interaction.user.mention}.", view=view, embed=None)
            # await interaction.response.send_message(f"El evento de roaming '{view.event_id}' ha sido cerrado por {interaction.user.mention}.", ephemeral=False) # Si quieres un mensaje separado


class Roaming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global event_counter
        event_counter = 0 # Reset for development, in production you might load from persistent storage

    @commands.command(name="roaming")
    async def roaming_command(self, ctx, composition_name: str, tier: str = None, ip: str = None, time_str: str = None, gank_swap: str = None, caller: discord.Member = None):
        global event_counter

        composition_name = composition_name.lower()
        if composition_name not in ROAMING_PARTIES:
            await ctx.send(f"Composición '{composition_name}' no encontrada. Las composiciones disponibles son: {', '.join(ROAMING_PARTIES.keys())}")
            return

        comp_data = ROAMING_PARTIES[composition_name]
        defaults = comp_data["default_params"]

        # Apply defaults if arguments are not provided
        tier = tier if tier else defaults["tier"]
        ip = ip if ip else defaults["ip"]
        time_offset_minutes = defaults["time_offset_minutes"]
        if time_str:
            try:
                time_offset_minutes = int(time_str)
            except ValueError:
                await ctx.send("La hora debe ser un número en minutos (ej. 20 para 20 minutos).")
                return
        
        gank_swap = gank_swap if gank_swap else defaults["gank_swap"]
        caller_display = caller.mention if caller else ctx.author.mention
        
        # Generar ID único para el evento
        event_counter += 1
        event_id = f"{ctx.author.name.replace(' ', '_')}-{event_counter}" # Use author's name and counter

        # Calculate ETA
        eta_time = datetime.now() + timedelta(minutes=time_offset_minutes)
        eta_timestamp = int(eta_time.timestamp())

        roles_needed_initial = comp_data["roles"].copy()
        
        # Build the initial embed
        embed = discord.Embed(
            title=f"📢 ¡ROAMING - Composición: {composition_name.upper()}!",
            description=f"**Tier**: {tier}\n**IP**: {ip}\n**ETA**: <t:{eta_timestamp}:R>\n**Gank Swap**: {gank_swap}\n**Caller**: {caller_display}\n\n",
            color=discord.Color.blue()
        )
        # --- CAMBIO AQUÍ PARA EL CAMPO LARGO DEL EMBED ---
        # El contenido de roles y jugadores se gestionará en la descripción principal del embed
        # Esto evitará el error de límite de caracteres de campo.
        embed.description += self.get_initial_composition_string_for_command(composition_name)

        embed.set_footer(text=f"Jugadores: 0/{comp_data['max_players']}")

        # Create the view with buttons and select menu
        mutual_exclusive_groups = comp_data.get("mutually_exclusive_groups", [])
        view = RoamingView(event_id, composition_name, roles_needed_initial, comp_data["max_players"], mutual_exclusive_groups, caller_display)

        # Send the message with the embed and view
        message = await ctx.send(f"@everyone ¡Preparando roaming!", embed=embed, view=view)
        
        # Store the event
        active_roaming_events[event_id] = {"message": message, "view": view, "caller_id": ctx.author.id}
    
    # Nuevo método para la string inicial del embed del comando
    def get_initial_composition_string_for_command(self, composition_name):
        comp_data = ROAMING_PARTIES[composition_name]
        composition_str = ""
        
        # Procesar roles normales
        normal_roles = []
        for role, count in comp_data["roles"].items():
            is_exclusive = False
            for group in comp_data.get("mutually_exclusive_groups", []):
                if role in group["roles"]:
                    is_exclusive = True
                    break
            if not is_exclusive:
                emoji_str = comp_data["emojis"].get(role, "")
                normal_roles.append(f"{emoji_str} **{role}**: {count} dispo.")
        
        if normal_roles:
            composition_str += "**Roles Necesarios:**\n" + "\n".join(normal_roles)

        # Procesar grupos de roles excluyentes
        exclusive_groups_info = []
        processed_exclusive_groups = set()
        for group in comp_data.get("mutually_exclusive_groups", []):
            group_key = tuple(sorted(group["roles"]))
            if group_key not in processed_exclusive_groups:
                combined_roles = " / ".join(group["roles"])
                max_total_display = group.get("max_total", 1) # Display 1 if not specified
                exclusive_groups_info.append(f"❓ **{combined_roles}**: {max_total_display} dispo.")
                processed_exclusive_groups.add(group_key)
        
        if exclusive_groups_info:
            if normal_roles:
                composition_str += "\n\n"
            composition_str += "**Roles Excluyentes:**\n" + "\n".join(exclusive_groups_info)

        return composition_str


async def setup(bot):
    await bot.add_cog(Roaming(bot))
