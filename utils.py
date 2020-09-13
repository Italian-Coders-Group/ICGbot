import discord
import traceback
from typing import Final

inviteLink: str = discord.utils.oauth_url( '754402963971113010', discord.abc.Permissions( 70569024 ) )
enderzombi: Final[int] = 350938367405457408


def embed(title: str, content: str, color: discord.Color) -> discord.Embed:
	data = discord.Embed(
		color=color,
		title=title,
		description=content,
		type='rich_embed'
	)
	return data


def getTraceback(tb: Exception) -> str:
	return traceback.format_exception( type(tb), value={tb.__cause__, tb.__context__, tb.__suppress_context__}, tb=tb )


def getTracebackEmbed(tb: Exception) -> discord.Embed:
	return embed(
		title='Uncaught Exception!',
		content=getTraceback(tb),
		color=discord.Color.red()
	)


