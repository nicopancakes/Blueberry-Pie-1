import discord
from discord import app_commands
from discord.ui import Button, View
import asyncio
# Apply Token Below
TOKEN = "TOKEN_HERE"
# Apply the Standard /raid Message Below
STANDARD_MESSAGE = """ """

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class RaidConfirmView(View):
    def __init__(self, content: str, max_count: int, user_id: int):
        super().__init__(timeout=30)
        self.content = content
        self.max_count = max_count
        self.user_id = user_id

    @discord.ui.button(label="Confirm Raid", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Not for you.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        sent = 0
        try:
            for _ in range(self.max_count):
                await interaction.followup.send(self.content, ephemeral=False)
                sent += 1
                print(f"[RAID] Sent {sent}/{self.max_count}")
                await asyncio.sleep(1.1)
        except discord.HTTPException as e:
            print(f"[RAID FAIL] {e.status} - {e.text}")
            await interaction.followup.send(f"Error: {e.status} {e.text[:100]}", ephemeral=True)
        except Exception as e:
            print(f"[RAID ERROR] {e}")

        self.clear_items()
        await interaction.edit_original_response(view=self)
        self.stop()

@tree.command(name="raid", description="start a raid")
async def raid(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="Confirm?",
        description="click the button below to start",
        color=0xff0000
    )
    embed.add_field(
        name="Message Preview",
        value=STANDARD_MESSAGE[:500] + ("..." if len(STANDARD_MESSAGE) > 500 else ""),
        inline=False
    )

    max_count = 15

    view = RaidConfirmView(STANDARD_MESSAGE, max_count, interaction.user.id)
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")

    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync failed: {e}")


if __name__ == "__main__":
    client.run(TOKEN)
