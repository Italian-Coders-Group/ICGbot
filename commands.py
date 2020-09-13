from discord import Message


class Commands:

	bot = None

	async def echo(self, msg: Message):
		await msg.channel.send( ' '.join( msg.content.split(' ')[ 1::len( msg.content.split(' ') )-1 ] ) )

	async def cp(self, msg: Message):
		msg.content = msg.content.replace('cp', '')
		if len( msg.content ) != 1:
			pre = self.bot.prefix
			self.bot.prefix = msg.content.strip()
			await msg.channel.send(f'successfully changed prefix from "{pre}" to "{self.bot.prefix}"')
		else:
			await msg.channel.send(f'the new prefix must be 1 char long, the provided prefix is {len(msg.content)}')

	async def whatsmyid(self, msg: Message):
		await msg.channel.send( msg.author.id )
