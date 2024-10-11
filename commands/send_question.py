import nextcord
from nextcord import Interaction, SlashOption, ButtonStyle, ui
import asyncio
from datetime import datetime, timedelta

# Colors for embeds based on difficulty level
DIFFICULTY_COLORS = {
    'facile': nextcord.Color.green(),
    'moyen': nextcord.Color.yellow(),
    'difficile': nextcord.Color.orange(),
    'extreme': nextcord.Color.red(),
}

# Modal for submitting a response
class ResponseModal(ui.Modal):
    def __init__(self, question, target_channel_id):
        super().__init__(title="Répondez à la question")
        self.question = question
        self.target_channel_id = target_channel_id
        self.response = ui.TextInput(
            label="Votre réponse", style=nextcord.TextInputStyle.paragraph)

        self.add_item(self.response)

    async def callback(self, interaction: Interaction):
        embed = nextcord.Embed(
            title="Nouvelle réponse",
            description=f"{interaction.user.mention} a répondu à la question :\n**{self.question}**",
            color=nextcord.Color.blurple(),
        )
        embed.add_field(
            name="Réponse", value=self.response.value, inline=False)

        target_channel = nextcord.utils.get(
            interaction.guild.text_channels, name="reponses-quizz")
        if target_channel:
            await target_channel.send(embed=embed)

        await interaction.response.send_message("Votre réponse a été envoyée.", ephemeral=True)

# View with the button to answer the question
class QuestionView(ui.View):
    def __init__(self, question, difficulty):
        super().__init__()
        self.question = question
        self.difficulty = difficulty

    @ui.button(label="Répondre", style=ButtonStyle.primary)
    async def respond(self, button: ui.Button, interaction: Interaction):
        modal = ResponseModal(self.question, None)
        await interaction.response.send_modal(modal)

# Command to send a question
async def quizz(interaction: Interaction,
                question: str = SlashOption(description="La question à poser", required=True),
                difficulty: str = SlashOption(description="La difficulté", choices=["facile", "moyen", "difficile", "extreme"], required=True),
                duration: int = SlashOption(description="Durée de la question en heures", required=True),
                image: nextcord.Attachment = SlashOption(description="Image (optionnel)", required=False)):

    embed_color = DIFFICULTY_COLORS.get(difficulty, nextcord.Color.default())
    embed = nextcord.Embed(
        title="Nouvelle question",
        description="## " + question,
        color=embed_color
    )

    # Calculate Discord timestamp for expiration, adjusting for UTC+2
    if duration > 0:
        expiration_time = datetime.utcnow() + timedelta(hours=duration+2)
        expiration_timestamp = int(expiration_time.timestamp())
        embed.add_field(name="Temps restant",
                        value=f"Se finit <t:{expiration_timestamp}:R>", inline=False)
    else:
        embed.set_footer(text=f"Difficulté : {difficulty.capitalize()}")

    if image:
        embed.set_image(url=image.url)

    view = QuestionView(question, difficulty)

    # Send the embed in the 'quizz' channel
    target_channel = nextcord.utils.get(
        interaction.guild.text_channels, name="quizz")
    if target_channel:
        sent_message = await target_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Votre question a bien été envoyée.", ephemeral=True)

        # Wait for the specified duration, then delete the message
        if duration > 0:
            await asyncio.sleep(duration * 3600)
            await sent_message.delete()

# Setup
def setup(bot):
    bot.slash_command(name='quizz', description="Envoyer une question")(quizz)
