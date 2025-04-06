from datetime import datetime
from typing import NamedTuple

import aiosqlite
import discord
import discord.utils
from discord import Interaction, app_commands
from discord.ext import commands
from discord.utils import escape_markdown
from io import BytesIO
from json import dumps

# from bjokeybot.logger import log
from .base import BjokeyCog


class Album(NamedTuple):
    id: int
    media_type: str
    season: int
    date: str
    choice: int
    artist: str
    title: str


class Rating(NamedTuple):
    album: int
    dogger: int
    score: int


class Amalgamation(NamedTuple):
    id: int
    season: int
    date: str
    choice: int
    artist: str
    title: str
    score: int

class AlbumsWithAverages(NamedTuple):
    title: str
    artist: str
    average: float

DB_FILEPATH = "../dogging.sqlite3"
DAYS_TO_CHANGE_SCORE = 1


def db_conn() -> aiosqlite.Connection:
    return aiosqlite.connect(DB_FILEPATH)

def unlistened_output_header(percentage: float) -> str:
    responses = {
        80.0: "So close now...",
        60.0: "You're over half way!",
        40.0: "You're on the right track...",
        20.0: "You're getting there...",
        0.0: "Not even a dent..."
    }
    return [responses[resp] for resp in responses.keys() if percentage >= resp][0]

def like(s: str) -> str:
    return f"%{s}%"

def averages_factory(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> AlbumsWithAverages:
    return AlbumsWithAverages(*row)

def album_factory(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> Album:
    return Album(*row)

def almalgamation_factory(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> Amalgamation:
    return Amalgamation(*row)

def rating_factory(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> Rating:
    return Rating(*row)


async def init_tables() -> None:
    async with db_conn() as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS Albums ("
            "id INTEGER PRIMARY KEY ASC,"
            "type TEXT NOT NULL,"
            "season INTEGER NOT NULL,"
            "date TEXT NOT NULL,"
            "choice INTEGER,"
            "artist TEXT NOT NULL,"
            "title TEXT NOT NULL,"
            "UNIQUE (artist, title)"
            ");"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS Ratings ("
            "album INTEGER REFERENCES Albums (id),"
            "dogger INTEGER NOT NULL,"
            "score INTEGER NOT NULL,"
            "PRIMARY KEY (album, dogger)"
            ");"
        )


async def fetch_albums_from_title(title: str) -> list[Album]:
    async with db_conn() as conn:
        conn.row_factory = album_factory  # type: ignore
        cur = await conn.execute(
            "SELECT * FROM Albums WHERE title LIKE ?;", (like(title),)
        )
        return list(await cur.fetchall())  # type: ignore

async def fetch_unlistened_albums(user_id: int) -> list[Album]:
    async with db_conn() as conn:
        conn.row_factory = album_factory  # type: ignore
        cur = await conn.execute(
            "select * from Albums where not exists (select * from Ratings where Ratings.album=Albums.id and Ratings.dogger = ?) AND type = 'Album' ", (user_id, )
        )
        return await cur.fetchall()  # type: ignore

async def count_of_all_albums() -> int:
    async with db_conn() as conn:
        # conn.row_factory = album_factory  # type: ignore
        cur = await conn.execute(
            "select count(*) from albums"
        )
        res = await cur.fetchone()
        if isinstance(res, tuple):
            return res[0]
        return await cur.fetchone()  # type: ignore

async def fetch_album_from_title(title: str) -> Album | None:
    async with db_conn() as conn:
        conn.row_factory = album_factory  # type: ignore
        cur = await conn.execute(
            "SELECT * FROM Albums WHERE title LIKE ?;", (like(title),)
        )
        return await cur.fetchone()  # type: ignore

async def fetch_albums_for_user(user_id: int) -> list[Amalgamation]:
    async with db_conn() as conn:
        conn.row_factory = almalgamation_factory  # type: ignore
        cur = await conn.execute(
            """select id, season, date, choice, artist, title, score from ratings
            inner join Albums ON ratings.album=Albums.id
            where dogger = ?
            order by score DESC""",
            (user_id,),
        )
        return list(await cur.fetchall()) # type: ignore

async def fetch_specific_rating(album: Album, user_id: int) -> Rating | None:
    async with db_conn() as conn:
        conn.row_factory = rating_factory  # type: ignore
        cur = await conn.execute(
            "SELECT * FROM Ratings WHERE album = ? AND dogger = ?", (album.id, user_id)
        )
        return await cur.fetchone()  # type: ignore

async def fetch_top_rated_albums() -> list[AlbumsWithAverages]:
    async with db_conn() as conn:
        conn.row_factory = averages_factory # type: ignore
        cur = await conn.execute (
            """select distinct title, artist, round(avg(score),2) as average from albums
            inner join ratings on albums.id=ratings.album
            group by id order by average desc limit 10""", (),
        )
        return list(await cur.fetchall()) #type: ignore

async def add_rating(rating: Rating, *, replace_existing: bool = False) -> None:
    async with db_conn() as conn:
        if replace_existing:
            command = "INSERT OR REPLACE INTO Ratings (album, dogger, score) VALUES (?, ?, ?);"
        else:
            command = "INSERT INTO Ratings (album, dogger, score) VALUES (?, ?, ?);"
        await conn.execute(
            command,
            (rating.album, rating.dogger, rating.score),
        )
        await conn.commit()


async def add_album(album: Album) -> None:
    async with db_conn() as conn:
        await conn.execute(
            "INSERT INTO Albums"
            "(season, type, date, choice, artist, title)"
            "VALUES (?, ?, ?, ?, ?, ?);",
            (
                album.season,
                album.media_type,
                album.date,
                album.choice,
                album.artist,
                album.title,
            ),
        )
        await conn.commit()


async def fetch_album_from_id(album_id: int) -> Album | None:
    async with db_conn() as conn:
        conn.row_factory = album_factory  # type: ignore
        cur = await conn.execute("SELECT * FROM Albums WHERE id = ?;", (album_id,))
        return await cur.fetchone()  # type: ignore


async def fetch_ratings(album: Album) -> list[Rating]:
    async with db_conn() as conn:
        old_factory = conn.row_factory
        conn.row_factory = rating_factory  # type: ignore
        cur = await conn.execute("SELECT * FROM Ratings WHERE album = ?;", (album.id,))
        ratings = await cur.fetchall()
        conn.row_factory = old_factory
    return ratings  # type: ignore


class DoggingCog(BjokeyCog):
    curr_album_id: int | None

    async def cog_load(self) -> None:
        self.curr_album_id = None
        await init_tables()
        await super().cog_load()

    async def album_autocomplete(
        self, interaction: Interaction, album: str
    ) -> list[app_commands.Choice]:

        albums = await fetch_albums_from_title(album)
        choices = [
            app_commands.Choice(name=f"{a.artist} - {a.title}", value=a.title)
            for a in albums[:25]
        ]
        return choices

    @app_commands.command(
        name="summary", description="Summarize the scores for an album."
    )
    @app_commands.autocomplete(album_title=album_autocomplete)
    async def summary(self, interaction: Interaction, album_title: str) -> None:
        album = await fetch_album_from_title(album_title)
        if album is None:
            await interaction.response.send_message(
                f"Couldn't find album matching title: {album_title}",
                ephemeral=True,
            )
            return
        ratings = await fetch_ratings(album)
        chooser = await self.bot.fetch_user(album.choice)
        doggers = {r: await self.bot.fetch_user(r.dogger) for r in ratings}

        output = []
        output.append(
            f"**{album.artist} - {album.title}** (Chosen by {escape_markdown(chooser.name)})"
        )
        output.append(f"Listened to on {album.date}")
        output.append("====")
        name_padded_len = max(len(user.name) for user in doggers.values()) + 2
        for rating, user in doggers.items():
            output.append(f"`{user.name + ':':<{name_padded_len}}{rating.score}`")
        if len(ratings) > 0:
            average = sum(r.score for r in ratings) / len(ratings)
            output.append(f"\r\n**OVERALL SCORE: {average:.2f}**")
        else:
            output.append("\r\n**OVERALL SCORE: ??**")

        await interaction.response.send_message(
            "\r\n".join(output),
            ephemeral=False,
        )

    @app_commands.command(name="rate", description="Rate an album!")
    @app_commands.autocomplete(album_title=album_autocomplete)
    async def rate(
        self, interaction: Interaction, album_title: str, score: int
    ) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not 0 <= score <= 100:
            await interaction.edit_original_response(
                content=f"{score}/100 is just plain silly, be fr"
            )
            return

        album = await fetch_album_from_title(album_title)
        if album is None:
            await interaction.edit_original_response(
                content=f"Couldn't find album title in DB: {album_title}\n"
                "Either you misspelled the title, or bjokey hasnt added it yet"
            )
            return

        rating = Rating(album.id, interaction.user.id, score)

        old_rating = await fetch_specific_rating(album, interaction.user.id)
        if old_rating is None:
            await add_rating(rating)
            await interaction.edit_original_response(
                content=f"Successfully gave {album.artist} - {album.title} a {rating.score}/100.",
            )
        else:
            album_date = datetime.strptime(album.date, "%Y-%m-%d")
            ago = datetime.now() - album_date
            if ago.days > DAYS_TO_CHANGE_SCORE:
                await interaction.edit_original_response(
                    content=f"You've already rated {album.title}, and it was listened to {ago.days} days ago! Your score is LOCKED IN!!!!"
                )
                return

            await interaction.edit_original_response(
                content=f"⚠ You already have a score for {album.artist} - {album.title} ({old_rating.score}/100). Want to replace it?",
                view=ReplaceRatingsView(old_rating, rating),
            )

    @app_commands.command(
        name="add_album", description="Add an album to the database (bjokey-only)"
    )
    async def add_album(self, interaction: Interaction) -> None:
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(
                "Only bjokey can do this, ask him to add the album", ephemeral=True
            )
        else:
            await interaction.response.send_modal(
                AddAlbumModal(self.bot, interaction.guild)
            )

    @commands.command(name="force_rate")
    @commands.is_owner()
    async def force_rate(
        self,
        ctx: commands.Context,
        album_title: str,
        dogger: discord.Member,
        score: int,
    ) -> None:
        album = await fetch_album_from_title(album_title)
        if album is None:
            await ctx.reply(f"Bad album title: {album_title}")
            return

        rating = Rating(album.id, dogger.id, score)
        await add_rating(rating, replace_existing=True)
        await ctx.message.add_reaction("✅")
        await ctx.reply(
            f"Set rating for {album.title} by {dogger.name} to be {score}/100"
        )

    @commands.command(name="dogdb")
    @commands.is_owner()
    async def export_db_file(self, ctx: commands.Context) -> None:
        db_file = discord.File(DB_FILEPATH, "dogging.sqlite3")
        dm = await ctx.author.create_dm()
        await dm.send(file=db_file)

    @app_commands.command(
        name="dogjson",
        description="get all the dogging data in nerd form, you probably don't want this",
    )
    async def export_json(self, interaction: Interaction) -> None:
        data = {}
        all_albums = await fetch_albums_from_title("")
        for album in all_albums:
            album_data = album._asdict()
            del album_data["id"]
            scores = await fetch_ratings(album)
            album_data["scores"] = {s.dogger: s.score for s in scores}
            data[album.id + 1] = album_data
        file_data = BytesIO(dumps(data, indent=4).encode("utf8"))
        file_data.seek(0)
        file = discord.File(file_data, filename="dogging.json")
        await interaction.response.send_message(file=file)

    @app_commands.command(name="ratings", description="see a users ratings")
    async def see_ratings(
        self, interaction: Interaction, dogger: discord.Member
    ) -> None:
        albums = await fetch_albums_for_user(dogger.id)
        if len(albums) == 0:
            await interaction.response.send_message(
                "This user hasn't rated any albums."
            )
            return
        output = []
        output.append(f"**{dogger.name}** has rated these albums:")
        # make this look nice ty :) - cris
        output.append("```")
        for album in albums:
            output.append(f"{album.artist} - {album.title} | {album.score}")
        output.append("```")
        output = "\r\n".join(output)
        await interaction.response.send_message(output)

    @app_commands.command(name="leaderboard", description="shows the top albums sorted by their average")
    async def leaderboard(self, interaction: Interaction) -> None:
        albums = await fetch_top_rated_albums()
        if len(albums) == 0:
            await interaction.response.send_message(
                "No albums found, either the database is empty or you haven't rated any."
            )
        output = []
        output.append("The top 10 albums:")
        output.append("```")
        for album in albums:
            output.append(f"{album.artist} - {album.title}: {album.average}")
        output.append("```")
        output = "\r\n".join(output)
        await interaction.response.send_message(output)

    @app_commands.command(name="unlistened", description="shows what albums you haven't listened to")
    async def unlistened(self, interaction: Interaction) -> None:
        
        albums = await fetch_unlistened_albums(interaction.user.id)
        if len(albums) == 0:
            await interaction.response.send_message("You've listened to every album :)")
        else:
            output = []
            total = await count_of_all_albums()
            amount_listened = (1 - (len(albums)/total))
            percentage = float("{0:.2f}".format( amount_listened * 100) )
            output.append(
                f" **{percentage}%** of albums listened to. {unlistened_output_header(percentage)} "
                "here are some that you're missing:"
            )
            output.append("```")
            for album in albums:
                output.append(f"{album.artist} - {album.title}")
            output.append("```")
            output = "\r\n".join(output)
            await interaction.response.send_message(output)

class ReplaceRatingsView(discord.ui.View):
    def __init__(self, old: Rating, new: Rating, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.old = old
        self.new = new

    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.blurple)
    async def overwrite_button(
        self, interaction: Interaction, button: discord.ui.Button
    ) -> None:
        await add_rating(self.new, replace_existing=True)
        await interaction.response.send_message(
            f"Score successfully updated from {self.old.score}/100 to {self.new.score}/100.",
            ephemeral=True,
        )
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel_button(
        self, interaction: Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.send_message(
            content="Score left unchanged.",
            ephemeral=True,
        )
        self.stop()


class AddAlbumModal(discord.ui.Modal, title="Add album"):
    def __init__(
        self, bot: commands.Bot, guild: discord.Guild | None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.bot = bot
        self.guild = guild

    season = discord.ui.TextInput(label="Season", required=True)
    date = discord.ui.TextInput(label="Date", placeholder="YYYY-mm-dd", required=False)
    choice = discord.ui.TextInput(
        label="Choice", placeholder="ID/username", required=True
    )

    media_type = discord.ui.TextInput(
        label="Media Type", placeholder="Either a Playlist or an Album", required=True
    )

    artist_and_album_title = discord.ui.TextInput(
        label="Artist and album title", placeholder="formatted like this: artist || album title", required=True
    )

    async def get_and_validate_input(self) -> Album:
        # We're just going through each field, and double-checking that its valid
        errors = []

        # Check season is an actual integer
        try:
            season = int(self.season.value)
        except ValueError:
            errors.append("Invalid season number.")

        # Date should be either blank, or parseable into a date of the form YYYY-mm-dd
        try:
            if len(self.date.value) > 0:
                date = datetime.strptime(self.date.value, "%Y-%m-%d")
            else:
                date = datetime.now()
            if date.year < 2020:
                errors.append(
                    f"The year value looked wrong ({date.year}), double-check that"
                )
            timestamp = date.strftime("%Y-%m-%d")
        except ValueError:
            errors.append("Invalid date provided.")

        media_type = self.media_type.value

        # anything about 
        # Error on album adding: TypeError('sequence item 0: expected str instance, list found') 
        # is this below
        if media_type not in ("Album", "Playlist"):
            errors.append(
                "Media type should either be an Album or a Playlist."
            )

        # Choice should be a valid server member ID or username
        # this code is horrible btw

        choice: int | str = self.choice.value
        try:
            choice = int(choice)
        except ValueError:
            pass

        if isinstance(choice, int):
            # int conversion worked, treat is like a discord ID
            user = await self.bot.fetch_user(choice)
            if user is None:
                errors.append("User ID is not a valid user.")
            elif self.guild is not None and self.guild.get_member(user.id) is None:
                errors.append(
                    "User ID is valid, but not in this server. Run command in DMs to ignore membership test."
                )
            else:
                choice_id = user.id
        else:
            # int conversion failed, treat it as a username
            if self.guild is None:
                errors.append("Cannot fetch user by username in DMs.")
            else:
                member = self.guild.get_member_named(choice)
                if member is None:
                    errors.append(f"Server member {choice} couldn't be found.")
                else:
                    choice_id = member.id

        artist,title = [i.strip() for i in str(self.artist_and_album_title).split("||")]
        if len(artist) == 0:
            errors.append("Artist name is blank")

        if len(title) == 0:
            errors.append("Album title is blank")

        if len(errors) == 0:
            return Album(-1, media_type, season, timestamp, choice_id, artist, title)
        else:
            raise ValueError(errors)

    async def on_submit(self, interaction: Interaction) -> None:
        try:
            album = await self.get_and_validate_input()
        except ValueError as e:
            errors = "\n".join(e.args)
            err_output = f"Error(s) when adding album:\n{errors}"
            await interaction.response.send_message(content=err_output, ephemeral=True)
            return

        await add_album(album)
        await interaction.response.send_message(
            content=f"Successfully added **{album.artist} - {album.title}** to albums"
        )

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            content=f"Error on album adding: {error!r}",
            ephemeral=True,
        )
