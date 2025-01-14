import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Replace sensitive values with environment variables for better security
ADMIN_ID = int(os.getenv("ADMIN_ID", "6706065410"))  # Replace with your admin's Telegram user ID
BOT_TOKEN = os.getenv("BOT_TOKEN", "7435981514:AAGWQuRTtGOsPMGbb-w5EgIjg3rdjBk_8mE")  # Replace with your bot token

# Store user data
user_data = {}

# Define stages in the conversation
ASK_NAME = range(1)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id == ADMIN_ID:
        await update.message.reply_text("Hello Admin! You are ready to validate requests.")
    else:
        await update.message.reply_text(
            "Welcome! Please provide your name to proceed."
        )
        return ASK_NAME
    return ConversationHandler.END

# Handle name input
async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    name = update.message.text
    context.user_data["name"] = name
    user_data[user_id] = name  # Store the user ID and name

    # Forward the name to the admin
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"User requested: {name} (User ID: {user_id})")
    
    await update.message.reply_text("Searching the database please wait...")
    return ConversationHandler.END

# Admin sends a message to a user
async def send_message_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != ADMIN_ID:
        await update.message.reply_text("Access denied. Only the admin can use this command.")
        return

    try:
        user_id = int(context.args[0])  # Get user ID from command arguments
        message = ' '.join(context.args[1:])  # Get the message to send
        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text(f"Message sent to User ID: {user_id}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /send <user_id> <message>")

# Fallback function for unknown messages
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")

# Main function to start the bot
def main():
    # Initialize the application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Define conversation handler for user interaction
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        },
        fallbacks=[MessageHandler(filters.ALL, fallback)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("send", send_message_to_user))  # Admin command to send messages

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()