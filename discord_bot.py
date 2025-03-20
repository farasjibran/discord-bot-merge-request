import discord
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_BASE_URL = "https://gitlab.impstudio.id/api/v4"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_project_id(project_name):
    url = f"{GITLAB_BASE_URL}/projects?search={project_name}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
        if projects:
            return projects[0]["id"]
    return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def approve(ctx, action: str, project_name: str, mr_id: int):
    if action.lower() == "merge":
        project_id = get_project_id(project_name)
        if not project_id:
            await ctx.send(f"❌ Project '{project_name}' not found!")
            return
        
        url = f"{GITLAB_BASE_URL}/projects/{project_id}/merge_requests/{mr_id}/approve"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            await ctx.send(f"✅ Merge Request {mr_id} in project '{project_name}' approved successfully!")
        else:
            await ctx.send(f"❌ Failed to approve MR {mr_id} in '{project_name}': {response.text}")
    else:
        await ctx.send("Invalid command usage. Use `!approve merge {project_name} {id}`")

@bot.command()
async def unapprove(ctx, action: str, project_name: str, mr_id: int):
    if action.lower() == "merge":
        project_id = get_project_id(project_name)
        if not project_id:
            await ctx.send(f"❌ Project '{project_name}' not found!")
            return
        
        url = f"{GITLAB_BASE_URL}/projects/{project_id}/merge_requests/{mr_id}/unapprove"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            await ctx.send(f"✅ Approval for Merge Request {mr_id} in project '{project_name}' has been revoked!")
        else:
            await ctx.send(f"❌ Failed to revoke approval for MR {mr_id} in '{project_name}': {response.text}")
    else:
        await ctx.send("Invalid command usage. Use `!revoke-approve merge {project_name} {id}`")

bot.run(TOKEN)
