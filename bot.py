import discord
from discord import app_commands
from discord.ext import commands

# The role ID that is allowed to use the buttons
OWNER_ROLE_ID = 1484611926137901116

class OpenCloseButtons(discord.ui.View):
    def __init__(self, target_channel):
        super().__init__(timeout=None)          # No timeout – buttons work forever
        self.target_channel = target_channel

    async def rename_channel(self, interaction: discord.Interaction, name: str):
        """Rename the target channel and confirm the action."""
        try:
            await self.target_channel.edit(name=name)
            await interaction.response.send_message(
                f"Channel renamed to **{name}**", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to rename that channel.", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Failed to rename channel: {e}", ephemeral=True
            )

    @discord.ui.button(label="🟢 Open", style=discord.ButtonStyle.green)
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Role check
        if OWNER_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "You don't have permission to use this button.", ephemeral=True
            )
            return
        await self.rename_channel(interaction, "🟢┃open")

    @discord.ui.button(label="🔴 Close", style=discord.ButtonStyle.red)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if OWNER_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "You don't have permission to use this button.", ephemeral=True
            )
            return
        await self.rename_channel(interaction, "🔴┃closed")


class OpenCloseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Set up open/close buttons for a channel")
    @app_commands.describe(
        channel="The channel to rename (leave empty to use the current channel)"
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None
    ):
        """Slash command that posts the button message."""

        # Optional: also restrict the command itself to the same role
        if OWNER_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "You need the owner role to run this command.", ephemeral=True
            )
            return

        # If no channel is provided, use the current channel
        target = channel or interaction.channel

        # Verify bot has permission to rename that channel
        if not target.permissions_for(interaction.guild.me).manage_channels:
            await interaction.response.send_message(
                f"I don't have `Manage Channels` permission in {target.mention}.",
                ephemeral=True
            )
            return

        # Create the embed and view
        embed = discord.Embed(
            title="Channel Status Control",
            description="Click the buttons below to change the channel name.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Target Channel", value=target.mention)
        embed.add_field(name="Allowed Role", value=f"<@&{OWNER_ROLE_ID}>")

        view = OpenCloseButtons(target_channel=target)

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(OpenCloseCog(bot))