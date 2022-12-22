import logging
import pandas as pd
from telegram.ext import Updater, CommandHandler
import os
import sys
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define command handlers
def start(update, context):
    update.message.reply_text('Hi! \nUse /set <YYYY-MM-DD> <REMINDER> to add a reminder, '
                              '/view to view all reminders, and /delete <index> to delete a reminder')

def set_reminder(update, context):
    # Extract the date and reminder from the user input
    reminder_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(.+)")
    reminder_match = reminder_pattern.search(update.message.text)

    if reminder_match:
        date = reminder_match.group(1)
        reminder = reminder_match.group(2)
    else:
        update.message.reply_text("Invalid reminder format. Please use /set <YYYY-MM-DD> <REMINDER>.")
        return

    # Read the Excel file
    df = pd.read_excel("reminders.xlsx")

    # Append the new reminder to the DataFrame
    df = pd.concat([df, pd.DataFrame.from_records([{"date": date, "reminder": reminder}])])

    # Save the updated DataFrame to the Excel file
    df.to_excel("reminders.xlsx", index=False)

    # Confirm the reminder has been set
    update.message.reply_text("Reminder set.")


def show_all_reminders(update, context):
    """Show all reminders."""
    # Read the Excel file
    df = pd.read_excel("reminders.xlsx")

    # Convert the DataFrame to a dictionary
    reminders = df.to_dict(orient="records")
    if not reminders:
        update.message.reply_text("No reminders.")
        return

    # Build the message
    message = "Reminders:\n"
    for i, reminder in enumerate(reminders):
        message += "{}: {} ({})\n".format(i, reminder["reminder"], reminder["date"])

    # Send the message
    update.message.reply_text(message)

def delete_reminder(update, context):
    # Extract the index of the reminder to delete
    index_pattern = re.compile(r"\d+")
    index_match = index_pattern.search(update.message.text)

    if index_match:
        index = int(index_match.group())
    else:
        update.message.reply_text("Invalid index format. Please enter a valid index.")
        return

    # Read the Excel file
    df = pd.read_excel("reminders.xlsx")

    # Check if the index is valid
    if index >= len(df):
        update.message.reply_text("Invalid index. Please enter a valid index.")
        return

    # Delete the reminder
    df = df.drop(index)

    # Save the updated DataFrame to the Excel file
    df.to_excel("reminders.xlsx", index=False)

    # Confirm the reminder has been deleted
    update.message.reply_text("Reminder deleted.")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    if not os.path.exists("reminders.xlsx"):
        pd.DataFrame(columns=["date", "reminder"]).to_excel("reminders.xlsx", index=False)

    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_reminder))
    dp.add_handler(CommandHandler("view", show_all_reminders))
    dp.add_handler(CommandHandler("delete", delete_reminder))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
