#-----------------------------------------------------------------------------
# Name:        Jungle Raiders
# Purpose:     2D platformer video game.
#
# Author:      Alec Tang
# Created:     18-Mar-2021
# Updated:     2-Apr-2021
#-----------------------------------------------------------------------------
#I think this project deserves a level 4 because I met all of the requirements
#for each level. The code is commented, efficient and organized. 
#
#Features Added:
#   High score list
#   Sound effects
#   Different pages
#   Animations
#   Replay options
#   Page navigation with buttons
#-----------------------------------------------------------------------------

#NOTE: If the game seems laggy, comment out the microbit code and play the game. You can
#substitue shaking the microbit with just pressing the button instead at the end screens.

#I also HIGHLY suggest you turn down your volume because some of the mp3 files are really loud

#the microbit code has 3 parts, the function right underneath here, one at the beginning of
#the main function, and one at the beginning of the while true loop.

'''
CODE FOR MICROBIT

from microbit import *
import time

while True:
    gesture = accelerometer.current_gesture()
    if gesture == "shake":
        display.show(Image.HAPPY)
        print("shakeYes")
    elif gesture != "shake":
        display.show(Image.ANGRY)
        print("shakeNo")
    time.sleep(0.5)
'''
import pygame
import copy
import random
import serial
import serial.tools.list_ports as list_ports

def findMicrobitComPort(pid=516, vid=3368, baud=115200):
    '''
    This function finds a device connected to usb by it's PID and VID and returns a serial connection
    Parameters
    ----------
    pid - Product id of device to search for
    vid - Vendor id of device to search for
    baud - Baud rate to open the serial connection at
    Returns
    -------
    Serial - If a device is found a serial connection for the device is configured and returned
    '''
    #Required information about the microbit so it can be found
    #PID_MICROBIT = 516
    #VID_MICROBIT = 3368
    TIMEOUT = 0.1
   
    #Create the serial object
    serPort = serial.Serial(timeout=TIMEOUT)
    serPort.baudrate = baud
   
    #Search for device on open ports and return connection if found
    ports = list(list_ports.comports())
    print('scanning ports')
    for p in ports:
        print('port: {}'.format(p))
        try:
            print('pid: {} vid: {}'.format(p.pid, p.vid))
        except AttributeError:
            continue
        if (p.pid == pid) and (p.vid == vid):
            print('found target device pid: {} vid: {} port: {}'.format(
                p.pid, p.vid, p.device))
            serPort.port = str(p.device)
            return serPort
   
    #If nothing found then return None
    return None

class Character():
    '''
    A class to make a character
      
    '''
    def __init__(self,charImage,charPos,charRect):
        '''
        initialize the class and set up variables. 

        Parameters
        ----------
        parameter1 : self
        Create variables within the method
        parameter2 : charImage
        to set which image you want to diplay
        parameter3 : charPos
        To set the characters position
        parameter4 : charRect
        To set the set the characters size 
        '''
        self.charImage = charImage
        self.charPos = charPos
        self.charRect = charRect
        #make a hitbox for the character
        self.hitbox = pygame.Rect([self.charPos[0],self.charPos[1],35,self.charRect[2]-15])
        
        self.origImageRect = copy.copy(self.charRect)
        self.patchNumber = 0 #Start at the initial patch
        self.numPatches = 2  #number of frames 
        self.frameCount = 0  #Start at intial frame
        self.animationFrameRate = 10
        
        self.moving = False
        self.direction = True
        
    def draw(self, surfaceIn):
        '''
        A method to draw the character onto the screen

        Parameters
        ----------
        parameter1 : self
        To access the attributes of the class
        parameter2 : surfaceIn
        To draw it onto the screen
        '''
        tempSurface = pygame.Surface((self.charRect[2],self.charRect[2]))
        tempSurface.set_colorkey((0,0,0))
        tempSurface.blit(self.charImage,(0,0),self.charRect)
        
        #flip the characer when you face left
        if not self.direction: #if u press left and are not already facing left
            tempSurface = pygame.transform.flip(tempSurface,True,False)
            self.hitbox[0] = self.charPos[0] + 45
            
        surfaceIn.blit(tempSurface, self.charPos)
    
    def shiftRight(self):
        '''
        A method to draw the character onto the screen
        
        Flipping the character shifts it over, so this is used to offset it.

        Parameters
        ----------
        parameter1 : self
        To access the attributes of the class
        '''
        self.charPos[0] = self.charPos[0] - 45
            
    def shiftLeft(self):
        '''
        A method to draw the character onto the screen
        
        Flipping the character shifts it over, so this is used to offset it.

        Parameters
        ----------
        parameter1 : self
        To access the attributes of the class
        '''
        self.charPos[0] = self.charPos[0] + 45
        
    def updateImageRect(self):
        '''
        A method to update the frames

        Parameters
        ----------
        parameter1 : self
        To access the attributes of the class
        '''
        self.hitbox[0] = self.charPos[0]
        self.hitbox[1] = self.charPos[1]
        
        #update the imageRect to show the next image
        if (self.patchNumber < self.numPatches-1) :
            self.patchNumber += 1
            self.charRect[0] += self.charRect[2]
        else:
            self.patchNumber = 0
            self.charRect = copy.copy(self.origImageRect)

    def update(self):
        '''
        A method to update the frames at a certain speed

        Parameters
        ----------
        parameter1 : self
        To access the attributes of the class
        '''
        self.frameCount += 1
        if (self.frameCount % self.animationFrameRate == 0):
            self.updateImageRect()
        
    def move(self, xIn, yIn):
        '''
        A method to move the character

        Parameters
        ----------
        parameter1 : self
        To access the attributes of the class
        Parameters
        ----------
        parameter2 : xIn
        To move across the x axis
        Parameters
        ----------
        parameter2 : yIn
        To move across the y axis
        '''
        self.charPos[0] += xIn
        self.charPos[1] += yIn
    
class Platform():
    '''
    A class to make platforms
    '''
    def __init__(self,platImage,platPos,platRect):
        '''
        initialize the class and set up variables. 

        Parameters
        ----------
        parameter1 : self
        Create variables within the method
        parameter2 : platImage
        to set which image you want to diplay
        parameter3 : platPos
        To set the platforms position
        parameter4 : platRect
        To set the set the platforms size 
        '''
        self.platImage = platImage
        self.platPos = platPos
        self.platRect = platRect
        self.platBox = pygame.Rect([platPos[0],platPos[1],platRect[2],10])
        self.bottomPlatBox = pygame.Rect([platPos[0],platPos[1]+platRect[3]-5,platRect[2],3])
        self.platBox.x = self.platPos[0]
        self.platBox.y = self.platPos[1]
        
    def draw(self,surface):
        '''
        A method to draw the platforms 

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class   
        parameter2 : surface
        To draw it onto a surface
        '''
        piece = pygame.Surface(([self.platRect[2],self.platRect[3]]))
        piece.blit(self.platImage,(0,0),self.platRect)
        piece.set_colorkey((0,0,0))
        surface.blit(piece,self.platPos)

class Item():
    '''
    A class to make items 
    '''
    def __init__(self,itemImage,itemPos,itemRect):
        '''
        initialize the class and set up variables. 

        Parameters
        ----------
        parameter1 : self
        Create variables within the method  
        parameter2 : itemImage
        to set which image you want to diplay
        parameter3 : itemPos
        To set the items position
        parameter4 : itemRect
        To set the set the items size 
        '''
        self.itemImage = itemImage
        self.itemPos = itemPos
        self.itemRect = itemRect
        self.itemBox = pygame.Rect([200,200,16,16])
        self.visible = True
        
        self.origImageRect2 = copy.copy(self.itemRect)
        self.patchNumber = 0 #Start at the initial patch
        self.numPatches = 5  
        self.frameCount = 0  #Start at intial frame
        self.animationFrameRate = 15
        
    def draw(self,surfaceIn):
        '''
        A method to draw the item

        Parameters
        ----------
        parameter1 : self
        Create variables within the method
        parameter2 : surfaceIn
        to draw the item to a surface
        '''
        tempSurface = pygame.Surface((self.itemRect[2],self.itemRect[2]))
        tempSurface.set_colorkey((0,0,0))
        tempSurface.blit(self.itemImage,(0,0),self.itemRect)
               
        surfaceIn.blit(tempSurface, self.itemPos)
        
    
    def updateImageRect(self):
        '''
        A method to update the frames of the item

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class  
        '''
        self.itemBox[0] = self.itemPos[0]
        self.itemBox[1] = self.itemPos[1]

        if (self.patchNumber < self.numPatches-1) :
            self.patchNumber += 1
            self.itemRect[0] += self.itemRect[2]
        else:
            self.patchNumber = 0
            self.itemRect = copy.copy(self.origImageRect2)
            
    def update(self):
        '''
        A method to update the frames at a certain speed

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class  
        parameter2 : charImage
        to set which image you want to diplay
        parameter3 : charPos
        To set the characters position
        parameter4 : charRect
        To set the set the characters size 
        '''
        self.frameCount += 1
        if (self.frameCount % self.animationFrameRate == 0):
            self.updateImageRect()

class Button():
    '''
    A class for the buttons 

    '''
    def __init__(self, rectIn, colorIn, valueIn = False ):
        '''
        Initialize the class. 

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class
        parameter2 : rectIn
        To set the buttons position
        parameter3 : colourIn
        To set the buttons colour
        
        '''
        self.rect = rectIn
        self.displayColor = colorIn
        self.baseColor = colorIn
        self.hoverColor = pygame.Color(0,0,0)
        #darken the colour of the button when it is being hovered
        if self.baseColor.r > 50: self.hoverColor.r = self.baseColor.r - 50
        if self.baseColor.g > 50: self.hoverColor.g = self.baseColor.g - 50
        if self.baseColor.b > 50: self.hoverColor.b = self.baseColor.b - 50
        self.value = valueIn        
        
    def draw(self, surfaceIn):
        '''
        Draw the button onto the screen. 

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class
        parameter2 : surfaceIn
        To draw the button onto a surface
        
        '''
        pygame.draw.rect(surfaceIn, self.displayColor, self.rect, border_radius =20)
        
    def update(self):
        '''
        Change colour of button whenever mouse is hovering over it.

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class        
        '''
        if self.collidePoint(pygame.mouse.get_pos()):
          
            self.displayColor = self.hoverColor
        else:
            self.displayColor = self.baseColor

    def collidePoint(self, pointIn):
        '''
        Check if the button is being clicked

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class
        parameter2 : pointIn
        Check the mouses position
        
        Returns
        -------
        Boolean value
        
        The buttons state is being returned depending on if it is clicked on.
        '''
        rectX = self.rect[0]
        rectY = self.rect[1]
        rectWidth = self.rect[2]
        rectHeight = self.rect[3]
        
        xIn = pointIn[0]
        yIn = pointIn[1]
        
        if (xIn > rectX and xIn < rectX + rectWidth and yIn > rectY and yIn < rectY + rectHeight):
            return True
        else:
            return False
        
    def toggleValue(self):
        '''
        Toggle the button True/False

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class        
        '''
        self.value = not self.value
        
    def getValue(self):
        '''
        Return the buttons state

        Parameters
        ----------
        parameter1 : self
        To access the attributes for the class
        '''
        return self.value
    
def main():
    '''
    The main chunk of code that runs the program.

    Here all the classes are used to create instances.
    The program is set up into different gamestates depending
    on what is currently occuring in the program.
    '''
    pygame.init()
    clock = pygame.time.Clock()
    
    #Comment out starting here --------
    try:
        
        print('looking for microbit')
        microbit = findMicrobitComPort()
        if not microbit:
            print('microbit not found')
            #return
       
        print('opening and monitoring microbit port')
        microbit.open()
    
    except:
        pass
    #Comment out ejding here -----------
    
    shaking = False
    
    #set up needed images
    mainSurface = pygame.display.set_mode((600,400))
    charRun = pygame.image.load("images//spritesheet.png")
    blocks = pygame.image.load("images//pieces.png")
    background = pygame.image.load("images//back.png")
    background = pygame.transform.scale(background,(600,400))
    item = pygame.image.load("images//coin.png")
    enemy = pygame.image.load("images//slime.png")
    heart = pygame.image.load("images//heart.png")
    heart = pygame.transform.scale(heart,(25,25))
    heart2 = pygame.image.load("images//heart.png")
    heart2 = pygame.transform.scale(heart2,(40,40))
    star = pygame.image.load("images//star.png")
    star = pygame.transform.scale(star,(30,30))
    store = pygame.image.load("images//store.png")
    store = pygame.transform.scale(store,(600,400))
    potion = pygame.image.load("images//potion.png")
    potion = pygame.transform.scale(potion,(60,50))
    jungle = pygame.image.load("images//mainscreen.jpg")
    jungle = pygame.transform.scale(jungle,(600,400))
    keyboard = pygame.image.load("images//keys.png")
    keyboard = pygame.transform.scale(keyboard,(160,120))
    click = pygame.mixer.Sound('click.mp3')
    chime = pygame.mixer.Sound('chime.mp3')
    cash = pygame.mixer.Sound('cash.mp3')
    buzzer = pygame.mixer.Sound('buzzer.mp3')
    hurt = pygame.mixer.Sound('hurt.mp3')
    loss = pygame.mixer.Sound('loss.mp3')
    victory = pygame.mixer.Sound('victory.mp3')
    winSound = pygame.mixer.Sound('winSound.mp3')
    
    #set up needed fonts
    font = pygame.font.SysFont('Comic Sans MS', 20)
    font2 = pygame.font.SysFont('impact', 40)
    font3 = pygame.font.SysFont('Comic Sans MS', 15)
    font4 = pygame.font.SysFont('impact', 20)
    font5 = pygame.font.SysFont('impact', 60)
    titleFont = pygame.font.SysFont('impact', 80)
    
    playButton = Button( [225,275,150,65], pygame.Color(34,139,34))
    shopButton = Button( [75,18,50,25], pygame.Color(0,255,0))
    returnButton = Button( [520,360,75,33], pygame.Color(148,3,3))
    homeButton = Button( [265,7,60,25], pygame.Color(105,105,105))
    home2Button = Button( [520,320,75,33], pygame.Color(34,139,34))
    scoreButton = Button( [15,350,120,30], pygame.Color(105,105,105))
    ruleButton = Button( [520,350,60,30], pygame.Color(105,255,105))
    heartButton = Button( [225,270,50,30], pygame.Color(105,105,105))
    potionButton = Button( [330,270,50,30], pygame.Color(105,105,105))
    
    #set gamestate (start, rules, score, game, shop, win, lose)
    gamestate = 'start'    
    
    coinPoint = 0
    lifeCount = 2
    heartY = 30
    starX = 530
    starY = 40
    starVel = -1
    heartMove = True
    slimeMove = True
    slime2Move = True
    slime3Move = True
    showText = False
    frameCount = 0
    timer = 0
    scoreList = []
    
    canAppend = True
    
    #main character(mc)
    mc = Character( charRun,[30,305],([780,740,75,75]) )
    
    #different slimes
    slime = Character( enemy,[100,150],([0,0,44,29]))
    groundSlime = Character( enemy,[350,345],([0,0,44,29]))
    platSlime = Character( enemy,[405,290],([0,0,44,29]))
    
    #coins needed in the game
    coin = []
    for i in range(4):
        coin.append(Item(item,[550,337],([0,0,16,16]) ))
    coin[1].itemPos[0] = 415
    coin[1].itemPos[1] = 140
    coin[3].itemPos[0] = 11
    coin[3].itemPos[1] = 9
    coin[2].itemPos[0] = 80
    coin[2].itemPos[1] = 80
    
    #coins for winning animation
    coinShower = []
    for i in range(30):
        coinShower.append(Item(item,[i*20 +3,random.randrange(0,400)],([0,0,16,16]) ))
    
    #one ground block is not wide enough to cover the floor so I just make enough to cover it
    ground = []
    for i in range(4):
        ground.append(Platform(blocks,[i*155,374],([20,230,155,26])))
    
    #the platforms in the game
    skyblock1 = Platform(blocks,[400,320],([322,147,108,43]))
    skyblock2 = Platform(blocks,[225,250],([322,147,108,43]))
    skyblock3 = Platform(blocks,[70,180],([322,147,108,43]))
    endblock = Platform(blocks,[400,160],([336,271,46,19]))
    groundBox  = pygame.draw.rect(mainSurface,(255,0,0), pygame.Rect(0, 372, 600, 10))
    
    vel = 0
    grav = .3
    onPlat =  True
    canMoveL = True
    canMoveR = True
    
    while True:

#Comment out starting here --------
        try:
            if (microbit.inWaiting()>0):
           
                #data = microbit.read(microbit.inWaiting()).decode('utf-8') #read the bytes and convert from binary array to utf-8
                data = microbit.readlines()  #Read lines into a list, one line per list entry
                     
                for i in range(len(data)): #Convert each entry in list from binary to a readable text format
                    data[i] = data[i].decode('utf-8').strip()
           
                    if data[i] == "shakeNo":
                        shaking = False
                    if data[i] == "shakeYes":
                        shaking = True
        except:
            pass
#Comment out ending here --------
        
        starHitbox = pygame.draw.rect(mainSurface,(255,0,0), pygame.Rect(starX,starY,30,30))
        slime.numPatches = 10
        groundSlime.numPatches = 10
        platSlime.numPatches = 10
        mc.animationFrameRate = 20
        
        keys = pygame.key.get_pressed()
        ev = pygame.event.poll()
        
        if ev.type == pygame.QUIT:
            break
        
        #stuff to do in the start gamestate
        if gamestate == 'start':
            
            #displaying text and buttons
            mainSurface.blit(jungle,(0,0))
            playButton.update()
            playButton.draw(mainSurface)
            ruleButton.update()
            ruleButton.draw(mainSurface)
            scoreButton.update()
            scoreButton.draw(mainSurface)
            title = titleFont.render("JUNGLE RAIDERS",1,(255,0,0))
            mainSurface.blit(title,(50,45))
            starButtonText = font2.render("PLAY",1,(255,255,255))
            mainSurface.blit(starButtonText,(262,282))
            rules = font4.render("RULES",1,(105,105,105))
            mainSurface.blit(rules,(527,352))
            scores = font4.render("HIGH SCORES",1,(255,255,255))
            mainSurface.blit(scores,(22,352))
            
            #if you press play
            if ev.type == pygame.MOUSEBUTTONUP:
                if playButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    #i reset all the characters and items in the game to their default postions
                    #because you can go back to the start gamestate when you already started the game
                    mc.charPos[0],mc.charPos[1] = 30,305
                    mc.numPatches = 4
                    mc.charRect = [650,630,90,75]
                    mc.origImageRect = [650,630,90,75]   
                    coinPoint = 0
                    lifeCount = 2
                    for i in range(len(coin)):
                        coin[i].visible = True
                    coin[0].itemPos[0] = 550
                    coin[0].itemPos[1] = 337
                    coin[1].itemPos[0] = 415
                    coin[1].itemPos[1] = 140
                    coin[2].itemPos[0] = 80
                    coin[2].itemPos[1] = 80
                    gamestate = 'game'
                    
                #change to rules page if you click on that button
                if ruleButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    gamestate = 'rules'
                
                #change to scores page if you click on that button
                if scoreButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    canAppend = True
                    gamestate = 'score'
        
        #when you are in the scores page
        if gamestate == 'score':
            
            #read the all the scores which are kept in a notepad
            file = open('score.txt', 'r')
            fileContents = file.readlines()
            file.close()
            
            if canAppend:
                for i in range(1,len(fileContents)+1):
                    #dont put the blank line from the notepad into the new list
                    #if fileContents[i-1] != '\n':
                    #strip the blank after each index
                    scoreTracker = fileContents[i-1] #.rstrip('\n')
                    #scoretracker reads 60 ticks/sec so divide by 60 to find seconds
                    highscore = int(scoreTracker) / 60
                    #change to 2 decimals 
                    highscore = round(highscore,2)
                    #print(scoreList)
                    scoreList.append(highscore)
                    #print(scoreList)
                #sort the list from smallest to biggest
                scoreList.sort()
                #print(scoreList)
                canAppend = False
            
            #display text and buttons needed on this screen
            returnButton.rect[0] = 520
            mainSurface.fill((255, 140, 105))
            returnButton.update()        
            returnButton.draw(mainSurface)
            returnText = font.render("Return",1,(255,255,255))
            mainSurface.blit(returnText,(528,360))
            topScores = font5.render("ALL-TIME HIGH SCORES",1,(105,105,105))
            mainSurface.blit(topScores,(35,20))
            first = font2.render("1st:",1,(255,215,0))
            mainSurface.blit(first,(185,100))
            second = font2.render("2nd:",1,(192,192,192))
            mainSurface.blit(second,(185,200))
            third = font2.render("3rd:",1,(176,141,87))
            mainSurface.blit(third,(185,300))
            #print out the top 3 scores 
            score1 = font2.render(f" {scoreList[0]} s",1,(255,215,0))
            mainSurface.blit(score1,(280,100))
            score2 = font2.render(f" {scoreList[1]} s",1,(192,192,192))
            mainSurface.blit(score2,(280,200))
            score3 = font2.render(f" {scoreList[2]} s",1,(176,141,87))
            mainSurface.blit(score3,(280,300))
            
            #return to start page when you click the button
            if ev.type == pygame.MOUSEBUTTONUP:
                if returnButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    gamestate = 'start'
                    #added
                    scoreList = []
        
        #if you are on teh rules page
        if gamestate == 'rules':
            
            #display the buttons and text needed
            mainSurface.fill((175,238,238))
            returnButton.rect[0] = 15
            returnButton.update()        
            returnButton.draw(mainSurface)
            returnText = font.render("Return",1,(255,255,255))
            mainSurface.blit(returnText,(21,360))
            
            description = font.render("- Collect the coins to redeem them in the shop",1,(105,105,105))
            mainSurface.blit(description,(75,23))
            description2 = font.render("- Number of lives",1,(105,105,105))
            mainSurface.blit(description2,(75,65))
            description3 = font.render("- Reach the star to win",1,(105,105,105))
            mainSurface.blit(description3,(75,110))
            description4 = font.render("- Don't run into the slimes",1,(105,105,105))
            mainSurface.blit(description4,(75,155))
            
            key1 = font4.render("JUMP",1,(105,105,105))
            mainSurface.blit(key1,(320,220))
            key2 = font4.render("MOVE BACKWARDS",1,(105,105,105))
            mainSurface.blit(key2,(100,330))
            key3 = font4.render("MOVE FORWARDS",1,(105,105,105))
            mainSurface.blit(key3,(430,330))
            
            #set the images needed for refence in this page
            coin[3].itemPos[0] = 30
            coin[3].itemPos[1] = 30
            coin[3].update()
            coin[3].draw(mainSurface)
            
            mainSurface.blit(heart,(27,70))
            mainSurface.blit(star,(25,110))
            mainSurface.blit(keyboard,(260,250))
            
            slime.charPos[0],slime.charPos[1] = 20,155
            slime.update()
            slime.draw(mainSurface)
            
            #return to start page if you click the button
            if ev.type == pygame.MOUSEBUTTONUP:
                if returnButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    slime.charPos[0] = 100
                    slime.charPos[1] = 150
                    gamestate = 'start'
        
        #gamestate for the actual game
        if gamestate == 'game':
            
            #needed for displaying things for small amounts of time
            frameCount += 1
            #keep track of time spent on this game (for highscores)
            timer += 1
            
            #coins are used in other gamestates, so I change them back to their default position
            coin[1].itemPos[0] = 415
            coin[1].itemPos[1] = 140
            coin[2].itemPos[0] = 80
            coin[2].itemPos[1] = 80
            coin[3].itemPos[0] = 11
            coin[3].itemPos[1] = 9
            
            # make all the slimes move around there designated locations
            if slimeMove:
                slime.move(.5,0)
            if not slimeMove:
                slime.move(-.5,0)            
            if slime.charPos[0] == 65:
                slimeMove = not slimeMove
            if slime.charPos[0] == 130:
                slimeMove = not slimeMove
            
            if slime2Move:
                groundSlime.move(-1,0)
            if not slime2Move:
                groundSlime.move(1,0)            
            if groundSlime.charPos[0] == 5:
                slime2Move = not slime2Move
            if groundSlime.charPos[0] == 350:
                slime2Move = not slime2Move
            
            if slime3Move:
                platSlime.move(.5,0)
            if not slime3Move:
                platSlime.move(-.5,0)            
            if platSlime.charPos[0] == 465:
                slime3Move = not slime3Move
            if platSlime.charPos[0] == 405:
                slime3Move = not slime3Move

            #check if hitting left side of final platbox
            if pygame.Rect.colliderect(mc.hitbox,endblock.platBox) and (mc.charPos[1] + mc.charRect[3] > endblock.platPos[1]+10) and mc.hitbox[0]<endblock.platPos[0]:
                canMoveR = False
            #check if hitting right side of final platbox
            if pygame.Rect.colliderect(mc.hitbox,endblock.platBox) and (mc.charPos[1] + mc.charRect[3] > endblock.platPos[1]+10) and mc.hitbox[0]>endblock.platPos[0]:
                canMoveL = False
            
            #check if hitting left side of 3rd platbox
            if pygame.Rect.colliderect(mc.hitbox,skyblock3.platBox) and (mc.charPos[1] + mc.charRect[3] > skyblock3.platPos[1]+10) and mc.hitbox[0]<skyblock3.platPos[0]:
                canMoveR = False
            #check if hitting right side of 3rd platbox
            if pygame.Rect.colliderect(mc.hitbox,skyblock3.platBox) and (mc.charPos[1] + mc.charRect[3] > skyblock3.platPos[1]+10) and mc.hitbox[0]>skyblock3.platPos[0]:
                canMoveL = False
                
            #check if hitting left side of middle platbox
            if pygame.Rect.colliderect(mc.hitbox,skyblock2.platBox) and (mc.charPos[1] + mc.charRect[3] > skyblock2.platPos[1]+10) and mc.hitbox[0]<skyblock2.platPos[0]:
                canMoveR = False
            #check if hitting right side of middle platbox
            if pygame.Rect.colliderect(mc.hitbox,skyblock2.platBox) and (mc.charPos[1] + mc.charRect[3] > skyblock2.platPos[1]+10) and mc.hitbox[0]>skyblock2.platPos[0]:
                canMoveL = False

            #check if hitting left side of bottom platbox
            if pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox) and (mc.charPos[1] + mc.charRect[3] > skyblock1.platPos[1]+10) and mc.hitbox[0]<skyblock1.platPos[0]:
                canMoveR = False
            if not (pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox)) and (mc.charPos[1] + mc.charRect[3] > skyblock1.platPos[1]+10) and (mc.hitbox[0] + 30) <skyblock1.platPos[0]:
                canMoveR = True
            #check if hitting right side of bottom platbox
            if pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox) and (mc.charPos[1] + mc.charRect[3] > skyblock1.platPos[1]+10) and mc.hitbox[0]>skyblock1.platPos[0]:
                canMoveL = False
            if not (pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox)) and (mc.charPos[1] + mc.charRect[3] > skyblock1.platPos[1]+10) and mc.hitbox[0]>=skyblock1.platPos[0] +108 :
                canMoveL = True
            
            if pygame.Rect.colliderect(mc.hitbox,groundBox) and not pygame.Rect.colliderect(mc.hitbox,skyblock1.bottomPlatBox):
                canMoveL = True
                canMoveR = True
                
            #if you collide with the second platform while underneath it 
            if (pygame.Rect.colliderect(mc.hitbox,skyblock2.bottomPlatBox)) and ((skyblock2.platPos[0] < mc.hitbox[0] + 30 < skyblock2.platPos[0] + 108) or (skyblock2.platPos[0] < mc.hitbox[0] < skyblock2.platPos[0] + 108)) and (mc.charPos[1] < skyblock2.platPos[1]+43):
                vel = 2
                vel += grav
                mc.charPos[1] += vel
                  
            #if you collide with the third platform while underneath it 
            if (pygame.Rect.colliderect(mc.hitbox,skyblock3.bottomPlatBox)) and (skyblock3.platPos[0] < mc.hitbox[0] < skyblock3.platPos[0] + 108) and (mc.charPos[1] < skyblock3.platPos[1]+43):
                vel = 2
                vel += grav
                mc.charPos[1] += vel
             
            #if you collide with the endblock while underneath it 
            if (pygame.Rect.colliderect(mc.hitbox,endblock.bottomPlatBox)) and (endblock.platPos[0] < mc.hitbox[0] < endblock.platPos[0] + 46) and (mc.charPos[1] < endblock.platPos[1]+43):
                vel = 2
                vel += grav
                mc.charPos[1] += vel
             
            #so you cant go above the screen
            if mc.hitbox[1] == 0:
                vel = 2
                vel += grav
                mc.charPos[1] += vel
            
            #checks if you are on top of any platform
            if pygame.Rect.colliderect(mc.hitbox,groundBox) and mc.charPos[1] + mc.charRect[3] < groundBox[1]+20:
                mc.charPos[1] = 305
                onPlat = True
            if pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox) and (mc.charPos[1] + mc.charRect[3]) < skyblock1.platBox[1]+20:
                mc.charPos[1] = 254
                onPlat = True
                canMoveR = True
                canMoveL = True
            if pygame.Rect.colliderect(mc.hitbox,skyblock2.platBox) and (mc.charPos[1] + mc.charRect[3]) < skyblock2.platBox[1]+20:
                mc.charPos[1] = 185
                onPlat = True
                canMoveR = True
                canMoveL = True
            if pygame.Rect.colliderect(mc.hitbox,skyblock3.platBox) and (mc.charPos[1] + mc.charRect[3]) < skyblock3.platBox[1]+20:
                mc.charPos[1] = 113
                onPlat = True
                canMoveR = True
                canMoveL = True
            if pygame.Rect.colliderect(mc.hitbox,endblock.platBox) and (mc.charPos[1] + mc.charRect[3]) < endblock.platBox[1]+20:
                mc.charPos[1] = 95
                onPlat = True
                canMoveR = True
                canMoveL = True
            
            #checks if you are not on a platform
            if not pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox) and not pygame.Rect.colliderect(mc.hitbox,groundBox) and not pygame.Rect.colliderect(mc.hitbox,skyblock2.platBox) and not pygame.Rect.colliderect(mc.hitbox,skyblock3.platBox)and not pygame.Rect.colliderect(mc.hitbox,endblock.platBox):
                onPlat = False
                
            #fix a bug where character gets stuck on first platform
            if mc.charPos[1] == 297.8:
                onPlat = False
            
            #if you are not on a platform, gravity will constantly pull you down
            if not onPlat: #gravity
                vel += grav
                mc.charPos[1] +=vel
            
            #to jump upwards
            if keys[pygame.K_UP] and ((pygame.Rect.colliderect(mc.hitbox,endblock.platBox) and (mc.charPos[1] + mc.charRect[3] < endblock.platBox[1]+20)) or (pygame.Rect.colliderect(mc.hitbox,skyblock3.platBox) and (mc.charPos[1] + mc.charRect[3] < skyblock3.platBox[1]+20)) or (pygame.Rect.colliderect(mc.hitbox,skyblock2.platBox) and (mc.charPos[1] + mc.charRect[3] < skyblock2.platBox[1]+20)) or (pygame.Rect.colliderect(mc.hitbox,skyblock1.platBox) and (mc.charPos[1] + mc.charRect[3] < skyblock1.platBox[1]+20)) or pygame.Rect.colliderect(mc.hitbox,groundBox)):
                vel = -7.5
                vel += grav
                mc.charPos[1] += vel 
                mc.numPatches = 1
                mc.charRect = [650,370,70,75]
                mc.origImageRect = [650,370,70,75]
                
            #if you can move left (not colliding with the side of a platform)
            if canMoveL:
                #move left and turn the character to face the left
                if keys[pygame.K_LEFT] and (mc.charPos[0] > -25):
                    if mc.direction == True: #first time turning left
                        mc.shiftRight()
                        mc.direction = False # left
                    if mc.moving == False:
                        mc.numPatches = 4
                        mc.charRect = [650,630,90,75]
                        mc.origImageRect = [650,630,90,75]
                        mc.moving = True
                    mc.move(-2,0)
            
            #move right
            if canMoveR:
                if keys[pygame.K_RIGHT] and (mc.charPos[0] < 550):
                    if mc.direction == False:
                        mc.shiftLeft()
                        mc.direction = True #right
                    if mc.moving == False:
                        mc.numPatches = 4
                        mc.charRect = [650,630,90,75]
                        mc.origImageRect = [650,630,90,75]
                        mc.moving = True
                    mc.move(2,0)
            
            #if you are pressing up and another movement key, display the walking animation instead of jumping
            #or else it will be stuck in the jumping animation even when you land on the floor
            if (keys[pygame.K_RIGHT] and keys[pygame.K_UP]) or (keys[pygame.K_LEFT] and keys[pygame.K_UP]):
                mc.numPatches = 4
                mc.charRect = [650,630,90,75]
                mc.origImageRect = [650,630,90,75]            
            
            #idle animation
            if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                mc.moving = False
                mc.origImageRect = [780,740,75,75]
                mc.numPatches = 2
            
            #hide the coin you hit
            for i in range(len(coin)):
                if pygame.Rect.colliderect(mc.hitbox,coin[i].itemBox):
                    chime.play()
                    coin[i].itemPos[0] = 0
                    coin[i].itemPos[1] = 0
                    coin[i].itemBox[0] = coin[i].itemPos[0]
                    coin[i].itemBox[1] = coin[i].itemPos[1]
                    coin[i].visible = False
                    coinPoint += 1

            #when you hit the slime, reset their positions so you dont immediately run into one again
            if pygame.Rect.colliderect(mc.hitbox,slime.hitbox) or pygame.Rect.colliderect(mc.hitbox,platSlime.hitbox) or pygame.Rect.colliderect(mc.hitbox,groundSlime.hitbox):
                
                groundSlime.charPos[0] = 345
                groundSlime.hitbox[0] = 345
                hurt.play()
                #remove one life
                if lifeCount > 0:
                    lifeCount -= 1
                    #coinPoint -= 1
                
                #spawn the character a in the air a little and have them fall down to the floor (no pracitcal usage, just for looks)
                mc.charPos[0] = 0
                mc.charPos[1] = 250
                showText = True
                frameCount = 0 #set framecount to zero (framecount is always increasing)
                        
            #when you reach the star, switch to the winning page
            if pygame.Rect.colliderect(mc.hitbox,starHitbox):
                victory.play()
                mc.origImageRect = [650,370,65,75]
                #write down the time needed to complete the game on a separate notepad
                countScore = open('score.txt', 'a')
                countScore.write(f"{timer}" + '\n')
                countScore.close()
                frameCount = 0
                gamestate = 'win'
            
            #the background images
            mainSurface.fill((64, 224, 208))
            mainSurface.blit(background,(0,0))
            
            #when you hit a slime display this text
            if showText:
                broke = font4.render("OUCH!!!",1,(255,0,0))
                mainSurface.blit(broke,(80,300))
            
            #framecount constantly increases and is set to zero when you hit a slime
            #thus the text will only show for a little 
            if showText and frameCount >25:
                showText = False
            
            #display the amount of lives and coins on the screen
            coinAmount = font.render(f": {coinPoint}",1,(0,0,0))
            mainSurface.blit(coinAmount,(40,0))
            
            lives = font.render(f": {lifeCount}",1,(0,0,0))
            mainSurface.blit(lives,(40,30))
            
            #when the player has 0 lives, switch to lose screen
            if lifeCount == 0:
                gamestate = 'lose'
                
            #animation for the heart and star
            if heartMove:   
                heartY += .25
            if heartY == 40:
                heartMove = not heartMove
            if not heartMove:
                heartY -= .25
            if heartY == 30:
                heartMove = not heartMove
            mainSurface.blit(heart,(7,heartY))
            
            if starY < 60:
                starVel += grav
                starY += starVel
            if starY > 60.1:
                starVel -= grav
                starY += starVel  
            mainSurface.blit(star,(starX,starY))
            
            #draw the platforms and their hitboxes
            skyblock1.draw(mainSurface)
            skyblock2.draw(mainSurface)
            skyblock3.draw(mainSurface)
            endblock.draw(mainSurface)
        
            #buttons and text
            shopButton.update()        
            shopButton.draw(mainSurface)
            shopText = font3.render("SHOP",1,(0,0,0))
            mainSurface.blit(shopText,(78,19))
            homeButton.update()        
            homeButton.draw(mainSurface)
            returnText = font3.render("HOME",1,(255,255,255))
            mainSurface.blit(returnText,(272,8))
            
            #if you click on one of the buttons, switch to their pages
            if ev.type == pygame.MOUSEBUTTONUP:
                if shopButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    gamestate = 'shop'
                if homeButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    gamestate = 'start'
            
            slime.update()
            slime.draw(mainSurface)
            groundSlime.update()
            groundSlime.draw(mainSurface)
            platSlime.update()
            platSlime.draw(mainSurface)
        
            
            #uncomment the block underneath here to look at the hitboxes 
            
#             pygame.draw.rect(mainSurface,(255,0,0),slime.hitbox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),groundSlime.hitbox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),platSlime.hitbox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),mc.hitbox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),skyblock1.platBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),skyblock2.platBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),skyblock3.platBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),endblock.platBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),groundBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),skyblock2.bottomPlatBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),skyblock3.bottomPlatBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),endblock.bottomPlatBox,2)
#             pygame.draw.rect(mainSurface,(255,0,0),starHitbox,2)
            
            for i in range(len(ground)):
                ground[i].draw(mainSurface)
                #pygame.draw.rect(mainSurface,(255,0,0),ground[i].platBox,2)

            for i in range(len(coin)):
                if coin[i].visible:
                    coin[i].update()
                    coin[i].draw(mainSurface)
                    #pygame.draw.rect(mainSurface,(255,0,0),coin[i].itemBox,2)
                    
            #drawing character and updating onto screen
            mc.update()
            #make characters hitbox follow her position
            mc.hitbox[0] = mc.charPos[0]
            mc.hitbox[1] = mc.charPos[1] + 8
            mc.draw(mainSurface)
            
        
        #for the shop page
        if gamestate == 'shop':
            
            frameCount += 1
            
            #text and buttons needed
            returnButton.rect[0] = 520
            mainSurface.blit(store,(0,0))
            shopText = font2.render("The Jungle Cache",1,(0,0,0))
            mainSurface.blit(shopText,(160,10))
            balance = font.render(f"Balance: {coinPoint}",1,(0,0,0))
            shopHeart = font.render(f": {lifeCount}",1,(0,0,0))
            mainSurface.blit(balance,(10,5))
            mainSurface.blit(shopHeart,(40,30))
            mainSurface.blit(heart,(7,33))
            returnButton.update()        
            returnButton.draw(mainSurface)
            heartButton.update()        
            heartButton.draw(mainSurface)
            potionButton.update()        
            potionButton.draw(mainSurface)
            returnText = font.render("Return",1,(255,255,255))
            mainSurface.blit(returnText,(528,360))
            price1 = font4.render("3",1,(255,255,255))
            mainSurface.blit(price1,(240,273))
            price2 = font4.render("5",1,(255,255,255))
            mainSurface.blit(price2,(342,273))
            mainSurface.blit(heart2,(230,230))
            mainSurface.blit(potion,(320,220))
            
            coin[1].itemPos[0] = 360
            coin[1].itemPos[1] = 278
            coin[1].update()
            coin[1].draw(mainSurface)
            coin[2].itemPos[0] = 115
            coin[2].itemPos[1] = 12
            coin[2].update()
            coin[2].draw(mainSurface)
            coin[3].itemPos[0] = 256
            coin[3].itemPos[1] = 278
            coin[3].update()
            coin[3].draw(mainSurface)
            
            if ev.type == pygame.MOUSEBUTTONUP:
                
                #if you purchase a life
                if heartButton.collidePoint(pygame.mouse.get_pos()):
                    if coinPoint >= 3:
                        cash.play()
                        coinPoint -= 3
                        lifeCount += 1
                                                
                    
                # if you don't have enough coins to purchase the item
                if potionButton.collidePoint(pygame.mouse.get_pos()) or (heartButton.collidePoint(pygame.mouse.get_pos()) and coinPoint < 3):
                    frameCount = 0
                    showText = True
                
                #return to game if button is pressed
                if returnButton.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    gamestate = 'game'
                    
                if potionButton.collidePoint(pygame.mouse.get_pos()):
                    buzzer.play()
            
            #show text for a bit if user doesn't have enough coins
            if showText:
                broke = font4.render("Insufficient Coins!!!",1,(255,0,0))
                mainSurface.blit(broke,(230,330))
                
            if showText and frameCount > 60:
                showText = False          
        
        #during win screen
        if gamestate == 'win':
            if frameCount < 66:
                frameCount += 1
            if frameCount == 65:
                winSound.play()
                
            #text, buttons, and animations needed
            returnButton.rect[0] = 520
            mc.origImageRect = [650,370,65,75]
            mainSurface.fill((209,237,242))
            
            mc.numPatches = 5
            mc.charPos[0],mc.charPos[1] = 260,190
            mc.update()
            mc.draw(mainSurface)
        
            winText = font2.render("The Jungle Raider has",1,((128,128,128)))
            mainSurface.blit(winText,(100,20))
            winText2 = font2.render("found the treasure!",1,((128,128,128)))
            mainSurface.blit(winText2,(120,65))
            
            #have a 'coin shower' where coins constantly fall 
            for i in range(len(coinShower)):
                coinShower[i].update()
                coinShower[i].draw(mainSurface)
                coinShower[i].itemPos[1] += 1
                
                if coinShower[i].itemPos[1] == 420:
                    coinShower[i].itemPos[1] = -25
            
            returnButton.update()        
            returnButton.draw(mainSurface)
            returnText = font.render("Replay",1,(255,255,255))
            mainSurface.blit(returnText,(528,360))
            home2Button.update()        
            home2Button.draw(mainSurface)
            homeText = font.render("Home",1,(255,255,255))
            mainSurface.blit(homeText,(532,320))
        
        #during the losing page
        if gamestate == 'lose':
            
            #all of this is just animations, text, and buttons for this screen

            if frameCount == 40:
                loss.play()
            returnButton.rect[0] = 520
            mainSurface.fill((177,156,217))
            
            if frameCount < 100:
                mc.animationFrameRate = 50
                frameCount += 1
                mc.numPatches = 2
                mc.charPos[0],mc.charPos[1] = 260,190
                mc.origImageRect = [510,105,70,60]
                
                nap = font3.render("Imma take a nap",1,(255,255,255))
                mainSurface.blit(nap,(300,155))
            
            else:
                mc.animationFrameRate = 20
                mc.numPatches = 1
                mc.origImageRect = [580,105,70,60]
                nap = font3.render("zzz",1,(255,255,255))
                mainSurface.blit(nap,(350,180))
        
            
            mc.update()
            mc.draw(mainSurface)
            
            returnButton.update()        
            returnButton.draw(mainSurface)
            returnText = font.render("Replay",1,(255,255,255))
            mainSurface.blit(returnText,(528,360))
            home2Button.update()        
            home2Button.draw(mainSurface)
            homeText = font.render("Home",1,(255,255,255))
            mainSurface.blit(homeText,(532,320))
            wake = font2.render("The Jungle Raider has fallen",1,(255,255,255))
            wake2 = font2.render("unconscious. Shake her awake!!!",1,(255,255,255))
            mainSurface.blit(wake,(20,5))
            mainSurface.blit(wake2,(20,50))
            shake = font.render("(Shake the Microbit or press 'Replay')",1,(255,255,255))
            mainSurface.blit(shake,(10,360))

              
        if gamestate == 'win' or gamestate == 'lose':
            #replay the game if user chooses to, also reset all characters positions back to default
            if (ev.type == pygame.MOUSEBUTTONUP and returnButton.collidePoint(pygame.mouse.get_pos())) or (gamestate == 'lose' and shaking == True):
                click.play()
                groundSlime.charPos[0] = 345
                groundSlime.hitbox[0] = groundSlime.charPos[0]
                groundSlime.hitbox[1] = groundSlime.charPos[1]
                mc.charPos[0],mc.charPos[1] = 30,305
                mc.numPatches = 4
                mc.charRect = [650,630,90,75]
                mc.origImageRect = [650,630,90,75]   
                coinPoint = 0
                lifeCount = 2
                for i in range(len(coin)):
                    coin[i].visible = True
                coin[0].itemPos[0] = 550
                coin[0].itemPos[1] = 337
                coin[1].itemPos[0] = 415
                coin[1].itemPos[1] = 140
                coin[2].itemPos[0] = 80
                coin[2].itemPos[1] = 80
                gamestate = 'game'
            
            #go to start page if button is pressed
            if ev.type == pygame.MOUSEBUTTONUP:
                if home2Button.collidePoint(pygame.mouse.get_pos()):
                    click.play()
                    gamestate = 'start'
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
main() #run the game for the first time