# ICGbot
Ultimate customization, Made by ENDERZOMBI102


## Whats this?
This a discord bot, with the possibility to be extended directly from discord, by using code blocks or .py files.
Those extensions, called modules, are the real deal with this bot, as they can do anything, from implemnting a ban command, to a database-backed chat game!


## Ok cool, but how do i implement a command?
Glad you asked! its simple, in a code block or .py file, you make a coroutine like this:<br>
<pre><code>
@modules.Command
async def commandName(msg: discord.Message):
  pass  # do stuff with the message
</code></pre>
the coroutine name will be the command name, pretty simple uh?<br>
the modules file will be imported automatically by the bot, so no worries about it!


## Fantastic! but there seems to be some hardcoded stuff, why?
This is a bot principally made a the Italian Coders group discord server, so it has hardcoded some ICG stuff, like permissions and ids.


## What if i want to implement commands without the module system?
Just add an async method to the commands.py file, like you would do on a module, but without the <code>@modules.Command</code>decorator.

## And if i want to disable modules?
well, then idk what you're doing here, but anyway, you can, just comment out the module command inside bot.py.
