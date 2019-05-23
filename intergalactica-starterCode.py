##### INTERGALACTICA 
#By Maya Krishnan
# 15-112 Term Project - S19
#This file contains the main game code for my term project, Intergalactica.
######
import pygame
import os
import sys
from pygame.locals import *
import math
import datetime
import random
import string
import copy

from classes import GameItem, Rocket, Missile, Asteroid, Coin, Life, Booster, EndPlanet, Alien, Wind, Wormhole, Meteor

####
####
### HELPER FUNCTIONS

#helper function to get center coordinates of an image relative to its position
def getCenterCoords(image):
    cx = image.get_width()//2
    cy = image.get_height()//2
    return (cx, cy)

#draws surface1 onto surface2 with center at position
def drawCentered(surface1, surface2, position):
    width = surface1.get_width()
    height = surface1.get_height()
    xCoord = position[0] - width//2
    yCoord = position[1] - height//2
    surface2.blit(surface1, (xCoord, yCoord))
 
#taken from 15-112 course notes
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

#taken from 15-112 course notes
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)
   
#finds the high score for a given username
def findHighScore(path, name1):
    bestScore = 0
    contents = readFile(path)
    for line in contents.splitlines():
        if line=='':
            continue
        else:
            name2 = line.split("\t")[0]
            if name2 == name1:
                score = int(line.split("\t")[1])
                if score>bestScore:
                    bestScore = score
    return bestScore
 
#creates a list of tuples of the form (username, highscore)
def createHighList(path):
    L = []
    seenSet = set()
    contents = readFile(path)
    for line in contents.splitlines():
        if line=='':
            continue
        else:
            name = line.split("\t")[0]
            if name not in seenSet:
                L.append((name, findHighScore(path, name)))
                seenSet.add(name)
    return L
 
#finds the coins associated with a given username
def findCoins(path, name1):
    coins = 0
    contents = readFile(path)
    for line in contents.splitlines():
        if line=='':
            continue
        else:
            name2 = line.split("\t")[0]
            if name2 == name1:
                coins = int(line.split("\t")[2])
    return coins

#returns whether the upgrade rocket is purchased or not by a given username    
def oneBought(path, name1):
    bought = False
    contents = readFile(path)
    for line in contents.splitlines():
        if line=='':
            continue
        else:
            name2 = line.split("\t")[0]
            if name2 == name1:
                bought = bool(int(line.split("\t")[3]))
    return bought
    
    
#creates a text surface
def createSurface(text, font, color):
    textsurface = font.render(text, False, color)
    return textsurface
    
#gets the highest score in a list of tuple of the form (username, highscore)    
def getHighest(L):
    best = 0
    for t in L:
        if t[1]>best:
            best = t[1]
    return best
        

###### 
######
#####

#structure of background scrolling taken from: https://github.com/techwithtim/side_scroller
#modified code from: https://github.com/aminb/asteroids/blob/master/game.py 
class myGame(object):
    
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.font.init()
        # soundtrack of game from https://github.com/aminb/asteroids/blob/master/game.py 
        self.soundtrack = pygame.mixer.Sound('sounds/soundtrack.wav')
        self.soundtrack.set_volume(.3)
        self.username = ""
        self.soundtrack.play(-1, 0, 1000)

        self.level = 1
        #from pngmart.com
        self.rocketImg1 = pygame.image.load(os.path.join('images', 'rocket-1.png'))
        #from dlpng.com
        self.rocketImg2 = pygame.image.load(os.path.join('images','rocket-2.png'))
        self.rocket = Rocket((100,150), self.rocketImg1)
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        
        #bg image from backgroundcheckall.com
        self.bg = pygame.image.load(os.path.join('images','bg-galaxy_1.png'))
        self.bgX = 0
        self.bgX2 = self.bg.get_width() 
        self.distanceCheck = 0
        self.distanceCheck2 = 0
        self.distanceCheck3 = 0
        self.distanceCheck4 = 0
        
        #from soundbible.com
        self.breakAstsound = pygame.mixer.Sound(os.path.join("sounds", "rock_break.wav"))
        self.turboSound = pygame.mixer.Sound(os.path.join("sounds", "turbo.wav"))
        self.thunderSound = pygame.mixer.Sound(os.path.join("sounds", "thunder.wav"))
        self.breakAstsound.set_volume(.6)
        
        self.width, self.height = 800, 447
        self.window = pygame.display.set_mode((self.width,self.height))
        self.objects = []
        self.score = 0
        self.lives = 6
        self.speed = 40
        self.clock = pygame.time.Clock()
        
        pygame.time.set_timer(USEREVENT+1, random.randint(1400, 1500))
        pygame.time.set_timer(USEREVENT+2, random.randint(5000, 8000))
        pygame.time.set_timer(USEREVENT+3, random.randint(15000, 18000))
        pygame.time.set_timer(USEREVENT+4, random.randint(5000, 9000))
        pygame.time.set_timer(USEREVENT+5, random.randint(2500, 4400))
        pygame.time.set_timer(USEREVENT+6, random.randint(16000, 30000))
        pygame.time.set_timer(USEREVENT+7, random.randint(14000, 15000))
        pygame.key.set_repeat(1, 24)

        self.turbulence = False
        self.turbulenceDist = 8
        self.turbulenceCounter = 1
        
        self.boostCount = 1
        self.turbo = False
        self.start = False
        self.backscroll = False
        self.push = 3.0
        self.restart = False
        self.helpMode = False
        self.reached1 = False
        self.reached2 = False
        self.reached3 = False
        self.reached4 = False
        self.levelUp = False
        self.pause = False
        self.gameOver = False
        self.youWon = False
        self.displayStats = False
        self.wormholeModeOn = False
        self.wormTimer = 1
        self.wormholeObjects = []
        self.wormBg = pygame.image.load(os.path.join('images','blackBG.png'))
        self.displayLeaderBoard = False
        self.upgrade1 = False
        
        self.menu1 = True
        self.menu2 = False
        
        self.playButton = pygame.image.load(os.path.join('images','buttons','play.png'))
        self.menuButton = pygame.image.load(os.path.join('images','buttons','menu.png'))
        self.helpButton = pygame.image.load(os.path.join('images','buttons','help.png'))
        self.leaderButton = pygame.image.load(os.path.join('images','buttons','leaderbord.png'))
        self.statsButton = pygame.image.load(os.path.join('images','buttons','stats.png'))
        self.upgradesButton = pygame.image.load(os.path.join('images','buttons','upgrades.png'))
        self.backButton = pygame.image.load(os.path.join('images','buttons','back.png'))
        self.helpscr = pygame.image.load(os.path.join('images','helpscr.png'))
        self.buy2 = pygame.image.load(os.path.join('images','buttons','buyImg.png'))
        self.r1 = pygame.image.load(os.path.join('images','buttons','r1disp.png'))
        self.r2 = pygame.image.load(os.path.join('images','buttons','r2disp.png'))
        self.r1desc = pygame.image.load(os.path.join('images','buttons','r1descrip.png'))
        self.r2desc = pygame.image.load(os.path.join('images','buttons','r2descrip.png'))
        self.coins2 = pygame.image.load(os.path.join('images','buttons','100coins.png'))
        self.bought1 = None
        self.r1select = True
        self.r2select = False
        
        self.newWormholes = []
        self.appendNewW = 1
        
        self.appendWormhole = 0

        self.fire_time = datetime.datetime.now()
        self.coinCount = 0
        self.highScoreList = []
        self.isActive = False
        myGame.signIn(self)
            
    #prompts the user to sign in with a username
    def signIn(self):
        while True:
            self.window.fill((0, 0, 0))
            start = pygame.image.load('images/signInscr.png')
            self.window.blit(start, (55, 0))
            prompt = createSurface("Click to enter your username", self.font, (255, 255, 255))
            input = createSurface(str(self.username), self.font, (255, 0, 0))
            
            drawCentered(prompt, self.window, (self.width//2, self.height//2))
            if self.isActive:
                pygame.draw.rect(self.window, (0, 0, 255),(self.width//2-150, 2*self.height//3-25, 300, 50))
                drawCentered(input, self.window, (self.width//2, 2*self.height//3))
            else:
                pygame.draw.rect(self.window, (255, 255, 255), (self.width//2-150, 2*self.height//3-25, 300, 50))
                drawCentered(input, self.window, (self.width//2, 2*self.height//3))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos[0], event.pos[1]
                    if self.width//2-150 < x < self.width//2-150 + 300 and 2*self.height//3-25 < y < 2*self.height//3-25 + 50:
                        self.isActive = not self.isActive
                if event.type == pygame.KEYDOWN:
                    if self.isActive:
                        if event.key == pygame.K_RETURN:
                            self.bought1 = oneBought('scoreTracker.txt', str(self.username))
                            self.coinCount = findCoins("scoreTracker.txt", str(self.username))
                            self.highScoreList = createHighList("scoreTracker.txt")
                            myGame.run(self)
                        elif event.key == pygame.K_BACKSPACE:
                            self.username = self.username[:-1]
                        else:
                            self.username += event.unicode
                pygame.display.update()
                
            
    #called when the user enters a wormhole - takes the rocket to an alternate universe    
    def wormholeMode(self):
        if self.r1select:
            rotated1 = pygame.image.load(os.path.join("images", "rocket-1-rotate.png"))
            self.rocket = Rocket((400, 350), rotated1)
        elif self.r2select:
            rotated2 = pygame.image.load(os.path.join("images", "rocket-2-rotate.png"))
            self.rocket = Rocket((400, 350), rotated1)
        while self.wormholeModeOn:
            
            self.appendNewW+=1
            self.push = 9.0
            
            self.window.blit(self.wormBg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type==USEREVENT+1:
                    #from kisspng.com
                    img = pygame.image.load(os.path.join('images','meteor.png'))
                    for i in range(3):
                        self.wormholeObjects.append(Meteor(img))
                        
                #flashes the screen to give a lightning effect
                if event.type==USEREVENT+4:
                    self.window.fill((255, 255, 255))
                    self.thunderSound.play()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.rocket.moveUp()
                elif keys[pygame.K_DOWN]:
                    self.rocket.moveDown()
                elif keys[pygame.K_RIGHT]:
                    self.rocket.moveRight()
                elif keys[pygame.K_LEFT]:
                    self.rocket.moveLeft()
            self.rocket.draw(self.window)
            for meteor in self.wormholeObjects:
                meteor.fall()
                meteor.draw(self.window)
                
            for meteor in self.wormholeObjects:
                if meteor.collidesWithRocket(self.rocket.position[0],\
                self.rocket.position[1], self.rocket.image):
                    self.wormholeObjects.remove(meteor)
                    self.lives-=1
            if self.lives==0:
                    self.gameOver=True
                    myGame.gameOver(self)
            for i in range(self.lives):
                life = pygame.image.load(os.path.join('images','rocket-lives.png'))
                self.window.blit(life, (10, 25+i*life.get_height()))
                
            if self.appendNewW>800:
                #image from clipart-library.com
                self.newWormholes.append(Wormhole((random.randint(0, 800), 0),pygame.image.load(os.path.join('images','wormhole.png'))))
                self.appendNewW = 0
                
            for wormhole in self.newWormholes:
                wormhole.draw(self.window)
                
            for wormhole in self.newWormholes:
                wormhole.fall()
            
            for wormhole in self.newWormholes:
                if wormhole.collidesWithRocket(self.rocket.position[0],\
                self.rocket.position[1], self.rocket.image):
                    self.appendNewW = 0
                    self.newWormholes = []
                    self.wormholeModeOn = False
                    self.start = True
                    if self.r1select:
                        self.rocket = Rocket((100,150),self.rocketImg1)
                    elif self.r2select:
                        self.rocket = Rocket((100,150),self.rocketImg2)
                    myGame.run(self)
            pygame.display.update()
    
    #displayes a leaderboard when called        
    def displayLeaderBoard(self):
        smallText = pygame.font.SysFont("Arial", 50)
        largeText = pygame.font.SysFont("Arial",80)
        L1 =copy.copy(self.highScoreList)
        valList = []
        L2 = []
        for t in L1:
            valList.append(t[1])
        newL = sorted(valList)[::-1]
        for i in range(len(L1)):
            if L1[i][1]==newL[0]:
                L2.append(L1[i])
                L1.pop(i)
                break
        for i in range(len(L1)):
            if L1[i][1]==newL[1]:
                L2.append(L1[i])
                L1.pop(i)
                break
        for i in range(len(L1)):
            if L1[i][1]==newL[2]:
                L2.append(L1[i])
                L1.pop(i)
                break
        for i in range(len(L1)):
            if L1[i][1]==newL[3]:
                L2.append(L1[i])
                L1.pop(i)
                break
        bg = pygame.image.load(os.path.join('images','leaderbg.png'))
        self.window.blit(bg, (0, 0))
        self.window.blit(self.backButton, (30, 30))
        title = createSurface("LEADERBOARD" ,largeText, (255, 255, 255))
        drawCentered(title, self.window, (self.width//2, self.height//2-120))
        firstname = createSurface("1. " +L2[0][0] ,smallText, (255, 255, 255))
        firstscore = createSurface(str(L2[0][1]), smallText, (255, 255, 255))
        self.window.blit(firstname, (self.width//2-200, self.height//2-60))
        drawCentered(firstscore, self.window, (self.width//2+150, self.height//2-50))
        secondname = createSurface("2. " +L2[1][0] ,smallText, (255, 255, 255))
        secondscore = createSurface(str(L2[1][1]), smallText, (255, 255, 255))
        self.window.blit(secondname, (self.width//2-200, self.height//2-20))
        drawCentered(secondscore, self.window, (self.width//2+150, self.height//2-10))
        thirdname = createSurface("3. " +L2[2][0] ,smallText, (255, 255, 255))
        thirdscore = createSurface(str(L2[2][1]), smallText, (255, 255, 255))
        self.window.blit(thirdname, (self.width//2-200, self.height//2+20))
        drawCentered(thirdscore, self.window, (self.width//2+150, self.height//2+30))
        fourthname = createSurface("4. " +L2[3][0] ,smallText, (255, 255, 255))
        fourthscore = createSurface(str(L2[3][1]), smallText, (255, 255, 255))
        self.window.blit(fourthname, (self.width//2-200, self.height//2+60))
        drawCentered(fourthscore, self.window, (self.width//2+150, self.height//2+70))
        while self.displayLeaderBoard:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    myGame.buttonCheck(self, x, y)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_l]:
                    self.displayLeaderBoard = False
                    myGame.run(self)
            pygame.display.update()
    
    #pauses the game        
    def paused(self):
        largeText = pygame.font.SysFont("comicsansms",115)
        TextSurf = createSurface("Paused", largeText, (255, 255, 255))
        drawCentered(TextSurf, self.window, (self.width//2, self.height//2))
        while self.pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_p]:
                    self.paused = False
                    myGame.run(self)
            pygame.display.update()
    
    #called to restart game
    def restartGame(self):
        myGame.__init__(self)
    
    #called when the user loses all lives
    def gameOver(self):
        largeText = pygame.font.SysFont("comicsansms",115)
        TextSurf = createSurface("GAME OVER", largeText, (255, 255, 255))
        smallText = pygame.font.SysFont("comicsansms", 70)
        surf2 = createSurface("Press [r] to restart", smallText, (255, 255, 255))
        drawCentered(TextSurf, self.window, (self.width//2, self.height//2))
        drawCentered(surf2, self.window, (self.width//2, self.height//2+70))
        #updates the score tracking text file
        file = open("scoreTracker.txt", "a+")
        file.write(str(self.username) + "\t" + str(self.score) +"\t" + str(self.coinCount)+ "\t" + str(int(self.bought1)) + "\n")
        file.close()
        while self.gameOver:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    myGame.restartGame(self)
            pygame.display.update()
    
    #called when user reaches the end of the last level
    def youWon(self):
        largeText = pygame.font.SysFont("comicsansms",115)
        TextSurf = createSurface("YAY! YOU WON!", largeText, (255, 255, 255))
        smallText = pygame.font.SysFont("comicsansms", 70)
        surf2 = createSurface("Press [r] to restart", smallText, (255, 255, 255))
        drawCentered(TextSurf, self.window, (self.width//2, self.height//2))
        drawCentered(surf2, self.window, (self.width//2, self.height//2+70))
        #updates the score tracking text file
        file = open("scoreTracker.txt", "a+")
        file.write(str(self.username) + "\t" + str(self.score) +"\t" + str(self.coinCount)+"\t" + str(int(self.bought1)) + "\n")
        file.close()
        while self.youWon:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    myGame.restartGame(self)
            pygame.display.update()
    
    #displays the help screen when called    
    def displayHelp(self):
        self.window.fill((0, 0, 0))
        help = pygame.image.load(os.path.join('images','helpscr.png'))
        drawCentered(help, self.window, (self.width//2, self.height//2))
        self.window.blit(self.backButton, (30, 30))
        pygame.display.update()
        while self.helpMode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    myGame.buttonCheck(self, x, y)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_h]:
                    self.helpMode = False
                    myGame.run(self)
            pygame.display.update()
     
    #called when the user reaches the end of a level
    def levelUp(self):
        self.window.fill((0, 0, 0))
        largeText = pygame.font.SysFont("comicsansms",90)
        TextSurf1 = createSurface("LEVEL UP!", largeText, (255, 255, 255))
        smallText = pygame.font.SysFont("comicsansms",50)
        TextSurf2 = createSurface("Press [Enter] to continue", smallText, (255, 255, 255))
        self.window.blit(TextSurf1, (160, 100))
        self.window.blit(TextSurf2, (100, 160))
        while self.levelUp:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    self.levelUp = False
                    myGame.run(self)
            pygame.display.update()
   
    #displays the rocket upgrades screen and allows a user to buy a new rocket
    def upgrade3(self):
        while self.upgrade1:
            bg = pygame.image.load(os.path.join('images','leaderbg.png'))
            self.window.blit(bg, (0, 0))
            largeText = pygame.font.SysFont("Arial",60)
            textSurf = createSurface("UPGRADES",largeText, (255, 255, 255))
            self.window.blit(textSurf, (270, 10))
            self.window.blit(self.backButton, (30, 30))
            coinTextSurf = createSurface(str(self.coinCount), self.font, (255, 255, 255))
            self.window.blit(coinTextSurf,(740, 10))
            self.window.blit(pygame.image.load(os.path.join('images','coin-small.png')), (700, 10))
            
            self.window.blit(self.r1, (200, 50))
            self.window.blit(self.r2, (500, 50))
            self.window.blit(self.r1desc, (140, 250))
            self.window.blit(self.r2desc,(420, 250))
            if not self.bought1:
                self.window.blit(self.coins2, (525, 400))
                self.window.blit(self.buy2, (490, 350))
                
            if self.r1select:
                pygame.draw.rect(self.window, (255, 255, 255), [190, 45, 20+self.r1.get_width(), 15+self.r1.get_height()], 6)
            elif self.r2select:
                pygame.draw.rect(self.window, (255, 255, 255), [490, 45, 20+self.r2.get_width(), 15+self.r2.get_height()], 6)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    myGame.buttonCheck(self, x, y)
            pygame.display.update()
    
    #displays the statistics for a given username
    def statsDisp(self):
        while self.displayStats:
            bg = pygame.image.load(os.path.join('images','leaderbg.png'))
            self.window.blit(bg, (0, 0))
            largeText = pygame.font.SysFont("comicsansms",90)
            smallText = pygame.font.SysFont("comicsansms",50)
            title = createSurface('STATS', largeText, (255, 255, 255))
            self.window.blit(title, (300, 10))
            
            scoreName = createSurface("Your Highscore: ", smallText, (255, 255, 255))
            highscore = findHighScore('scoreTracker.txt', str(self.username))
            scoreSurf = createSurface(str(highscore), smallText, (255, 255, 255))
            
            coinName = createSurface("Coins: ", smallText, (255, 255, 255))
            coins = findCoins('scoreTracker.txt', str(self.username))
            coinSurf = createSurface(str(coins), smallText, (255, 255, 255))
            self.window.blit(self.backButton, (30, 30))
            
            self.window.blit(scoreName, (200, 100))
            self.window.blit(scoreSurf, (600, 100))
            
            self.window.blit(coinName, (200, 200))
            self.window.blit(coinSurf, (600, 200))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    myGame.buttonCheck(self, x, y)
            pygame.display.update()
            
            
    #checks for MOUSEBUTTONDOWN events and calls appropriate functions
    def buttonCheck(self, x, y):
        if self.menu1:
            if 200<x<200+self.playButton.get_width() and 350<y<350+self.playButton.get_height():
                self.start = True
                myGame.run(self)
            if 450<x<450+self.menuButton.get_width() and 350<y<350+self.menuButton.get_height():
                self.menu2 = True
                self.menu1 = False
                myGame.run(self)
        
        if self.helpMode:
            if 30<x<30+self.backButton.get_width() and 30<y<30+self.backButton.get_height():
                self.helpMode = False
                self.menu2 = True
                myGame.run(self)
                
        if self.upgrade1:
            if 30<x<30+self.backButton.get_width() and 30<y<30+self.backButton.get_height():
                self.upgrade1 = False
                self.menu2 = True
                myGame.run(self)
                
            if 490<x<490+self.buy2.get_width() and 350<y<350+self.buy2.get_width():
                if self.coinCount>=100:
                    self.bought1 = True
                    self.coinCount-=100
                    myGame.upgrade3(self)
                else:
                    myGame.upgrade3(self)
            if 500<x<500+self.r2.get_width() and 50<y<50+self.r2.get_height():
                if self.bought1:
                    self.rocket = Rocket((100,150),self.rocketImg2)
                    self.r2select = True
                    self.r1select = False
            if 200<x<200+self.r1.get_width() and 50<y<50+self.r1.get_height():
                self.rocket = Rocket((100, 150), self.rocketImg1)
                self.r1select = True
                self.r2select = False
        if self.displayLeaderBoard:
            if 30<x<30+self.backButton.get_width() and 30<y<30+self.backButton.get_height():
                self.displayLeaderBoard = False
                self.menu2 = True
                myGame.run(self)
        if self.displayStats:
            if 30<x<30+self.backButton.get_width() and 30<y<30+self.backButton.get_height():
                self.displayStats = False
                self.menu2 = True
                myGame.run(self)
            
        if self.menu2:
            if self.width//2-self.helpButton.get_width()//2<x<self.width//2+self.helpButton.get_width()//2 and self.height//2-130 - self.helpButton.get_height()//2<y<self.height//2-130+self.helpButton.get_height():
                self.menu2 = False
                self.helpMode = True
                myGame.displayHelp(self)
                
                
            if self.width//2-self.leaderButton.get_width()//2<x<self.width//2+self.leaderButton.get_width()//2 and self.height//2-40 - self.leaderButton.get_height()//2<y<self.height//2-40+self.leaderButton.get_height():
                self.menu2 = False
                self.displayLeaderBoard = True
                myGame.displayLeaderBoard(self)
                
            if self.width//2-self.statsButton.get_width()//2<x<self.width//2+self.statsButton.get_width()//2 and self.height//2+50 - self.statsButton.get_height()//2<y<self.height//2+50+self.statsButton.get_height():
                self.menu2 = False
                self.displayStats = True
                myGame.statsDisp(self)
                
            if self.width//2-self.upgradesButton.get_width()//2<x<self.width//2+self.upgradesButton.get_width()//2 and self.height//2+140 - self.upgradesButton.get_height()//2<y<self.height//2+140+self.upgradesButton.get_height():
                self.menu2 = False
                self.upgrade1 = True
                myGame.upgrade3(self)
            
            if 30<x<30+self.backButton.get_width() and 30<y<30+self.backButton.get_height():
                self.menu2 = False
                self.menu1 = True
                myGame.run(self)
      
    #called in the run function: draws all on screen objects while the game is running or menus are being displayed
    def redrawWindow(self):
        if (not self.start) and self.menu1:
            self.window.fill((0, 0, 0))
            start = pygame.image.load(os.path.join('images','menu1scr.png'))
            self.window.blit(start, (50, 0))
            self.window.blit(self.playButton, (200, 350))
            self.window.blit(self.menuButton, (450, 350))
            pygame.display.update()
            
        if (not self.start) and self.menu2:
            bg = pygame.image.load(os.path.join('images','leaderbg.png'))
            self.window.blit(bg, (0, 0))
            drawCentered(self.helpButton, self.window, (self.width//2, self.height//2-130))
            drawCentered(self.leaderButton, self.window, (self.width//2, self.height//2-40))
            drawCentered(self.statsButton, self.window, (self.width//2, self.height//2+50))
            drawCentered(self.upgradesButton, self.window, (self.width//2, self.height//2+140))
            self.window.blit(self.backButton,(30, 30))
            pygame.display.update()
            
        if self.start:
            self.window.blit(self.bg, (self.bgX, 0))
            self.window.blit(self.bg, (self.bgX2, 0))
            for missile in self.rocket.missiles:
                missile.draw(self.window)
            self.rocket.draw(self.window)
            for object in self.objects:
                object.draw(self.window)
            scoreTextSurf = createSurface("Score: " + str(self.score), self.font, (255, 255, 255))
            coinTextSurf = createSurface(str(self.coinCount), self.font, (255, 255, 255))
            levelTextSurf = createSurface("LEVEL " + str(self.level), self.font, (255, 255, 255))
            self.window.blit(scoreTextSurf, (10, 10))
            self.window.blit(coinTextSurf,(740, 10))
            self.window.blit(levelTextSurf,(380, 10))
            self.window.blit(pygame.image.load(os.path.join('images','coin-small.png')), (700, 10))
            for i in range(self.lives):
                life = pygame.image.load(os.path.join('images','rocket-lives.png'))
                self.window.blit(life, (10, 25+i*life.get_height()))
            if self.turbo:
                turboTextSurf = createSurface("TURBO MODE ON!", self.font, (255, 255, 255))
                self.window.blit(turboTextSurf, (330, 400))
                smallFire = pygame.image.load(os.path.join('images','fire-small.png'))
                self.window.blit(smallFire, (300, 400))
            startX = 240
            if self.level==1:
                endX = startX + self.distanceCheck//60
                pygame.draw.line(self.window, (255, 255, 255), (startX, 35),(endX, 35), 10)
            if self.level==2:
                endX = startX + (self.distanceCheck2-20000)//60
                pygame.draw.line(self.window, (255, 255, 255), (startX, 35),(endX, 35), 10)
            if self.level==3:
                endX = startX + (self.distanceCheck3-40000)//60
                pygame.draw.line(self.window, (255, 255, 255), (startX, 35),(endX, 35), 10)
            if self.level==4:
                endX = startX + (self.distanceCheck4-60000)//60
                pygame.draw.line(self.window, (255, 255, 255), (startX, 35),(endX, 35), 10)
            planetDisplay = pygame.image.load(os.path.join('images','end-planetred-small.png'))
            self.window.blit(planetDisplay,(590, 30))
            pygame.display.update()
            
    #modified/edited code from https://github.com/aminb/asteroids/blob/master/game.py 
    def run(self):
        running = True
        while running:
            #calls draw function
            myGame.redrawWindow(self)
            if self.turbulence and self.turbulenceCounter%20==0:
                self.turbulenceDist = -self.turbulenceDist
                if self.turbulenceDist<0:
                    self.turbulenceDist+=1
                if self.turbulenceDist>0:
                    self.turbulenceDist-=1
                if self.turbulenceDist==0:
                    self.turbulence=False
                    self.turbulenceDist=6
            
            #increments the turbulence counter
            if self.turbulence:
                self.turbulenceCounter+=1
                
                self.rocket.position[1]+=self.turbulenceDist
                self.rocket.cY += self.turbulenceDist
            
            #implements backward side scrolling
            if self.rocket.collidesWithLeft():
                if self.turbo:
                    self.push = -12
                else:
                    self.push = -3
                
            #checks for turbo mode and changes the sidescroll rate accordingly
            if not self.rocket.collidesWithLeft():
                if self.turbo and self.boostCount%300!=0:
                    self.boostCount += 1
                    self.push = 12.0
                elif self.turbo and self.boostCount%300==0:
                    self.push = 3.0
                    self.turbo = False
                    self.boostCount = 1
                elif not self.turbo:
                    self.push = 3.0
                
            #increments the distance variables
            if self.start and not self.levelUp:
                self.distanceCheck += self.push
                self.distanceCheck2+= self.push
                self.distanceCheck3+= self.push
                self.distanceCheck4+=self.push
            
            #checks for the end of levels
            if self.distanceCheck>20000 and self.distanceCheck%3==0 and (not self.reached1):
                
                #from pinclipart.com
                planet = pygame.image.load(os.path.join('images', 'end-planetred.png'))
                endNew = EndPlanet(planet)
                self.objects.append(endNew)
                self.reached1 = True
                
            if self.distanceCheck2>40000 and self.distanceCheck%3==0 and (not self.reached2):
                planet = pygame.image.load(os.path.join('images', 'end-planetred.png'))
                endNew = EndPlanet(planet)
                self.objects.append(endNew)
                self.reached2 = True
                
            if self.distanceCheck3>60000 and self.distanceCheck3%3==0 and (not self.reached3):
                planet = pygame.image.load(os.path.join('images', 'end-planetred.png'))
                endNew = EndPlanet(planet)
                self.objects.append(endNew)
                self.reached3 = True
                
            if self.distanceCheck4>80000 and self.distanceCheck4%3==0 and (not self.reached4):
                planet = pygame.image.load(os.path.join('images', 'end-planetred.png'))
                endNew = EndPlanet(planet)
                self.objects.append(endNew)
                self.reached4 = True
            
            #chekcs for level ups or winning
            if (self.level==1 and self.distanceCheck>20350) or (self.level==2 and self.distanceCheck2>40370) or (self.level==3 and self.distanceCheck3>60380) or (self.level==4 and self.distanceCheck4>80370):
                self.level+=1
                if self.level==5:
                    self.youWon = True
                    myGame.youWon(self)
                #changes the background accordingle
                self.bg = pygame.image.load(os.path.join('images','bg-galaxy_%d.png')%self.level)
                self.objects=[]
                self.levelUp=True
                myGame.levelUp(self)
                
            #sidescroller source code: https://github.com/techwithtim/side_scroller
            #moves on screen objects at sidescroll rate and implements gravity for level 3
            if self.start and not self.levelUp:
                for objectA in self.objects:
                    objectA.position[0] -= self.push
                if self.level==3 or self.level==4:
                    self.rocket.gravityDown()
                    
            #moves the background to sidescroll
            if self.start and not self.levelUp:
                self.bgX -= self.push
                self.bgX2 -= self.push
            if self.bgX < self.bg.get_width() * -1:
                self.bgX = self.bg.get_width()
            if self.bgX2 < self.bg.get_width() * -1:
                self.bgX2 = self.bg.get_width()
                
             #calls game over function
            if self.lives==0:
                self.gameOver = True
                myGame.gameOver(self) 

            #checks for user interaction and adds objects to the screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    quit()
                if not self.start:
                    if event.type==MOUSEBUTTONDOWN:
                        x, y = event.pos
                        myGame.buttonCheck(self, x, y)
                if self.start and not self.levelUp and not self.rocket.collidesWithLeft():
                #objects on screen dependent on level
                    if self.level==1:
                        #generates a random asteroid on the screen 
                        if event.type == USEREVENT+5:
                            #images from pngmart.com
                            img = random.choice([pygame.image.load(os.path.join('images',\
                            'asteroid-big.png')), pygame.image.load(os.path.join('images',\
                            'asteroid-medium.png')),pygame.image.load(os.path.join('images',
                            'asteroid-small.png'))])
                            newAsteroid = Asteroid(img)
                            self.objects.append(newAsteroid)
                        #generates a random coin on the screen
                        if event.type == USEREVENT+2:
                            #image from searchpng.com
                            img = pygame.image.load(os.path.join('images', 'coin.png'))
                            newCoin = Coin(img)
                            self.objects.append(newCoin)
                        #generates a random booster on the screen 
                        if event.type == USEREVENT+3:
                            #image from pngmart.com
                            img = pygame.image.load(os.path.join('images', 'fire-booster.png'))
                            self.objects.append(Booster(img))
                            
                        if event.type == USEREVENT+6:
                            #image from pinclipart.com
                            img = pygame.image.load(os.path.join('images', 'life.png'))
                            self.objects.append(Life(img))
                        
                    if self.level==2:
                        if event.type == USEREVENT+5:
                            img = random.choice([pygame.image.load(os.path.join('images',\
                            'asteroid-big.png')), pygame.image.load(os.path.join('images',\
                            'asteroid-medium.png')),pygame.image.load(os.path.join('images',
                            'asteroid-small.png'))])
                            newAsteroid = Asteroid(img)
                            self.objects.append(newAsteroid)
                            
                        if event.type == USEREVENT+2:
                            img = pygame.image.load(os.path.join('images', 'coin.png'))
                            newCoin = Coin(img)
                            self.objects.append(newCoin)
                            
                        if event.type == USEREVENT+3:
                            img = pygame.image.load(os.path.join('images', 'fire-booster.png'))
                            self.objects.append(Booster(img))
                        #generates a random alien on the screen 
                        if event.type == USEREVENT+4:
                            #from clipartmag.com
                            img = pygame.image.load(os.path.join('images', 'alien-red.png'))
                            self.objects.append(Alien(img))
                    
                        if event.type == USEREVENT+6:
                            img = pygame.image.load(os.path.join('images', 'life.png'))
                            self.objects.append(Life(img))
                            
                    if self.level==3:
                        if event.type == USEREVENT+5:
                            img = random.choice([pygame.image.load(os.path.join('images',\
                            'asteroid-big.png')), pygame.image.load(os.path.join('images',\
                            'asteroid-medium.png')),pygame.image.load(os.path.join('images',
                            'asteroid-small.png'))])
                            newAsteroid = Asteroid(img)
                            self.objects.append(newAsteroid)
                        if event.type == USEREVENT+2:
                            img = pygame.image.load(os.path.join('images', 'coin.png'))
                            newCoin = Coin(img)
                            self.objects.append(newCoin)
                        if event.type == USEREVENT+3:
                            img = pygame.image.load(os.path.join('images', 'fire-booster.png'))
                            self.objects.append(Booster(img))
                            
                        if event.type == USEREVENT+4:
                            img = pygame.image.load(os.path.join('images', 'alien-red.png'))
                            self.objects.append(Alien(img))
                            
                        if event.type == USEREVENT+6:
                            img = pygame.image.load(os.path.join('images', 'life.png'))
                            self.objects.append(Life(img))


                    if self.level == 4:
                        
                        if event.type == USEREVENT+5:
                            img = random.choice([pygame.image.load(os.path.join('images',\
                            'asteroid-big.png')), pygame.image.load(os.path.join('images',\
                            'asteroid-medium.png')),pygame.image.load(os.path.join('images',
                            'asteroid-small.png'))])
                            newAsteroid = Asteroid(img)
                            self.objects.append(newAsteroid)
                        if event.type == USEREVENT+2:
                            img = pygame.image.load(os.path.join('images', 'coin.png'))
                            newCoin = Coin(img)
                            self.objects.append(newCoin)
                        if event.type == USEREVENT+3:
                            img = pygame.image.load(os.path.join('images', 'fire-booster.png'))
                            self.objects.append(Booster(img))
                            
                        if event.type == USEREVENT+4:
                            img = pygame.image.load(os.path.join('images', 'alien-red.png'))
                            self.objects.append(Alien(img))
                            
                        if event.type == USEREVENT+6:
                            img = pygame.image.load(os.path.join('images', 'life.png'))
                            self.objects.append(Life(img))
                            
                        if event.type==USEREVENT+7:
                            #from kisspng.com
                            img = pygame.image.load(os.path.join('images', 'wind.png'))
                            self.objects.append(Wind(img))
                        
                #checks user interaction
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.rocket.moveUp()
                elif keys[pygame.K_DOWN]:
                    self.rocket.moveDown()
                elif keys[pygame.K_RIGHT]:
                    self.rocket.moveRight()
                elif keys[pygame.K_LEFT]:
                    self.rocket.moveLeft()
                if keys[pygame.K_p]:
                    self.pause = not self.pause
                    if self.pause:
                        myGame.paused(self)
                if keys[pygame.K_SPACE]:
                    #interval in between consecutive missiles being fired
                        new_time = datetime.datetime.now()
                        if new_time - self.fire_time > \
                                datetime.timedelta(seconds=0.15):
                                    self.rocket.fire()
                
                #the following are keyboard shortcuts to skip ahead to certain levels
                if keys[pygame.K_2]:
                    self.distanceCheck = 20001
                    self.distanceCheck2= 20001
                    self.distanceCheck3= 20001
                    self.distanceCheck4 = 20001
                    
                if keys[pygame.K_3]:
                    self.distanceCheck = 40002
                    self.distanceCheck2= 40002
                    self.distanceCheck3= 40002
                    self.distanceCheck4 = 40002
                    
                if keys[pygame.K_4]:
                    self.distanceCheck = 60000
                    self.distanceCheck2= 60000
                    self.distanceCheck3= 60000
                    self.distanceCheck4 = 60000
                
            if self.start and not self.levelUp:
                #adds wormholes to the screen
                if self.level==3 or self.level==4:
                    self.appendWormhole+=1
                    if self.appendWormhole>700:
                        self.objects.append(Wormhole((800, random.randint(0, 400)),pygame.image.load(os.path.join("images", "wormhole.png"))))
                        self.appendWormhole = 0   
                             
            #moves the missiles
            for missile in self.rocket.missiles:
                missile.move()
                if missile.offScreen():
                    self.rocket.missiles.remove(missile)
             
             #moves on screen objects   
            for object1 in self.objects:
                if isinstance(object1, Asteroid):
                    if self.level==1:
                        object1.moveAsteroid()
                    if self.level==2 or self.level==3 or self.level==4:
                        object1.moveAsteroidMore()
                if isinstance(object1, Alien):
                    object1.moveAlien()
            
            #checks for asteroid/alien and missile collisions
            for missile in self.rocket.missiles:
                rightX = missile.position[0] + missile.image.get_width()
                y = missile.position[1]
                for object1 in self.objects:
                    if isinstance(object1, Asteroid) or isinstance(object1, Alien):
                        if object1.collidesWithMis(rightX, y):
                            self.objects.remove(object1)
                            if isinstance(object1, Asteroid):
                                self.breakAstsound.play()
                            if missile in self.rocket.missiles:
                                self.rocket.missiles.remove(missile)
                            self.score += 1
                            
            #checks for rocket collisions with all game objects and calls appropriate functions
            for object1 in self.objects:
                if not isinstance(object1, EndPlanet):
                    if object1.collidesWithRocket(self.rocket.position[0],\
                        self.rocket.position[1], self.rocket.image):
                            if isinstance(object1, Coin):
                                self.objects.remove(object1)
                                self.coinCount += 1
                            elif isinstance(object1, Life):
                                self.objects.remove(object1)
                                self.lives += 1
                            elif isinstance(object1, Booster):
                                self.turboSound.play()
                                self.objects.remove(object1)
                                self.turbo = True
                            elif isinstance(object1, Asteroid):
                                self.objects.remove(object1)
                                self.lives-=1
                            elif isinstance(object1, Wind):
                                self.objects.remove(object1)
                                self.turbulence=True
                            elif isinstance(object1, Alien):
                                self.objects.remove(object1)
                                if self.level==2:
                                    self.lives -= 1
                                if self.level==3 or self.level==4:
                                    self.rocket.increaseGrav()
                            elif isinstance(object1, Wormhole):
                                self.objects.remove(object1)
                                self.start = False
                                self.wormholeModeOn = True
                                myGame.wormholeMode(self)

            

myGame().__init__()
pygame.quit()
sys.exit()


####CITATIONS
#images and sounds are cited in a commnent above where they are first loaded in the game
#sidescroller source code: https://github.com/techwithtim/side_scroller
#asteroids source code: https://github.com/aminb/asteroids/blob/master/game.py 
####





