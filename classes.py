import pygame
from settings.colors import *
from utils import load_sprite
 
pygame.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
#OBJECTS USED THE GAME

class Movable:
    def __init__(self,x,y,height,width,dir, vel=4):
        self.body = pygame.Rect(x,y,height,width)
        self.vel = vel
        self.dir = dir
    def move_obj(self):
        x=self.dir[0]
        y=self.dir[1]
        temp_x=0
        temp_y=0
        if x==0 and y!=0:
            self.body.y += y//abs(y)*self.vel
        elif y==0 and x!=0:
            self.body.x +=x//abs(x)*self.vel
        elif x!=0 and y!=0:
            #wir aproximieren vom Richtungsvektor eine Rate, wie viele pixel nach x bevor ein pixel nach y bewegt wird
            #bzw. andersherum, je nachdem in welche Richtung am stärksten ist
            if abs(x)>abs(y):
                a=x
                n=1//(abs(y)/abs(x)) #anzahl der schritte nach x pro ein step in Richtung y
            else:
                a=y
                n=1//(abs(x)/abs(y))
            #Damit wenn mehr als ein pixel pro frame bewegt, es nicht zu schlangenlinien kommt,
            #werden einfach die nächsten bewegungen abgespeichert der Reihe nach so häufig wie
            #pixel pro frame bewegt werden und dann anschließend der position in x und y zugefügt
            #anstat immer so und so viele pixel pro frame nur in eine Richtung
            for i in range(self.vel):
                if a==x:
                    if self.n<=n:
                        temp_x += x//abs(x)
                        self.n +=1
                    else:
                        temp_y += y//abs(y)
                        self.n=0
                elif a==y:
                    if self.n<=n:
                        temp_y += y//abs(y)
                        self.n +=1
                    else:
                        temp_x += x//abs(x)
                        self.n=0
            self.body.x += temp_x
            self.body.y += temp_y

class Portable:
    def __init__(self,ported = False):
        self.ported = ported
        self.temp=[]
    def change_ported(self,value):
        self.ported=value
    def tick(self):
        for t in self.temp:
            t[0]-=1
            if t[0]<=0:
                t[1](t[2])
                self.temp.remove(t)
    def timer_change(self,attr_change,old_value,new_value,time):
        self.temp.append([time,attr_change,old_value])
        attr_change(new_value)

class Weapon:
    def __init__(self,cd,shotdamage,shotrange,shotspeed):
        self.cd =cd
        self.shotdamage=shotdamage
        self.shotrange=shotrange
        self.shotspeed=shotspeed

class Weaponized:
    def __init__(self,bullet_list, bullet_color, weapon):
        self.bullet_list = bullet_list
        self.bullet_color = bullet_color
        self.weapon = weapon
    def add_bullet(self,bullet):
        self.bullet_list.append(bullet)
    def remove_bullet(self,bullet):
        self.bullet_list.remove(bullet)
    def swap_weapon(self, new_weapon):
        self.weapon = new_weapon

class Portal:
    color=LILA
    solid=False
    def __init__(self,x_change,y_change, x,y, height, width):
        self.x_change = x_change
        self.y_change = y_change
        self.body = pygame.Rect(x,y,height, width)
        self.sprite = pygame.transform.scale(load_sprite("portal_fluid",False),(height, width))

class Line:
    color = BLUE
    solid= True
    sprite= load_sprite("blueline",False)
    def __init__(self,x,y,width,height):
        self.body = pygame.Rect(x,y,width, height)

class Asteroid(Movable,Portable):
    n=0
    item_drop = True
    solid=False
    color=BROWN
    sprite= pygame.transform.scale(load_sprite("asteroid2",True,'.jpg'),(15,15))

    def __init__(self,x,y,height,width,vel=5,dir=[1,0], health= 1):
        Movable.__init__(self,x,y,height,width,dir,vel)
        Portable.__init__(self,False)
        self.health= health

class Bullet(Movable,Portable):
    solid=False
    def __init__(self, x,y,height, width, vel,dir,range,color=YELLOW,step=0):
        Movable.__init__(self,x,y,height,width,dir,vel)
        Portable.__init__(self,False)
        self.range = range
        self.step= step
        self.color=color

class Item:
    solid= False
    color=GREEN
    def __init__(self,x,y,width,height):
        self.body = pygame.Rect(x,y,height,width)
    
class Ship_Item(Item):
    def __init__(self,x,y,width,height,func):
        Item.__init__(self,x,y,width,height)
        self.effect = func
    def On_ship_collision(self,ship):
        self.effect(ship)

class Weapon_Item(Item):
    def __init__(self,x,y,width,height,weapon):
        Item.__init__(self,x,y,width,height)
        self.weapon=weapon
    def On_ship_collision(self,ship):
        ship.weapon_change(self.weapon)
    
        
class Wall:
    solid = True
    color=WHITE
    def __init__(self,x,y,width,height,sprite=load_sprite('stone',False)):
        self.body=pygame.Rect(x,y,width,height)
        self.sprite =pygame.transform.scale(sprite,(width,height))

class spaceship(Portable,Weaponized):
    color=LILA
    solid=True
    def __init__(self,bullet_list, x,y,height,width,bullet_color,item_drop=False,vel=3, health=10,shotspeed = 3,shotrange=100, shotdamage= 10,ori='right', score=0):
        Portable.__init__(self,False)
        Weaponized.__init__(self,bullet_list,bullet_color,Weapon([0,40],shotdamage,shotrange,shotspeed))
        self.body = pygame.Rect(x,y,height, width)
        self.item_drop=item_drop
        self.vel=vel
        self.health = health
        self.oriantation=ori
        self.score = score
    def change_score(self,n):
        self.score = n