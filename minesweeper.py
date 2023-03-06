import PIL
import mouseinfo
import pyautogui
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Listener
import keyboard
# from pynput.keyboard import Key, Controller
import time
import random

'''
Minesweeper AI V1.2.0:
This version works about 90% of the time. It misses some logic sometimes, it bugs out other times, but overall, it works and solves minesweeper. 
I do plan on updating more though.  
TO DO:
Picture of times, if wanted
'''


#DO THIS: make sure zoom is 100% and set it to hard mode (other difficulties maybe incoming
#Make sure minesweeper is in the first monitor/main screen and the cmd line doesn't block the screenshot
#HOLD DOWN Q TO SHUT IT OFF


BARSIZE = 60
PATH = r'C:\Users\677708\Downloads\minesweeper' # r'D:\PyCharm Projects\minesweeper' # The path to where the python file is. RECOMMENDATION: It is recommended that you put it in its own folder so that saved screenshots are easy to find
SLEEP = .55

''' UNUSED AS OF CURRENT
# These variables are the same as above, but it takes a screenshot of the time once it is over to save THIS ISN'T IMPLEMENTED YET
TX1 = 385  # The first x position to start the screenshot for the time at the end
TY1 = 112  # The first y position to start the screenshot for the time at the end
TSWIDTH = 100  # The width of the screenshot for the time at the end
TSHEIGHT = 80  # The height of the screenshot for the time at the end
'''


myScreenshot = pyautogui.screenshot()
firstSquare = pyautogui.locateOnScreen(PATH+r'\screenshots\search.png')
X1 = firstSquare.left
Y1 = firstSquare.top-60

print('"easy", "medium", or "hard"? Other strings will default to hard')
difficulty = input()
#difficulty = "easy"
if difficulty == "easy":
    WIDTH = 10
    HEIGHT = 8
    SQUARESIZE = 45
    TOTALFLAGS = 10
elif difficulty == "medium":
    WIDTH = 18
    HEIGHT = 14
    SQUARESIZE = 30
    TOTALFLAGS = 40
else:
    WIDTH = 24  # How many squares wide #Hard mode
    HEIGHT = 20  # How many squares tall #Hard mode
    SQUARESIZE = 25
    TOTALFLAGS = 99

LEFTOFFSET = (SQUARESIZE // 2)  # The distance the first square is from the left side, no centering needed: If you set up Y1 and X1 properly these shouldn't matter
TOPOFFSET = BARSIZE + (SQUARESIZE // 2)  # The distance the first square is from the top, no centering needed: If you set up Y1 and X1 properly these shouldn't matter
SWIDTH = WIDTH * SQUARESIZE  # The width of the screenshot
SHEIGHT = HEIGHT * SQUARESIZE + TOPOFFSET - (SQUARESIZE // 2)  # The height of the screenshot

# These don't need to be updated
# Tile States
UNKNOWN = "?"
FLAG = "F"
n0 = 0
n1 = 1
n2 = 2
n3 = 3
n4 = 4
n5 = 5
n6 = 6
n7 = 7
n8 = 8
# c0 = (0, 0, 0)
# c1 = (0, 0, 0)
# c2 = (0, 0, 0)
# c3 = (0, 0, 0)
# c4 = (0, 0, 0)
# c5 = (0, 0, 0)
# c6 = (0, 0, 0)
# c7 = (0, 0, 0)
TEST = "T"  # DEBUG ONLY
ANY = "A"

playing = True

def newScreenshot():
  mouse.position = (0, 0)
  time.sleep(.0008)
  myScreenshot = pyautogui.screenshot(region=(X1, Y1, SWIDTH, SHEIGHT))
  return myScreenshot
'''
def on_press(key):
    global playing
    if key.is_pressed('q'):
      print(key)
      playing = False
'''


class Game:
  def __init__(self, width, height):  # Defines all variables
    global myScreenshot
    self.width = width
    self.height = height
    self.clicks = 0
    self.time = 0
    self.tiles = []
    self.flagsleft = TOTALFLAGS
    for row in range(self.height):
      self.tiles.append([])
      for col in range(self.width):  # You may or may not want to add this +1
        color = myScreenshot.getpixel((LEFTOFFSET + (col * SQUARESIZE) + 1, TOPOFFSET + (row * SQUARESIZE)))
        # print((col,row), color)
        self.tiles[row].append(Tile(col, row, color, self, True))

  def printBoard(self):  # Prints Board
    for row in self.tiles:
      # print(row)
      for tile in row:
        print(tile.state, end='')
      print()
    print()

  def offBoard(self, x, y):  # Checks if a certain tile is off the board
    if x < 0 or y < 0 or x >= self.width or y >= self.height:
      return True
    return False

  def xytocords(self, x, y):
    newx = x * SQUARESIZE + LEFTOFFSET + X1
    newy = y * SQUARESIZE + TOPOFFSET + Y1
    return (newx, newy)
  
  def cordstoxy(self, cordx, cordy):
    newx = cordx / SQUARESIZE - LEFTOFFSET - X1
    newy = cordy / SQUARESIZE - TOPOFFSET - Y1
    return (newx, newy)

  def clickTile(self, x, y, override=False):
    if self.playing() or override:
        global mouse
        self.clicks += 1
        cord = self.xytocords(x, y)
        mouse.position = cord
        # print("Clicking",x,y)
        mouse.click(Button.left)
    
  def flagTile(self, x, y, override=False):
    if self.playing() or override:
        global mouse
        self.flagsleft -= 1
        self.clicks += 1
        cord = self.xytocords(x, y)
        mouse.position = cord
        # print("Flagging",x,y)
        if self.flagsleft != 0:
            mouse.click(Button.right)
        surrounding = self.tiles[y][x].findSurrounding(self, ANY)
        self.tiles[y][x].state = FLAG
        for i in surrounding:
            curr = self.tiles[i[1]][i[0]]
            if curr.state != FLAG and curr.state != UNKNOWN and curr.state != TEST and curr.state != 0:
                curr.state -= 1
    
  def clickAll(self):
    for row in range(self.height):
      for col in range(self.width):
        if self.tiles[row][col].state == UNKNOWN:
            self.clickTile(col,row)

  def playing(self):  # Sees if the game is being played or not
    global myScreenshot
    # print(myScreenshot.getpixel((LEFTOFFSET + (WIDTH//3 * SQUARESIZE), TOPOFFSET + (HEIGHT/1.53846153846 * SQUARESIZE))))
    return not myScreenshot.getpixel((LEFTOFFSET + (WIDTH//3 * SQUARESIZE), TOPOFFSET + (HEIGHT/1.53846153846 * SQUARESIZE))) == (74,117,44)

  def updateBoard(self):  # Updates the Boards Current State
    global mouse
    myScreenshot = newScreenshot()
    for row in range(self.height):
      for col in range(self.width):                  # You may or may not want to remove this +1
        color = myScreenshot.getpixel((LEFTOFFSET + (col * SQUARESIZE)+1, TOPOFFSET + (row * SQUARESIZE)))
        self.tiles[row][col].setState(color, self)
   
  def logic(self):
    self.clicks = 0
    for row in range(self.height):
      for col in range(self.width): 
        curr = self.tiles[row][col]
        if curr.state == UNKNOWN or curr.state == FLAG or curr.state == TEST:
            continue
        else:
            #Simple Logic
            flags = curr.findSurrounding(self, FLAG)
            unknowns = curr.findSurrounding(self, UNKNOWN)
            # flags.sort()
            # unknowns.sort()
            # print(curr.state)
            if curr.state == 0:
                for tile in unknowns:
                    self.clickTile(tile[0],tile[1])
            if len(unknowns) == curr.state:
                for tile in unknowns:
                    self.flagTile(tile[0],tile[1])
            
            #Subset Logic:

            numbers = curr.findSurrounding(self, ANY)
            for tile in numbers:
                oCurr = self.tiles[tile[1]][tile[0]]
                # If there is the same number of bombs left around two tiles and the open tiles have the same subset of tiles except one is larger, then all of the tiles in the larger subset not in the smaller subset can be clicked
                if oCurr.state == curr.state != 0:
                    oUnknowns = oCurr.findSurrounding(self,UNKNOWN)
                    # oUnknowns.sort()
                    if set(oUnknowns).issubset(set(unknowns)) or set(unknowns).issubset(set(oUnknowns)):
                        if len(oUnknowns) > len(unknowns):
                            for i in oUnknowns:
                                if i not in unknowns:
                                    # print("Clicking", (i[0],i[1]))
                                    self.clickTile(i[0],i[1])
                        else:
                            for i in unknowns:
                                if i not in unknowns:
                                    # print("Clicking", (i[0],i[1]))
                                    self.clickTile(i[0],i[1])
                # If there is a different number of bombs around two tiles and the difference in the subsets of tiles is equal to the difference of the two numbers, then all of the tiles in the larger subset not in the smaller subset are bombs
                elif oCurr.isNonZeroNumber():
                    oUnknowns = oCurr.findSurrounding(self,UNKNOWN)
                    if set(oUnknowns).issubset(set(unknowns)) or set(unknowns).issubset(set(oUnknowns)):
                        difference = abs(len(oUnknowns)-len(unknowns))
                        difference2 = abs(curr.state-oCurr.state)
                        if difference == difference2:
                            if len(oUnknowns) > len(unknowns):
                                for i in oUnknowns:
                                    if i not in unknowns:
                                        # print("Clicking", (i[0],i[1]))
                                        self.flagTile(i[0],i[1])
                            else:
                                for i in unknowns:
                                    if i not in unknowns:
                                        # print("Clicking", (i[0],i[1]))
                                        self.flagTile(i[0],i[1])
    if self.clicks == 0:
      if myGame.flagsleft == 0:
        myGame.clickAll()
      else:
        self.time += 1
        if self.time > 12:
            myGame.clickRandom()
            self.time = 0
    else:
        self.time = 0
    
    # print(self.time)
   
  def clickRandom(self):
    for row in range(self.height):
      for col in range(self.width): 
        if self.tiles[row][col].state == UNKNOWN:
            self.clickTile(col,row)
            return
    

class Tile:
  def __init__(self, x, y, color, game, noSubract=False):  # Init variables
    self.size = SQUARESIZE
    self.x = x
    self.y = y
    self.state = None
    self.setState(color, game, noSubract)
  '''
  This isn't clean, but essentially due to slight changes in screenshots and pixel readings,
  Any time it read a number incorrectly I would add that color to their list, since they shouldn't repeat
  It also has to do with opacities on different backgrounds, so any time a color isn't in the list, I print out that color
  So I can see what it is and put it in the right category
  '''
  def setState(self, color, game, noSubract=False):  # Set the state based on a color
    self.prevState = self.state
    # print(color[2])
    if self.prevState == UNKNOWN or self.prevState == TEST or self.prevState == None:
      if color == (170, 215, 81) or color == (162, 209, 73):
        self.state = UNKNOWN
      elif color == (242, 54, 7): # or color == (191, 225, 125):
        self.state = FLAG
      elif color == (229, 194, 159) or color == (215, 184, 153):
        self.state = n0
      elif color == (211, 47, 47) or color == (211, 49, 48):  # Red
        self.state = n3
        self.subtractFlags(game,noSubract)
      elif color == (56, 142, 60) or color == (60, 143, 62) or color == (64, 144, 64) or color ==(63, 144, 64) or color == (61, 143, 63) or color == (60, 143, 63) or color == (87, 150, 78) or color == (89, 152, 79):  # Green # color == (228, 194, 159) or color == (214, 184, 153) or color == (168, 176, 125) or color == (159, 170, 121) or 
        self.state = n2
        self.subtractFlags(game,noSubract)
      elif color == (25, 118, 210) or color == (40, 123, 206) or color == (41, 124, 206):  # Blue 
        self.state = n1
        self.subtractFlags(game,noSubract)
      elif color == (227, 191, 159) or color == (214, 182, 153) or color == (173, 107, 160) or color == (166, 102, 157) or color == (136, 51, 162) or color == (134, 50, 161) or color == (166, 102, 158) or color == (172, 107, 161) or color == (155, 85, 159) or color == (160, 89, 161) or color == (200, 159, 154):  # Purple
        self.state = n4
        self.subtractFlags(game,noSubract)
      elif color == (255, 143, 0) or color == (244, 163, 64) or color == (239, 159, 62) or color == (244, 164, 64) or color == (239, 160, 62) or color == (233, 185, 132) or color == (222, 177, 127):
        self.state = n5  # If needed, I can make it find the colors for me
        self.subtractFlags(game,noSubract)
      elif color == (102, 170, 163) or color == (96, 165, 160) or color == (83, 166, 164) or color == (78, 163, 162) or color == (96, 166, 161):
        self.state = n6
        self.subtractFlags(game,noSubract)
      else:
        # self.state = TEST
        self.state = self.prevState
        if self.state == None:
            self.state = UNKNOWN
        print("UNKNOWN COLOR", color) # TURN THIS BACK ON WHEN RUNNING FOR TEST PURPOSES
    

    return self.state
    
  def subtractFlags(self, game, noSubract = False):
    if not noSubract:
        flags = self.findSurrounding(game, FLAG)
        self.state -= len(flags)
  
  def isNonZeroNumber(self):
    return self.state == n1 or self.state == n2 or self.state == n3 or self.state == n4 or self.state == n5 or self.state == n6 or self.state == n7 or self.state == n8
  
  def findSurrounding(self, game, check): #Just simply for removing double heads, don't worry a whole lot about how it actually works
    surrounding = []
    for i in range(2):
      xoffset = i or -1
      if not game.offBoard(self.x+xoffset, self.y) and (game.tiles[self.y][self.x+xoffset].state == check or check == ANY):
        surrounding.append((self.x+xoffset, self.y))
    
    for i in range(2):
      yoffset = i or -1
      if not game.offBoard(self.x, self.y+yoffset) and (game.tiles[self.y+yoffset][self.x].state == check or check == ANY):
        surrounding.append((self.x, self.y+yoffset))
    
    for i in range(2):
      xoffset = i or -1
      for j in range(2):
        yoffset = j or -1
        if not game.offBoard(self.x+xoffset, self.y+yoffset) and (game.tiles[self.y+yoffset][self.x+xoffset].state == check or check == ANY):
            surrounding.append((self.x+xoffset, self.y+yoffset))
    
    return surrounding

photoCount = 0  # When rerunning, this will delete old times
# myScreenshot = pyautogui.screenshot(region=(TX1,TY1,TSWIDTH,TSHEIGHT)) #Use PIL's instead?
# myScreenshot.save(PATH + r'\screenshots\timetest.png')

myScreenshot = pyautogui.screenshot(region=(X1, Y1, SWIDTH, SHEIGHT))  # Use PIL's instead?
myScreenshot.save(PATH + r'\screenshots\board.png')

myGame = Game(WIDTH, HEIGHT)

# keyboard = Controller()
mouse = Controller()
# listen = Listener(
#     on_press = on_press
# )
# listen.start()

# time.sleep(SLEEP)

myGame.clickTile(WIDTH//2-1, HEIGHT//2-1)
#myGame.clickTile(0,0)
time.sleep(SLEEP)
myGame.updateBoard()
# myGame.printBoard()


while (True):
    myScreenshot = newScreenshot() #Use PIL's instead?
    myGame.updateBoard()
    if myGame.playing() and not keyboard.is_pressed('q'):
      if myGame.flagsleft == 0:
        myGame.clickAll()
      myGame.logic()
    elif keyboard.is_pressed('q'):
        break
    else:
      print("done")
      time.sleep(1)
      if difficulty != "easy":
        myGame.clickTile(WIDTH//2-1, HEIGHT//2+3, True)
      else:
        myGame.clickTile(WIDTH//2-1, HEIGHT//2+1, True)
      time.sleep(1.4)
      # myGame.clickTile(1,1,True)
      myGame.clickTile(WIDTH//2-1, HEIGHT//2-1, True)
      time.sleep(SLEEP*1.5)
      myScreenshot = pyautogui.screenshot(region=(X1, Y1, SWIDTH, SHEIGHT))
      myGame = Game(WIDTH, HEIGHT)
      myGame.time = 0
      myGame.updateBoard()
      # myGame.printBoard()
    myGame.printBoard()
    # time.sleep(SLEEP)


