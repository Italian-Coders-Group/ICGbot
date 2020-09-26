import discord
import traceback
from typing import Union

from discord import Message, Embed

inviteLink: str = discord.utils.oauth_url( '754402963971113010', discord.abc.Permissions( 70569024 ) )


def enderzombi() -> int:
	return 350938367405457408


def embed(title: str, content: str, color: discord.Color) -> Embed:
	data = Embed(
		color=color,
		title=title,
		description=content,
		type='rich_embed'
	)
	return data


def getTraceback(tb) -> str:
	return traceback.format_exception( type(tb), value={tb.__cause__, tb.__context__, tb.__suppress_context__}, tb=tb )


def getTracebackEmbed(tb: Exception) -> Embed:
	return embed(
		title='Uncaught Exception!',
		content=getTraceback(tb),
		color=discord.Color.red()
	)


async def send(msg: Message, text: Union[str, int] = None, embed: Embed = None) -> None:
	if embed is not None:
		await msg.channel.send(embed=embed)
	else:
		await msg.channel.send(text)


