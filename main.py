import json
import io
import shutil
import os
import re
from pathlib import Path
from threading import Thread
from flask import Flask

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")  # lee el archivo .env junto a bot.py

# ───────────────────────── CONFIG ─────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")      # viene del archivo .env, NUNCA lo pongas en el código
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR))).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "data.json"         # ruta fija: junto a bot.py
LOGO_URL = ""                           # opcional: URL del logo para miniatura de anuncios
MAX_SLOTS = 20

COLORES = {
    "rojo": 0xE74C3C, "azul": 0x3498DB, "verde": 0x2ECC71,
    "dorado": 0xF1C40F, "morado": 0x9B59B6, "naranja": 0xE67E22,
}

# ───────────────────────── DATOS ─────────────────────────
def load():
    if DATA_FILE.exists():
        contenido = DATA_FILE.read_text(encoding="utf-8").strip()
        datos = json.loads(contenido) if contenido else {}
    else:
        datos = {}
    datos.setdefault("comps", {})
    datos.setdefault("pings", {})
    datos.setdefault("verification", {})
    datos.setdefault("verification_pending", {})
    return datos

db = load()

def save():
    tmp = DATA_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DATA_FILE)

# ───────────────────────── HELPERS ─────────────────────────
def parse_roles(texto: str):
    """'Tank; Healer; Arcano/Arcano pesado' -> lista de roles (con variantes si hay / o ' o ')."""
    roles = []
    for raw in texto.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        opts = [o.strip() for o in re.split(r"\s*/\s*|\s+o\s+", raw) if o.strip()]
        if len(opts) > 1:
            roles.append({"name": " / ".join(opts), "options": opts[:25]})
        else:
            roles.append({"name": raw, "options": []})
    return roles

def format_hora(txt: str) -> str:
    t = txt.strip()
    if t.lower() in ("ahora", "ya", "now"):
        return "¡AHORA!"
    m = re.fullmatch(r"(\d{1,2})[:h.]?(\d{2})?\s*(utc)?", t, re.I)
    if m:
        return f"{int(m[1]):02d}:{m[2] or '00'} UTC"
    return t

def parse_color(txt: str) -> int:
    t = (txt or "").strip().lower()
    if t in COLORES:
        return COLORES[t]
    try:
        return int(t.lstrip("#"), 16)
    except ValueError:
        return COLORES["dorado"]

def size(p): return len(p["roles"])

def user_slot(p, uid):
    for k, v in p["slots"].items():
        if v["user"] == uid:
            return k
    return None

def assign(p, uid, name, i, choice):
    k = user_slot(p, uid)
    if k is not None:
        del p["slots"][k]
    p["slots"][str(i)] = {"user": uid, "name": name, "choice": choice}

def can_manage(interaction, p):
    perms = interaction.user.guild_permissions
    return interaction.user.id == p["author_id"] or perms.manage_messages or perms.administrator

def build_embed(p, cancelled=False):
    n = size(p)
    e = discord.Embed(
        title=f"{'❌ CTA CANCELADA' if cancelled else '⚔️ CTA'} — {p['comp']}",
        description=f"🕒 **Hora:** {p['hora']}\n👤 **Convoca:** <@{p['author_id']}>",
        color=0xE74C3C if cancelled else 0xF1C40F,
    )
    for party in range(p["parties"]):
        lines, filled = [], 0
        for j in range(n):
            s = p["slots"].get(str(party * n + j))
            if s:
                filled += 1
                lines.append(f"`{j+1:>2}.` {s['choice']} — <@{s['user']}>")
            else:
                lines.append(f"`{j+1:>2}.` {p['roles'][j]['name']} — *libre*")
        e.add_field(name=f"Party {party+1} ({filled}/{n})", value="\n".join(lines), inline=False)
    if not cancelled:
        e.set_footer(text="Elige tu slot en el menú de abajo")
    return e

async def refresh(interaction, pid):
    p = db["pings"][pid]
    save()
    if interaction.response.is_done():
        ch = interaction.client.get_partial_messageable(p["channel_id"])
        await ch.get_partial_message(int(pid)).edit(embed=build_embed(p), view=PingView(pid))
    else:
        await interaction.response.edit_message(embed=build_embed(p), view=PingView(pid))

# ───────────────────────── VISTA DEL PING ─────────────────────────
class SlotSelect(discord.ui.Select):
    def __init__(self, pid, party, p):
        n = size(p)
        opts = []
        for j in range(n):
            i = party * n + j
            s = p["slots"].get(str(i))
            opts.append(discord.SelectOption(
                label=f"{j+1}. {p['roles'][j]['name']}"[:100],
                value=str(i),
                description=(f"Ocupado: {s['name']}" if s else "Libre")[:100],
                emoji="🔴" if s else "🟢",
            ))
        super().__init__(custom_id=f"ping:{pid}:p{party}",
                         placeholder=f"Elige tu slot — Party {party+1}", options=opts)
        self.pid = pid

    async def callback(self, interaction: discord.Interaction):
        await choose_slot(interaction, self.pid, int(self.values[0]))

async def choose_slot(interaction, pid, i):
    p = db["pings"].get(pid)
    if not p:
        return await interaction.response.send_message("Este ping ya no está activo.", ephemeral=True)
    uid = interaction.user.id
    if uid in p["kicked"]:
        return await interaction.response.send_message("🚫 Fuiste expulsado de este ping.", ephemeral=True)
    cur = p["slots"].get(str(i))
    if cur and cur["user"] == uid:
        return await interaction.response.send_message("Ya estás en ese slot.", ephemeral=True)
    if cur:
        return await interaction.response.send_message("❌ Ese slot ya está ocupado.", ephemeral=True)
    role = p["roles"][i % size(p)]
    if role["options"]:
        return await interaction.response.send_message(
            f"**{role['name']}** — elige tu variante:", view=VariantView(pid, i, role["options"]), ephemeral=True)
    
    assign(p, uid, interaction.user.display_name, i, role["name"])
    await refresh(interaction, pid)

class VariantView(discord.ui.View):
    def __init__(self, pid, i, options):
        super().__init__(timeout=120)
        self.pid, self.i = pid, i
        sel = discord.ui.Select(placeholder="Elige tu rol",
                                options=[discord.SelectOption(label=o[:100]) for o in options])
        sel.callback = self.pick
        self.sel = sel
        self.add_item(sel)

    async def pick(self, interaction: discord.Interaction):
        p = db["pings"].get(self.pid)
        if not p:
            return await interaction.response.edit_message(content="Este ping ya no está activo.", view=None)
        if str(self.i) in p["slots"]:
            return await interaction.response.edit_message(content="❌ Alguien tomó ese slot antes.", view=None)
        choice = self.sel.values[0]
        assign(p, interaction.user.id, interaction.user.display_name, self.i, choice)
        await interaction.response.edit_message(content=f"✅ Anotado como **{choice}**", view=None)
        await refresh(interaction, self.pid)

class KickView(discord.ui.View):
    def __init__(self, pid, p):
        super().__init__(timeout=120)
        self.pid = pid
        items = list(p["slots"].items())
        for c in range(0, len(items), 25):
            sel = discord.ui.Select(
                placeholder="Elige a quién expulsar",
                options=[discord.SelectOption(label=f"{v['name']} — {v['choice']}"[:100], value=k)
                         for k, v in items[c:c + 25]])
            sel.callback = self.make_cb(sel)
            self.add_item(sel)

    def make_cb(self, sel):
        async def cb(interaction: discord.Interaction):
            p = db["pings"].get(self.pid)
            if not p:
                return await interaction.response.edit_message(content="Este ping ya no está activo.", view=None)
            s = p["slots"].pop(sel.values[0], None)
            if s:
                p["kicked"].append(s["user"])
            await interaction.response.edit_message(
                content=f"🥾 {s['name'] if s else 'Usuario'} fue expulsado del ping.", view=None)
            await refresh(interaction, self.pid)
        return cb

class PingView(discord.ui.View):
    def __init__(self, pid):
        super().__init__(timeout=None)
        self.pid = pid
        p = db["pings"].get(pid)
        if not p:
            return
        for party in range(p["parties"]):
            self.add_item(SlotSelect(pid, party, p))
        self._btn("Salirme", discord.ButtonStyle.secondary, "🚪", "leave", self.leave)
        self._btn("Kick", discord.ButtonStyle.secondary, "🥾", "kick", self.kick)
        if p["parties"] == 1:
            self._btn("Añadir Party 2", discord.ButtonStyle.primary, "➕", "party2", self.party2)
        self._btn("Cancelar CTA", discord.ButtonStyle.danger, "🛑", "cancel", self.cancel)

    def _btn(self, label, style, emoji, key, cb):
        b = discord.ui.Button(label=label, style=style, emoji=emoji, custom_id=f"ping:{self.pid}:{key}")
        b.callback = cb
        self.add_item(b)

    async def leave(self, interaction: discord.Interaction):
        p = db["pings"].get(self.pid)
        if not p:
            return await interaction.response.send_message("Este ping ya no está activo.", ephemeral=True)
        k = user_slot(p, interaction.user.id)
        if k is None:
            return await interaction.response.send_message("No estás anotado.", ephemeral=True)
        del p["slots"][k]
        await refresh(interaction, self.pid)

    async def kick(self, interaction: discord.Interaction):
        p = db["pings"].get(self.pid)
        if not p:
            return await interaction.response.send_message("Este ping ya no está activo.", ephemeral=True)
        if not can_manage(interaction, p):
            return await interaction.response.send_message("❌ Solo quien convocó o el Staff puede hacer esto.", ephemeral=True)
        if not p["slots"]:
            return await interaction.response.send_message("Nadie está anotado todavía.", ephemeral=True)
        await interaction.response.send_message("¿A quién quieres expulsar?", view=KickView(self.pid, p), ephemeral=True)

    async def party2(self, interaction: discord.Interaction):
        p = db["pings"].get(self.pid)
        if not p:
            return await interaction.response.send_message("Este ping ya no está activo.", ephemeral=True)
        if not can_manage(interaction, p):
            return await interaction.response.send_message("❌ Solo quien convocó o el Staff puede hacer esto.", ephemeral=True)
        libres = size(p) - len(p["slots"])
        if libres > 0:
            return await interaction.response.send_message(
                f"La Party 1 aún tiene {libres} slot(s) libre(s).", ephemeral=True)
        p["parties"] = 2
        save()
        await interaction.response.edit_message(embed=build_embed(p), view=PingView(self.pid))

    async def cancel(self, interaction: discord.Interaction):
        p = db["pings"].get(self.pid)
        if not p:
            return await interaction.response.send_message("Este ping ya no está activo.", ephemeral=True)
        if not can_manage(interaction, p):
            return await interaction.response.send_message("❌ Solo quien convocó o el Staff puede hacer esto.", ephemeral=True)
        del db["pings"][self.pid]
        save()
        await interaction.response.edit_message(content=None, embed=build_embed(p, cancelled=True), view=None)

# ─────────────── VERIFICACIÓN THETFORD ───────────────
"""Verificación manual para un único servidor de Thetford."""

VERDE = 0x743FA2


def instalar(bot, db, save):
    db.setdefault('verification', {})
    db.setdefault('verification_dm', {})
    EJEMPLOS_DIR = DATA_DIR / 'ejemplos_thetford'

    def cfg(guild_id):
        return db['verification'].get(str(guild_id))

    def es_staff(member, config):
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild or any(r.id == config['staff_role'] for r in member.roles)

    async def enviar_solicitud(interaction, personaje, servidor, captura_personaje, captura_faccion, guild_id=None):
        gid = guild_id or interaction.guild_id
        guild = bot.get_guild(gid)
        config = cfg(gid)
        if not guild or not config:
            return await interaction.response.send_message('La verificación no está configurada.', ephemeral=True)
        try:
            member = guild.get_member(interaction.user.id) or await guild.fetch_member(interaction.user.id)
        except (discord.NotFound, discord.Forbidden):
            return await interaction.response.send_message('No puedo confirmar que estés en el servidor de Thetford.', ephemeral=True)
        role = guild.get_role(config['member_role'])
        if role and role in member.roles:
            return await interaction.response.send_message('Ya tienes el rol Thetfordiano.', ephemeral=True)
        pending = db['verification_pending'].setdefault(str(guild.id), {})
        uid = str(interaction.user.id)
        if uid in pending:
            return await interaction.response.send_message('Ya tienes una solicitud pendiente.', ephemeral=True)
        personaje, servidor = personaje.strip(), servidor.strip()
        if not 2 <= len(personaje) <= 60 or not 1 <= len(servidor) <= 30:
            return await interaction.response.send_message('Revisa el nombre del personaje o servidor.', ephemeral=True)
        for img in (captura_personaje, captura_faccion):
            if Path(img.filename).suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'} or not (img.content_type or '').startswith('image/'):
                return await interaction.response.send_message('Ambas capturas deben ser imágenes PNG, JPG o WEBP.', ephemeral=True)
            if img.size > 8 * 1024 * 1024:
                return await interaction.response.send_message('Cada captura debe pesar 8 MB o menos.', ephemeral=True)
        channel = guild.get_channel(config['staff_channel'])
        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message('No encuentro el canal privado del staff.', ephemeral=True)
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            raws = [await img.read() for img in (captura_personaje, captura_faccion)]
            if any(len(raw) > 8 * 1024 * 1024 for raw in raws):
                return await interaction.followup.send('Una captura supera los 8 MB.', ephemeral=True)
            nombres = ['personaje' + Path(captura_personaje.filename).suffix.lower(),
                       'faccion' + Path(captura_faccion.filename).suffix.lower()]
            embed = discord.Embed(
                title='🟢 Nueva solicitud · Thetford', color=VERDE,
                description=(f'**Discord:** {interaction.user.mention}\n'
                             f'**Personaje:** {discord.utils.escape_markdown(personaje)}\n'
                             f'**Servidor:** {discord.utils.escape_markdown(servidor)}\n'
                             '**Estado:** ⏳ Pendiente\n\n'
                             'Se adjuntan **dos capturas obligatorias**: personaje y facción.'))
            embed.set_image(url=f'attachment://{nombres[0]}')
            embed.set_footer(text=f'Usuario ID: {interaction.user.id}')
            files = [discord.File(io.BytesIO(raw), filename=nombre) for raw, nombre in zip(raws, nombres)]
            msg = await channel.send(embed=embed, files=files, view=DecisionView())
            pending[uid] = {'message_id': msg.id, 'channel_id': channel.id,
                            'personaje': personaje, 'servidor': servidor}
            save()
        except (discord.Forbidden, discord.HTTPException, OSError) as exc:
            return await interaction.followup.send(f'No pude guardar la solicitud. ({type(exc).__name__})', ephemeral=True)
        await interaction.followup.send('✅ Las dos capturas fueron enviadas al staff. Tu solicitud está pendiente de aprobación.', ephemeral=True)

    # En discord.py moderno FileUpload se coloca dentro de Label.
    # No recibe `label=` directamente.
    soporta_upload = hasattr(discord.ui, 'FileUpload') and hasattr(discord.ui, 'Label')
    if soporta_upload:
        class SolicitudModal(discord.ui.Modal, title='🟢 Verificación de Thetford'):
            personaje = discord.ui.TextInput(label='Personaje de Albion', min_length=2, max_length=60)
            servidor = discord.ui.TextInput(label='Servidor de Albion', default='Americas', max_length=30)

            def __init__(self, guild_id=None):
                super().__init__()
                self.guild_id = guild_id
                self.captura_personaje = discord.ui.FileUpload(required=True, min_values=1, max_values=1)
                self.captura_faccion = discord.ui.FileUpload(required=True, min_values=1, max_values=1)
                self.add_item(discord.ui.Label(text='Captura 1: nombre del personaje', component=self.captura_personaje))
                self.add_item(discord.ui.Label(text='Captura 2: facción Thetford', component=self.captura_faccion))

            async def on_submit(self, interaction: discord.Interaction):
                personaje_imgs = self.captura_personaje.values
                faccion_imgs = self.captura_faccion.values
                if not personaje_imgs or not faccion_imgs:
                    return await interaction.response.send_message('Debes adjuntar ambas capturas.', ephemeral=True)
                await enviar_solicitud(interaction, str(self.personaje.value), str(self.servidor.value),
                                      personaje_imgs[0], faccion_imgs[0], guild_id=self.guild_id)

    class ContinuarDMView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label='Continuar verificación', emoji='📸', style=discord.ButtonStyle.success, custom_id='thet:continuar_dm:v1')
        async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
            gid = db['verification_dm'].get(str(interaction.user.id))
            if not gid or not cfg(gid):
                return await interaction.response.send_message('Vuelve al servidor Thetford y pulsa Solicitar verificación.', ephemeral=True)
            if soporta_upload:
                await interaction.response.send_modal(SolicitudModal(guild_id=int(gid)))
            else:
                await interaction.response.send_message('Actualiza discord.py para cargar capturas desde el formulario.', ephemeral=True)

    class SolicitarView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label='Solicitar verificación', emoji='🟢', style=discord.ButtonStyle.success, custom_id='thet:solicitar:v1')
        async def solicitar(self, interaction: discord.Interaction, button: discord.ui.Button):
            gid = interaction.guild_id
            if not cfg(gid):
                return await interaction.response.send_message('La verificación no está configurada.', ephemeral=True)
            # Discord exige reconocer la interacción antes de 3 segundos.
            await interaction.response.defer(ephemeral=True, thinking=True)
            db['verification_dm'][str(interaction.user.id)] = gid
            try:
                save()
            except OSError:
                return await interaction.followup.send('No pude guardar la solicitud. Avisa al staff.', ephemeral=True)
            embed = discord.Embed(
                title='🟢 Verificación de Thetford', color=VERDE,
                description='¡Bienvenido! Mira las **dos capturas de ejemplo** y prepara **dos capturas**: una donde se vea tu personaje y otra donde se vea la facción Thetford.\n\nPulsa **Continuar verificación** para indicar tu personaje y adjuntar **las dos capturas obligatorias**. El staff revisará la solicitud antes de asignarte el rol.')
            archivos = []
            for i in (1, 2):
                matches = list(EJEMPLOS_DIR.glob(f'ejemplo_{i}.*'))
                if matches:
                    archivos.append(discord.File(matches[0], filename=matches[0].name))
            try:
                await interaction.user.send(embed=embed, files=archivos, view=ContinuarDMView())
            except discord.Forbidden:
                return await interaction.followup.send(
                    '❌ No pude enviarte un DM. Habilita los mensajes privados del servidor o usa `/solicitar_verificacion` para adjuntar tu captura.', ephemeral=True)
            except (discord.HTTPException, OSError) as exc:
                print(f'No se pudo enviar DM de verificación: {exc}')
                return await interaction.followup.send(
                    '❌ Hubo un problema enviando el DM. Intenta nuevamente o usa `/solicitar_verificacion`.', ephemeral=True)
            await interaction.followup.send('📩 ¡Te envié las instrucciones y ejemplos por mensaje privado! Revisa tus DM.', ephemeral=True)

    class DecisionView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        async def decidir(self, interaction, aprobar):
            config = cfg(interaction.guild_id)
            if not config or not isinstance(interaction.user, discord.Member) or not es_staff(interaction.user, config):
                return await interaction.response.send_message('Solo el staff autorizado puede decidir.', ephemeral=True)
            pending = db['verification_pending'].setdefault(str(interaction.guild_id), {})
            uid, entry = next(((uid, e) for uid, e in pending.items() if e['message_id'] == interaction.message.id and e['channel_id'] == interaction.channel_id), (None, None))
            if uid is None:
                return await interaction.response.send_message('Esta solicitud ya fue procesada o no está registrada.', ephemeral=True)
            member = interaction.guild.get_member(int(uid))
            if member is None:
                try:
                    member = await interaction.guild.fetch_member(int(uid))
                except (discord.NotFound, discord.Forbidden):
                    return await interaction.response.send_message('El usuario ya no está en el servidor o no puedo consultarlo.', ephemeral=True)
            if aprobar:
                role = interaction.guild.get_role(config['member_role'])
                if not role:
                    return await interaction.response.send_message('El rol Thetfordiano ya no existe.', ephemeral=True)
                try:
                    await member.add_roles(role, reason=f'Verificación aprobada por {interaction.user}')
                except discord.Forbidden:
                    return await interaction.response.send_message('No puedo asignar el rol. Revisa mi jerarquía y permisos.', ephemeral=True)
            # El nickname se cambia solo cuando el staff aprueba la solicitud.
            # El nombre se toma del registro original, no de lo que escriba el staff.
            nick_resultado = None
            if aprobar:
                nombre_albion = str(entry.get('personaje', '')).strip()
                if nombre_albion:
                    try:
                        await member.edit(nick=nombre_albion[:32], reason=f'Verificación Thetford aprobada por {interaction.user}')
                        nick_resultado = '✅ Apodo actualizado al personaje de Albion.'
                    except discord.Forbidden:
                        nick_resultado = '⚠️ Rol asignado, pero no pude cambiar el apodo. Revisa Manage Nicknames y la jerarquía del bot.'
                    except discord.HTTPException as exc:
                        nick_resultado = f'⚠️ Rol asignado, pero Discord rechazó el cambio de apodo ({exc.status}).'
                else:
                    nick_resultado = '⚠️ La solicitud no tiene un nombre de personaje guardado.'
            pending.pop(uid)
            save()
            embed = interaction.message.embeds[0].copy() if interaction.message.embeds else discord.Embed(title='Solicitud Thetford')
            embed.color = discord.Color.green() if aprobar else discord.Color.red()
            embed.add_field(name='Resolución', value=f"{'✅ Aprobada' if aprobar else '❌ Rechazada'} por {interaction.user.mention}", inline=False)
            if nick_resultado:
                embed.add_field(name='Apodo en Discord', value=nick_resultado, inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
            try:
                await member.send(f"{'✅ Tu verificación de Thetford fue aprobada.' if aprobar else '❌ Tu solicitud de verificación de Thetford fue rechazada.'}" + (f"\n{nick_resultado}" if nick_resultado else ''))
            except discord.Forbidden:
                pass

        @discord.ui.button(label='Aprobar', emoji='✅', style=discord.ButtonStyle.success, custom_id='thet:aprobar:v1')
        async def aprobar(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.decidir(interaction, True)

        @discord.ui.button(label='Rechazar', emoji='❌', style=discord.ButtonStyle.danger, custom_id='thet:rechazar:v1')
        async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.decidir(interaction, False)

    bot.add_view(SolicitarView())
    bot.add_view(ContinuarDMView())
    bot.add_view(DecisionView())
    db.setdefault('verification_pending', {})

    @bot.tree.command(name='solicitar_verificacion', description='Solicita acceso a Thetford con dos capturas obligatorias')
    @app_commands.guild_only()
    @app_commands.describe(personaje='Nombre de tu personaje de Albion', captura_personaje='Captura donde se vea el nombre del personaje', captura_faccion='Captura donde se vea la facción Thetford', servidor='Servidor de Albion')
    async def solicitar_verificacion(interaction: discord.Interaction, personaje: str, captura_personaje: discord.Attachment, captura_faccion: discord.Attachment, servidor: str = 'Americas'):
        await enviar_solicitud(interaction, personaje, servidor, captura_personaje, captura_faccion)

    @bot.tree.command(name='config_verificacion', description='Configura la verificación de Thetford sin crear canales')
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(canal_publico='Canal existente donde publicar el botón', canal_staff='Canal privado existente de solicitudes', rol_miembro='Rol existente que recibirá el aprobado', rol_staff='Rol existente autorizado para aprobar')
    async def config_verificacion(interaction: discord.Interaction, canal_publico: discord.TextChannel, canal_staff: discord.TextChannel, rol_miembro: discord.Role, rol_staff: discord.Role):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message('Necesitas Gestionar servidor.', ephemeral=True)
        if canal_publico.id == canal_staff.id:
            return await interaction.response.send_message('El canal público y el de staff deben ser diferentes.', ephemeral=True)
        if canal_staff.permissions_for(interaction.guild.default_role).view_channel:
            return await interaction.response.send_message('⚠️ El canal del staff es visible para @everyone. Hazlo privado primero.', ephemeral=True)
        me = interaction.guild.me
        if not me.guild_permissions.manage_roles or rol_miembro >= me.top_role:
            return await interaction.response.send_message('Necesito Gestionar roles y estar por encima del rol de miembro.', ephemeral=True)
        if not canal_publico.permissions_for(me).send_messages or not canal_staff.permissions_for(me).send_messages:
            return await interaction.response.send_message('Necesito poder escribir en ambos canales.', ephemeral=True)
        db['verification'][str(interaction.guild_id)] = {'public_channel': canal_publico.id, 'staff_channel': canal_staff.id, 'member_role': rol_miembro.id, 'staff_role': rol_staff.id}
        save()
        await interaction.response.send_message('✅ Configuración guardada. Usa `/publicar_verificacion` para publicar el panel.', ephemeral=True)

    @bot.tree.command(name='publicar_verificacion', description='Publica el panel de verificación con dos capturas de ejemplo')
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(ejemplo_1='Primera captura de ejemplo (adjuntar imagen)', ejemplo_2='Segunda captura de ejemplo (adjuntar imagen)')
    async def publicar_verificacion(interaction: discord.Interaction, ejemplo_1: discord.Attachment, ejemplo_2: discord.Attachment):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message('Necesitas Gestionar servidor.', ephemeral=True)
        config = cfg(interaction.guild_id)
        if not config:
            return await interaction.response.send_message('Primero usa `/config_verificacion`.', ephemeral=True)
        channel = interaction.guild.get_channel(config['public_channel'])
        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message('No encuentro el canal público configurado.', ephemeral=True)
        for img in (ejemplo_1, ejemplo_2):
            if not (img.content_type or '').startswith('image/') or Path(img.filename).suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
                return await interaction.response.send_message('Los dos ejemplos deben ser imágenes PNG, JPG o WEBP.', ephemeral=True)
            if img.size > 8 * 1024 * 1024:
                return await interaction.response.send_message('Cada ejemplo debe pesar 8 MB o menos.', ephemeral=True)
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            EJEMPLOS_DIR.mkdir(exist_ok=True)
            files = []
            for i, img in enumerate((ejemplo_1, ejemplo_2), start=1):
                raw = await img.read()
                if len(raw) > 8 * 1024 * 1024:
                    raise ValueError('Imagen demasiado grande')
                # Eliminar versiones anteriores de este ejemplo.
                for old_file in EJEMPLOS_DIR.glob(f'ejemplo_{i}.*'):
                    old_file.unlink()
                suffix = Path(img.filename).suffix.lower()
                path = EJEMPLOS_DIR / f'ejemplo_{i}{suffix}'
                path.write_bytes(raw)
                files.append(discord.File(io.BytesIO(raw), filename=path.name))
            embed = discord.Embed(
                title='🟢 VERIFICACIÓN DE THETFORD', color=VERDE,
                description='**¿Luchas por Thetford?** Verifica tu personaje para acceder a los canales de organización PvP.\n\n'
                            '**Cómo verificarte**\n'
                            '1️⃣ Pulsa el botón verde para recibir las dos capturas de ejemplo por DM.\n'
                            '2️⃣ En el DM pulsa **Continuar verificación**.\n'
                            '3️⃣ Escribe tu personaje y **adjunta dos capturas**: personaje y facción Thetford.\n'
                            '4️⃣ Espera la aprobación del staff.\n\n'
                            '🔒 El rol **Thetfordiano** se asigna solo tras la aprobación.')
            embed.set_footer(text='Thetford • Verificación manual de miembros')
            for f in files:
                f.close()
            await channel.send(embed=embed, view=SolicitarView())
        except (discord.Forbidden, discord.HTTPException, OSError, ValueError) as exc:
            return await interaction.followup.send(f'No pude publicar el panel. Revisa permisos y tamaño de imágenes. ({type(exc).__name__})', ephemeral=True)
        await interaction.followup.send(f'✅ Panel publicado; las dos imágenes se enviarán por DM en {channel.mention}.', ephemeral=True)


# ───────────────────────── BOT ─────────────────────────
intents = discord.Intents.default()

class MiBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        instalar(self, db, save)  # registrar paneles y comandos de verificación antes de sincronizar
        for pid in db["pings"]:  # reactivar botones de pings tras reiniciar
            self.add_view(PingView(pid), message_id=int(pid))
        await self.tree.sync()
        print("Comandos slash sincronizados.")

bot = MiBot()

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ───────────────────────── /crearcomp ─────────────────────────

# ─────────────── ASISTENTE DE CANALES DE THETFORD ───────────────
# Vista previa privada: NO crea nada hasta pulsar Confirmar.
PLANTILLA_CANALES = [
    ("💎 ─ [ ◈ ] INFORMACIÓN", [
        ("📩│bienvenida", "text", "public"),
        ("📜│reglas-y-normas", "text", "public"),
        ("🪪│como-verificar", "text", "public"),
        ("💎│verificacion-faccion", "text", "public"),
        ("📣│anuncios-oficiales", "text", "member"),
        ("🎫│tickets", "text", "public"),
    ]),
    ("💬 ─ [ ◈ ] COMUNIDAD", [
        ("💬│chat-general", "text", "member"),
        ("⚔️│pings-pvp", "text", "member"),
        ("📯│pings-pve", "text", "member"),
        ("🎬│clips-y-memes", "text", "member"),
        ("🎵│musica", "text", "member"),
        ("🛒│mercado", "text", "member"),
    ]),
    ("🎉 │ EVENTOS", [
        ("🎯│eventos", "text", "member"),
        ("🎁│sorteos-y-premios", "text", "member"),
        ("📋│composiciones", "text", "member"),
    ]),
    ("⚔️ │ BUILDS", [
        ("⚔️│builds-zvz", "text", "member"),
        ("🛠️│builds-pve", "text", "member"),
    ]),
    ("🔊 ─ [ ◈ ] VOZ", [
        ("🔊│voz-general", "voice", "member"),
        ("🟣│party-1", "voice", "member"),
        ("🟣│party-2", "voice", "member"),
        ("⚔️│cta", "voice", "member"),
    ]),
    ("🔒 ─ [ ⭐ ] ZONA EXCLUSIVA", [
        ("🛡️│solicitudes-verificacion", "text", "staff"),
        ("🔒│staff-chat", "text", "staff"),
        ("⭐│veteranos-chat", "text", "staff"),
        ("📯│callers", "text", "staff"),
    ]),
]

# Permisos seguros de servidor para roles administrados por la plantilla.
ROLES_PLANTILLA = [
    ("🟣 Thetford", discord.Colour.from_rgb(116, 68, 165)),
    ("🛡️ Staff", discord.Colour.from_rgb(195, 68, 68)),
    ("📯 Caller", discord.Colour.from_rgb(221, 156, 60)),
    ("⭐ Veterano", discord.Colour.from_rgb(76, 171, 150)),
    ("🤖 Bots", discord.Colour.from_rgb(112, 119, 129)),
]

def permisos_rol(nombre):
    # No se conceden Administrador, Gestionar roles ni Gestionar canales.
    p = discord.Permissions.none()
    p.update(view_channel=True, read_message_history=True,
             send_messages=True, send_messages_in_threads=True,
             add_reactions=True, embed_links=True, attach_files=True,
             use_external_emojis=True, use_external_stickers=True,
             use_application_commands=True, connect=True, speak=True,
             stream=True, use_voice_activation=True, use_embedded_activities=True)
    if nombre == "🛡️ Staff":
        p.update(manage_messages=True, moderate_members=True, kick_members=True,
                 manage_threads=True, move_members=True, mute_members=True,
                 deafen_members=True)
    elif nombre == "📯 Caller":
        p.update(move_members=True, mute_members=True)
    elif nombre == "🤖 Bots":
        # Los permisos especiales de cada bot se otorgan individualmente.
        p = discord.Permissions.none()
    return p

def permisos_plantilla(guild, roles, nivel):
    everyone = guild.default_role
    base = {everyone: discord.PermissionOverwrite(view_channel=(nivel == "public"))}
    miembro, staff = roles["🟣 Thetford"], roles["🛡️ Staff"]
    if nivel == "public":
        base[everyone] = discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=False, add_reactions=False)
    elif nivel == "member":
        base[miembro] = discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, use_external_emojis=True, use_external_stickers=True, send_messages_in_threads=True, create_public_threads=True, use_application_commands=True, connect=True, speak=True, stream=True, use_voice_activation=True, use_embedded_activities=True)
    elif nivel == "staff":
        base[staff] = discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, use_application_commands=True, connect=True, speak=True)
    # El staff también puede administrar y consultar canales públicos y de miembros.
    if nivel != "staff":
        base[staff] = discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, connect=True, speak=True, use_embedded_activities=True)
    return base

class ConfirmarCanalesView(discord.ui.View):
    def __init__(self, solicitante):
        super().__init__(timeout=180)
        self.solicitante = solicitante
        self.ejecutando = False

    @discord.ui.button(label="Confirmar roles y canales", style=discord.ButtonStyle.success, emoji="✅")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.solicitante or not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Solo el administrador que pidió la vista previa puede confirmar.", ephemeral=True)
        if self.ejecutando:
            return await interaction.response.send_message("Ya se está ejecutando.", ephemeral=True)
        guild = interaction.guild
        me = guild.me
        if not (me.guild_permissions.manage_channels and me.guild_permissions.manage_roles):
            return await interaction.response.send_message("El bot necesita Gestionar canales y Gestionar roles.", ephemeral=True)
        self.ejecutando = True
        for item in self.children: item.disabled = True
        await interaction.response.edit_message(content="⏳ Creando roles y canales que faltan…", view=self)
        creados, existentes, errores = [], [], []
        roles = {}
        for nombre, color in ROLES_PLANTILLA:
            role = discord.utils.get(guild.roles, name=nombre)
            if role is None:
                try:
                    role = await guild.create_role(name=nombre, colour=color, permissions=permisos_rol(nombre), reason=f"Plantilla Thetford confirmada por {interaction.user}")
                    creados.append(f"Rol: {nombre}")
                except (discord.Forbidden, discord.HTTPException) as exc:
                    errores.append(f"Rol {nombre}: {exc}")
                    continue
            else:
                existentes.append(f"Rol: {nombre}")
                try:
                    if role >= me.top_role:
                        errores.append(f"Rol {nombre}: está sobre el bot; no se pueden actualizar sus permisos")
                    else:
                        await role.edit(permissions=permisos_rol(nombre), reason=f"Permisos Thetford confirmados por {interaction.user}")
                except (discord.Forbidden, discord.HTTPException) as exc:
                    errores.append(f"Permisos del rol {nombre}: {exc}")
            roles[nombre] = role
        if "🟣 Thetford" not in roles or "🛡️ Staff" not in roles:
            return await interaction.edit_original_response(content="❌ No se pudo crear o encontrar Thetford y Staff. " + "; ".join(errores[:3]), view=None)
        # Orden de menor a mayor prioridad. Discord exige que el bot esté
        # por encima de cada rol que intenta mover.
        orden_bajo_a_alto = ["🤖 Bots", "🟣 Thetford", "⭐ Veterano", "📯 Caller", "🛡️ Staff"]
        movibles = [roles[n] for n in orden_bajo_a_alto if n in roles and roles[n] < me.top_role]
        for n in orden_bajo_a_alto:
            if n in roles and roles[n] >= me.top_role:
                errores.append(f"Jerarquía {n}: el rol está a la altura o por encima del bot")
        if movibles:
            try:
                # Colocarlos consecutivos justo debajo del rol más alto del bot.
                # No mueve el rol propio del bot ni toca roles superiores.
                inicio = max(1, me.top_role.position - len(movibles))
                await guild.edit_role_positions(
                    positions={rol: inicio + i for i, rol in enumerate(movibles)},
                    reason=f"Jerarquía Thetford confirmada por {interaction.user}"
                )
                existentes.append("Jerarquía: Staff > Caller > Veterano > Thetford > Bots")
            except (discord.Forbidden, discord.HTTPException, ValueError) as exc:
                errores.append(f"Orden de roles: {exc}")
        canales_encontrados = {}
        for nombre_cat, canales in PLANTILLA_CANALES:
            try:
                categoria = discord.utils.get(guild.categories, name=nombre_cat)
                if categoria is None:
                    categoria = await guild.create_category(name=nombre_cat, overwrites=permisos_plantilla(guild, roles, canales[0][2]), reason=f"Plantilla Thetford confirmada por {interaction.user}")
                    creados.append(f"Categoría: {nombre_cat}")
                else:
                    existentes.append(f"Categoría: {nombre_cat}")
                    # Se actualizan overwrites de la categoría sin eliminar permisos ajenos.
                    for objetivo, overwrite in permisos_plantilla(guild, roles, canales[0][2]).items():
                        await categoria.set_permissions(objetivo, overwrite=overwrite, reason="Sincronizar permisos Thetford")
            except (discord.Forbidden, discord.HTTPException) as exc:
                errores.append(f"Categoría {nombre_cat}: {exc}")
                continue
            for nombre, tipo, nivel in canales:
                encontrado = discord.utils.get(categoria.channels, name=nombre)
                if encontrado is not None:
                    existentes.append(f"{nombre_cat} / {nombre}")
                    canales_encontrados[nombre] = encontrado
                    try:
                        for objetivo, overwrite in permisos_plantilla(guild, roles, nivel).items():
                            await encontrado.set_permissions(objetivo, overwrite=overwrite, reason="Sincronizar permisos Thetford")
                    except (discord.Forbidden, discord.HTTPException) as exc:
                        errores.append(f"Permisos de {nombre}: {exc}")
                    continue
                try:
                    overwrites = permisos_plantilla(guild, roles, nivel)
                    if tipo == "voice":
                        canal = await guild.create_voice_channel(nombre, category=categoria, overwrites=overwrites, reason="Plantilla Thetford")
                    else:
                        canal = await guild.create_text_channel(nombre, category=categoria, overwrites=overwrites, reason="Plantilla Thetford")
                    canales_encontrados[nombre] = canal
                    creados.append(f"{nombre_cat} / {nombre}")
                except (discord.Forbidden, discord.HTTPException) as exc:
                    errores.append(f"{nombre}: {exc}")
        # Canales especializados: se aplica a canales recién creados; existentes quedan intactos.
        for nombre, rol_nombre in [("⭐│veteranos-chat", "⭐ Veterano"), ("📯│callers", "📯 Caller")]:
            canal = canales_encontrados.get(nombre)
            if canal and rol_nombre in roles:
                try:
                    await canal.set_permissions(roles[rol_nombre], view_channel=True, read_message_history=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, reason="Acceso especial Thetford")
                except (discord.Forbidden, discord.HTTPException) as exc:
                    errores.append(f"Permisos {nombre}: {exc}")
        publico = canales_encontrados.get("💎│verificacion-faccion")
        staff = canales_encontrados.get("🛡️│solicitudes-verificacion")
        if isinstance(publico, discord.TextChannel) and isinstance(staff, discord.TextChannel):
            db['verification'][str(guild.id)] = {'public_channel': publico.id, 'staff_channel': staff.id, 'member_role': roles['🟣 Thetford'].id, 'staff_role': roles['🛡️ Staff'].id}
            try: save()
            except OSError as exc: errores.append(f"Guardar configuración: {exc}")
        resultado = (f"🟣 **Configuración finalizada**\nCreados: **{len(creados)}** · Ya existentes: **{len(existentes)}** · Errores: **{len(errores)}**\n\n"
                     "Los roles y permisos de canales existentes se sincronizaron (sin borrar canales).\n"
                     "Para el panel de verificación usa `/publicar_verificacion` con las dos imágenes.")
        if errores: resultado += "\n\n⚠️ " + "\n".join(errores[:5])
        await interaction.edit_original_response(content=resultado[:1900], view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.solicitante:
            return await interaction.response.send_message("Esta vista previa no es tuya.", ephemeral=True)
        await interaction.response.edit_message(content="❌ Cancelado. No se creó ningún rol ni canal.", view=None)

@bot.tree.command(name="previsualizar_canales", description="Vista previa de roles y canales de Thetford; confirma antes de crear")
@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
async def previsualizar_canales(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Necesitas ser administrador.", ephemeral=True)
    if not (interaction.guild.me.guild_permissions.manage_channels and interaction.guild.me.guild_permissions.manage_roles):
        return await interaction.response.send_message("El bot necesita Gestionar canales y Gestionar roles.", ephemeral=True)
    guild = interaction.guild
    texto = ["🟣 **VISTA PREVIA — THETFORD**", "**No se creará nada hasta que confirmes.**", "", "**ROLES**"]
    for nombre, _ in ROLES_PLANTILLA:
        estado = "ya existe" if discord.utils.get(guild.roles, name=nombre) else "se creará"
        texto.append(f"• {nombre} — {estado}")
    texto.append("")
    for categoria, canales in PLANTILLA_CANALES:
        texto.append(f"**{categoria}**")
        for nombre, tipo, nivel in canales:
            texto.append(f"{'🔊' if tipo == 'voice' else '#'} {nombre} · {'público' if nivel == 'public' else 'Thetford' if nivel == 'member' else 'staff'}")
        texto.append("")
    texto.append("Jerarquía prevista (de arriba hacia abajo): Staff > Caller > Veterano > Thetford > Bots, debajo del bot. Se reordenarán los roles existentes administrables.")
    texto.append("Al confirmar se actualizarán permisos de los roles y canales de esta plantilla, incluso si ya existen. No se borrarán canales ni se concederá Administrador.")
    # Discord limita los mensajes a 2000 caracteres.
    contenido = "\n".join(texto)
    if len(contenido) > 1950:
        contenido = contenido[:1920] + "\n…"
    await interaction.response.send_message(contenido, view=ConfirmarCanalesView(interaction.user.id), ephemeral=True)

@bot.tree.command(name="crearcomp", description="Crea una composición (hasta 20 roles separados por ;)")
@app_commands.describe(
    nombre="Nombre de la composición",
    roles="Roles separados por ;  — para slots con opciones usa / (ej: Arcano/Arcano pesado)")
@app_commands.guild_only()
@app_commands.default_permissions(manage_messages=True)
async def crearcomp(interaction: discord.Interaction, nombre: str, roles: str):
    lista = parse_roles(roles)
    if not 1 <= len(lista) <= MAX_SLOTS:
        return await interaction.response.send_message(
            f"❌ Necesito entre 1 y {MAX_SLOTS} roles (recibí {len(lista)}).", ephemeral=True)
    comps = db["comps"].setdefault(str(interaction.guild_id), {})
    existia = nombre.lower() in comps
    comps[nombre.lower()] = {"name": nombre, "roles": lista}
    save()
    txt = "\n".join(f"`{i+1:>2}.` {r['name']}" for i, r in enumerate(lista))
    await interaction.response.send_message(
        f"✅ Composición **{nombre}** {'actualizada' if existia else 'creada'} ({len(lista)} slots):\n{txt}",
        ephemeral=True)

@bot.tree.command(name="vercomps", description="Lista las composiciones guardadas")
@app_commands.guild_only()
async def vercomps(interaction: discord.Interaction):
    comps = db["comps"].get(str(interaction.guild_id), {})
    if not comps:
        return await interaction.response.send_message("No hay composiciones. Crea una con /crearcomp.", ephemeral=True)
    txt = "\n".join(f"• **{c['name']}** — {len(c['roles'])} slots" for c in comps.values())
    await interaction.response.send_message(txt, ephemeral=True)

@bot.tree.command(name="borrarcomp", description="Borra una composición")
@app_commands.guild_only()
@app_commands.default_permissions(manage_messages=True)
async def borrarcomp(interaction: discord.Interaction, nombre: str):
    comps = db["comps"].get(str(interaction.guild_id), {})
    if comps.pop(nombre.lower(), None) is None:
        return await interaction.response.send_message("No encontré esa composición.", ephemeral=True)
    save()
    await interaction.response.send_message(f"🗑️ **{nombre}** borrada.", ephemeral=True)

async def comp_autocomplete(interaction: discord.Interaction, current: str):
    comps = db["comps"].get(str(interaction.guild_id), {})
    return [app_commands.Choice(name=c["name"], value=c["name"])
            for c in comps.values() if current.lower() in c["name"].lower()][:25]

borrarcomp.autocomplete("nombre")(comp_autocomplete)

# ───────────────────────── /lanzarping ─────────────────────────
@bot.tree.command(name="lanzarping", description="Lanza un ping de CTA")
@app_commands.describe(
    composicion="Composición a usar",
    hora='Hora UTC (ej: 21:00) o "ahora"',
    mencion="Mención de rol, @everyone o @here")
@app_commands.autocomplete(composicion=comp_autocomplete)
@app_commands.guild_only()
@app_commands.default_permissions(manage_messages=True)
async def lanzarping(interaction: discord.Interaction, composicion: str, hora: str, mencion: str):
    comp = db["comps"].get(str(interaction.guild_id), {}).get(composicion.lower())
    if not comp:
        return await interaction.response.send_message(
            "❌ Esa composición no existe. Créala con /crearcomp.", ephemeral=True)
    
    p = {
        "guild_id": interaction.guild_id, "channel_id": interaction.channel_id,
        "author_id": interaction.user.id, "comp": comp["name"], "roles": comp["roles"],
        "hora": format_hora(hora), "slots": {}, "parties": 1, "kicked": [],
    }
    
    texto_mencion = mencion.strip()
    
    await interaction.response.send_message(
        content=texto_mencion, 
        embed=build_embed(p),
        allowed_mentions=discord.AllowedMentions(everyone=True, roles=True)
    )
    msg = await interaction.original_response()
    pid = str(msg.id)
    db["pings"][pid] = p
    save()
    await msg.edit(view=PingView(pid))

# ───────────────────────── /anuncio ─────────────────────────
class ConfirmView(discord.ui.View):
    def __init__(self, canal, embed, mencion):
        super().__init__(timeout=300)
        self.canal, self.embed, self.mencion = canal, embed, mencion

    @discord.ui.button(label="Enviar", style=discord.ButtonStyle.success, emoji="✅")
    async def enviar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.canal.send(
                content=self.mencion if self.mencion else None, embed=self.embed,
                allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))
        except discord.Forbidden:
            return await interaction.response.edit_message(
                content=f"❌ No tengo permisos para escribir en {self.canal.mention}.", embed=None, view=None)
        await interaction.response.edit_message(content=f"✅ Anuncio enviado en {self.canal.mention}", embed=None, view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Anuncio cancelado.", embed=None, view=None)

class AnuncioModal(discord.ui.Modal, title="📢 Nuevo anuncio"):
    titulo = discord.ui.TextInput(label="Título", max_length=200, placeholder="📜 Reglas y Bienvenida")
    mensaje = discord.ui.TextInput(label="Mensaje", style=discord.TextStyle.paragraph, max_length=4000,
                                   placeholder="Admite **negrita**, *cursiva*, > cita, - listas")
    color = discord.ui.TextInput(label="Color (opcional)", required=False, max_length=7,
                                 placeholder="azul, rojo, verde, dorado, morado o #5865F2")
    imagen = discord.ui.TextInput(label="Imagen grande (URL, opcional)", required=False)
    pie = discord.ui.TextInput(label="Texto del pie (opcional)", required=False, max_length=200)

    def __init__(self, canal, mencion):
        super().__init__()
        self.canal, self.mencion = canal, mencion

    async def on_submit(self, interaction: discord.Interaction):
        e = discord.Embed(title=self.titulo.value, description=self.mensaje.value,
                          color=parse_color(self.color.value), timestamp=discord.utils.utcnow())
        if self.imagen.value.strip().startswith("http"):
            e.set_image(url=self.imagen.value.strip())
        if LOGO_URL:
            e.set_thumbnail(url=LOGO_URL)
        if self.pie.value:
            e.set_footer(text=self.pie.value)
        await interaction.response.send_message(
            f"👀 Vista previa — se enviará en {self.canal.mention}:", embed=e,
            view=ConfirmView(self.canal, e, self.mencion), ephemeral=True)

@bot.tree.command(name="anuncio", description="Envía un anuncio con formato")
@app_commands.describe(canal="Canal donde enviarlo (por defecto, este)", mencion="Mención de rol u @everyone (opcional)")
@app_commands.guild_only()
@app_commands.default_permissions(manage_messages=True)
async def anuncio(interaction: discord.Interaction, canal: discord.TextChannel = None,
                  mencion: str = None):
    await interaction.response.send_modal(AnuncioModal(canal or interaction.channel, mencion))

# ───────────────────────── RENDER / UPTIMEPING ─────────────────────────
web_app = Flask(__name__)

@web_app.get("/")
def healthcheck():
    return "Bot Thetford activo", 200

def iniciar_web():
    puerto = int(os.getenv("PORT", "8080"))
    web_app.run(host="0.0.0.0", port=puerto, use_reloader=False)

# ───────────────────────── RUN ─────────────────────────
if not TOKEN:
    raise SystemExit("Falta la variable de entorno DISCORD_TOKEN.")
Thread(target=iniciar_web, daemon=True).start()
bot.run(TOKEN)
