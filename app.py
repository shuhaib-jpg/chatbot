import os
import sys
import traceback
from aiohttp import web

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity, ActivityTypes

# =========================================================
# CONFIGURATION (ENV VARIABLES)
# =========================================================

APP_ID = os.getenv("MicrosoftAppId", "")
APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
APP_TENANT_ID = os.getenv("MicrosoftAppTenantId", "")  # Add this line
PORT = int(os.getenv("PORT", 8000))

# =========================================================
# ADAPTER SETUP
# =========================================================

settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD,
    tenant_id=APP_TENANT_ID
)

adapter = BotFrameworkAdapter(settings)

# =========================================================
# ERROR HANDLER
# =========================================================

async def on_error(context: TurnContext, error: Exception):
    print("❌ [on_turn_error]", error, file=sys.stderr)
    traceback.print_exc()

    await context.send_activity(
        "Sorry 😕, something went wrong on the bot."
    )

adapter.on_turn_error = on_error

# =========================================================
# BOT LOGIC
# =========================================================

async def on_message_activity(turn_context: TurnContext):
    user_message = (turn_context.activity.text or "").lower()

    print(f"📩 User message: {user_message}")

    if "hello" in user_message or "hi" in user_message:
        response = "Hello! 👋 How can I help you today?"
    elif "help" in user_message:
        response = (
            "I'm here to help 🤖\n\n"
            "Try typing:\n"
            "- hello\n"
            "- name\n"
            "- bye"
        )
    elif "name" in user_message:
        response = "I'm your Microsoft Teams Chatbot 🤖"
    elif "bye" in user_message:
        response = "Goodbye! 👋 Have a great day!"
    else:
        response = f"You said: '{turn_context.activity.text}'"

    await turn_context.send_activity(response)


async def bot_logic(turn_context: TurnContext):
    if turn_context.activity.type == ActivityTypes.message:
        await on_message_activity(turn_context)

    elif turn_context.activity.type == ActivityTypes.conversation_update:
        if turn_context.activity.members_added:
            for member in turn_context.activity.members_added:
                if member.id != turn_context.activity.recipient.id:
                    await turn_context.send_activity(
                        "Welcome! 👋 Type `help` to get started."
                    )

# =========================================================
# HTTP ENDPOINT
# =========================================================

async def messages(req: web.Request) -> web.Response:
    print("🔔 Incoming request: /api/messages")

    if "application/json" not in req.headers.get("Content-Type", ""):
        return web.Response(
            status=415,
            text="Content-Type must be application/json"
        )

    try:
        body = await req.json()
    except Exception:
        return web.Response(status=400, text="Invalid JSON")

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    try:
        await adapter.process_activity(activity, auth_header, bot_logic)
        return web.Response(status=200)
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=str(e))


async def health(req: web.Request) -> web.Response:
    return web.Response(text="🤖 Bot is running!", status=200)

# =========================================================
# APP STARTUP
# =========================================================

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/", health)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Teams Chatbot")
    print(f"🌐 Listening on port {PORT}")
    print("📨 Endpoint: /api/messages")
    print("🔐 Authentication:", "ENABLED" if APP_ID else "DISABLED (local)")
    print("=" * 60)

    web.run_app(app, host="0.0.0.0", port=PORT)
