#### Intergalactica - Classes
#### By Maya Krishnan


import pygame
import os
import sys
from pygame.locals import *
import math
import datetime
import random
import string

#####

#helper function to get center coordinates of an image relative to its position
def getCenterCoords(image):
    cx = image.get_width()//2
    cy = image.get_height()//2
    return (cx, cy)

#modified code from: https://github.com/aminb/asteroids/blob/master/game.py 
#any object on the screen is a GameItem
class GameItem(object):
    def __init__(self, position, image):
        self.position = list(position[:])
        self.image = image
    def draw(self, win):
        win.blit(self.image, (self.position[0], self.position[1]))
    
#a rocket can move, fire missiles and get affected by gravity
class Rocket(GameItem):
    def __init__(self, position, image):
        super().__init__(position, image)
        self.speed = 10
        self.missiles = []
        self.center = getCenterCoords(self.image)
        self.cX = self.center[0] + self.position[0]
        self.cY = self.center[1] + self.position[1]
        self.asteroids = []
        self.turbulence = 3
        self.gravity = 1
        
    def moveUp(self):
        self.position[1] -= self.speed
        self.cY -= self.speed
        if self.position[1] + self.center[1]<=0:
            self.position[1] = 447
            self.cY = 447 + self.center[1]
    def moveDown(self):
        self.position[1] += self.speed
        self.cY += self.speed
        if self.position[1]>=447:
            self.position[1] = 0
            self.cY = self.center[1]
    def moveRight(self):
        self.position[0] += self.speed
        self.cX += self.speed
        if self.position[0] + self.center[0]>=800:
            self.position[0] = 800 - self.center[0]
            self.cX = 800 + self.center[0]
    def moveLeft(self):
        self.position[0] -= self.speed
        self.cX -= self.speed
        if self.position[0]<0:
            self.position[0] = 0
            self.cX = self.center[0]
            
    def collidesWithLeft(self):
        return self.position[0] == 0
        
    def gravityDown(self):
        self.position[1] += self.gravity
        self.cY += self.gravity
        if self.position[1]>=447:
            self.position[1] = 0
            self.cY = self.center[1]
            
    def increaseGrav(self):
        self.gravity += 2
    
    #fires a missile
    def fire(self):
        missileImage = pygame.image.load(os.path.join('images', 'missile.png'))
        newMissileY = self.cY - (missileImage.get_height())//2
        newMissile = Missile((self.cX, newMissileY))
        self.missiles.append(newMissile)
 
#a missile can destroy an asteroid or an alien
class Missile(GameItem):
    def __init__(self, position):
        super().__init__(position, \
        pygame.image.load(os.path.join('images', 'missile.png')))
        self.speed = 25

    def move(self):
        self.position[0] += self.speed
        
    def offScreen(self):
        if self.position[0]>800:
            return True
        else: return False

#an asteroid is generated randomly on the screen and can be destroyed by a missile
class Asteroid(GameItem):
    def __init__(self, image):
        super().__init__((800, \
        random.randint(0, 440)), image)
        self.speed = 6
        self.angle = 0
        self.r = 90
    
    def collidesWithMis(self, xPos, yPos):
        return self.position[0]<=xPos and self.position[1]<yPos<(self.position[1]\
        + self.image.get_height())
       
    #make the asteroid move up and down in level 1     
    def moveAsteroid(self):
        self.position[1]+=self.speed
        if self.position[1]>=447 or self.position[1]<=0:
            self.speed = -self.speed
    
    #makes the asteroid move diagonally in level 2        
    def moveAsteroidMore(self):
        self.position[0]-= self.speed
        self.position[1]+=self.speed
        if self.position[1]>=447 or self.position[1]<=0:
            self.speed = -self.speed
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0] and self.position[1]<yPos + image.get_height() and yPos< self.position[1] + self.image.get_height()

#a coin is randomly generated on the screen and can be collected by the rocket        
class Coin(GameItem):
    def __init__(self, image):
        super().__init__((800, random.randint(0, 400)), image)
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0]\
         and self.position[1]<yPos + image.get_height() and yPos< self.position[1] + \
         self.image.get_height()
  
  
class Life(GameItem):
    def __init__(self, image):
        super().__init__((800, random.randint(0, 400)), image)
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0]\
         and self.position[1]<yPos + image.get_height() and yPos< self.position[1] + \
         self.image.get_height()
    
#when the rocket collects a booster, it goes faster for a while
class Booster(GameItem):
    def __init__(self, image):
        super().__init__((800, random.randint(0, 400)), image)
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0]\
         and self.position[1]<yPos + image.get_height() and yPos< self.position[1]\
          + self.image.get_height()
  
#this object sucks you into another darker, more sinister universe for a while and then spits you back out
class Wormhole(GameItem):
    def __init__(self, position, image):
        super().__init__(position, image)
    
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0]\
         and self.position[1]<yPos + image.get_height() and yPos< self.position[1] + \
         self.image.get_height()

        
    def fall(self):
        self.position[1]+=2
    
    
#htese fall from the sky inside the alternate universe of the wormhole
class Meteor(GameItem):
    def __init__(self, image):
        super().__init__((random.randint(0,800), 0), image)
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0]\
         and self.position[1]<yPos + image.get_height() and yPos< self.position[1] + \
         self.image.get_height()
         
    def fall(self):
        self.position[1]+=7
    
#the goal planet which approaches at the end of every level
class EndPlanet(GameItem):
    def __init__(self, image):
        super().__init__((800, 0), image)

#these move onto the screen in a zig-zag fashion and either makes you lose a life, or increases your gravity in levels 3 and 4
class Alien(GameItem):
    def __init__(self, image):
        super().__init__((800, random.randint(0, 400)), image)
        self.speedX = -3
        self.speedY = -5
        self.angle = 10
        self.zigZagDist = 60
        self.ogPos = self.position[1]
        
    def moveAlien(self):
        self.position[0] += self.speedX
        self.position[1] += self.speedY
        if abs(self.position[1]-self.ogPos)>self.zigZagDist:
            self.speedY = -self.speedY
       
    def collidesWithMis(self, xPos, yPos):
        return self.position[0]<=xPos and self.position[1]<yPos<(self.position[1]\
        + self.image.get_height())
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and \
        xPos<self.position[0] and self.position[1]<yPos + image.get_height() and yPos< self.position[1] + self.image.get_height()
         

#this object makes you experience turbulence
class Wind(GameItem):
    def __init__(self, image):
        super().__init__((800, random.randint(0, 400)), image)
        
    def collidesWithRocket(self, xPos, yPos, image):
        return self.position[0]<xPos + image.get_width() and xPos<self.position[0]\
         and self.position[1]<yPos + image.get_height() and yPos< self.position[1]\
          + self.image.get_height()