import json
from pathlib import Path
from types import ModuleType, FunctionType
from typing import List, Dict, Union, Literal
import importlib.util
import os
from discord.message import Message
import discord

import utils


class Module:
	author: int
	path: Path
	module: ModuleType
	_name: str = None

	def __init__( self, author: int, path: str ):
		self.author = author
		self.path = Path( path )
		self.module = getModule( self.name, str( self.path ) )

	def reload( self ):
		spec = self.module.__spec__
		# delete old event listeners
		for evt in Modules.eventListeners.keys():
			if f'{self.name}.py' in Modules.eventListeners[ evt ].keys():
				del Modules.eventListeners[ evt ][ f'{self.name}.py' ]
		self.module = importlib.util.module_from_spec( spec )
		spec.loader.exec_module( self.module )

	@property
	def name(self):
		if self._name is None:
			self._name = self.path.name[:-3]
		return self._name

	def __eq__( self, other: Union[str, 'Module'] ):
		if isinstance(other, Module):
			if other is self:
				return True
			elif other.name == self.name and other.author == self.author:
				return True
			else:
				return False
		elif isinstance(other, str):
			if other == self.name or other == self.path:
				return True
		return False

	@property
	def __dict__( self ) -> Dict[ str, List[ Union[str, int] ] ]:
		return {
			self.name: [
				self.author,
				self.path
			]
		}


class Modules:

	modules: Dict[ str, Module ] = {}
	bot = None
	savedata: Dict[ str, List[ Union[ int, str ] ] ] = {}
	commands: Dict[str, FunctionType] = {}
	eventListeners: Dict[str, Dict[str, List[FunctionType] ] ] = {}

	def __init__(self):
		with open('./options', 'r') as file:
			data = json.load(file)
		# get the saved modules
		Modules.savedata = data['modules']
		for name, mod in Modules.savedata.items():
			try:
				Modules.modules[name] = Module( mod[0], mod[1] )
			except BaseException as e:
				print( f'caught {e.__class__.__name__} from module {name}, this module will not be available')
			else:
				print( f'loaded {name} from {mod[ 1 ]}' )

	async def mhandle(self, message: Message):
		"""
		Handles $(prefix)module commands
		:param message: the message with the command
		"""
		# remove "module" from the command
		txt = message.content
		if txt.startswith('modules'):
			txt = txt[7::]
		elif txt.startswith('module'):
			txt = txt[6::]
		cmd = txt.split(' ')
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
					f'the specified module ({cmd[1]}) does not exist. you can list all modules using {self.bot.prefix}modules list all'
				)
				return
			# author check
			if message.author.id not in (self.modules[ cmd[1] ].author, utils.enderzombi):
				await message.channel.send(
					f'only {await message.guild.fetch_member( self.modules[ cmd[1] ].author )} can delete this module'
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
				cmd.append('all')
			if cmd[1] == 'all':
				for name, value in self.savedata.items():
					modules.append(f'{name}{"" if name in self.modules.keys() else "*"} by {await message.channel.guild.fetch_member( int( value[0] ) )}')
				if len( modules ) == 0:
					modules.append('no modules found')
				await message.channel.send(
					embed=utils.makeEmbed(
						title='Module List',
						content='\n'.join(modules),
						color=discord.Color.blue(),
						footer='modules with a leading * are disabled\nICGbot by (mainly) ENDERZOMBI102'
					)
				)
			else:
				if ( len( message.mentions ) == 0 ) or ( len( message.mentions ) > 1 ):
					await message.channel.send(f'should have as parameter exactly ONE mention or "all"')
				else:
					user = message.mentions[0]
					for name, value in self.savedata.items():
						if value[0] == user.id:
							modules.append(f'{name}{"" if name in self.modules.keys() else "*"}')
					if len(modules) == 0:
						modules.append("seems like this user didn't made any module")
					await message.channel.send(
						embed=utils.makeEmbed(
							title=f'Modules Made By {user}',
							content='\n'.join(modules),
							color=discord.Color.blue(),
							footer='modules with a leading * are disabled\nICGbot by (mainly) ENDERZOMBI102'
						)
					)

		else:

			isCodeBlock: bool = not message.content.find("```python") == -1

			# attachment check
			if ( ( len(message.attachments) == 0) or (message.attachments is None) ) and ( not isCodeBlock ):
				await message.channel.send('missing module (.py) file')
				return
			# module name check
			if len(cmd) < 2 and isCodeBlock:
				await message.channel.send(f'missing parameter <modulename>.')
				return
			# create needed variables
			modulename: str = cmd[1] if isCodeBlock else message.attachments[0].filename.replace('.py', '', 1)
			if '\n' in modulename:
				modulename = modulename.split('\n')[0]
			modulepath = f'./user-modules/{modulename + ".py"}'

			if cmd[0] == 'add':
				# parameter check

				# exist check
				if modulename in self.modules.keys():
					await message.channel.send(f'module "{modulename}" already exist! use module update to update it')
					return
				if isCodeBlock:
					saveCodeBlock( txt, modulepath, modulename )
				else:
					await message.attachments[0].save(modulepath)
				try:
					self.modules[ modulename ] = Module( message.author.id, modulepath )
					self.savedata[ modulename ] = [ message.author.id, modulepath ]
					await message.channel.send( f'module "{modulename}" successfully added' )
				except Exception as e:
					await utils.send( message, embed=utils.getTracebackEmbed(e) )
					return

			elif cmd[0] == 'update':
				# parameter check
				if len(cmd) < 2:
					await message.channel.send(f'missing parameter <modulename>.')
					return
				# exist check
				if modulename not in self.modules.keys():
					await message.channel.send(f'module "{modulename}" does not exist! use module add to add it')
					return
				# person check
				if self.modules[ modulename ].author != message.author.id:
					await message.channel.send( f"You're not the author of {modulename}!" )
					return
				if isCodeBlock:
					saveCodeBlock( txt, modulepath, modulename )
				else:
					await message.attachments[0].save(modulepath)
				try:
					self.modules[ modulename ] = Module( message.author.id, modulepath )
					self.savedata[ modulename ] = [ message.author.id, modulepath ]
					await message.channel.send( f'module "{modulename}" successfully updated' )
				except Exception as e:
					await utils.send( message, embed=utils.getTracebackEmbed(e) )
					return

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
		for key in self.commands.keys():
			if cmd.lower() == key.lower():
				try:
					await self.commands[ key ]( msg )
				except Exception as e:
					await msg.channel.send( embed=utils.getTracebackEmbed( e ) )
				break

	async def handleEvent( self, evt: Literal['memberJoin', 'memberLeave', 'memberUpdate', 'message', 'command'], **kwargs ):
		if evt not in Modules.eventListeners:
			if evt != 'message':
				print(f'no listeners for event {evt}')
		else:
			for module in Modules.eventListeners[evt].values():
				for hdlr in module:
					print(f'{hdlr.__module__}.{hdlr.__name__} is handling event {evt}')
					await hdlr( **kwargs )

	async def reload(self, module: str) -> None:
		self.modules[module].reload()


def saveCodeBlock(text: str, path: str, modulename: str) -> None:
	code: str = text.replace(f' add {modulename}\n', '')
	code = code.replace(f' update {modulename}\n', '')
	code = code.replace("```python", '').replace("```", '')
	if 'from modules import Command, EventHandler' not in code or 'import modules' not in code:
		code = 'from modules import Command, EventHandler\n' + code
	x = Path(path)
	mode = 'w' if x.exists() else 'x'
	with x.open( mode ) as file:
		file.write( code )


def Command(func):
	"""
	A the decorated function name is the command name
	:param func: * decorated function *
	"""
	CName = func.__code__.co_name
	Modules.commands[CName] = func


def EventHandler( evt: Literal['memberJoin', 'memberLeave', 'memberUpdate'] ):
	"""
	A decorator for event handlers,
	the decorated functions will be called when the subscribed event occours
	:param evt: one of memberJoin memberLeave memberUpdate
	"""
	if evt not in Modules.eventListeners.keys():
		Modules.eventListeners[ evt ] = {}

	def decorator(func: FunctionType):
		print(f'Found event handler for event "{evt}": {func.__name__}')
		filename = f'{func.__module__}.py'
		if filename not in Modules.eventListeners[ evt ]:
			Modules.eventListeners[ evt ][ filename ] = []
		Modules.eventListeners[ evt ][ filename ].append(func)
		return func

	return decorator


def getModule(name: str, path: str) -> ModuleType:
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec( spec )
	spec.loader.exec_module(module)
	return module
