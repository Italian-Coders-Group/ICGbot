import modules

@modules.Command
async def hello(msg):
	await msg.channel.send(f'hello {msg.author.name}!')