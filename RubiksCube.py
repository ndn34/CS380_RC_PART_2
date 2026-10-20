import heapq
import random
import sys
import time

# different moves
# https://ruwix.com/online-puzzle-simulators/2x2x2-pocket-cube-simulator.php

MOVES = {
    "U": [2,  0,  3,  1, 20, 21,  6,  7,  4,  5, 10, 11, 12, 13, 14, 15,  8,  9, 18, 19, 16, 17, 22, 23],
    "U'": [1,  3,  0,  2,  8,  9,  6,  7, 16, 17, 10, 11, 12, 13, 14, 15, 20, 21, 18, 19,  4,  5, 22, 23],
    "R": [0,  9,  2, 11,  6,  4,  7,  5,  8, 13, 10, 15, 12, 22, 14, 20, 16, 17, 18, 19,  3, 21,  1, 23],
    "R'": [0, 22,  2, 20,  5,  7,  4,  6,  8,  1, 10,  3, 12, 9, 14, 11, 16, 17, 18, 19, 15, 21, 13, 23],
    "F": [0,  1, 19, 17,  2,  5,  3,  7, 10,  8, 11,  9, 6,  4, 14, 15, 16, 12, 18, 13, 20, 21, 22, 23],
    "F'": [0,  1,  4,  6, 13,  5, 12,  7,  9, 11,  8, 10, 17, 19, 14, 15, 16,  3, 18,  2, 20, 21, 22, 23],
    "D": [0,  1,  2,  3,  4,  5, 10, 11,  8,  9, 18, 19, 14, 12, 15, 13, 16, 17, 22, 23, 20, 21,  6,  7],
    "D'": [0,  1,  2,  3,  4,  5, 22, 23,  8,  9,  6,  7, 13, 15, 12, 14, 16, 17, 10, 11, 20, 21, 18, 19],
    "L": [23,  1, 21,  3,  4,  5,  6,  7,  0,  9,  2, 11, 8, 13, 10, 15, 18, 16, 19, 17, 20, 14, 22, 12],
    "L'": [8,  1, 10,  3,  4,  5,  6,  7, 12,  9, 14, 11, 23, 13, 21, 15, 17, 19, 16, 18, 20,  2, 22,  0],
    "B": [5,  7,  2,  3,  4, 15,  6, 14,  8,  9, 10, 11, 12, 13, 16, 18,  1, 17,  0, 19, 22, 20, 23, 21],
    "B'": [18, 16,  2,  3,  4,  0,  6,  1,  8,  9, 10, 11, 12, 13,  7,  5, 14, 17, 15, 19, 21, 23, 20, 22],
}

# use these 3 for heuristic
CORNERS = [ # all corners
  (0, 16, 21), 
  (1, 5, 20), 
  (2, 8, 17), 
  (3, 9, 4),
  (10, 12, 19), 
  (11, 6, 13), 
  (14, 18, 23), 
  (15, 7, 22)
]

CORNER_COLORS = { # where each tuple of colors should be in respect to CORNERS list
    ('B', 'O', 'W'): 0,
    ('B', 'R', 'W'): 1,
    ('G', 'O', 'W'): 2,
    ('G', 'R', 'W'): 3,
    ('G', 'O', 'Y'): 4,
    ('G', 'R', 'Y'): 5,
    ('B', 'O', 'Y'): 6,
    ('B', 'R', 'Y'): 7,
}

CORNER_XYZ = { # XYZ Coords for each corner
  (0, 16, 21): (0,1,0), 
  (1, 5, 20): (1,1,0), 
  (2, 8, 17): (0,1,1), 
  (3, 9, 4): (1,1,1),
  (10, 12, 19): (0,0,1), 
  (11, 6, 13): (1,0,1), 
  (14, 18, 23): (0,0,0), 
  (15, 7, 22): (1,0,0)
}

'''
sticker indices:

      0  1
      2  3
16 17  8  9   4  5  20 21
18 19  10 11  6  7  22 23
      12 13
      14 15

face colors:

    0
  4 2 1 5
    3

moves:
[ U , U', R , R', F , F', D , D', L , L', B , B']
'''


class cube:

  def __init__(self, string="WWWW RRRR GGGG YYYY OOOO BBBB"):
    self.cubeString = string.replace(" ", "") # Taking in the string and removing spaces

    # Checking for validity
    if len(self.cubeString) != 24: # if string is not length 24 then it is invalid
      print("Error: Cube string has invalid length.")
      sys.exit(1)
    for letter in ["W", "R", "G", "Y", "O", "B"]: # if 4 of each color is not present it is not valid, this would also exclude invalid colors
      if self.cubeString.count(letter) != 4:
        print("Error: Cube string has invalid colors.")
        sys.exit(1)
    
    return
    
  def norm(self): # returns new cube that is the norm of self
    partners = {"W": "Y", "Y": "W", "R": "O", "O": "R", "G": "B", "B": "G"} # parter values
    cubeString = self.cubeString
    oldColors = [cubeString[10], cubeString[12], cubeString[19]] # copies old colors at the positions
    newColors = ["G", "Y", "O"]
    mapping = {}
    for i in range(3):
      mapping[oldColors[i]] = newColors[i] # map old color to new color
      mapping[partners[oldColors[i]]] = partners[newColors[i]] # map parter colors for old and new

    newCubeString = ""
    for i in range(24): # build new string
      newCubeString += mapping[cubeString[i]]
    return cube(newCubeString) # return new cube

  def equals(self, cube):
    for color in range(24):
      if self.cubeString[color] != cube.cubeString[color]: #if any of the colors are not equal then return false
        return False
    return True

  def clone(self): # returns a clone of the cube
    return cube(self.cubeString)

    # apply a move to a state
  def applyMove(self, move):
    if move not in MOVES: #check for valid moves
      print("Error: Invalid move provided.")
      sys.exit(1)

    newCubeString = ""
    for index in range(24): #append the value at the position from t he dictionary to the new string
      newCubeString += self.cubeString[MOVES[move][index]]
    
    self.cubeString = newCubeString
    return

    # apply a string sequence of moves to a state
  def applyMovesStr(self, alg):
    cloneCube = self.clone()

    for move in alg.split(): # run for each move in alg, split to get each move individually
      cloneCube.applyMove(move)
    return cloneCube

    # check if state is solved
  def isSolved(self): #each selection of 4 characters should be the same, if not its not solved
    for i in range(0, 24, 4):
      if self.cubeString[i:i+4].count(self.cubeString[i]) != 4: #if the count isn't 4 then it is not solved
        return False
    return True

    # print state of the cube
  def print(self):
    for i in range(2): # prints the different faces at the correct positions
      print("   " + self.cubeString[i*2] + self.cubeString[i*2+1])
    for i in range(2):
      print(self.cubeString[16+i*2] + self.cubeString[17+i*2] + " " + self.cubeString[8+i*2] + self.cubeString[9+i*2] + " " + self.cubeString[4+i*2] + self.cubeString[5+i*2] + " " + self.cubeString[20+i*2] + self.cubeString[21+i*2])
    for i in range(2):
      print("   " + self.cubeString[12+i*2] + self.cubeString[13+i*2])
    return

  def shuffle(self, n):
    if not n.isdigit(): # insure valid input
      print("Error: Invalid number of moves.")
      sys.exit(1)
    #list of moves
    potentialMoves = [ "U" , "U'" , "R" , "R'" , "F" , "F'" , "D" , "D'" , "L" , "L'" , "B" , "B'" ]

    moves = []
    for i in range(int(n)):
      moves.append(random.choice(potentialMoves)) # add a random move

    moves_str = " ".join(moves) # make the list into a string

    newCube = self.applyMovesStr(moves_str) # apply moves to cube
    print(moves_str +"\n") # print the moves
    return newCube

  def random(self, alg, n, seconds):
    baseCube = self.applyMovesStr(alg)
    if not n.isdigit(): # insure valid input
          print("Error: Invalid number of moves.")
          sys.exit(1)
    if not seconds.isdigit(): # insure valid input
          print("Error: Invalid number of seconds.")
          sys.exit(1)

    # set some variables
    potentialMoves = [ "U" , "U'" , "R" , "R'" , "F" , "F'" , "D" , "D'" , "L" , "L'" , "B" , "B'" ] # all possible moves
    moves=[] # moves taken by algorithm
    iterations, movesTaken = 1, 0 #saving iteration and moves taken
    startTime = time.time() #saving time
    iterativeCube = baseCube.clone()

    while (time.time() - startTime) < int(seconds):
      if iterativeCube.isSolved(): # check if solved
        print(" ".join(moves)) # print moves taken to solution

        #print moves taken
        copyCube = baseCube.clone()
        copyCube.print()
        print()
        for move in moves:
          copyCube.applyMove(move)
          copyCube.print()
          print()

        print(str(iterations)) #print iteratiosn and time taken
        print(round((time.time() - startTime),4))
        return

      if movesTaken == int(n): # reset if we hit the max number of moves
        movesTaken = 0
        moves = []
        iterativeCube = baseCube.clone()
        iterations += 1
      else:
        tempMove = random.choice(potentialMoves) # generate random move
        moves.append(tempMove) #add it list
        iterativeCube.applyMove(tempMove) # apply move to cube
        movesTaken += 1
    print("No solution in time limit!!")

  def printThreeCubes(self,cube1, cube2, cube3):
    for i in range(2): # print all the lines of the cubes, i added correct spacing to ensure they are properly separeted
      string = "   " + cube1.cubeString[i*2] + cube1.cubeString[i*2+1]
      if cube2:
        string += "            " + cube2.cubeString[i*2] + cube2.cubeString[i*2+1]
      if cube3:
        string += "            " + cube3.cubeString[i*2] + cube3.cubeString[i*2+1]
      print(string)
    for i in range(2): # 
      string = cube1.cubeString[16+i*2] + cube1.cubeString[17+i*2] + " " + cube1.cubeString[8+i*2] + cube1.cubeString[9+i*2] + " " + cube1.cubeString[4+i*2] + cube1.cubeString[5+i*2] + " " + cube1.cubeString[20+i*2] + cube1.cubeString[21+i*2]
      if cube2:
        string += "   " + cube2.cubeString[16+i*2] + cube2.cubeString[17+i*2] + " " + cube2.cubeString[8+i*2] + cube2.cubeString[9+i*2] + " " + cube2.cubeString[4+i*2] + cube2.cubeString[5+i*2] + " " + cube2.cubeString[20+i*2] + cube2.cubeString[21+i*2]
      if cube3:
        string += "   " + cube3.cubeString[16+i*2] + cube3.cubeString[17+i*2] + " " + cube3.cubeString[8+i*2] + cube3.cubeString[9+i*2] + " " + cube3.cubeString[4+i*2] + cube3.cubeString[5+i*2] + " " + cube3.cubeString[20+i*2] + cube3.cubeString[21+i*2]
      print(string)
    for i in range(2):
      string = "   " + cube1.cubeString[12+i*2] + cube1.cubeString[13+i*2]
      if cube2:
        string += "            " + cube2.cubeString[12+i*2] + cube2.cubeString[13+i*2]
      if cube3:
        string += "            " + cube3.cubeString[12+i*2] + cube3.cubeString[13+i*2]
      print(string)
    return

  def bfs(self, alg):
    initialState = self.applyMovesStr(alg)

    potentialMoves = [ "U" , "U'" , "R" , "R'" , "F" , "F'" , "D" , "D'" , "L" , "L'" , "B" , "B'" ] # all possible moves
    nodesExplored = 0 #saving nodes explored
    startTime = time.time() #saving time

    queue = [ [initialState.clone(), []] ] # each state will be a list including the current state plus moves made to create that state from the initial state
    repeatedState = set()
    repeatedState.add(initialState.cubeString) # add initial state to repeated states
    while(queue):
      currentState = queue.pop(0)
      nodesExplored+= 1
      if currentState[0].isSolved(): # if goal is found
        print(" ".join(currentState[1])) #print moves
        print()

        stateList = [initialState.clone()] # get initial state
        for i in range(len(currentState[1])): # get all states between initial and goal
          newState = initialState.applyMovesStr(" ".join(currentState[1][0:i+1]))
          stateList.append(newState)

        for i in range(0, len(stateList), 3): # print states to 3 per line
          self.printThreeCubes(stateList[i], stateList[i+1] if i+1 < len(stateList) else None, stateList[i+2] if i+2 < len(stateList) else None)
          print()

        print()
        print(nodesExplored) #print nodes explored
        print(round((time.time() - startTime),4)) #print time to find
        return

      for move in potentialMoves: # for each possible move
        if self.redundant(move, currentState[1]):
          continue
        newState = currentState[0].clone() 
        newState.applyMove(move)
        if newState.cubeString not in repeatedState: # if it has not been seen before add it to the queue and repeated states
          repeatedState.add(newState.cubeString)
          newList = currentState[1] + [move]
          queue.append([newState, newList])

  def redundant(self, move, alg):
    complementaryMoves = { # these are moves that simply rotate the cube and do not change the state of the cube, so they are redundant
        ("U", "D'"),
        ("D'", "U"),
        ("U'", "D"),
        ("D", "U'"),
        ("L'", "R"),
        ("R", "L'"),
        ("L", "R'"),
        ("R'", "L"),
        ("F", "B'"),
        ("B'", "F"),
        ("F'", "B"),
        ("B", "F'"),
    }
    leng = len(alg)
    last_move = alg[-1] if leng > 0 else None
    second_last_move = alg[-2] if leng > 1 else None
    if len(move) == 1 and last_move == move + "'" or len(move) == 2 and last_move == move[0]: # if the last move was the inverse of the current move then skip it
      return True
    elif move == last_move and leng > 1 and move == second_last_move: # if the last two moves were the same as the current move then skip it
      return True
    elif (last_move, move) in complementaryMoves: # if the last move and the current move are a complementary pair then skip it
      return True
    return False

  def dls(self, alg, depth, ids=False): # i added an ids parameter so i could reuse this func for ids
    if not depth.isdigit(): # insure valid input
      print("Error: Invalid depth.")
      sys.exit(1)
    initialState = self.applyMovesStr(alg)

    potentialMoves = [ "U" , "U'" , "R" , "R'" , "F" , "F'" , "D" , "D'" , "L" , "L'" , "B" , "B'" ] # all possible moves
    potentialMoves.reverse() # in testing, my code runs faster if this list is reverse, which means that U and U' are first thigns checked instead of last things checked
    nodesExplored = 0 #saving nodes explored
    startTime = time.time() #saving time

    queue = [ [initialState.clone(), []] ] # each state will be a list including the current state plus moves made to create that state from the initial state

    while(queue):
      currentState = queue.pop()
      if currentState[0].isSolved(): # if goal is found
        if ids: return currentState[1], nodesExplored # ids bypass
        print(" ".join(currentState[1])) #print moves
        print()

        stateList = [initialState.clone()] # get initial state
        for i in range(len(currentState[1])): # get all states between initial and goal
          newState = initialState.applyMovesStr(" ".join(currentState[1][0:i+1]))
          stateList.append(newState)

        for i in range(0, len(stateList), 3): # print states to 3 per line
          self.printThreeCubes(stateList[i], stateList[i+1] if i+1 < len(stateList) else None, stateList[i+2] if i+2 < len(stateList) else None)
          print()

        print()
        print(nodesExplored) #print nodes explored
        print(round((time.time() - startTime),4)) #print time to find
        return
      nodesExplored+= 1
      if len(currentState[1]) < int(depth): # if we are not at the max depth yet
        for move in potentialMoves: # for each possible move
          if self.redundant(move, currentState[1]):
            continue
          newState = currentState[0].clone() 
          newState.applyMove(move)
          newList = currentState[1] + [move]
          queue.append([newState, newList])
    if ids: return None, nodesExplored - 1 # ids bypass, i return -1 bc my code counts 1 higher than the examples in the directions, its just a difference in how the counting is done
    print("No solution found within depth limit.")
    
  def ids(self, alg, depth): 
    if not depth.isdigit(): # insure valid input
      print("Error: Invalid depth.")
      sys.exit(1)
    initialState = self.applyMovesStr(alg)
    totalNodesExplored = 0 #saving nodes explored
    startTime = time.time() #saving time
    for i in range(int(depth)+1): # run dls for each depth from 0 to the max depth
      moveList, nodesExplored = initialState.dls("", str(i), ids=True) # reusing dls
      print("Depth: " + str(i) + " d: " + str(nodesExplored)) # print depth and nodes
      totalNodesExplored += nodesExplored
      if moveList: # if a solution was found, print the solution and the states
        print("IDS found a solution at depth " + str(i))
        print(" ".join(moveList)) #print moves
        print()

        stateList = [initialState.clone()] # get initial state
        for j in range(len(moveList)): # get all states between initial and goal
          newState = initialState.applyMovesStr(" ".join(moveList[0:j+1]))
          stateList.append(newState)

        for j in range(0, len(stateList), 3): # print states to 3 per line
          self.printThreeCubes(stateList[j], stateList[j+1] if j+1 < len(stateList) else None, stateList[j+2] if j+2 < len(stateList) else None)
          print()

        print()
        print(totalNodesExplored) #print total nodes explored
        print(round((time.time() - startTime),4)) #print time to find
        return
    print("IDS did not find a solution within depth limit.")

  def distance(self, c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

  def heuristic(self):
    newCubeString = self.norm().cubeString # use norm
    val = 0
    for corner in CORNERS: # CONERS is a list of each corner
      colors = []
      for num in corner:
        colors.append(newCubeString[num])
      colors.sort()

      colorTuple = tuple(colors) # all of this color stuff gets the TUPLE of colors from a corner
      val += self.distance(CORNER_XYZ[corner], CORNER_XYZ[CORNERS[CORNER_COLORS[colorTuple]]])
      # distance calcs the manhattan distance between the two corners
      # the corners being the current corner and the corner it should be at
    return (val+3) // 4 # add 3 to force a round up instead of round down, 

  def astar(self, alg):
    initialState = self.applyMovesStr(alg)

    potentialMoves = [ "U" , "U'" , "R" , "R'" , "F" , "F'" , "D" , "D'" , "L" , "L'" , "B" , "B'" ] # all possible moves
    nodesExplored = 0 #saving nodes explored
    startTime = time.time() #saving time

    queue = [ ] # each state will be a list including the current state plus moves made to create that state from the initial state
    counter = 0 # using heap bc lists are really slow
    heapq.heappush(queue, (initialState.heuristic(), 0, counter, initialState.clone(), []))
    repeatedState = set()
    repeatedState.add(initialState.norm().cubeString) # add initial state to repeated states
    while(queue):
      currentState = heapq.heappop(queue)
      
      nodesExplored+= 1
      if currentState[3].isSolved(): # if goal is found
        print(" ".join(currentState[4])) #print moves
        print()

        stateList = [initialState.clone()] # get initial state
        for i in range(len(currentState[4])): # get all states between initial and goal
          newState = initialState.applyMovesStr(" ".join(currentState[4][0:i+1]))
          stateList.append(newState)

        for i in range(0, len(stateList), 3): # print states to 3 per line
          self.printThreeCubes(stateList[i], stateList[i+1] if i+1 < len(stateList) else None, stateList[i+2] if i+2 < len(stateList) else None)
          print()

        print()
        print(nodesExplored) #print nodes explored
        print(round((time.time() - startTime),4)) #print time to find
        return

      for move in potentialMoves: # for each possible move
        if self.redundant(move, currentState[4]):
          continue
        newState = currentState[3].clone() 
        newState.applyMove(move)
        if newState.norm().cubeString not in repeatedState: # if it has not been seen before add it to the queue and repeated states
          repeatedState.add(newState.norm().cubeString)
          newList = currentState[4] + [move]
          counter += 1
          heapq.heappush(queue, (newState.heuristic() + currentState[1] + 1, currentState[1] + 1, counter, newState, newList))

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Error: Too few arguments provided.")
    sys.exit(1)
  elif len(sys.argv) > 5:
    print("Error: Too many arguments provided.")
    sys.exit(1)

  command = sys.argv[1]

  if command == "print":
    if len(sys.argv) > 3: # cleans input
      print("Error: Invalid number of arguments for print command.")
      sys.exit(1)
    elif len(sys.argv) == 3: # checks for if cube string was provided
      c = cube(sys.argv[2])
    else:
      c = cube()
    c.print()

  elif command == "goal":
    if len(sys.argv) > 3: # cleans input
      print("Error: Invalid number of arguments for goal command.")
      sys.exit(1)

    if len(sys.argv) == 3: # checks for if cube string was provided
      c = cube(sys.argv[2])
    else: # generate default cube
      c = cube()
  
    if c.isSolved(): # check for solved
      print("True")
    else:
      print("False")

  elif command == "applyMovesStr":
    if len(sys.argv) > 4 or len(sys.argv) < 3: # cleans input
      print("Error: Invalid number of arguments for applyMoveStr command.")
      sys.exit(1)
    elif len(sys.argv) == 4: # pass arg if cube string was given
      c = cube(sys.argv[3])
    else: #generate default cube otherwise
      c = cube()
    c2 = c.applyMovesStr(sys.argv[2])
    c2.print()

  elif command == "shuffle":
    if len(sys.argv) != 3: # cleans input
      print("Error: Invalid number of arguments for shuffle command.")
      sys.exit(1)

    c = cube()
    c2 = c.shuffle(sys.argv[2])
    c2.print()

  elif command == "random":
    if len(sys.argv) != 5: # cleans input
      print("Error: Invalid number of arguments for random command.")
      sys.exit(1)

    c = cube()
    c.random(sys.argv[2], sys.argv[3], sys.argv[4])

  elif command == "bfs": # all of these below do the same, make sure input length is valid and call the respective function
    if len(sys.argv) != 3:
      print("Error: Invalid number of arguments for bfs command.")
      sys.exit(1)

    c = cube()
    c.bfs(sys.argv[2])

  elif command == "dls":
    if len(sys.argv) != 4:
      print("Error: Invalid number of arguments for dls command.")
      sys.exit(1)

    c = cube()
    c.dls(sys.argv[2], sys.argv[3])

  elif command == "ids":
    if len(sys.argv) != 4:
      print("Error: Invalid number of arguments for ids command.")
      sys.exit(1)

    c = cube()
    c.ids(sys.argv[2], sys.argv[3])

  elif command == "astar":
    if len(sys.argv) != 3:
      print("Error: Invalid number of arguments for astar command.")
      sys.exit(1)

    c = cube()
    c.astar(sys.argv[2])

  elif command == "norm":
    if len(sys.argv) != 3:
      print("Error: Invalid number of arguments for norm command.")
      sys.exit(1)
    c = cube(sys.argv[2])
    c = c.norm()
    c.print()

  else:
    print("Error: Invalid command provided.")
    sys.exit(1)