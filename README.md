# Bot de Soporte Técnico Nivel 1 – Telegram

Chatbot desarrollado en Python para la materia **Organización Empresarial** – TUP UTN.  
Automatiza el proceso de soporte técnico nivel 1 mediante una máquina de estados, consultando una base de datos CSV y registrando tickets.

---

## Tecnologías

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 20.7
- python-dotenv 1.0.0
- CSV (base de datos y registro de tickets)

---

## Estructura del proyecto

```
├── bot.py                   # Lógica principal del bot
├── base_datos.csv           # Base de conocimiento (categorías, palabras clave, soluciones)
├── tickets_registrados.csv  # Generado automáticamente al recibir consultas
├── requirements.txt
├── .env                     # Token de Telegram (no incluido en el repositorio)
└── README.md
```

---

## Configuración

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repo>
   cd <nombre-del-repo>
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Crear el archivo `.env` en la raíz del proyecto:
   ```
   TOKEN=tu_token_de_telegram
   ```
   El token se obtiene hablando con [@BotFather](https://t.me/BotFather) en Telegram.

4. Ejecutar el bot:
   ```bash
   python bot.py
   ```

---

## Uso

| Paso | Acción del usuario |
|------|--------------------|
| 1 | Escribir `/start` para iniciar |
| 2 | Ingresar nombre |
| 3 | Seleccionar categoría del problema: `red`, `pc`, `impresora` o `software` |
| 4 | Describir el problema |
| 5 | Recibir solución automática o escalado a técnico |
| 6 | Confirmar si el problema fue resuelto |

---

## Base de conocimiento

El archivo `base_datos.csv` contiene 12 problemas técnicos organizados en 4 categorías.  
El bot busca coincidencias entre las palabras clave del CSV y la descripción del usuario.

Para agregar nuevos casos, editar `base_datos.csv` respetando el formato:

```
id,categoria,palabras_clave,problema,solucion
```

---

## Autores

- Santiago Gonzalez
- Lucas Claveri
