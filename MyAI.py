# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
from collections import Counter


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################

		self._rowDimension = rowDimension
		self._colDimension  = colDimension
		self._totalMines = totalMines
		self._startX = startX
		self._startY = startY
		self._mineX = 0
		self._mineY = 0

		# Stores V and C tiles
		# C are uncovered tiles next to a covered unmarked tile
		# V are covered tiles next to an uncovered tile
		self.V = []
		self.C = []

		self.V_c = {}
		self.C_v = {}
		
		self.warnings = []
		self._numOfWarnings = 0

		
		self.uncovered = set([(startX, startY)])
		self.safeTiles = set()

		self._numberOfUncoveredTiles = 0
		self._flags = False

		self._recentX = startX
		self._recentY = startY
		self.board = [['x' for _ in range(rowDimension)] for _ in range(colDimension)]
		self.board[startX][startY] = 0


		pass
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################

		# number is the number of the uncovered tile
		
		# gets all adjacent, in bound tiles to the coordinates
		def get_adjacent_tiles(x, y):
			adjacentTiles = []
			# Top Left
			if x-1 >= 0 and y + 1 < self._rowDimension:
				adjacentTiles.append((x-1, y+1))
			# Top Middle
			if y + 1 < self._rowDimension:
				adjacentTiles.append((x, y+1))
			# Top Right
			if x+1 < self._colDimension and y + 1 < self._rowDimension:
				adjacentTiles.append((x+1, y+1))
			# Middle Left
			if x-1 < self._colDimension:
				adjacentTiles.append((x-1, y))
			# Middle Right
			if x+1 < self._colDimension:
				adjacentTiles.append((x+1,y))
			# Bottom Left
			if x-1 >= 0 and y - 1 >= 0:
				adjacentTiles.append([x-1, y-1])
			# Bottom Middle
			if y - 1 >= 0:
				adjacentTiles.append((x, y-1))
			# Bottom Right
			if x + 1 < self._colDimension and y - 1 >= 0:
				adjacentTiles.append((x+1, y-1))
			return adjacentTiles
		

		############## PRE-PROCESSING ##############

		# simple algorithm: adds tiles into V and C
		def simple_add_frontier(self):
			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[x][y] == 'x':
						continue

					elif (x,y) in self.uncovered and self.board[x][y] != 'x':
						adjacentTiles = self.get_adjacent_tiles(x,y)
						for adj_x, adj_y in adjacentTiles:
							if (adj_x, adj_y) not in self.uncovered and (adj_x, adj_y) not in self.warnings:
								if (x,y) not in self.C:
									self.C.append((x,y))
					
					elif (x,y) not in self.uncovered and self.board[x][y] != 'x':
						adjacentTiles = self.get_adjacent_tiles(x,y)
						for adj_x, adj_y in adjacentTiles:
							if (adj_x, adj_y) not in self.uncovered and (adj_x, adj_y) not in self.warnings:
								if (x,y) not in self.V:
									self.V.append((x,y))

		# advanced algorithm: add tiles into V and C, also computes C(v) and V(c)
		def advanced_add_frontier(self):
			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[x][y] == 'x':
						continue

					elif (x,y) in self.uncovered and self.board[x][y] != 'x':
						adjacentTiles = self.get_adjacent_tiles(x,y)
						for adj_x, adj_y in adjacentTiles:
							if (adj_x, adj_y) not in self.uncovered and (adj_x, adj_y) not in self.warnings:
								if (x,y) not in self.C:
									self.C.append((x,y))
								if (adj_x, adj_y) not in self.V:
									self.V.append((adj_x, adj_y))
									self.C_v[(adj_x, adj_y)] = []
								if (x,y) not in self.V_c:
									self.V_c[(x,y)] = []
								if (adj_x, adj_y) not in self.V_c[(x,y)]:
									self.V_c[(x,y)].append((adj_x, adj_y))
								if (x,y) not in self.C_v[(adj_x, adj_y)]:
									self.C_v[(adj_x, adj_y)].append((x,y))

			self.V.sort(key=lambda v:len(self.C_v[v]))
			

		# checks the var assignments with the board
		# v - the tile being verified, coordinates
		# value - int, 0 or 1
		# currWorld - the current assignment in backtrack
		def checkVarAssignment(self, v, value, currWorld):
			for c in self.C_v[v] :
				u = 0 #assigned neighbors of c
				mine_count = 0
				for c_neighbor in self.V_c[c] :
					if currWorld.get(c_neighbor) == None :
						#if the nieghbor is not present, it has no assigned value
						u+=1
					elif currWorld.get(c_neighbor) == 1:
						mine_count += 1
					# if value is 0, do nothing
				# c should have a label on the board
				el = self.board[c] - u #effective label
				if mine_count <= el <= mine_count+u :
					continue
				else :
					return False #constraints violated
			return True
		
		# recurses via backtracking to find a valid, full assignment
		def backtracking(self, currWorld):
			if len(currWorld) == len(self.V):
				# add current world to some instance variable for storage
				return
			v = self.V[len(currWorld)] #takes next unassigned tile
			for i in range(0,1) : #checks validity of values 0 and 1
				if checkVarAssignment(v, i, currWorld) :
					currWorld[v] = i
					self.backtracking(currWorld)
					currWorld.pop(v)
		
		
		# code for minimal AI 5x5
		if self._rowDimension == 5 and self._colDimension == 5:
			
			# Update the returned value of tile
			self.board[self._recentX][self._recentY] = number

			# iterate through board, finding safe tiles and adding them to the safeTiles set
			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[x][y] != 'x':
						# the tile is uncovered
						adjacentTiles = get_adjacent_tiles(x, y)
						if self.board[x][y] == 0:
							# the tile is 0, so we know the neighbors are safe
							for (tileX, tileY) in adjacentTiles:
								# if it is covered, add it to the sets if it has not been uncovered already
								if self.board[tileX][tileY] == 'x' and 0 <= tileX < self._rowDimension and 0<= tileY < self._colDimension and (tileX, tileY) not in self.uncovered:
									self.safeTiles.add((tileX, tileY))
									self.uncovered.add((tileX, tileY))
						# currently no check for if the tile is 1, ignores
			
			# make the moves we know are safe
			if self.safeTiles:
				# pops the safe tile, saves the coordinates, and uncovers
				tile = self.safeTiles.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				return Action(AI.Action.UNCOVER, tile[0], tile[1])
			
			# move randomly, if no safe moves can be made
			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					# if a spot is covered, uncover it
					if self.board[x][y] == 'x' and (x,y) not in self.uncovered:
						self.uncovered.add((x,y))
						self._recentX = x
						self._recentY = y
						return Action(AI.Action.UNCOVER, x, y)
					
			return Action(AI.Action.LEAVE)

		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
