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
import random


class MyAI(AI):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################

        self.__rowDimension = rowDimension
        self.__colDimension = colDimension
        self.__startX = startX
        self.__startY = startY
        self.__totalMines = totalMines

        # Current X Y coord keep track of which cell the AI just make a move on
        self.__currentX = self.__startY
        self.__currentY = self.__startX

        # Initialize map, with starting cell is guaranteed to be safe
        self.__Map = []
        for i in range(self.__colDimension):
            self.__Map.append([])
            for j in range(self.__rowDimension, 0, -1):
                self.__Map[i].append(-2)

        self.total_safe_tiles = self.__rowDimension * self.__colDimension - self.__totalMines
        self.__safeList = []
        self.__mineList = []
        self.__uncoveredList = []
        self.__flaggedList = []
        self.__frontier = []

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################

        # Number in parameter stands for perception number for previous move
        # 0 or positive numbers stands for number of mines around the cell
        # -1 stands for there is a mine on the cell(we flag it so we believed it)
        # NOTICE in this approach, we try to avoid flag uncertain cells, and thus
        # avoid unflag
        try:
            # update map
            self.__Map[self.__currentY][self.__currentX] = number
            for tile in self.__uncoveredList + self.__flaggedList:
                if tile in self.__safeList:
                    self.__safeList.remove(tile)
                if tile in self.__mineList:
                    self.__mineList.remove(tile)

            if len(self.__flaggedList) == self.__totalMines:
                return self.rest_are_all_safe_or_mines(True)
            elif len(self.__uncoveredList) == self.total_safe_tiles:
                return self.rest_are_all_safe_or_mines(False)
            else:
                pass
            # If the previous uncover return 0, add adjacent cells to safe list
            if number == 0:
                self.getSafeList(self.__currentY, self.__currentX)
            elif number > 0:
                self.__frontier.append([self.__currentY, self.__currentX])

            self.getMines()

            # print("mine list: ")
            # print(self.__mineList)
            #
            # print("safe list: ")
            # print(self.__safeList)

            # If there is no more safe move, search for flag move or other safe move
            if len(self.__safeList) == 0:
                if len(self.__mineList) != 0:
                    self.__flaggedList.append(self.__mineList[0])
                    self.__currentY = self.__mineList[0][0]
                    self.__currentX = self.__mineList[0][1]
                    self.__mineList.pop(0)
                    return Action(AI.Action.FLAG, self.__currentY, self.__currentX)
                else:
                    return self.makeGuessAction()
            else:
                self.__uncoveredList.append(self.__safeList[0])
                self.__currentY = self.__safeList[0][0]
                self.__currentX = self.__safeList[0][1]
                self.__safeList.pop(0)
                return Action(AI.Action.UNCOVER, self.__currentY, self.__currentX)
        except Exception as e:
            print("Exception Caught: {}".format(e))
            return self.makeGuessAction()

    def makeGuessAction(self) -> Action:
        (action_type, (y, x)) = self.guess()
        self.__currentY = y
        self.__currentX = x
        if action_type == "safe":
            self.__uncoveredList.append([self.__currentY, self.__currentX])
            # print("Taking a guess: " + str(y) + " , " + str(x))
            return Action(AI.Action.UNCOVER, self.__currentY, self.__currentX)
        elif action_type == "Leave":
            return Action(AI.Action.LEAVE)
        else:
            self.__flaggedList.append([self.__currentY, self.__currentX])
            return Action(AI.Action.FLAG,  self.__currentY, self.__currentX)

    def getReducedMap(self) -> (list,list):
        # return board with numbers reduced based on surrounding flags
        # and list of unexplored tiles
        reduced_map = [list(row) for row in self.__Map]
        unexplored_list = []
        watchlist = self.__safeList + self.__mineList
        f_map = [list(row) for row in self.__Map]
        for i in range(len(reduced_map)):
            for j in range(len(reduced_map[i])):
                if reduced_map[i][j] > 0:
                    for k in range(-1,2):
                        for l in range(-1,2):
                            surround_block = [i+k, j+l]
                            if [i,j] != surround_block\
                                and (surround_block in self.__flaggedList\
                                    or surround_block in self.__mineList):
                                reduced_map[i][j] -= 1
                            if [i,j] != surround_block and surround_block in self.__flaggedList:
                                f_map[i][j] -= 1
                elif reduced_map[i][j] == -2 and [i,j] not in watchlist:
                    unexplored_list.append([i,j])

        # clear identified tiles out of frontier
        for i in range(len(reduced_map)):
            for j in range(len(reduced_map[i])):
                if f_map[i][j] == 0 and [i,j] in self.__frontier:
                    self.__frontier.remove([i,j])
        return (reduced_map, unexplored_list)

    def boundCheck(self, y, x) -> bool:
        return 0 <= y < self.__colDimension and 0 <= x < self.__rowDimension

    def getMineGroups(self):
        mine_groups = []
        for [y,x] in self.__frontier:
            current_group = set()
            current_mine_count = self.__Map[y][x]
            for i in range(-1,2):
                for j in range(-1,2):
                    if i == 0 and j == 0: continue
                    new_y = y + i
                    new_x = x + j
                    isValid = self.boundCheck(new_y,new_x)
                    if isValid and self.__Map[new_y][new_x] == -2:
                        current_group.add((new_y, new_x))
                    elif isValid and self.__Map[new_y][new_x] == -1:
                        current_mine_count -= 1
            mine_groups.append((current_group, current_mine_count))
        return mine_groups

    def groupCheck(self):
        mine_groups = self.getMineGroups()
        # match groups of tiles for flag and uncover actions
        watchList = self.__mineList + self.__safeList + self.__uncoveredList + self.__flaggedList
        for locationsA, numMineA in mine_groups:
            for locationsB, numMineB in mine_groups:
                if locationsB != locationsA and locationsB.issubset(locationsA):
                    diff = locationsA - locationsB
                    if len(diff) == numMineA - numMineB:
                        for (y,x) in diff:
                            if [y,x] not in watchList:
                                self.__mineList.append([y, x])
                                watchList.append([y,x])
                    if numMineA - numMineB == 0:
                        for (y,x) in diff:
                            if [y,x] not in watchList:
                                self.__safeList.append([y, x])
                                watchList.append([y,x])
                                

    def patternCheck(self) -> None:
        # reduce map
        (reduced_map, unexplored_list) = self.getReducedMap()

        watchlist = self.__mineList + self.__safeList
        for tiles in unexplored_list:
            (y,x)= tiles
            if y-1 > -1 and y+2 < self.__colDimension and x+1 < self.__rowDimension:
                '''
                1 2 2 1
                . * * .
                '''
                pattern1 = [[(y-1,x+1),(y,x+1),(y+1,x+1),(y+2,x+1)], 
                            [(y-1,x),  (y,x),  (y+1,x),  (y+2,x)]]
                matched = True
                match_pattern = [1,2,2,1]
                for i in range(4):
                    (cy,cx) = pattern1[0][i]
                    if reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                if matched:
                    if [y,x] not in watchlist:
                        self.__mineList.append([y,x])
                        watchlist.append([y,x])
                    if [y+1,x] not in watchlist and self.__Map[y+1][x] == -2:
                        self.__mineList.append([y+1,x])
                        watchlist.append([y+1,x])
            if y-1 > -1 and y+2 < self.__colDimension and x-1 > -1:
                '''
                pattern1:    
                . * * .      
                1 2 2 1      
                '''
                pattern1 = [[(y-1,x-1),(y,x-1),(y+1,x-1),(y+2,x-1)], 
                            [(y-1,x),  (y,x),  (y+1,x),  (y+2,x)]]
                matched = True
                match_pattern = [1,2,2,1]
                for i in range(4):
                    (cy,cx) = pattern1[0][i]
                    if reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                if matched:
                    if [y,x] not in watchlist:
                        self.__mineList.append([y,x])
                        watchlist.append([y,x])
                    if [y+1,x] not in watchlist and self.__Map[y+1][x] == -2:
                        self.__mineList.append([y+1,x])
                        watchlist.append([y+1,x])
            
            if y-1 > -1 and x-2 > -1 and x+1 < self.__rowDimension:
                '''
                1 .
                2 *
                2 *
                1 .
                '''
                pattern2 = [[(y-1,x+1),(y,x+1)],
                            [(y-1,x),  (y,x)],
                            [(y-1,x-1),(y,x-1)],
                            [(y-1,x-2),(y,x-2)]]
                match_pattern = [1,2,2,1]
                matched = True
                for i in range(4):
                    (cy,cx) = pattern2[i][0]
                    if reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                if matched:
                    if [y,x] not in watchlist:
                        self.__mineList.append([y,x])
                        watchlist.append([y,x])
                    if [y,x-1] not in watchlist and self.__Map[y][x-1] == -2:
                        self.__mineList.append([y,x-1])
                        watchlist.append([y,x-1])
            if y+1 < self.__colDimension and x-2 > -1 and x+1 < self.__rowDimension:
                '''
                . 1
                * 2
                * 2
                . 1
                '''
                pattern2 = [[(y+1,x+1),(y,x+1)],
                            [(y+1,x),  (y,x)],
                            [(y+1,x-1),(y,x-1)],
                            [(y+1,x-2),(y,x-2)]]
                match_pattern = [1,2,2,1]
                matched = True
                for i in range(4):
                    (cy,cx) = pattern2[i][0]
                    if reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                if matched:
                    if [y,x] not in watchlist:
                     self.__mineList.append([y,x])
                     watchlist.append([y,x])
                    if [y,x-1] not in watchlist and self.__Map[y][x-1] == -2:
                        self.__mineList.append([y,x-1])
                        watchlist.append([y,x-1])
            if y-1 > -1 and y+1 < self.__colDimension and x+1 < self.__rowDimension:
                '''
                1 2 1
                * . *
                '''
                pattern3 = [[(y-1,x+1),(y,x+1),(y+1,x+1)], 
                            [(y-1,x),  (y,x),  (y+1,x)]]
                match_pattern = [1,2,1]
                matched = True
                for i in range(3):
                    (cy,cx) = pattern3[0][i]
                    if reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                if matched:
                    if [y-1,x] not in watchlist and self.__Map[y-1][x] == -2:
                        self.__mineList.append([y-1,x])
                        watchlist.append([y-1,x])
                    if [y+1,x] not in watchlist and self.__Map[y+1][x] == -2:
                        self.__mineList.append([y+1,x])
                        watchlist.append([y+1,x])
            if y-1 > -1 and y+1 < self.__colDimension and x-1 > -1:
                '''
                * . *
                1 2 1
                '''
                pattern3 = [[(y-1,x-1),(y,x-1),(y+1,x-1)], 
                            [(y-1,x),  (y,x),  (y+1,x)]]
                match_pattern = [1,2,1]
                matched = True
                for i in range(3):
                    (cy,cx) = pattern3[0][i]
                    if reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                if matched:
                    if [y-1,x] not in watchlist and self.__Map[y-1][x] == -2:
                        self.__mineList.append([y-1,x])
                        watchlist.append([y-1,x])
                    if [y+1,x] not in watchlist and self.__Map[y+1][x] == -2:
                        self.__mineList.append([y+1,x])
                        watchlist.append([y+1,x])
            
        
        for tiles in unexplored_list:
            (y,x) = tiles
            if y-3 >= -1 and x-1 > -1:
                '''
                patternL: X is value >= 0, * is (y,x)
                X . . *
                X 1 1 X
                '''
                patternL = [[(y-3,x),  (y-2,x),  (y-1,x), (y,x)],
                            [(y-3,x-1),(y-2,x-1),(y-1,x-1),(y,x-1)]]
                match_pattern = ['out of bound or any value > -1',1,1,'any value > -1']
                matched = True
                top_left = patternL[0][0]
                if top_left[0] > -1 and reduced_map[top_left[0]][top_left[1]] == -2:
                    matched = False
                for i in range(4):
                    (cy,cx) = patternL[1][i]
                    if i == 0 and cy > -1 and reduced_map[cy][cx] < 0:
                        matched = False
                    elif 0 < i < 3 and reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                    elif i == 3 and reduced_map[cy][cx] < 0:
                        matched = False
                        
                if matched:
                    if [y,x] not in self.__safeList and [y,x] not in self.__mineList:
                        self.__safeList.append([y,x])
            if y-3 >= -1 and x+1 < self.__rowDimension:
                '''
                patternL: X is value >= 0, * is (y,x)
                X 1 1 X
                X . . *
                '''
                patternL = [[(y-3,x+1),(y-2,x+1),(y-1,x+1),(y,x+1)],
                            [(y-3,x),  (y-2,x),  (y-1,x), (y,x)]]
                match_pattern = ['out of bound or any value > -1',1,1,'any value > -1']
                matched = True
                bot_left = patternL[1][0]
                if bot_left[0] > -1 and reduced_map[bot_left[0]][bot_left[1]] == -2:
                    matched = False
                for i in range(4):
                    (cy,cx) = patternL[0][i]
                    if i == 0 and cy > -1 and reduced_map[cy][cx] < 0:
                        matched = False
                    elif 0 < i < 3 and reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                    elif i == 3 and reduced_map[cy][cx] < 0:
                        matched = False
                        
                if matched:
                    if [y,x] not in self.__safeList and [y,x] not in self.__mineList:
                        self.__safeList.append([y,x])
            if y+3 <= self.__colDimension and x-1 > -1:
                '''
                patternL: X is value >= 0, * is (y,x)
                * . . X
                X 1 1 X
                '''
                patternL = [[(y,x), (y+1,x),  (y+2,x),  (y+3,x)],
                            [(y,x-1),(y+1,x-1),(y+2,x-1),(y+3,x-1)]]
                match_pattern = ['any value > -1',1,1,'out of bound or any value > -1']
                matched = True
                top_right = patternL[0][3]
                if top_right[0] < self.__colDimension and reduced_map[top_right[0]][top_right[1]] == -2:
                    matched = False
                for i in range(4):
                    (cy,cx) = patternL[1][i]
                    if i == 0 and reduced_map[cy][cx] < 0:
                        matched = False
                    elif 0 < i < 3 and reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                    elif i==3 and cy < self.__colDimension and reduced_map[cy][cx] < 0:
                        matched = False

                if matched:
                    if [y,x] not in self.__safeList and [y,x] not in self.__mineList:
                        self.__safeList.append([y,x])
            if y+3 <= self.__colDimension and x+1 < self.__rowDimension:
                '''
                patternL: X is value >= 0, * is (y,x)
                X 1 1 X
                * . . X
                '''
                patternL = [[(y,x+1),(y+1,x+1),(y+2,x+1),(y+3,x+1)],
                            [(y,x), (y+1,x),  (y+2,x),  (y+3,x)]]
                match_pattern = ['any value > -1',1,1,'out of bound or any value > -1']
                matched = True
                bot_right = patternL[1][3]
                if bot_right[0] < self.__colDimension and reduced_map[bot_right[0]][bot_right[1]] == -2:
                    matched = False
                for i in range(4):
                    (cy,cx) = patternL[0][i]
                    if i == 0 and reduced_map[cy][cx] < 0:
                        matched = False
                    elif 0 < i < 3 and reduced_map[cy][cx] != match_pattern[i]:
                        matched = False
                    elif i==3 and cy < self.__colDimension and reduced_map[cy][cx] < 0:
                        matched = False

                if matched:
                    if [y,x] not in self.__safeList and [y,x] not in self.__mineList:
                        self.__safeList.append([y,x])

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    # Call when perception number return 0, this means all cells adjacent to the cell are safe
    def getSafeList(self, coordY: int, coordX: int) -> None:

        # For every cell in range, if it is the safe cell itself or it is already mark as safe on map,
        # ignore these cells, add remaining cell to safe list
        temp_lst = self.getSearchListOfTile(coordY, coordX)
        for coord_pair in temp_lst:
            if self.__Map[coord_pair[0]][coord_pair[1]] == 0:
                pass
            elif coord_pair in self.__safeList:
                pass
            elif coord_pair in self.__uncoveredList:
                pass
            else:
                self.__safeList.append([coord_pair[0], coord_pair[1]])

    def getSearchListOfTile(self, coordY: int, coordX: int) -> "List of cells to explored":
        return_list = []
        # Check for boundaries
        if coordX == 0:
            list_x_coords = [0, 1]
        elif coordX == self.__rowDimension - 1:
            list_x_coords = [coordX - 1, coordX]
        else:
            list_x_coords = [coordX - 1, coordX, coordX + 1]

        if coordY == 0:
            list_y_coords = [0, 1]
        elif coordY == self.__colDimension - 1:
            list_y_coords = [coordY - 1, coordY]
        else:
            list_y_coords = [coordY - 1, coordY, coordY + 1]

        for i in list_y_coords:
            for j in list_x_coords:
                if i == coordY and j == coordX:
                    pass
                else:
                    return_list.append([i, j])

        return return_list

    # If percept number of cell = numbers of uncover cell around it,
    # Then all those cell are mines
    # For tiles that are not safe (0), or uncover(-2), search around them
    def getMines(self) -> None:
        for i in range(self.__colDimension):
            for j in range(self.__rowDimension):
                if self.__Map[i][j] not in [0, -2, -1]:
                    check_lst = self.getSearchListOfTile(i, j)
                    self.findMines(check_lst, self.__Map[i][j])

    def findMines(self, lst: list, mines_number: int) -> None:

        number_of_explored = 0
        number_of_mine_flagged = 0
        unexplored_list = []
        if len(lst) != 0:
            for tiles in lst:
                if self.__Map[tiles[0]][tiles[1]] >= 0:
                    number_of_explored += 1
                elif self.__Map[tiles[0]][tiles[1]] == -1:
                    number_of_explored += 1
                    number_of_mine_flagged += 1
                else:
                    unexplored_list.append(tiles)
        # If number unexplored tiles = number of mines showing
        # All unexplored tiles are mines
        if len(lst) - number_of_explored == mines_number - number_of_mine_flagged:
            for tiles in unexplored_list:
                if tiles not in self.__mineList and tiles not in self.__flaggedList:
                    self.__mineList.append(tiles)

        if mines_number == number_of_mine_flagged:
            for tiles in unexplored_list:
                if tiles not in self.__safeList and tiles not in self.__uncoveredList:
                    self.__safeList.append(tiles)

    def guess(self) -> (str, (int, int)):
        self.patternCheck()
        if len(self.__safeList) > 0:
            return ("safe",self.__safeList.pop(0))
        if len(self.__mineList) > 0:
            self.__flaggedList.append(self.__mineList[0])
            return ("mine",self.__mineList.pop(0))
        
        self.groupCheck()
        if len(self.__safeList) > 0:
            return ("safe",self.__safeList.pop(0))
        if len(self.__mineList) > 0:
            self.__flaggedList.append(self.__mineList[0])
            return ("mine",self.__mineList.pop(0))
        
        possible_list = []
        preferred_list = []
        for i in range(self.__colDimension):
            for j in range(self.__rowDimension):
                if self.__Map[i][j] == -2:
                    # prefer corner and edge coordinates
                    if (i,j) in [(0,0), 
                                (0, self.__rowDimension-1),
                                (self.__colDimension-1, 0),
                                (self.__colDimension-1, self.__rowDimension-1)]:
                        preferred_list.append((i,j))
                    elif i==0 or j == 0 or i == self.__colDimension-1 or j == self.__rowDimension -1:
                        preferred_list.append((i,j))
                    else:
                        possible_list.append((i, j))
        (y,x) = (None,None)
        if len(preferred_list) > 0:
            (y,x) = random.choice(preferred_list)
        elif len(possible_list) > 0:
            (y,x) = random.choice(possible_list)
        else:
            return ("Leave", (y,x))
        return ("safe",(y, x))

    def rest_are_all_safe_or_mines(self, mineF_safeT: bool) -> Action:
        # print("Executing rest")
        for i in range(self.__colDimension):
            for j in range(self.__rowDimension):
                if self.__Map[i][j] == -2:
                    self.__currentY = i
                    self.__currentX = j
                    if mineF_safeT == True:
                        return Action(AI.Action.UNCOVER, self.__currentY, self.__currentX)
                    else:
                        return Action(AI.Action.FLAG, self.__currentY, self.__currentX)
        return Action(AI.Action.LEAVE)


