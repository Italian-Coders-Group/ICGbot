from time import sleep

import bot
import multiprocessing


# little function to make sure the bot can be exited and restarted
def Bot():
	instance = bot.Bot()
	instance.prefix = '!'
	instance.run()


def run():
	while True:
		instance = multiprocessing.Process(target=Bot)
		instance.start()
		while instance.is_alive():
			sleep(100)
		del instance


if __name__ == '__main__':
	# run bot _FOR ETERNITY_
	run()
