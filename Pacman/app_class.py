import pygame, sys
from player_class import *
from enemy_class import *
from blinky import *
from inky import *
from pinky import *
from clyde import *
import neat
import pickle
pygame.init()
vec = pygame.math.Vector2

class App:
	def __init__(self):
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		self.state = 'playing'
		self.running = True
		self.cell_width = MAZE_WIDTH//28
		self.cell_height = MAZE_HEIGHT//30
		self.walls = []
		self.map = []
		self.background = pygame.image.load('imgs/background.png').convert()
		self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))
		self.generation = -1
		self.best_genome = None

	def run(self, genomes, config):
		self.generation += 1

		for _, g in genomes:
			self.running = True
			self.hit_by_ghost = False
			self.coins = []
			self.enemies = []
			self.enemy_pos = []
			self.map = []
			self.game_start_time = 0
			self.loops_since_score_chg = 0
			self.prev_score = 0
			self.load()
			self.time_since_last_coin = pygame.time.get_ticks()

			self.net = neat.nn.FeedForwardNetwork.create(g, config)
			self.player = Player(self, vec(13,23))
			g.fitness = 0

			while self.running:
				if self.state == 'playing':
					self.playing_update()
					self.playing_draw()
					g.fitness = self.player.current_score
					if self.hit_by_ghost:
						self.running = False

				elif self.state == 'player_won':
					self.player_won()

				self.clock.tick(FPS)


	def draw_text(self, words, screen, pos, size, color, font_name, centered=False):
		font = pygame.font.SysFont(font_name, size)
		text = font.render(words, False, color)
		text_size = text.get_size()
		if centered:
			pos[0] = pos[0] - text_size[0] // 2
			pos[1] = pos[1] - text_size[1] // 2
		screen.blit(text, pos)

	def load(self):
		self.game_start_time = pygame.time.get_ticks()

		with open('walls.txt', 'r') as file:
			for yindex, line in enumerate(file):
				for xindex, char in enumerate(line):
					if char == '1':
						self.walls.append(vec(xindex, yindex))
					elif char == 'C':
						self.coins.append(vec(xindex, yindex))
					elif char in ['2','3','4','5']:
						self.enemy_pos.append(vec(xindex, yindex))
					elif char == 'G':
						pygame.draw.rect(self.background, BLACK, (xindex*self.cell_width, yindex*self.cell_height, self.cell_width, self.cell_height))

				self.map.append([char for char in line])

	def make_enemies(self, player_obj):
		enemies = []
		for index, position in enumerate(self.enemy_pos):
			if index == 0:
				blinky_obj = Blinky(self, position, player_obj)
				enemies.append(blinky_obj)	
			elif index == 1:
				enemies.append(Pinky(self, position, player_obj))
			elif index == 2:
				enemies.append(Inky(self, position, player_obj, blinky_obj))
			else:
				enemies.append(Clyde(self, position, player_obj))

		return enemies


	def playing_update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					self.hit_by_ghost = True

		num_coins = self.player.num_coins_on_path()

		num_coins_left = num_coins[0]
		num_coins_right = num_coins[1]
		num_coins_up = num_coins[2]
		num_coins_down = num_coins[3]
		distance_to_blinky = 0
		distance_to_pinky = 0
		distance_to_inky = 0
		distance_to_clyde = 0



		outputs = self.net.activate((
			num_coins_left,
			num_coins_right,
			num_coins_up,
			num_coins_down,
			distance_to_blinky,
			distance_to_pinky,
			distance_to_inky,
			distance_to_clyde
			))


		maxVal = 0
		direction = 0
		for idx, output in enumerate(outputs):
			if output > maxVal:
				maxVal = output
				direction = idx


		if maxVal > 0.8:
			if direction == 0:
				self.player.move(LEFT)
			elif direction == 1:
				self.player.move(RIGHT)
			elif direction == 2:
				self.player.move(UP)
			elif direction == 3:
				self.player.move(DOWN)

		self.player.update()


		if self.time_since_last_coin + 2500 < pygame.time.get_ticks():
			self.hit_by_ghost = True

		if len(self.coins) == 0:
			self.state = 'player_won'


	def playing_draw(self):
		self.screen.fill(BLACK)
		self.screen.blit(self.background, (TOP_BOTTOM_BUFFER//2, TOP_BOTTOM_BUFFER//2))
		self.draw_coins()
		self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score), self.screen, [60, 2], START_TEXT_SIZE, WHITE, START_FONT)
		self.draw_text('GENERATION: {}'.format(self.generation), self.screen, [350, 2], START_TEXT_SIZE, WHITE, START_FONT)
		self.player.draw() # draw player


		pygame.display.update()

	def draw_coins(self):
		for coin in self.coins:
			pygame.draw.circle(self.screen, (124,123,7), 
				((int(coin.x*self.cell_width)+self.cell_width//2)+TOP_BOTTOM_BUFFER//2, 
					(int(coin.y*self.cell_height)+self.cell_height//2)+TOP_BOTTOM_BUFFER//2), 3)



	def player_won(self):
		self.draw_text('YOU WON!', self.screen, [WIDTH//2, HEIGHT//2 - 100], 36, (170, 132, 58), START_FONT, centered=True) # PUSH SPACE BAR text
		self.draw_text('PUSH SPACE BAR TO PLAY AGAIN', self.screen, [WIDTH//2, HEIGHT//2 + 100], 28, (44, 167, 198), START_FONT, centered=True) # PUSH SPACE BAR text
		pygame.display.update()


	def player_lost(self):
		self.__init__()
