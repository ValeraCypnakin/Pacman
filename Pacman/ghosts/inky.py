import pygame
import collections
import math
from settings import *
from enemy_class import Enemy
from player_class import *
import pdb

vec = pygame.math.Vector2

class Inky(Enemy):
	def __init__(self, app, pos, player_obj, blinky_obj):
		self.color = 0x00ffff
		self.img = pygame.image.load("imgs/inky.png")
		super(Inky, self).__init__(app, pos, player_obj, self.img)
		self.possible_directions = [[1,0],[-1,0],[0,1],[0,-1]] #right, left, down, up
		self.blinky = blinky_obj
		self.direction = vec(0,0)


	def update(self):
		if len(self.app.coins) < 215:

			self.pix_pos += self.direction*self.speed
			find = self.find_next_tile(self.player.grid_pos, self.player.direction, self.blinky.grid_pos)

			if self.in_ghost_house:
				if self.grid_pos.x == 11 and self.grid_pos.y == 15:
					self.direction = vec(1,0)
				if self.grid_pos.x == 14 and self.grid_pos.y == 15:
					self.direction = vec(0,-1)
				if self.grid_pos.x == 14 and self.grid_pos.y == 11:
					self.in_ghost_house = False
			else:
				if self.time_to_move():
					if find != None:
						self.direction = vec(find[0],find[1])

		self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER+self.app.cell_width//2)//self.app.cell_width+1 # grid position x-axis
		self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER+self.app.cell_height//2)//self.app.cell_height+1 # grid position y-axis


	def find_next_tile(self, player_pos, player_dir, blinky_pos):

		direction_to_move = 0
		min_distance = 0


		x_dist = (player_pos.x+player_dir.x*2 - blinky_pos.x) * 2

		if x_dist != 0: 
			target_slope = (blinky_pos.y-(player_pos.y+player_dir.y*2))/(blinky_pos.x-(player_pos.x+player_dir.x*2))
			x_coord = blinky_pos.x + x_dist
			y_coord = x_dist * target_slope
			target_tile = vec(x_coord,y_coord)

			try:
				for index, direction in enumerate(self.possible_directions):
					if direction != self.direction*-1 and self.app.map[int(self.grid_pos.y+direction[1])][int(self.grid_pos.x+direction[0])] != '1' and self.app.map[int(self.grid_pos.y+direction[1])][int(self.grid_pos.x+direction[0])] != 'G':
						distance = math.sqrt(((self.grid_pos.x+direction[0])-target_tile.x)**2 + ((self.grid_pos.y+direction[1])-target_tile.y)**2)
						if distance < min_distance or min_distance == 0:
							min_distance = distance
							direction_to_move = index

				if direction_to_move == 0:
					return [1,0]
				elif direction_to_move == 1:
					return [-1,0]
				elif direction_to_move == 2:
					return [0,1]
				elif direction_to_move == 3:
					return [0,-1]

			except:
				self.grid_pos = vec(9,15) 


