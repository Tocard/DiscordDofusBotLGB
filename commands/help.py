import discord

def helper_wrapper(client):
    @client.tree.command(name="help", description="Displays the help menu")
    async def help_command(interaction: discord.Interaction):
        embed = discord.Embed(title="Assistant LBG", description="Available commands:", color=0x3498db)
        embed.add_field(name="/percepteur", value="Percepteur action menu", inline=False)
        embed.add_field(name="/metier", value="Metier action menu", inline=False)
        embed.add_field(name="/admin", value="Admin action menu", inline=False)
        embed.set_footer(text="A+")
        await interaction.response.send_message(embed=embed)
