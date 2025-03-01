import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta

TOKEN = "YOUR_DISCORD_TOKEN"  # This will be set in Railway Environment Variables
GUILD_ID = YOUR_GUILD_ID  # Replace with your server ID
CATEGORY_ID = YOUR_CATEGORY_ID  # Replace with the Music Archives category ID
POST_LIMIT = 2  # Max posts per user per week
RESET_TIME = timedelta(days=7)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to track user submissions
submissions = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    reset_submissions.start()  # Start the reset loop

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    guild = bot.get_guild(GUILD_ID)
    category = discord.utils.get(guild.categories, id=CATEGORY_ID)
    
    if category and message.channel.category == category:
        author_id = message.author.id
        now = datetime.utcnow()
        
        if author_id not in submissions:
            submissions[author_id] = []
        
        submissions[author_id] = [t for t in submissions[author_id] if now - t < RESET_TIME]
        
        if len(submissions[author_id]) >= POST_LIMIT:
            await message.delete()
            await message.author.send("⚠️ You can only post **2 songs per week** in Music Archives.")
            return
        
        submissions[author_id].append(now)
        
        await message.add_reaction("👍")  # Like reaction
        await message.add_reaction("👎")  # Dislike reaction
    
    await bot.process_commands(message)

@tasks.loop(hours=24)
async def reset_submissions():
    now = datetime.utcnow()
    for user_id in list(submissions.keys()):
        submissions[user_id] = [t for t in submissions[user_id] if now - t < RESET_TIME]
        if not submissions[user_id]:
            del submissions[user_id]

bot.run(TOKEN)
