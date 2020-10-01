import json
from typing import Union, Tuple

import discord
from discord import Message, Embed

import utils
import bot


class Commands:

	_bot: bot.Bot = None

	async def echo(self, msg: Message):
		await msg.channel.send( ' '.join( msg.content.split(' ')[ 1::len( msg.content.split(' ') )-1 ] ) )

	async def cp(self, msg: Message):
		msg.content = msg.content.replace('cp', '')
		if len( msg.content ) != 1:
			pre = self._bot.prefix
			self._bot.prefix = msg.content.strip()
			await msg.channel.send(f'successfully changed prefix from "{pre}" to "{self._bot.prefix}"')
			await msg.guild.me.edit(nick=f'[{self._bot.prefix}] ICGbot')
			# save changes
			with open('./options', 'r') as file:
				data = json.load(file)
			# update with new data
			data['bot']['prefix'] = self._bot.prefix
			# write options
			with open('./options', 'w') as file:
				json.dump(data, file, indent=4)
		else:
			await msg.channel.send(f'the new prefix must be 1 char long, the provided prefix is {len(msg.content)}')

	async def whatsmyid(self, msg: Message):
		await utils.send( msg, msg.author.id )

	async def breaker(self, msg: Message):
		if msg.author.id != utils.enderzombi():
			await utils.send(msg, 'only ENDERZOMBI102 can use that command')
			return
		print('break!')

	async def setActivity(self, msg: Message):
		if msg.author.id != utils.enderzombi():
			await utils.send(msg, 'only ENDERZOMBI102 can use that command')
			return
		act = discord.Game( msg.content.replace('setActivity ', '', 1) )
		await self._bot.client.change_presence( activity=act )

	async def ping(self, msg: Message):
		await utils.send(msg, f'pong! my ping is {int(self._bot.client.latency*1000)}ms')

