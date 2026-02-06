from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
import requests
import ipaddress
import os
import subprocess
import threading

TOKEN = os.getenv("BOT_TOKEN")

# Stati della conversazione
MENU, ASK_INPUT = range(2)

# MODULO IP LOOKUP
async def ip_lookup_core(ip: str) -> str:
    # Validazione IP
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return "IP non valido."

    # Chiamata API
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = r.json()
    except Exception:
        return "Errore durante la richiesta all'API."

    # Output formattato
    msg = (
        f"🔍 **RISULTATI IP LOOKUP**\n\n"
        f"• IP: {data.get('ip', 'N/D')}\n"
        f"• Città: {data.get('city', 'N/D')}\n"
        f"• Regione: {data.get('region', 'N/D')}\n"
        f"• Nazione: {data.get('country', 'N/D')}\n"
        f"• Provider: {data.get('org', 'N/D')}\n"
        f"• Posizione: {data.get('loc', 'N/D')}\n"
    )

    return msg

# MODULO SHERLOCK
def run_sherlock(username, callback):
    def task():
        try:
            result = subprocess.run(
                ["python", "-m", "sherlock", username, "--print-found"],
                capture_output=True,
                text=True
            )
            output = result.stdout if result.stdout else "Nessun risultato trovato."
        except Exception as e:
            output = f"Errore durante l'esecuzione di Sherlock: {e}"

        callback(output)

    thread = threading.Thread(target=task)
    thread.start()

# COMANDI BASE
async def start(update, context):
    await update.message.reply_text(
        "Bot OSINT avviato!\n"
        "Scrivi /help per vedere i comandi."
    )

async def help_cmd(update, context):
    await update.message.reply_text(
        "Comandi disponibili:\n"
        "/ip <indirizzo IP>\n"
        "/menu (menu interattivo)\n"
        "/help"
    )

async def ip_lookup(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Usa: /ip 8.8.8.8")
        return

    ip = context.args[0]
    msg = await ip_lookup_core(ip)
    await update.message.reply_text(msg, parse_mode="Markdown")

# MENU INTERATTIVO
async def menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Ricerca IP", callback_data="ip")],
        [InlineKeyboardButton("Username Scan", callback_data="username")],
        [InlineKeyboardButton("Email Scan", callback_data="email")],
        [InlineKeyboardButton("Dominio / DNS", callback_data="dns")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Scegli un'operazione OSINT:", reply_markup=reply_markup)
    return MENU

async def menu_choice(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data["choice"] = query.data

    if query.data == "ip":
        await query.edit_message_text("Inserisci l'indirizzo IP:")
    elif query.data == "username":
        await query.edit_message_text("Inserisci lo username da cercare:")
    elif query.data == "email":
        await query.edit_message_text("Inserisci l'email:")
    elif query.data == "dns":
        await query.edit_message_text("Inserisci il dominio:")

    return ASK_INPUT

async def process_input(update, context):
    choice = context.user_data.get("choice")
    user_input = update.message.text

    if choice == "ip":
        msg = await ip_lookup_core(user_input)
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif choice == "username":
        await update.message.reply_text(f"Avvio ricerca Sherlock per: {user_input}")

        def send_result(output):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"**Risultati Sherlock per {user_input}:**\n\n{output}",
                parse_mode="Markdown"
            )

        run_sherlock(user_input, send_result)

    elif choice == "email":
        await update.message.reply_text(f"Sto analizzando email: {user_input}\n(qui colleghi Holehe)")

    elif choice == "dns":
        await update.message.reply_text(f"Sto analizzando dominio: {user_input}\n(qui farai DNS lookup)")

    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Operazione annullata.")
    return ConversationHandler.END

# AVVIO BOT

app = Application.builder().token(TOKEN).build()

# Handlers base
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("ip", ip_lookup))

# Handler menu interattivo
conv = ConversationHandler(
    entry_points=[CommandHandler("menu", menu)],
    states={
        MENU: [CallbackQueryHandler(menu_choice)],
        ASK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_input)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv)
app.run_polling()