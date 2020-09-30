import modules
import utils
from pathlib import Path


@modules.Command
async def showcode(msg):
	module = msg.content.replace('showcode', '', 1).strip()
	# there's a parameter?
	if module == '':
		await msg.channel.send('missing parameter <modulename>!')
		return
	else:
		# use correct path
		if module not in ['commands', 'modules']:
			path = Path(f'./modules/{module}.py')
			# check if exists
			if not path.exists():
				await msg.channel.send(f"module {module} does't exist!")
				return
			# get author
			author = msg.channel.guild.get_member(modules.Modules.savedata[module][0])
		else:
			# bot files
			path = Path(f'./{module}.py')
			author = 'ENDERZOMBI102'
		# read code file
		with path.open('r') as file:
			code = file.read().replace("`", "\`")
		# create embed
		embed = utils.embed(
			title=f"showing {module}'s code",
			content=f'```python\n{code}```',
			color=utils.getColor('255,255,255')
		)
		embed.set_footer(text=f'Made by {author}')
		# send
		await msg.channel.send(embed=embed)
