import discord
from discord.ext import commands
from typing import Literal, Optional
from discord.ext.commands import Greedy, Context
import openai

f = open("openai.txt", "r")
keys = f.readlines()
openai.organization = keys[0][:-1:]
openai.api_key = keys[1]
f.close()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = Bot()

# Tree syncer
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


# Generate a response from a prompt
def generate_response(prompt):
    # Set up the parameters for the API request
    prompt = f"{prompt.strip()}"
    model = "gpt-3.5-turbo"

    # Generate a response from the OpenAI API
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content":prompt}],
        max_tokens=3000
    )

    # Return the generated response
    message = response['choices'][0]['message']['content']
    return message

@bot.tree.command()
async def fancy(interaction: discord.Interaction, message: str):
    prompt = f"Please rewrite the following phrase \"{message}\" using complex and lengthy language. Please respond with only the resulting rewritten phrase." # Always be nice to AI, say please
    response = generate_response(prompt)
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(response)

@bot.tree.command()
async def ego(interaction: discord.Interaction, message: str):
    prompt = f"Please rewrite the following phrase \"{message}\" so it sounds like an egothistical and condescending rant. Please respond with only the resulting rewritten phrase."
    response = generate_response(prompt)
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(response)

@bot.tree.command()
async def summarize(interaction: discord.Interaction, message: str):
    prompt = f"Please rewrite the following phrase \"{message}\" so it is more summarized and short. Please respond with only the resulting rewritten phrase."
    response = generate_response(prompt)
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(response)

@bot.tree.command()
async def custom(interaction: discord.Interaction, message: str, tone: str):
    prompt = f"Please rewrite the following phrase \"{message}\" so it follows a tone that can be described as {tone}. Please respond with only the resulting rewritten phrase."
    response = generate_response(prompt)
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(response)

@bot.tree.command()
async def faq(interaction: discord.Interaction):
    await interaction.followup.send('This bot uses ChatGPT API to rewrite any statement you like, with whatever tone you like! \nThere are built-in tones such as /ego, /fancy or /summarize, but also /custom which allows for any custom writing style.')

f = open("secret.txt", "r")
token = f.read()
f.close()
bot.run(token)