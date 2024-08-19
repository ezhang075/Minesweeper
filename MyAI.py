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
		self._startX = startX
		self._startY = colDimension - startY - 1

		self.V = []
		self.C = []

		self.V_c = {}
		self.C_v = {}

		self.warnings = set()
		self.uncovered = set([(self._startX, self._startY)])
		self.safeTiles = set()

		self._recentX = self._startX
		self._recentY = self._startY
		self.board = [['x' for _ in range(rowDimension)] for _ in range(colDimension)]
		self.board[self._recentY][self._recentX] = 0

		# Initialize the missing attribute _flagged_tiles
		self._flagged_tiles = set()

	def get_adjacent_tiles(self, x, y):
		adjacentTiles = []
		# Bottom Left
		if x - 1 >= 0 and y + 1 < self._rowDimension:
			adjacentTiles.append((x - 1, y + 1))
		# Bottom Middle
		if y + 1 < self._rowDimension:
			adjacentTiles.append((x, y + 1))
		# Bottom Right
		if x + 1 < self._colDimension and y + 1 < self._rowDimension:
			adjacentTiles.append((x + 1, y + 1))
		# Middle Left
		if x - 1 >= 0:
			adjacentTiles.append((x - 1, y))
		# Middle Right
		if x + 1 < self._colDimension:
			adjacentTiles.append((x + 1, y))
		# Top Left
		if x - 1 >= 0 and y - 1 >= 0:
			adjacentTiles.append((x - 1, y - 1))
		# Top Middle
		if y - 1 >= 0:
			adjacentTiles.append((x, y - 1))
		# Top Right
		if x + 1 < self._colDimension and y - 1 >= 0:
			adjacentTiles.append((x + 1, y - 1))
		return adjacentTiles

	def advanced_add_frontier(self):
		self.V.clear()
		self.C.clear()
		self.V_c.clear()
		self.C_v.clear()

		for x in range(self._rowDimension):
			for y in range(self._colDimension):
				if self.board[y][x] == 'm':
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
			effective_label = self.board[c[1]][c[0]] - u if self.board[c[1]][c[0]] - u > 0 else 0
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
			print("uncovering")
			return Action(AI.Action.UNCOVER, tile[0], self._colDimension - tile[1] - 1)

		if self.warnings:
			tile = self.warnings.pop()
			self._recentX = tile[0]
			self._recentY = tile[1]
			self.board[tile[1]][tile[0]] = 'm'
			self._flagged_tiles.add((tile[0], tile[1]))
			print("flagging")
			return Action(AI.Action.FLAG, tile[0], self._colDimension - tile[1] - 1)

		for x in range(self._rowDimension):
			for y in range(self._colDimension):
				if self.board[y][x] == 'x' and (x, y) not in self.uncovered:
					print("Random Uncovering")
					self._recentX = x
					self._recentY = y
					self.uncovered.add((x, y))
					return Action(AI.Action.UNCOVER, x, self._colDimension - y - 1)

		return Action(AI.Action.LEAVE)
		
	def getAction(self, number: int) -> "Action Object":
		print(f"Uncovered tile: ({self._recentX}, {self._recentY}), Value: {number}")

		# 5x5 minimal code
		if self._rowDimension == 5 and self._colDimension == 5:
			self.board[self._recentY][self._recentX] = number

			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[y][x] != 'x':
						adjacentTiles = self.get_adjacent_tiles(x, y)
						if self.board[y][x] == 0:
							for (tileX, tileY) in adjacentTiles:
								if self.board[tileY][tileX] == 'x' and (tileX, tileY) not in self.uncovered:
									self.safeTiles.add((tileX, tileY))
									self.uncovered.add((tileX, tileY))
									print(f"Added safe tile: ({tileX}, {tileY})")

			return self.revaluate_after_guess()
		# Draft code
		else:
			if self.board[self._recentY][self._recentX] == 'x':
				self.board[self._recentY][self._recentX] = number

			print("Current Board")
			for i in range(self._rowDimension):
				for j in range(self._colDimension):
					print(self.board[i][j], end =" ")
				print("\n")

			if len(self.safeTiles) == 0 and len(self.warnings) == 0 and len(self._flagged_tiles) != self._totalMines and number != 0:
				possibleBoards = []
				self.advanced_add_frontier()
				print(f"Frontier added. V: {self.V}, C: {self.C}")
				self.backtracking({}, possibleBoards)

				print(f"Generated {len(possibleBoards)} possible board configurations")
				mines, safe = self.boardChecker(possibleBoards)

				if len(safe) > 0:
					self.safeTiles.add(safe[0])
					print(f"Identified safe tile: {safe[0]}")

				highest_value = 0
				highest_tile = None

				for key, value in mines.items():
					if value > highest_value:
						highest_value = value
						highest_tile = key
				if highest_tile is not None:
					self.warnings.add(highest_tile)
					print(f"Flagging potential mine: {highest_tile}")

			elif number == 0:
				# tile is 0, so all surrounding tiles are safe
				safe = self.get_adjacent_tiles(self._recentX, self._recentY)
				for tileX, tileY in safe:
					if (tileX, tileY) not in self.uncovered:
						self.safeTiles.add((tileX, tileY))
						print(f"Safe tiles around 0: ({tileX}, {tileY})")
			
			# marks safe tiles
			if self.safeTiles:
				tile = self.safeTiles.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				self.uncovered.add((tile[0], tile[1]))
				return Action(AI.Action.UNCOVER, tile[0], self._colDimension - tile[1] - 1)

			# marks mines on the board
			if self.warnings:
				tile = self.warnings.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				self.board[tile[1]][tile[0]] = 'm'
				self._flagged_tiles.add((tile[0], tile[1]))
				return Action(AI.Action.FLAG, tile[0], self._colDimension - tile[1] - 1)

			# If all mines have been flagged, uncover remaining safe tiles
			if len(self._flagged_tiles) == self._totalMines:
				print("All mines flagged, uncovering remaining tiles.")
				for x in range(self._rowDimension):
					for y in range(self._colDimension):
						if self.board[y][x] == 'x' and (x, y) not in self.uncovered:
							self._recentX = x
							self._recentY = y
							self.uncovered.add((x, y))
							print(f"Uncovering {x}, {self._colDimension - y - 1}")
							return Action(AI.Action.UNCOVER, x, self._colDimension - y - 1)

			# if all options have been exhausted, proceed with an educated guess

			print("Checking uncovered tiles with covered neighbors to mark mines.")
			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[y][x] != 'x' and (x, y) in self.uncovered:
						adjacentTiles = self.get_adjacent_tiles(x, y)
						covered_neighbors = [(tileX, tileY) for (tileX, tileY) in adjacentTiles if self.board[tileY][tileX] == 'x']
						if len(covered_neighbors) > 0 and len(covered_neighbors) == self.board[y][x]:
							for (tileX, tileY) in covered_neighbors:
								if (tileX, tileY) not in self.warnings:
									self.warnings.add((tileX, tileY))
									print(f"Marking tile ({tileX}, {tileY}) as a mine.")
									
			print("Safe tiles: ", self.safeTiles)
			print("Warning tiles: ", self.warnings)

			return self.revaluate_after_guess()
		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################