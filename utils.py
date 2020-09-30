import discord
import traceback
import io
from typing import Union

from discord import Message, Embed

inviteLink: str = discord.utils.oauth_url( '754402963971113010', discord.abc.Permissions( 70569024 ) )


# Please keep in alphabetical order and [a-z] only thanks
def enderzombi() -> int:
	return 350938367405457408


def samplasion() -> int:
	return 280399026749440000


def embed(title: str, content: str, color: discord.Color) -> Embed:
	data = Embed(
		color=color,
		title=title,
		description=content,
		type='rich_embed'
	)
	return data


def getColor(RGB: str) -> discord.Color:
	rgb = RGB.split(',')
	r: int = int( rgb[0] )
	g: int = int( rgb[1] )
	b: int = int( rgb[2] )
	return discord.colour.Color.from_rgb(r, g, b)


def getTracebackEmbed(exc: Exception) -> Embed:
	prettyExc = ''.join( traceback.format_exception(type(exc), exc, exc.__traceback__) )
	print(prettyExc)
	return embed(
		title='Uncaught Exception!',
		content=prettyExc,
		color=discord.Color.red()
	)


async def send(msg: Message, text: Union[str, int] = None, embed: Embed = None) -> None:
	if embed is not None:
		await msg.channel.send(embed=embed)
	else:
		await msg.channel.send(text)


