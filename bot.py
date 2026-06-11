
#Materia: Organización Empresarial - TUP UTN

import os
from dotenv import load_dotenv
import csv
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
load_dotenv()
TOKEN = os.getenv("TOKEN") # Reemplazá el token obtenido de @BotFather
ARCHIVO_CSV = "base_datos.csv"

# Categorías disponibles 
CATEGORIAS = ["red", "pc", "impresora", "software"]

# ─── LOGGING (para ver errores en consola) ────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ─── FUNCIONES DE BASE DE DATOS ───────────────────────────────────────────────

def buscar_solucion(categoria: str, descripcion: str) -> str | None:

    descripcion = descripcion.lower()

    with open(ARCHIVO_CSV, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            # Filtramos primero por categoría
            if fila["categoria"] != categoria:
                continue
            # Buscamos si alguna palabra clave aparece en la descripción
            palabras = fila["palabras_clave"].split()
            for palabra in palabras:
                if palabra in descripcion:
                    return fila["solucion"]

    return None  


def registrar_ticket(nombre: str, categoria: str, problema: str, resultado: str):

    with open("tickets_registrados.csv", "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([nombre, categoria, problema, resultado])


# ─── (funciones que responden a mensajes) ────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Limpiamos cualquier estado anterior del usuario
    context.user_data.clear()
    context.user_data["estado"] = "esperando_nombre"

    await update.message.reply_text(
        "👋 ¡Bienvenido al sistema de Soporte Técnico Nivel 1!\n\n"
        "Estoy aquí para ayudarte a resolver problemas técnicos.\n\n"
        "¿Cuál es tu nombre?"
    )


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text.strip()
    estado = context.user_data.get("estado", None)

    # ── Si el usuario escribe sin haber iniciado con /start ──────────────────
    if estado is None:
        await update.message.reply_text(
            "Bienvenido a SL, para comenzar escribí el comando /start 😊"
        )
        return

    # ── ESTADO 1: Esperando nombre ───────────────────────────────────────────
    if estado == "esperando_nombre":

        # Camino infeliz: nombre vacío o con números
        if not texto.replace(" ", "").isalpha():
            await update.message.reply_text(
                "⚠️ El nombre solo debe contener letras. Intentá de nuevo:"
            )
            return

        # Guardamos el nombre y avanzamos
        context.user_data["nombre"] = texto
        context.user_data["estado"] = "esperando_categoria"

        # Mostramos teclado con categorías
        teclado = ReplyKeyboardMarkup(
            [CATEGORIAS[:2], CATEGORIAS[2:]],  # dos filas de dos botones
            one_time_keyboard=True,
            resize_keyboard=True
        )

        await update.message.reply_text(
            f"¡Hola {texto}! 😊\n\n"
            "Seleccioná la categoría de tu problema:",
            reply_markup=teclado
        )

    # ── ESTADO 2: Esperando categoría ────────────────────────────────────────
    elif estado == "esperando_categoria":

        categoria = texto.lower()

        # Camino infeliz: categoría no válida
        if categoria not in CATEGORIAS:
            teclado = ReplyKeyboardMarkup(
                [CATEGORIAS[:2], CATEGORIAS[2:]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
            await update.message.reply_text(
                "⚠️ Por favor elegí una de las opciones del teclado:",
                reply_markup=teclado
            )
            return

        # Guardamos categoría y avanzamos
        context.user_data["categoria"] = categoria
        context.user_data["estado"] = "esperando_problema"

        await update.message.reply_text(
            f"Entendido, categoría: *{categoria.upper()}* 🔧\n\n"
            "Describí tu problema con el mayor detalle posible:",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )

    # ── ESTADO 3: Esperando descripción del problema ─────────────────────────
    elif estado == "esperando_problema":

        # Camino infeliz: descripción muy corta
        if len(texto) < 5:
            await update.message.reply_text(
                "⚠️ La descripción es muy corta. "
                "Por favor describí el problema con más detalle:"
            )
            return

        context.user_data["problema"] = texto
        categoria = context.user_data["categoria"]

        await update.message.reply_text("🔍 Buscando solución en nuestra base de datos...")

        # ── GATEWAY 1: ¿Existe solución? ─────────────────────────────────────
        solucion = buscar_solucion(categoria, texto)

        if solucion:
            # SÍ hay solución → la enviamos y preguntamos si se resolvió
            context.user_data["solucion"] = solucion
            context.user_data["estado"] = "esperando_confirmacion"

            teclado = ReplyKeyboardMarkup(
                [["si", "no"]],
                one_time_keyboard=True,
                resize_keyboard=True
            )

            await update.message.reply_text(
                f"✅ Encontré una posible solución:\n\n"
                f"_{solucion}_\n\n"
                "¿Se resolvió tu problema?",
                reply_markup=teclado,
                parse_mode="Markdown"
            )

        else:
            # NO hay solución → escalamos directamente
            nombre = context.user_data["nombre"]
            registrar_ticket(nombre, categoria, texto, "escalado_sin_solucion")
            context.user_data["estado"] = None

            await update.message.reply_text(
                "😔 No encontré una solución automática para tu problema.\n\n"
                "📋 *Tu caso fue escalado a un técnico especialista.*\n"
                f"Te contactaremos a la brevedad, {nombre}.\n\n"
                "Número de ticket registrado ✓\n\n"
                "Escribí /start para iniciar una nueva consulta.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown"
            )

    # ── ESTADO 4: Esperando confirmación (¿se resolvió?) ─────────────────────
    elif estado == "esperando_confirmacion":

        respuesta = texto.lower()

        # Camino infeliz: respuesta no válida
        if respuesta not in ["si", "sí", "no"]:
            teclado = ReplyKeyboardMarkup(
                [["si", "no"]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
            await update.message.reply_text(
                "⚠️ Por favor respondé solo *si* o *no*:",
                reply_markup=teclado,
                parse_mode="Markdown"
            )
            return

        nombre = context.user_data["nombre"]
        categoria = context.user_data["categoria"]
        problema = context.user_data["problema"]

        # ── GATEWAY 2: ¿Se resolvió? ─────────────────────────────────────────
        if respuesta in ["si", "sí"]:
            # SÍ se resolvió → cerramos el ticket exitosamente
            registrar_ticket(nombre, categoria, problema, "resuelto")
            context.user_data["estado"] = None

            await update.message.reply_text(
                f"🎉 ¡Excelente, {nombre}! Me alegra que se haya resuelto.\n\n"
                "Tu consulta fue cerrada exitosamente ✓\n\n"
                "Escribí /start para iniciar una nueva consulta.",
                reply_markup=ReplyKeyboardRemove()
            )

        else:
            # NO se resolvió → escalamos a técnico humano
            registrar_ticket(nombre, categoria, problema, "escalado_no_resuelto")
            context.user_data["estado"] = None

            await update.message.reply_text(
                f"Entendido, {nombre}. Lamentamos que no se haya resuelto.\n\n"
                "📋 *Tu caso fue escalado a un técnico especialista.*\n"
                "Te contactaremos a la brevedad.\n\n"
                "Número de ticket registrado ✓\n\n"
                "Escribí /start para iniciar una nueva consulta.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown"
            )


# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

def main():
    # Creamos la aplicación con el token
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))

    print("🤖 Bot iniciado. Esperando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    main()