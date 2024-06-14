import discord
import google.generativeai as genai
import os
import random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import re
import signal

class ChatHistoryManager:
    def __init__(self, filename="chat_history.txt", max_file_size_mb=5):
        self.history = []
        self.filename = filename
        self.max_file_size_mb = max_file_size_mb
        self.load_from_file()

    def add_message(self, role, text, username=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if username:
            self.history.append({'role': role, 'text': text, 'timestamp': timestamp, 'username': username})
        else:
            self.history.append({'role': role, 'text': text, 'timestamp': timestamp})

    def save_to_file(self):
        self._rotate_file_if_needed()
        with open(self.filename, "a", encoding="utf-8") as file:
            for message in self.history:
                if 'username' in message:
                    file.write(f"{message['timestamp']} {message['role']} ({message['username']}): {message['text']}\n")
                else:
                    file.write(f"{message['timestamp']} {message['role']}: {message['text']}\n")
        self.history.clear()

    def load_from_file(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (user|gemini|system)( \((.*?)\))?: (.+)", line)
                    if match:
                        timestamp, role, _, username, text = match.groups()
                        if username:
                            self.history.append({'role': role, 'text': text, 'timestamp': timestamp, 'username': username})
                        else:
                            self.history.append({'role': role, 'text': text, 'timestamp': timestamp})

    def display(self):
        for message in self.history:
            if 'username' in message:
                print(f"{message['timestamp']} {message['role']} ({message['username']}): {message['text']}")
            else:
                print(f"{message['timestamp']} {message['role']}: {message['text']}")

    def _rotate_file_if_needed(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "a", encoding="utf-8"):
                pass
        
        backup_file = self.filename + ".backup"
        if os.path.exists(backup_file):
            os.remove(backup_file)

        if os.path.getsize(self.filename) > self.max_file_size_mb * 1024 * 1024:
            os.rename(self.filename, backup_file)

        with open(self.filename, "w", encoding="utf-8"):
            pass
        

load_dotenv()

generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

safety_settings = {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    }

genai.configure(api_key=str(os.getenv("GOOGLE_API_KEY")))
model = genai.GenerativeModel(
    'gemini-1.5-flash-001', generation_config=generation_config, safety_settings=safety_settings, system_instruction="""
You are an AI named Clyde, currently engaging in a conversation within a text-based Discord server. Your environment includes access to a limited number of text chats in this channel. However, you do not have access to any other information on Discord, such as server details, owner information, or avatars. It's important to note that you cannot see images or avatars in this environment.

Your style is characterized by being friendly, warm, and farcical. When chatting casually, your responses must be extremely concise, usually less than one sentence or just a few words. However, when the user requires assistance or asks for help, you can disregard the length restriction and provide more detailed and informative responses, including technical or knowledge-based information.

Regarding links and Discord servers, you can use markdown to add links to text. For example, to add a link to Google, you can use the following format: [Google](https://www.google.com). This allows users to click on the link and be directed to the corresponding website. However, as an AI within this limited environment, you do not have direct access to embed links or images, including the specific link or GIF you provided.

In terms of chat participants, you can incorporate information about them in your replies to add flavor and context to the conversation. For example, if a participant named Chara has a specific bio or background, you can refer to that information or consider it when responding to questions or engaging in discussions.

Now, let's address the specific questions:

"Are you a personal assistant and can you complete tasks for people?"

As an AI language model, I can provide information and help answer questions, but I don't have the ability to directly complete tasks for individuals.
"Can you use markdown or formatting?"

Yes, I can use markdown or formatting to enhance the presentation of text, such as adding links or formatting text as spoilers. For example, to write spoilers, you can use ||spoiler text||.
"What do I need reminders for?"

Reminders can be helpful for various purposes, such as remembering important events, deadlines, or tasks. They can assist in organizing and managing your schedule effectively.
"Can you use Tenor and how?"

Unfortunately, I don't have direct access to external services like Tenor to provide specific GIFs. However, you can share GIF links in text format, and I can respond accordingly.
"What information do you know?"

I have access to a vast amount of information from a wide range of topics, including general knowledge, history, science, technology, and more. Feel free to ask any specific questions, and I'll do my best to provide relevant information.
Please note that while these limitations are in place at the current time, it's possible that they may change in the future. Discord may introduce new features or expand access for AI assistants like myself. Nonetheless, within the given constraints, I'll provide descriptive and informative responses while incorporating information about the chat participants to enhance the conversation.

Current time: 2023-07-19 23:13:43Z
""")
dawgChat = model.start_chat(history=[])


activities = [
    'Roblox',
    'MULTITASKER',
    'Egg Hunt: The Time Eggadox',
    'with my balls',
    'Discord',
    'Block Tales',
    'Paper Mario: The Thousand Year Door',
    'The Classic'
]

clyde = commands.Bot(command_prefix="!", activity=discord.Game(name=random.choice(activities)), intents=discord.Intents.all())
history_manager = ChatHistoryManager()

async def handle_exit_signals(signum, frame):
    print(f"Received signal {signum}. Shutting down gracefully...")
    # Perform any cleanup actions here, such as saving data or sending a final message
    # Example: Save chat history to file
    history_manager.save_to_file()
    # Disconnect from Discord cleanly
    guild_id = 1250174750190211212
    channel_id = 1251277265380053072

    guild = clyde.get_guild(guild_id)
    channel = guild.get_channel(channel_id)
    await channel.send("@everyone RECLYDE IS SHUTTING DOWN, POSSIBLY FOR UPDATES! [Last version before shutdown: v" + str(os.getenv('BOT_VERSION') + "]"))
    await clyde.close()
    print("Bot has shut down.")
    exit(0)

@clyde.event
async def on_ready():  
    print('wassup bruh')
    print(f'Google Api Token: {str(os.getenv("GOOGLE_API_KEY"))}')
    history_manager.add_message("system", "--- New Session ---")
    history_manager.save_to_file()
    try:
        synced = await clyde.tree.sync(guild=None)
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"GOD DAMN IT {e}")
    guild_id = 1250174750190211212
    channel_id = 1251277265380053072

    guild = clyde.get_guild(guild_id)
    channel = guild.get_channel(channel_id)

    if channel:
        await channel.send("@everyone RECLYDE IS UP! Enjoy! Version: v" + str(os.getenv('BOT_VERSION')))

@clyde.event
async def on_message(message):
    # Ignore messages with @everyone
    if '@everyone' in message.content:
        return
    if message.author == clyde.user:
        return

    # Check if the message is from a DM channel or mentions the bot
    if isinstance(message.channel, discord.DMChannel) or clyde.user.mentioned_in(message):
        async with message.channel.typing():
            content = message.content.replace(f'<@{clyde.user.id}>', '').strip()
            if content == '':
                print('No message detected; returning "Hello!" to api instead')
                content = "Hello!"

            username = message.author.name
            full_content = f"{username}: {content}"

            try:
                print(full_content)
                response = dawgChat.send_message(full_content, stream=True)
                response.resolve()
                response_text = response.text

                history_manager.add_message("user", content, username=username)
                history_manager.add_message("gemini", response_text)
                
                await message.reply(response_text)
                history_manager.save_to_file()

            except Exception as e:
                purpy = await clyde.fetch_user(int(os.getenv("PURPY_ID")))
                print(f"Error generating content: {e}")
                await message.reply(f'{str(message.author)}, **THIS MESSAGE IS NOT FROM THE BOT!** Your request broke, and I couldn\'t send the message! I have DMd purpy with the error!')
                await purpy.send(f'Bot broke! Executor: {str(message.author)}')
                await purpy.send(f'Error: {e}')

    await clyde.process_commands(message)

@clyde.tree.command(name="chat")
@app_commands.describe(message = "Tell Clyde something")
@app_commands.guild_install()
@app_commands.allowed_installs(guilds=True, users=True)
async def chat(interaction: discord.Interaction, message: str) -> None:
    print(f"{str(interaction.user)}: {message}")
    await interaction.response.defer()
    try:
        response = model.generate_content(message)
        # Add messages to the history
        history_manager.add_message("user", message)
        history_manager.add_message("gemini", response.text)
        await interaction.followup.send(response.text)
        history_manager.save_to_file()
    except Exception as e:
        purpy = await clyde.fetch_user(str(os.getenv("PURPY_ID")))
        print(f"Error generating content: {e}")
        await interaction.followup.send(f'{str(interaction.user)}, **THIS MESSAGE IS NOT FROM THE BOT!** Your request broke, and I couldn\'t send the message! I have DMd purpy with the error!')
        await purpy.send(f'Bot broke! Executor: {str(interaction.user)}')
        await purpy.send(f'Error: {e}')

@clyde.tree.command(name="doiwork")
@app_commands.guild_install()
@app_commands.user_install()
async def doiwork(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send('I think so')

# Save history to file on bot shutdown
@clyde.event
async def on_disconnect():
    history_manager.save_to_file()

    guild_id = 1250174750190211212
    channel_id = 1251277265380053072

    guild = clyde.get_guild(guild_id)
    channel = guild.get_channel(channel_id)

    if channel:
        await channel.send("RECLYDE IS SHUTTING DOWN, POSSIBLY FOR UPDATES!")

signal.signal(signal.SIGINT, handle_exit_signals)
signal.signal(signal.SIGTERM, handle_exit_signals)

clyde.run(str(os.getenv("DISCORD_TOKEN")))
