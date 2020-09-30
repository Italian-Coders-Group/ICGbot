import modules

@modules.Command
async def kick(msg):
  await msg.mentions[0].kick()
