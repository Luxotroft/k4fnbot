# Bot de facción Thetford 🟣

Bot independiente del servidor Lymhurst. Incluye pings, composiciones, anuncios, verificación con dos capturas, DM con ejemplos, aprobación del staff y cambio de apodo al personaje de Albion.

## Instalación
1. Crea una **aplicación/bot de Discord diferente** para Thetford. Invítala al nuevo servidor con scopes `bot` y `applications.commands`, y permisos para gestionar roles y apodos, enviar mensajes, adjuntar archivos y ver canales.
2. En un repositorio GitHub **distinto al de Lymhurst**, sube `main.py`, `requirements.txt`, `.gitignore`. Nunca subas `.env` ni tokens.
3. Crea un servicio **separado** en Render (Web Service si vas a usar Flask/UptimePing). Build: `pip install -r requirements.txt`. Start: `python main.py`. Variable de entorno: `DISCORD_TOKEN` = token del bot de Thetford.
4. Configura `/config_verificacion` con el canal público, canal privado de staff, rol de miembro y rol de staff. Publica con `/publicar_verificacion` y adjunta **dos imágenes de referencia**.
5. La aprobación del staff asigna el rol y cambia el apodo al nombre de Albion (si el bot tiene `Manage Nicknames` y jerarquía suficiente).

**Aviso sobre Render gratuito:** `data.json` y las imágenes locales se perderán al reiniciar o redesplegar si no hay almacenamiento persistente. Para producción estable, usa una base de datos/almacenamiento externo. El ping HTTP no garantiza 24/7 ni persistencia.

**Permisos de comandos:** `/crearcomp`, `/borrarcomp`, `/lanzarping` y `/anuncio` requieren por defecto `Gestionar mensajes`; la verificación administrativa requiere `Gestionar servidor`. Ajusta los permisos de comandos en Discord o cambia las restricciones en el código según tus roles.
