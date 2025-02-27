import datetime
import logging
from platform import python_implementation, python_version
from typing import List, Optional, Union

import discord
from discord import NotFound, app_commands
from discord.ext import commands

from nameless import Nameless, shared_vars
from NamelessConfig import NamelessConfig


__all__ = ["GeneralCog"]


class GeneralCog(commands.Cog):
    def __init__(self, bot: Nameless) -> None:
        self.bot = bot

    @commands.hybrid_command()
    @app_commands.guilds(*getattr(NamelessConfig, "GUILD_IDs", []))
    @app_commands.describe(member="Target member, you by default")
    async def user(
        self,
        ctx: commands.Context,
        member: Optional[Union[discord.Member, discord.User]],
    ):
        """View someone's information"""
        await ctx.defer()

        member = member if member else ctx.author

        account_create_date = member.created_at
        join_date = member.joined_at  # pyright: ignore

        flags = [flag.replace("_", " ").title() for flag, has in member.public_flags if has]

        # should add to cache if possible
        mutual_guilds: List[str] = [g.name for g in ctx.bot.guilds if g.get_member(member.id)]

        embed = (
            discord.Embed(
                description=f"User ID: {member.id}",
                timestamp=datetime.datetime.now(),
                title=f"Something about {member}",
                color=discord.Color.orange(),
            )
            .set_thumbnail(url=member.avatar.url)  # pyright: ignore
            .add_field(
                name="Account creation date",
                value=f"<t:{int(account_create_date.timestamp())}:R>",
            )
            .add_field(
                name="Membership date",
                value=f"<t:{int(join_date.timestamp())}:R>",  # pyright: ignore
            )
            .add_field(
                name="Guild owner?",
                value=member.guild.owner == member,  # pyright: ignore
            )
            .add_field(name="Bot?", value=member.bot)
            .add_field(name="Badges", value=", ".join(flags) if flags else "None")
            .add_field(
                name="Mutual guilds with me",
                value=", ".join(mutual_guilds) if mutual_guilds else "None",
            )
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.guild_only()
    @app_commands.guilds(*getattr(NamelessConfig, "GUILD_IDs", []))
    async def guild(self, ctx: commands.Context):
        """View this guild's information"""
        await ctx.defer()

        guild = ctx.guild
        guild_create_date = guild.created_at  # pyright: ignore
        members = guild.members  # pyright: ignore

        bots_count = len([member for member in members if member.bot])
        humans_count = len([member for member in members if not member.bot])
        total_count = bots_count + humans_count
        public_threads_count = len([thread for thread in guild.threads if not thread.is_private()])  # pyright: ignore
        events = guild.scheduled_events  # pyright: ignore
        boosters_count = len(guild.premium_subscribers)  # pyright: ignore
        boosts_count = guild.premium_subscription_count  # pyright: ignore
        boost_lvl = guild.premium_tier  # pyright: ignore
        is_boosted = boosts_count > 0

        embed = (
            discord.Embed(
                description=f"Guild ID: {guild.id}"  # pyright: ignore
                f"- Owner {guild.owner}"  # pyright: ignore
                f"- Shard #{guild.shard_id}",  # pyright: ignore
                timestamp=datetime.datetime.now(),
                title=f"Something about '{guild.name}'",  # pyright: ignore
                color=discord.Color.orange(),
            )
            .set_thumbnail(url=guild.banner.url if guild.banner else "")  # pyright: ignore
            .add_field(
                name="Guild creation date",
                value=f"<t:{int(guild_create_date.timestamp())}:R>",
            )
            .add_field(
                name="Member(s)",
                value=f"Bot(s): {bots_count}\n" f"Human(s): {humans_count}\n" f"Total: {total_count}",
            )
            .add_field(
                name="Channel(s)",
                value=f"{len(guild.channels)} channel(s) - {public_threads_count} public thread(s)",  # pyright: ignore
            )
            .add_field(name="Role(s) count", value=str(len(guild.roles)))  # pyright: ignore
            .add_field(name="Pending event(s) count", value=f"{len(events)} pending event(s)")
            .add_field(
                name="Boost(s)",
                value=f"{boosts_count} boost(s) from {boosters_count} booster(s) reaching lvl. {boost_lvl}"
                if is_boosted
                else "Not boosted",
            )
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.guild_only()
    @app_commands.guilds(*getattr(NamelessConfig, "GUILD_IDs", []))
    async def the_bot(self, ctx: commands.Context):
        """View my information"""
        await ctx.defer()

        servers_count = len(ctx.bot.guilds)
        total_members_count = sum(len(guild.members) for guild in ctx.bot.guilds)
        uptime = int(shared_vars.start_time.timestamp())
        bot_inv = (
            f"https://discord.com/api/oauth2/authorize"
            f"?client_id={ctx.bot.user.id}"
            f"&permissions={shared_vars.needed_permissions.value}"
            f"&scope=bot%20applications.commands"
        )

        nameless_meta = getattr(NamelessConfig, "META", {})
        github_link = nameless_meta.get("github", None)
        github_link = (
            github_link
            if github_link
            else "https://github.com/nameless-on-discord/nameless"
            if isinstance(github_link, str)
            else "{github_link}"
        )
        support_inv = ""

        try:
            if sp_url := getattr(NamelessConfig, "SUPPORT_SERVER_URL", ""):
                inv = await self.bot.fetch_invite(sp_url)
                support_inv = inv.url
        except NotFound:
            pass

        embed = (
            discord.Embed(
                title="Something about me!",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(),
                description=getattr(
                    NamelessConfig,
                    "BOT_DESCRIPTION",
                    "I am a bot created from [nameless*]({github_link}) code "
                    "made by Swyrin#7193 and [FoxeiZ](https://github.com/FoxeiZ)",
                ).replace("{github_link}", github_link),
            )
            .set_thumbnail(url=ctx.bot.user.avatar.url)
            .add_field(name="Servers count", value=f"{servers_count}")
            .add_field(name="Members count", value=f"{total_members_count}")
            .add_field(name="Last launch/Uptime", value=f"<t:{uptime}:R>")
            .add_field(
                name="Bot version",
                value=shared_vars.__nameless_current_version__,
            )
            .add_field(name="Library version", value=f"discord.py v{discord.__version__}")
            .add_field(
                name="Python version",
                value=f"{python_implementation()} {python_version()}",
            )
            .add_field(name="Commands count", value=f"{len(list(self.bot.walk_commands()))}")
            .add_field(
                name="Invite link",
                value=f"[Click this]({bot_inv}) or click me then 'Add to Server'"
                if ctx.bot.application.bot_public
                else "N/A",
            )
            .add_field(
                name="Support server",
                value=f"[Click this]({support_inv})" if support_inv else "N/A",
            )
        )

        await ctx.send(embed=embed)


async def setup(bot: Nameless):
    await bot.add_cog(GeneralCog(bot))
    logging.info("Cog of %s added!", __name__)


async def teardown(bot: Nameless):
    await bot.remove_cog("GeneralCog")
    logging.warning("Cog of %s removed!", __name__)