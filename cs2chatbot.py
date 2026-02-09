import os
from util.bot import Bot
import threading
import keyboard

def start_bot(bot):
    """Start the bot logic in a separate thread."""
    bot.run()  # Assuming you have a `run` method in the Bot class

if __name__ == "__main__":
    bot = Bot()

    # Start the bot logic in a separate thread
    bot_thread = threading.Thread(target=start_bot, args=(bot,))
    bot_thread.daemon = True  # Ensure the thread exits when the main program exits
    bot_thread.start()

    keyboard.wait()



