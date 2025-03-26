import discord
from discord.commands import Option
from discord.ext import commands
from discord.ui import Button, Select, View
import random
import os

# ===== INITIALIZE BOT =====
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} 🟢")


# ===== IMPORT CATEGORIES =====
from categories.dating import mindful, red_flags, halal, haram
from categories.would_you_rather.would_you_rather import would_you_rather as wyr_questions
from categories.interview import (top_10_questions, elevator_pitch,
                                  entry_level, career_change, internship,
                                  uncomfortable_questions)
from categories.ielts import (personal_stories, society_culture, education,
                              technology, business)


# ===== UI COMPONENTS =====
class RegenerateButton(Button):

    def __init__(self, category_type, current_category):
        super().__init__(label="🔁 New Question",
                         style=discord.ButtonStyle.blurple)
        self.category_type = category_type
        self.current_category = current_category

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.category_type == "interview":
                module = globals()[self.current_category.lower().replace(
                    " ", "_")]
                qa_pair = random.choice(module.questions)
                tips = PRO_TIPS
            elif self.category_type == "ielts":
                qa_pair = random.choice(
                    IELTS_CATEGORIES[self.current_category])
                tips = IELTS_TIPS
            elif self.category_type == "dating":
                qa_pair = random.choice(DATING_OPTIONS[self.current_category])
                tips = DATING_TIPS

            await interaction.response.edit_message(
                content=
                f"**{qa_pair['question']}**\n\n{qa_pair['guidance']}\n\n{random.choice(tips)}",
                view=self.view)
        except Exception as e:
            await interaction.response.send_message(
                "Failed to regenerate question!", ephemeral=True)


class CategoryDropdown(Select):

    def __init__(self, options_list, current_category, category_type):
        options = [
            discord.SelectOption(label=cat,
                                 value=cat,
                                 default=(cat == current_category))
            for cat in options_list
        ]
        super().__init__(placeholder="Switch category...", options=options)
        self.category_type = category_type

    async def callback(self, interaction: discord.Interaction):
        try:
            new_category = self.values[0]
            view = View(timeout=180)

            if self.category_type == "interview":
                view.add_item(
                    CategoryDropdown(INTERVIEW_OPTIONS, new_category,
                                     "interview"))
                module = globals()[new_category.lower().replace(" ", "_")]
                qa_pair = random.choice(module.questions)
                tips = PRO_TIPS
            elif self.category_type == "ielts":
                view.add_item(
                    CategoryDropdown(list(IELTS_CATEGORIES.keys()),
                                     new_category, "ielts"))
                qa_pair = random.choice(IELTS_CATEGORIES[new_category])
                tips = IELTS_TIPS
            elif self.category_type == "dating":
                view.add_item(
                    CategoryDropdown(list(DATING_OPTIONS.keys()), new_category,
                                     "dating"))
                qa_pair = random.choice(DATING_OPTIONS[new_category])
                tips = DATING_TIPS

            view.add_item(RegenerateButton(self.category_type, new_category))
            await interaction.response.edit_message(
                content=
                f"**{qa_pair['question']}**\n\n{qa_pair['guidance']}\n\n{random.choice(tips)}",
                view=view)
        except Exception as e:
            await interaction.response.send_message("Category switch failed!",
                                                    ephemeral=True)


# ===== CONSTANTS =====
PRO_TIPS = [
    "💬 Discuss different approaches with your team!",
    "🤝 Compare strategies after answering!",
    "🎙️ Roleplay interviewer/candidate now!", "🌟 Give each other feedback!"
]

IELTS_TIPS = [
    "⏰ Practice timing your responses!", "📝 Focus on clear structure!",
    "🗣️ Record yourself for analysis!", "📚 Use topic-specific vocabulary!"
]

DATING_TIPS = [
    "💭 Reflect before answering!", "🤔 Consider different perspectives!",
    "🗣️ Share personal experiences!", "⚖️ Balance heart and logic!"
]

INTERVIEW_OPTIONS = [
    "Top 10 Questions", "Elevator Pitch", "Entry Level", "Career Change",
    "Internship", "Uncomfortable Questions"
]

IELTS_CATEGORIES = {
    "Personal Stories": personal_stories.questions,
    "Society & Culture": society_culture.questions,
    "Education Debates": education.questions,
    "Technology": technology.questions,
    "Business": business.questions
}

DATING_OPTIONS = {
    "Mindful Dating": mindful.questions,
    "Red Flags": red_flags.questions,
    "Halal Perspectives": halal.questions,
    "Relationship Boundaries": haram.questions
}


# ===== COMMANDS =====
@bot.slash_command(name="interview",
                   description="Practice interview questions")
async def interview(ctx: discord.ApplicationContext,
                    category: Option(str, choices=INTERVIEW_OPTIONS)):
    try:
        module = globals()[category.lower().replace(" ", "_")]
        qa_pair = random.choice(module.questions)
        view = View(timeout=180)
        view.add_item(
            CategoryDropdown(INTERVIEW_OPTIONS, category, "interview"))
        view.add_item(RegenerateButton("interview", category))
        await ctx.respond(
            f"**{qa_pair['question']}**\n\n{qa_pair['guidance']}\n\n{random.choice(PRO_TIPS)}",
            view=view)
    except Exception as e:
        await ctx.respond("Failed to start session!", ephemeral=True)


@bot.slash_command(name="ielts", description="IELTS speaking practice")
async def ielts(ctx: discord.ApplicationContext,
                category: Option(str, choices=list(IELTS_CATEGORIES.keys()))):
    try:
        qa_pair = random.choice(IELTS_CATEGORIES[category])
        view = View(timeout=180)
        view.add_item(
            CategoryDropdown(list(IELTS_CATEGORIES.keys()), category, "ielts"))
        view.add_item(RegenerateButton("ielts", category))
        await ctx.respond(
            f"**{qa_pair['question']}**\n\n{qa_pair['guidance']}\n\n{random.choice(IELTS_TIPS)}",
            view=view)
    except Exception as e:
        await ctx.respond("Failed to start IELTS session!", ephemeral=True)


@bot.slash_command(name="dating", description="Relationship scenarios")
async def dating(ctx: discord.ApplicationContext,
                 style: Option(str, choices=list(DATING_OPTIONS.keys()))):
    try:
        qa_pair = random.choice(DATING_OPTIONS[style])
        view = View(timeout=180)
        view.add_item(
            CategoryDropdown(list(DATING_OPTIONS.keys()), style, "dating"))
        view.add_item(RegenerateButton("dating", style))
        await ctx.respond(
            f"**{qa_pair['question']}**\n\n{qa_pair['guidance']}\n\n{random.choice(DATING_TIPS)}",
            view=view)
    except Exception as e:
        await ctx.respond("Failed to start dating session!", ephemeral=True)


@bot.slash_command(name="would_you_rather",
                   description="Fun dilemma questions")
async def would_you_rather(ctx: discord.ApplicationContext):
    try:
        qa_pair = random.choice(wyr_questions)
        view = View(timeout=180)
        new_dilemma_button = Button(label="🔀 New Dilemma",
                                    style=discord.ButtonStyle.green)

        async def new_dilemma_callback(interaction: discord.Interaction):
            new_qa = random.choice(wyr_questions)
            await interaction.response.edit_message(
                content=f"**🤔 {new_qa['question']}**\n\n{new_qa['guidance']}",
                view=view)

        new_dilemma_button.callback = new_dilemma_callback
        view.add_item(new_dilemma_button)

        await ctx.respond(
            f"**🤔 {qa_pair['question']}**\n\n{qa_pair['guidance']}", view=view)
    except Exception as e:
        await ctx.respond("Failed to load Would You Rather question!",
                          ephemeral=True)


# ===== RUN BOT =====
if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])
