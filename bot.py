import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import tasks
import json
import os

TOKEN = "vP7wIqhbgRjKesSFYEkmabzm-mV1wZ6u"  # Replace with your Discord bot token
CHANNEL_ID = 123456789012345678  # Replace with your Discord channel ID
SENT_FILE = "sent_announcements.json"

# Initialize sent announcements file
def load_sent_announcements():
    if not os.path.exists(SENT_FILE):
        return []
    with open(SENT_FILE, "r") as file:
        return json.load(file)

def save_sent_announcements(sent_announcements):
    with open(SENT_FILE, "w") as file:
        json.dump(sent_announcements, file)

# Fetch announcements
def fetch_announcements():
    url = "https://www.northsouth.edu/nsu-announcements/"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch announcements")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    announcements = []
    
    for item in soup.select("div.blog-title > a"):  # Adjust selector based on NSU page
        title = item.get_text(strip=True)
        link = item["href"]
        announcements.append({"title": title, "link": link})
    
    return announcements

# Discord bot
client = discord.Client(intents=discord.Intents.default())
sent_announcements = load_sent_announcements()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_announcements.start()

@tasks.loop(minutes=10)
async def check_announcements():
    global sent_announcements
    channel = client.get_channel(CHANNEL_ID)
    announcements = fetch_announcements()

    for announcement in announcements:
        if announcement["title"] not in sent_announcements:
            message = f"**{announcement['title']}**\n{announcement['link']}"
            await channel.send(message)
            sent_announcements.append(announcement["title"])

    save_sent_announcements(sent_announcements)

client.run(TOKEN)
