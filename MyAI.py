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

		
		self.uncovered = set([(startX, colDimension-startY-1)])
		self.safeTiles = set()

		self._numberOfUncoveredTiles = 0
		self._flags = False
		self._flagged_tiles = []

		self._recentX = startX
		self._recentY = colDimension-startY-1
		self.board = [['x' for _ in range(rowDimension)] for _ in range(colDimension)]
		self.board[colDimension-startY-1][startX] = 0


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
		def get_adjacent_tiles( x, y):
			adjacentTiles = []
			# bottom Left
			if x-1 >= 0 and y + 1 < self._rowDimension:
				adjacentTiles.append((x-1, y+1))
			# bottom Middle
			if y + 1 < self._rowDimension:
				adjacentTiles.append((x, y+1))
			# bottom Right
			if x+1 < self._colDimension and y + 1 < self._rowDimension:
				adjacentTiles.append((x+1, y+1))
			# Middle Left
			if 0 <= x-1 < self._colDimension:
				adjacentTiles.append((x-1, y))
			# Middle Right
			if x+1 < self._colDimension:
				adjacentTiles.append((x+1,y))
			# top Left
			if x-1 >= 0 and y - 1 >= 0:
				adjacentTiles.append((x-1, y-1))
			# top Middle
			if y - 1 >= 0:
				adjacentTiles.append((x, y-1))
			# top Right
			if x + 1 < self._colDimension and y - 1 >= 0:
				adjacentTiles.append((x+1, y-1))
			return adjacentTiles
		

		############## PRE-PROCESSING ##############

		# advanced algorithm: add tiles into V and C, also computes C(v) and V(c)
		def advanced_add_frontier():
			# clear the V, C, V(c), and C(v) lists
			self.V.clear()
			self.C.clear()
			self.V_c.clear()
			self.C_v.clear()

			for x in range(self._rowDimension):
				for y in range(self._colDimension):
					if self.board[x][y] == 'm':
						continue

					if (x,y) in self.uncovered:
						adjacentTiles = get_adjacent_tiles(x,y)
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
			print("self.C_v", self.C_v)
			print("self.V_c", self.V_c)
			print("self.c", self.C)
			print("self.V", self.V)
			

		# checks the var assignments with the board
		# v - the tile being verified, coordinates
		# value - int, 0 or 1
		# currWorld - the current assignment in backtrack
		def checkVarAssignment(v, value, currWorld):
			for c in self.C_v[v] :
				print("Checking ", c)
				u = 0 #assigned neighbors of c
				mine_count = 0
				for c_neighbor in self.V_c[c] :
					if c_neighbor not in currWorld :
						#if the neighbor is not present, it has no assigned value
						u+=1
					elif currWorld[c_neighbor] == 1:
						mine_count += 1
					# if value is 0, do nothing
				# c should have a label on the board
				if value == 1:
					mine_count+=1
				el = self.board[c[1]][c[0]] - u if self.board[c[1]][c[0]] - u > 0 else 0 #effective label
				print(f"Tile {c} has clue: {self.board[c[1]][c[0]]}, effective label: {el}, u: {u}, mine_count: {mine_count}")
				if not(mine_count <= el <= mine_count+u) :
					print("Checking var: NO")
					return False
				print("Checking var: OK")
			return True

		
		# recurses via backtracking to find a valid, full assignment
		def backtracking(currWorld, possibleBoards):
			if len(currWorld) == len(self.V):
				#print("Backtracking base case")
				# add current world to some instance variable for storage
				possibleBoards.append(currWorld.copy())
				return
			v = self.V[len(currWorld)] #takes next unassigned tile
			print("next unassigned tile ", v)
			for i in [0,1] : #checks validity of values 0 and 1
				if checkVarAssignment(v, i, currWorld) :
					currWorld[v] = i
					backtracking(currWorld, possibleBoards)
		
		# checks the boards 
		def boardChecker(possibleBoards) :
			# find most commonly marked tile to flag as mine
			possibleMines = {}
			possibleSafe = []
			for board in possibleBoards:
				for key, value in board.items() :
					if value == 1:
						if key in possibleMines:
							# increment count by 1
							possibleMines[key] += 1
						else :
							possibleMines[key] = 1
						if key in possibleSafe :
							possibleSafe.remove(key)
					else :
						possibleSafe.append(key)
			print("Boardchecking finished")
			return possibleMines, possibleSafe
		
		# code for minimal AI 5x5
		if self._rowDimension == 5 and self._colDimension == 5:
			
			# Update the returned value of tile
			self.board[self._recentY][self._recentX] = number

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
								if self.board[tileY][tileX] == 'x' and 0 <= tileX < self._rowDimension and 0<= tileY < self._colDimension and (tileX, tileY) not in self.uncovered:
									self.safeTiles.add((tileX, tileY))
									self.uncovered.add((tileX, tileY))
						# currently no check for if the tile is 1, ignores
			
			# make the moves we know are safe
			if self.safeTiles:
				# pops the safe tile, saves the coordinates, and uncovers
				tile = self.safeTiles.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				# added the line to append the tile to uncovered set
				self.uncovered.append((self._recentX, self._recentY))
				return Action(AI.Action.UNCOVER, tile[0], tile[1])

			# flag tiles that are believed to be mines
			if self.warnings:
				# pops the warnings, saves the coordinates, and flags
				tile = self.warnings.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				self._flagged_tiles.append((self._recentX, self._recentY))
				return Action(AI.Action.FLAG, tile[0], tile[1])
			
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


		# Main Loop for 8x8, 16x16:
		else :
			if self.board[self._recentY][self._recentX] == 'x':
				print("Tile number ", number)
				self.board[self._recentY][self._recentX] = number

			print("Current Board")
			for i in range(self._rowDimension):
				for j in range(self._colDimension):
					print(self.board[i][j], end =" ")
				print("\n")
			
			if len(self.safeTiles) == 0 and len(self.warnings)==0 and len(self._flagged_tiles) != self._totalMines and number != 0:
				#print("Processing")
				# update returned tile
				possibleBoards = []
				advanced_add_frontier() # preprocess
				#print("after advanced add frontier")
				backtracking({}, possibleBoards)
				print("Number of possible boards: " + str(len(possibleBoards)))
				#print("Backtracking finished")
				# check boards for most common marked mine+safe tile, and mark it
				#print("possibleBoards", possibleBoards)

				mines, safe = boardChecker(possibleBoards)
				

				if len(safe) > 0 :
					print("Possible safe ", safe[0])
					self.safeTiles.add(safe[0]) #removes safe tile
				# loop through to find highest value key
				highest_value = 0
				highest_tile = None
				#print("Highest_Value")
				for key, value in mines.items():
					if value > highest_value:
						highest_value = value
						highest_tile = key
				if highest_tile != None :
					self.warnings.append(highest_tile)
				print("Possible mines ", highest_tile)

			elif number == 0:
				print("Safe tile ", self._recentX, " ", self._recentY)
				safe = get_adjacent_tiles(self._recentX, self._recentY)

				for tileX, tileY in safe:
					if (tileX, tileY) not in self.uncovered :
						self.safeTiles.add((tileX, tileY))

			#print("Picking action")
			# copied from minimal
			# then find a safe tile and return an action
			print("Safe Tiles", self.safeTiles)
			if self.safeTiles:
				# pops the safe tile, saves the coordinates, and uncovers
				tile = self.safeTiles.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				print("Uncovering ", tile)
				self.uncovered.add((tile[0], tile[1]))
				return Action(AI.Action.UNCOVER, tile[0], self._colDimension-tile[1]-1)
			#print("Warnings", self.warnings)
			if self.warnings:
				# pops the warnings, saves the coordinates, and flags
				tile = self.warnings.pop()
				self._recentX = tile[0]
				self._recentY = tile[1]
				self.board[tile[1]][tile[0]] = 'm'
				print("Flagging ", tile)
				self._flagged_tiles.append((tile[0], tile[1]))
				return Action(AI.Action.FLAG, tile[0], self._colDimension-tile[1]-1)
			
			if not self.safeTiles :
				for x in range(self._rowDimension):
					for y in range(self._colDimension):
						# if a spot is covered, uncover it
						if self.board[x][y] == 'x' and (y,x) not in self.uncovered:
							self._recentX = x
							self._recentY = y
							self.uncovered.add((x, y))
							print("Random uncovering ", x, " ", y)
							return Action(AI.Action.UNCOVER, x, self._colDimension-y-1)
		print("Leaving")
		return Action(AI.Action.LEAVE)
		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################