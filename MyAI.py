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

class MyAI(AI):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		

		self._rowDimension = rowDimension
		self._colDimension = colDimension
		self._totalMines = totalMines
		self._startX = rowDimension - startY - 1
		self._startY = startX

		# set of covered tiles that are next to an uncovered tile
		self.V = []
		# set of uncovered tiles that are next to a covered tile
		self.C = []

		# all tiles in V that are neighbors of c (an uncovered tile)
		self.V_c = {}
		# all tiles in C that are neighbors of v (a covered tile)
		self.C_v = {}

		self.warnings = set()
		self.uncovered = set([(self._startX, self._startY)])
		self.safeTiles = set()

		self._recentX = self._startX
		self._recentY = self._startY
		self.board = [['x' for _ in range(colDimension)] for _ in range(rowDimension)]
		self.board[self._recentX][self._recentY] = 0

		# Initialize the missing attribute _flagged_tiles
		self._flagged_tiles = set()

	# gets adjacent tiles based on position on self.board, x->row # and y->col #
	def get_adjacent_tiles(self, row, col):
		adjacentTiles = []
		# Top Left
		if row - 1 >= 0 and col + 1 < self._colDimension:
			adjacentTiles.append((row - 1, col + 1))
		# Middle left
		if col + 1 < self._colDimension:
			adjacentTiles.append((row, col + 1))
		# Bottom Left
		if row + 1 < self._rowDimension and col + 1 < self._colDimension:
			adjacentTiles.append((row + 1, col + 1))
		# Top
		if row - 1 >= 0:
			adjacentTiles.append((row - 1, col))
		# Bottom 
		if row + 1 < self._rowDimension:
			adjacentTiles.append((row + 1, col))
		# Top Right
		if row - 1 >= 0 and col - 1 >= 0:
			adjacentTiles.append((row - 1, col - 1))
		# Middle Right
		if col - 1 >= 0:
			adjacentTiles.append((row, col - 1))
		# Bottom Right
		if row + 1 < self._rowDimension and col - 1 >= 0:
			adjacentTiles.append((row + 1, col - 1))
		return adjacentTiles

	""" adds tiles to V, C, V_c, and C_v based on their neighbors
	V - set of covered tiles that are next to an uncovered tile 
	C - set of uncovered tiles that are next to a covered tile
	V_c - all tiles in V that are neighbors of c (an uncovered tile)
	C_v - all tiles in C that are neighbors of v (a covered tile) """
	def advanced_add_frontier(self):
		self.V.clear()
		self.C.clear()
		self.V_c.clear()
		self.C_v.clear()

		for x in range(self._rowDimension):
			for y in range(self._colDimension):
				if self.board[x][y] == 'm':
					continue

				if (x, y) in self.uncovered:
					adjacentTiles = self.get_adjacent_tiles(x, y)
					for adj_x, adj_y in adjacentTiles:
						if (adj_x, adj_y) not in self.uncovered and (adj_x, adj_y) not in self.warnings:
							if (x, y) not in self.C:
								self.C.append((x, y))
							if (adj_x, adj_y) not in self.V:
								self.V.append((adj_x, adj_y))
								self.C_v[(adj_x, adj_y)] = []
							if (x, y) not in self.V_c:
								self.V_c[(x, y)] = []
							if (adj_x, adj_y) not in self.V_c[(x, y)]:
								self.V_c[(x, y)].append((adj_x, adj_y))
							if (x, y) not in self.C_v[(adj_x, adj_y)]:
								self.C_v[(adj_x, adj_y)].append((x, y))

		self.V.sort(key=lambda v: len(self.C_v[v]))

	def checkVarAssignment(self, v, value, currWorld):
		for c in self.C_v[v]:
			u = 0  # Number of unassigned neighbors
			mine_count = 0
			for c_neighbor in self.V_c[c]:
				if c_neighbor not in currWorld:
					u += 1
				elif currWorld[c_neighbor] == 1:
					mine_count += 1
			if value == 1:
				mine_count += 1
			effective_label = self.board[c[0]][c[1]] - u if self.board[c[0]][c[1]] - u > 0 else 0
			
			if not (mine_count <= effective_label <= mine_count + u):
				return False
		return True

	def backtracking(self, currWorld, possibleBoards):
		if len(currWorld) == len(self.V):
			possibleBoards.append(currWorld.copy())
			return
		v = self.V[len(currWorld)]
		for i in [0, 1]:
			if self.checkVarAssignment(v, i, currWorld):
				currWorld[v] = i
				self.backtracking(currWorld, possibleBoards)

	def boardChecker(self, possibleBoards):
		possibleMines = {}
		possibleSafe = []
		for board in possibleBoards:
			for key, value in board.items():
				if value == 1:
					if key in possibleMines:
						possibleMines[key] += 1
					else:
						possibleMines[key] = 1
					if key in possibleSafe:
						possibleSafe.remove(key)
				else:
					possibleSafe.append(key)
		return possibleMines, possibleSafe

	def revaluate_after_guess(self):
		if self.safeTiles:
			tile = self.safeTiles.pop()
			self._recentX = tile[0]
			self._recentY = tile[1]
			self.uncovered.add((tile[0], tile[1]))
			return Action(AI.Action.UNCOVER, tile[1], self._rowDimension - tile[0] - 1)

		if self.warnings:
			tile = self.warnings.pop()
			self._recentX = tile[0]
			self._recentY = tile[1]
			self.board[tile[0]][tile[1]] = 'm'
			self._flagged_tiles.add((tile[0], tile[1]))
			#print("flagging")
			return Action(AI.Action.FLAG, tile[1], self._rowDimension - tile[0] - 1)
		
		for x in range(self._rowDimension):
			for y in range(self._colDimension):
				if self.board[x][y] == 'x' and (x, y) not in self.uncovered:
					#print("Random Uncovering ", x, y)
					self._recentX = x
					self._recentY = y
					self.uncovered.add((x, y))
					return Action(AI.Action.UNCOVER, y, self._rowDimension - x - 1)

		return Action(AI.Action.LEAVE)
		
	def getAction(self, number: int) -> "Action Object":
		#print(f"Uncovered tile: ({self._recentX}, {self._recentY}), Value: {number}")

		# 5x5 minimal code
		if self._rowDimension == 5 and self._colDimension == 5:
			self.board[self._recentX][self._recentY] = number

			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[x][y] != 'x':
						adjacentTiles = self.get_adjacent_tiles(x, y)
						if self.board[x][y] == 0:
							for (tileX, tileY) in adjacentTiles:
								if self.board[tileX][tileY] == 'x' and (tileX, tileY) not in self.uncovered:
									self.safeTiles.add((tileX, tileY))
									self.uncovered.add((tileX, tileY))

			return self.revaluate_after_guess()
		# Draft code
		else:
			if self.board[self._recentX][self._recentY] == 'x':
				self.board[self._recentX][self._recentY] = number

			""" print("Current Board")
			for i in range(self._rowDimension):
				for j in range(self._colDimension):
					print(self.board[i][j], end =" ")
				print("\n") """

			self.advanced_add_frontier()

			if len(self.safeTiles) == 0 and len(self.warnings) == 0 and len(self._flagged_tiles) != self._totalMines and number != 0:
				possibleBoards = []
				
				#print(f"Frontier added. V: {self.V}, C: {self.C}")
				self.backtracking({}, possibleBoards)

				#print(f"Generated {len(possibleBoards)} possible board configurations")
				mines, safe = self.boardChecker(possibleBoards)

				if len(safe) > 0:
					self.safeTiles.add(safe[0])
					#print(f"Identified safe tile: {safe[0]}")

				highest_value = 0
				highest_tile = None

				for key, value in mines.items():
					if value > highest_value:
						highest_value = value
						highest_tile = key
				if highest_tile is not None:
					self.warnings.add(highest_tile)
					#print(f"Flagging potential mine: {highest_tile}")

			elif number == 0:
				# tile is 0, so all surrounding tiles are safe
				safe = self.get_adjacent_tiles(self._recentX, self._recentY)
				for tileX, tileY in safe:
					if (tileX, tileY) not in self.uncovered:
						self.safeTiles.add((tileX, tileY))
						#print(f"Safe tiles around 0: ({tileX}, {tileY})")
			
			# marks safe tiles
			if self.safeTiles:
				tile = self.safeTiles.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				self.uncovered.add((tile[0], tile[1]))
				return Action(AI.Action.UNCOVER, tile[1], self._rowDimension - tile[0] - 1)

			# marks mines on the board
			if self.warnings:
				tile = self.warnings.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				self.board[tile[0]][tile[1]] = 'm'
				self._flagged_tiles.add((tile[0], tile[1]))
				return Action(AI.Action.FLAG, tile[1], self._rowDimension - tile[0] - 1)

			# If all mines have been flagged, uncover remaining safe tiles
			if len(self._flagged_tiles) == self._totalMines:
				#print("All mines flagged, uncovering remaining tiles.")
				for x in range(self._rowDimension):
					for y in range(self._colDimension):
						if self.board[x][y] == 'x' and (x, y) not in self.uncovered:
							self._recentX = x
							self._recentY = y
							self.uncovered.add((x, y))
							#print(f"Uncovering {x}, {self._colDimension - y - 1}")
							return Action(AI.Action.UNCOVER, y, self._rowDimension - x - 1)

			# if all options have been exhausted, proceed with an educated guess
			for uncovered in self.C :
				# for each tile with covered neighbors, compare the number of neighbors and the value
				u = 0 #unmarked neighbors
				m = 0 #marked mines nearby
				covered = []
				for c_neighbor in self.V_c[uncovered]:
					if c_neighbor not in self.uncovered and c_neighbor not in self._flagged_tiles:
						u += 1
						covered.append(c_neighbor)
					elif self.board[c_neighbor[0]][c_neighbor[1]] == 'm':
						m += 1

				if self.board[uncovered[0]][uncovered[1]] == m :
					# if the value of the tile == num of marked mines, it's covered neighbors are safe
					for neighbor in covered :
						self.safeTiles.add(neighbor)
				elif self.board[uncovered[0]][uncovered[1]]-m == u :
					# all the covered neighbors are mines
					for neighbor in covered :
						self.warnings.add(neighbor)

			#print("Safe tiles: ", self.safeTiles)
			#print("Warning tiles: ", self.warnings)

			return self.revaluate_after_guess()
		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################