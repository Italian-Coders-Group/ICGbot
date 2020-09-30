
import modules
import os

@modules.Command
async def pipinstall(msg):
  await msg.channel.send( os.system(f'pip install {msg.content.split(" ")[1]}') )
