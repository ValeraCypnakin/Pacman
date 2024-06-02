import neat
import os
from app_class import *

try:
    import cPickle as pickle
except ImportError:
    import pickle

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, 
		neat.DefaultStagnation, config_path)


	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	p.add_reporter(neat.StatisticsReporter())
	p.add_reporter(neat.Checkpointer(1))

	app = App()

	winner = p.run(app.run,100)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)
