import json
from pathlib import Path
from types import ModuleType
from typing import List, Dict, Union, Callable
import importlib.util
import os
from discord.message import Message
import discord

import utils


class Modules:

	modules: Dict[ str, List[ Union[ str, ModuleType] ] ] = {}
	bot = None
	savedata: Dict[ str, List[ str ] ] = {}
	commands: Dict[str, Callable] = {}

	def __init__(self):
		with open('./options', 'r') as file:
			data = json.load(file)
		# get the saved modules
		Modules.savedata = data['modules']
		for name, mod in Modules.savedata.items():
			print(f'loaded {name} from {mod[1]}')
			Modules.modules[name] = [ mod[0], getModule( name, mod[1] ) ]

	async def mhandle(self, message: Message):
		"""
		Handles $(prefix)module commands
		:param message: the message with the command
		"""
		# remove "module " from the command
		message.content = message.content.replace('module ', '', 1).replace('modules ', '', 1)
		cmd = message.content.split(' ')
		if cmd[0] == 's':
			cmd.remove('s')
		if cmd[0] == '':
			del cmd[0]
		if len( cmd ) == 0:
			await message.channel.send(
				f'missing subcommand, subcommands available: add, update, remove, list'
			)
		elif cmd[0] == 'remove':
			# parameter check
			if len( cmd ) < 2:
				await message.channel.send(
					f'missing parameter <modulename>. you can list all modules using {self.bot.prefix}modules list all'
				)
				return
			# module check
			if cmd[1] not in self.modules.keys():
				await message.channel.send(
					f'the specified module ({cmd[1]}) does not exist. you can list all modules using {self.prefix}modules list all'
				)
				return
			# author check
			if message.author.id not in (self.modules[ cmd[1] ][0], utils.enderzombi):
				await message.channel.send(
					f'only {message.guild.get_member( self.modules[ cmd[1] ][0] )} can delete this module'
				)
				return
			os.remove( self.savedata[ cmd[1] ][1] )
			del self.modules[ cmd[1] ]
			del self.savedata[ cmd[1] ]
			await message.channel.send(f'removed module "{cmd[1]}"')

		# list modules
		elif cmd[0] == 'list':
			modules = []
			if len( cmd ) < 2:
				await message.channel.send('missing parameter, all or <AUTHOR>')
			elif cmd[1] == 'all':
				for name, value in self.modules.items():
					modules.append(f'{name} by {message.channel.guild.get_member(value[0])}')
				if len( modules ) == 0:
					modules.append('no modules found')
				await message.channel.send( embed=utils.embed( 'Module List', '\n'.join(modules), discord.Color.blue() ) )
			else:
				if ( len( message.mentions ) == 0 ) or ( len( message.mentions ) > 1 ):
					await message.channel.send(f'should have as parameter exactly ONE mention or "all"')
				else:
					user = message.mentions[0]
					for name, value in self.modules.items():
						if value[0] == user.id:
							modules.append(name)
					if len(modules) == 0:
						modules.append('no modules found')
					await message.channel.send( embed=utils.embed( f'Modules Made By {user}', '\n'.join(modules), discord.Color.blue() ) )

		else:

			isCodeBlock: bool = not message.content.find("```python") == -1

			# attachment check
			if ( ( len(message.attachments) == 0) or (message.attachments is None) ) and ( not isCodeBlock ):
				await message.channel.send('missing module (.py) file')
				return
			# module name check
			if len(cmd) < 2:
				await message.channel.send(f'missing parameter <modulename>.')
				return
			# create needed variables
			modulename: str = cmd[1]
			if '\n' in modulename:
				modulename = modulename.split('\n')[0]
			path = f'./modules/{message.attachments[0].filename if not isCodeBlock else modulename + ".py"}'

			if cmd[0] == 'add':
				# parameter check

				# exist check
				if modulename in self.modules.keys():
					await message.channel.send(f'module "{modulename}" already exist! use module update to update it')
					return
				if isCodeBlock:
					saveCodeBlock( message, path, modulename )
				else:
					await message.attachments[0].save(path)
				try:
					module = getModule( cmd[0], path )
				except Exception as e:
					await utils.send( message, embed=utils.getTracebackEmbed(e) )
					return
				self.modules[ modulename ] = [ message.author.id, module ]
				self.savedata[ modulename ] = [ message.author.id, path]
				await message.channel.send(f'module "{modulename}" successfully added')

			elif cmd[0] == 'update':
				# parameter check
				if len(cmd) < 2:
					await message.channel.send(f'missing parameter <modulename>.')
					return
				# exist check
				if modulename not in self.modules.keys():
					await message.channel.send(f'module "{modulename}" does not exist! use module add to add it')
					return
				if isCodeBlock:
					saveCodeBlock( message, path, modulename )
				else:
					await message.attachments[0].save(path)
				try:
					module = getModule(cmd[0], path)
				except Exception as e:
					await utils.send( message, embed=utils.getTracebackEmbed(e) )
					return
				self.modules[ modulename ] = [message.author.id, module]
				self.savedata[ modulename ] = [message.author.id, path]
				await message.channel.send(f'module "{modulename}" successfully updated')
		# save everything
		with open('./options', 'r') as file:
			data = json.load(file)
		# update with new data
		data['modules'] = self.savedata
		# write options
		with open('./options', 'w') as file:
			json.dump(data, file, indent=4)

	async def handle(self, msg: Message):
		cmd = msg.content.split(' ')[0]
		if cmd in self.commands.keys():
			try:
				await self.commands[cmd](msg)
			except Exception as e:
				await msg.channel.send( embed=utils.getTracebackEmbed(e) )

	async def reload(self, module: str) -> None:
		spec = self.modules[module][1].__spec__
		self.modules[module][1] = importlib.util.module_from_spec( spec )
		spec.loader.exec_module( self.modules[module][1] )

	def __getattr__(self, item):
		if item == 'prefix':
			return self.bot.prefix


def saveCodeBlock(msg: Message, path: str, modulename: str) -> None:
	code: str = msg.content.replace(f' add {modulename}\n', '')
	code = code.replace(f' update {modulename}\n', '')
	code = code.replace("```python", '').replace("```", '')
	if 'import modules' not in code:
		code = 'import modules\n' + code
	x = Path(path)
	mode = 'w' if x.exists() else 'x'
	with x.open( mode ) as file:
		file.write( code )


def Command(func):
	"""
	a decorator for commands
	the decorated function name is the command name
	:param func:
	:return:
	"""
	CName = func.__code__.co_name
	Modules.commands[CName] = func


def getModule(name: str, path: str) -> ModuleType:
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec( spec )
	spec.loader.exec_module(module)
	return module
