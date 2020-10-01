import importlib
import os
import string
import json

import discord
from discord.message import Message

import modules
import utils
import commands


class Bot:

	instance = None
	client: discord.Client
	prefix: str = '!'
	module = None
	stdCommands = None
	lastReload: str = None

	def __init__(self):
		# load saved data
		with open('./options', 'r') as file:
			data = json.load(file)
		Bot.prefix = data['bot']['prefix']
		# init stuff
		Bot.instance = self
		Bot.client = discord.Client()
		self.client.event(self.on_ready)
		self.client.event(self.on_message)
		self.module = modules.Modules()
		self.module.bot = self
		Bot.stdCommands = commands.Commands()
		Bot.stdCommands._bot = self

	async def on_ready(self):
		await self.client.get_guild(500396398324350989).me.edit(nick=f'[{self.prefix}] ICGbot')
		print(f'discord.py v{discord.__version__}')
		print(f'We have logged in as {self.client.user}')

	async def on_message(self, msg: Message):
		# if the message doesn't starts with the prefix or is sent by a bot, ignore it
		if not self.client.user.bot:
			return
		if not msg.content.startswith(self.prefix):
			return
		msg.content = msg.content.replace(self.prefix, '', 1)
		cmd = msg.content.split(" ")
		print(f'command: {cmd[0]}, parameters: {cmd[1::len(cmd)-1] if len(cmd) > 1 else None}, issuer: {msg.author.name}')
		if msg.content.startswith('reload'):
			await self.reload(msg)
		elif msg.content.startswith('module'):
			await self.module.mhandle(msg)
		else:
			await self.handleCommand(msg)

	async def reload(self, msg: Message):
		# user check
		if not msg.author.id == utils.enderzombi():
			await msg.channel.send('only ENDERZOMBI102 can do that')
			return
		module: str = msg.content.replace('reload', '', 1).strip()
		if not len( module ) > 0:
			if self.lastReload is None:
				await msg.channel.send('missing parameter')
				return
			else:
				module = self.lastReload
		self.lastReload = module
		await msg.channel.send(f'reloading module "{module}"')
		if module in self.module.modules.keys():
			try:
				await self.module.reload(module)
			except Exception as e:
				await msg.channel.send( embed=utils.getTracebackEmbed(e) )
				raise e
			else:
				await msg.channel.send(f'custom module "{module}" reloaded')
		else:
			if module == 'modules':
				try:
					importlib.reload( modules )
				except Exception as e:
					await msg.channel.send( embed=utils.getTracebackEmbed(e) )
					return
				else:
					self.module = modules.Modules()
					self.module.bot = self
			elif module == 'commands':
				try:
					importlib.reload(commands)
				except Exception as e:
					await msg.channel.send( embed=utils.getTracebackEmbed(e) )
					return
				else:
					self.stdCommands = commands.Commands()
					self.stdCommands._bot = self
			elif module == 'utils':
				try:
					importlib.reload(utils)
				except Exception as e:
					await msg.channel.send( e )
					return
				else:
					self.stdCommands = commands.Commands()
					self.stdCommands._bot = self
			else:
				await utils.send(msg, 'invalid module "{module}"')
				return
			await msg.channel.send(f'bot module "{module}" reloaded')

	async def handleCommand(self, msg: Message):
		await getattr(self.stdCommands, msg.content.split(' ')[0], self.module.handle)(msg)

	def run(self):
		token = os.getenv('TOKEN')
		if token is None:
			with open('./.env', 'r') as file:
				token = file.read().replace('TOKEN=', '', 1)
		self.client.run(token)

	def __delete__(self, instance):
		with open('./options', 'w') as file:
			data = {
				'bot': {
					'prefix': Bot.prefix,
				},
				'modules': self.module.modules
			}
			json.dump(data, file, indent=4)


if __name__ == '__main__':
	bot = Bot()
	bot.run()
