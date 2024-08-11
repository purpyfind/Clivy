import discord
import google.generativeai as gemini
import os
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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

prompt = os.open('prompt_2.txt', os.O_RDONLY)
with os.fdopen(prompt, 'r') as file:
    prompt = file.read()

key = os.getenv('GOOGLE_API_KEY')

gemini.configure(api_key=str(key))
ActiveModel = gemini.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, generation_config=generation_config, system_instruction=prompt)

def format_message(message: discord.Message):
    content_to_send = ""

    content = message.content.replace(f'<@{client.user.id}>', '').strip()
    if content == "":
        if not message.attachments:
            content = "Hello!"
        else:
            content = "[undefined]"

    content_to_send = content

    formatted = {
        "display_name": message.author.display_name,
        "username": message.author.name,
        "content": content_to_send,
        "timestamp": message.created_at
    }

    return formatted

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

chat_history = {}

async def handle_message(message):
    if message.author == client.user or '@everyone' in message.content:
        return

    channel_id = message.channel.id

    formatted_message = format_message(message)

    if channel_id not in chat_history:
        chat_history[channel_id] = []
        current_chat = ActiveModel.start_chat(history=[]) 
    else:
        current_chat = ActiveModel.start_chat(history=chat_history[channel_id])

    if client.user.mentioned_in(message):
        async with message.channel.typing():
            if message.attachments:
                for attachment in message.attachments:
                    if str(attachment.url).find('.gif') or str(attachment.url).find('.png') or str(attachment.url).find('.jpeg') or str(attachment.url).find('.jpg'):
                        image_data = BytesIO(requests.get(attachment.url, stream=True).content)
                        try:
                            image = Image.open(image_data)

                            response = current_chat.send_message([str(formatted_message), image])
                            await message.reply(response.text)
                        except:
                            response = current_chat.send_message(f"User named {message.author.display_name} attempted to send you an image that you didn't understand. This is your technical message. Respond to them with saying that you couldn't understand the image.")
                            await message.reply(response.text)
                    else:
                        response = current_chat.send_message(f"User named {message.author.display_name} attempted to send you an image that you didn't understand. This is your technical message. Respond to them with saying that you couldn't understand the image.")
                        await message.reply(response.text)
            else:
                response = current_chat.send_message(str(formatted_message))
                await message.reply(response.text)

        chat_history[channel_id].append({'role': 'user', 'parts': str(formatted_message)})
        chat_history[channel_id].append({'role': 'model', 'parts': response.text})
    else:
        if isinstance(message.channel, discord.DMChannel):
            async with message.channel.typing():
                if message.attachments:
                    for attachment in message.attachments:
                        if str(attachment.url).find('.gif') or str(attachment.url).find('.png') or str(attachment.url).find('.jpeg') or str(attachment.url).find('.jpg'):
                            image_data = BytesIO(requests.get(attachment.url, stream=True).content)
                            try:
                                image = Image.open(image_data)

                                response = current_chat.send_message([str(formatted_message), image])
                                await message.reply(response.text)
                            except:
                                response = current_chat.send_message(f"User named {message.author.display_name} attempted to send you an image that you didn't understand. This is your technical message. Respond to them with saying that you couldn't understand the image.")
                                await message.reply(response.text)
                        else:
                            response = current_chat.send_message(f"User named {message.author.display_name} attempted to send you an image that you didn't understand. This is your technical message. Respond to them with saying that you couldn't understand the image.")
                            await message.reply(response.text)
                else:
                    response = current_chat.send_message(str(formatted_message))
                    await message.reply(response.text)

            chat_history[channel_id].append({'role': 'user', 'parts': str(formatted_message)})
            chat_history[channel_id].append({'role': 'model', 'parts': response.text})
            

@client.event
async def on_message(message):
    await handle_message(message)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
