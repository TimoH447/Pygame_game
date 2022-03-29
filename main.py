from pickle import FALSE, TRUE
from turtle import circle
import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Platzhalter")

SHIP_HEIGHT, SHIP_WIDTH = 19,19

SHIP_IMG = pygame.image.load("Schiff.png")
SHIP_IMG = pygame.transform.scale(SHIP_IMG, (SHIP_HEIGHT,SHIP_WIDTH))
ASTEROID= pygame.image.load('asteroid2.jpg')
ASTEROID=pygame.transform.scale(ASTEROID, (15,15))
STONE=pygame.image.load('stone.png')

FPS = 90
SCORE=0

BLACK = (0,0,0)
LIGHTGREY=(200,200,200)
GREEN = (0,255,0)
BLUE = (0,0,255)
BROWN = (139,69,20)
YELLOW=(255,255,0)
WHITE=(255,255,255)
LILA=(130,0,130)

SCREEN_COLOR = BLACK

MAP_SIZE_X = 2000
MAP_SIZE_Y = 2000
BORDERSIZE = 100

COMET_CAP = 10

MAP = 0


class portal:
    color=LILA
    solid=True
    def __init__(self,FROM,TO, x,y, height, width):
        self.FROM = FROM
        self.TO = TO
        self.body = pygame.Rect(x,y,height, width)
class meteo:
    n=0
    item_drop = True
    solid=False
    color=BROWN
    sprite= ASTEROID
    def __init__(self,x,y,height,width,vel=5,dir=[1,0], health= 1):
        self.body = pygame.Rect(x,y,height, width)
        self.vel = vel
        self.dir = dir
        self.health= health

class bullet:
    color=YELLOW
    solid=False
    def __init__(self, x,y,height, width, vel,dir,range,step=0):
        self.body=pygame.Rect(x,y,height,width)
        self.vel = vel
        self.dir = dir
        self.range = range
        self.step= step

class ship_item:
    solid= False
    color=GREEN
    def __init__(self,x,y,width,height,func):
        self.body = pygame.Rect(x,y,height,width)
        self.effect = func
        

class wall:
    solid = True
    color=WHITE
    def __init__(self,x,y,width,height,sprite=STONE):
        self.body=pygame.Rect(x,y,width,height)
        self.sprite =pygame.transform.scale(sprite,(width,height))


class spaceship:
    color=LILA
    solid=True
    item_drop=True
    def __init__(self, x,y,height,width,vel=3, health=50,shotspeed = 3,shotrange=100, shotdamage= 10, bullets=[], ori='right'):
        self.body = pygame.Rect(x,y,height, width)
        self.weapon_cd = [0,40]
        self.vel=vel
        self.health = health
        self.shotspeed = shotspeed
        self.shotrange= shotrange
        self.shotdamage= shotdamage
        self.bullets= bullets
        self.oriantation=ori
    def add_bullet(self,bullet):
        self.bullets.append(bullet)
    def remove_bullet(self,bullet):
        self.bullets.remove(bullet)
        

def get_input(input):
    keys_pressed={
        pygame.K_a: False,
        pygame.K_s: False,
        pygame.K_d:False,
        pygame.K_w:False,
        pygame.K_UP:False,
        pygame.K_DOWN:False,
        pygame.K_RIGHT:False,
        pygame.K_LEFT:False
    }
    for i in input:
        if i==0:
            keys_pressed[pygame.K_w]=True
        if i==1:
            keys_pressed[pygame.K_a]=True
        if i==2:
            keys_pressed[pygame.K_s]=True
        if i==3:
            keys_pressed[pygame.K_d]=True
        if i==4:
            keys_pressed[pygame.K_UP]=True
        if i==5:
            keys_pressed[pygame.K_DOWN]=True
        if i==6:
            keys_pressed[pygame.K_LEFT]=True
        if i==7:
            keys_pressed[pygame.K_RIGHT]=True
    return keys_pressed


#returns True if 2 rectangles are in a certain proximity
def distance_rect(obj1, obj2,d): 
    temp_rect = pygame.Rect(obj1.x-d,obj1.y-d,2*d+obj1.width,2*d+obj1.height)
    if temp_rect.colliderect(obj2):
        return True
    else:
        return False

def spawn_met(meteorites,ship, d):
    if random.randint(0,1000)>960 and len(meteorites)<COMET_CAP:
        x=random_ship_buff([random.randint(-BORDERSIZE,0),random.randint(MAP_SIZE_X,MAP_SIZE_X+BORDERSIZE)])
        
        if random.randint(0,50)>49:
            met = meteo(x,random.randint(0,400),50,50,1,[random.randint(-5,5),random.randint(-5,5)],health=40)
            if not distance_rect(ship.body,met.body,d):
                meteorites.append(met)
        else:
            met = meteo(x,random.randint(0,400),10,10,random.randint(1,4),[random.randint(-5,5),random.randint(-5,5)])
            if not distance_rect(ship.body,met.body,d):
                meteorites.append(met)

def speed_up(obj):
    obj.vel+=1

def shotspeed_up(ship):
    ship.shotspeed+=1

def fire_rate(obj):
    obj.weapon_cd[1]/=2

def health_up(obj):
    obj.health+=10

def random_ship_buff(liste):
    
    return liste[random.randint(0,len(liste)-1)]

def flip_to_ori(image, ori):
    if ori=='right':
        return image
    if ori=='left':
        return pygame.transform.flip(image,True,True)
    if ori=='up':
        return pygame.transform.rotate(image,90)
    if ori=='down':
        return pygame.transform.rotate(image,270)
def central_draw(color,rect, adjust_x,adjust_y):
    obj=rect.copy()
    obj.x+=adjust_x
    obj.y+=adjust_y
    pygame.draw.rect(WIN,color,obj)

def draw_window(ship,map_objects, SCORE):
    
    #Text written on the screen
    myfont= pygame.font.SysFont('Comic Sans MS', 40)
    score = myfont.render('Score: '+str(SCORE),False,(255,255,255))
    health= myfont.render('Health: '+str(ship.health),False,(255,255,255))
    
    #Ship is in the center of the Screen, moving on an underlying grid
    adjust_x = WIDTH//2-ship.body.x-ship.body.width
    adjust_y = HEIGHT//2-ship.body.y-ship.body.height

    WIN.fill(BLUE)
    central_draw(SCREEN_COLOR, pygame.Rect(0,0,MAP_SIZE_X,MAP_SIZE_Y), adjust_x, adjust_y)
    for obj in map_objects:
        for element in obj:
            try:
                WIN.blit(element.sprite,(element.body.x+adjust_x,element.body.y+adjust_y))
            except:
                central_draw(element.color,element.body,adjust_x,adjust_y)

    # for met in meteorites:
    #     #pygame.draw.rect(WIN,BROWN,met.body)
    #     central_draw(BROWN,met.body,adjust_x,adjust_y)
    #     ASTEROID_scaled = pygame.transform.scale(ASTEROID,(15*met.body.width/10,15*met.body.height/10))
    #     WIN.blit(ASTEROID_scaled,(met.body.x+adjust_x-3*met.body.width/10,met.body.y+adjust_y-3*met.body.height/10))
    
    WIN.blit(flip_to_ori(SHIP_IMG, ship.oriantation), (ship.body.x+adjust_x,ship.body.y+adjust_y))

    central_draw(LIGHTGREY,pygame.Rect(-WIDTH,-HEIGHT,2*WIDTH+MAP_SIZE_X,HEIGHT),adjust_x,adjust_y)
    central_draw(LIGHTGREY,pygame.Rect(-WIDTH,-HEIGHT,WIDTH,2*HEIGHT+MAP_SIZE_Y),adjust_x,adjust_y)

    WIN.blit(health,(600,10))
    WIN.blit(score,(50,10))

    pygame.display.update()

def end_screen():
    WIN.fill(SCREEN_COLOR)
    myfont= pygame.font.SysFont('Comic Sans MS', 40)
    end= myfont.render('GAME OVER',False,WHITE)
    WIN.blit(end,(300,220))
    pygame.display.update()

def handle_doors(ship, doors):
    global SCREEN_COLOR
    for door in doors:
        if ship.body.colliderect(door.rect):
            SCREEN_COLOR = BROWN

def move_meteo(met):
    x=met.dir[0]
    y=met.dir[1]
    temp_x=0
    temp_y=0
    if x==0 and y!=0:
        met.body.y += y//abs(y)*met.vel
    elif y==0 and x!=0:
        met.body.x +=x//abs(x)*met.vel
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
        for i in range(met.vel):
            if a==x:
                if met.n<=n:
                    temp_x += x//abs(x)
                    met.n +=1
                else:
                    temp_y += y//abs(y)
                    met.n=0
            elif a==y:
                if met.n<=n:
                    temp_y += y//abs(y)
                    met.n +=1
                else:
                    temp_x += x//abs(x)
                    met.n=0
        met.body.x += temp_x
        met.body.y += temp_y


def bullet_handler(shooter,items,hit_by_player_bullets, stops_bullets):
    global SCORE
    if shooter.weapon_cd[0] > 0:
        shooter.weapon_cd[0] -=1
    for bullet in shooter.bullets:
            move_meteo(bullet)
            bullet.step+=1
    for obj in hit_by_player_bullets:
        for element in obj:
            for bullet in shooter.bullets:
                if bullet.body.colliderect(element.body):
                    element.health-=shooter.shotdamage
                    print('hi')
                    print(len(obj))
                    SCORE+=10
    
    for obj in stops_bullets:
        for element in obj:
            for bullet in shooter.bullets:
                if bullet.body.colliderect(element.body):
                    shooter.remove_bullet(bullet)
            
    for obj in hit_by_player_bullets:
        for element in obj:
            if element.health<=0:
                obj.remove(element)
                if element.item_drop==True:
                    if random.randint(0,100)>5:
                        items.append(ship_item(element.body.x,element.body.y,10,10,random_ship_buff([fire_rate,speed_up,shotspeed_up,health_up])))


def item_handler(ship,items):
    for item in items:
        if ship.body.colliderect(item.body):
            item.effect(ship)
            items.remove(item)

def meteo_handler(meteorites,ship,walls):
    for met in meteorites:
        if ship.body.colliderect(met.body):
            meteorites.remove(met)
            ship.health -=10
        elif met.body.x<0-BORDERSIZE or met.body.x>MAP_SIZE_X+BORDERSIZE or met.body.y<0-BORDERSIZE or met.body.y>MAP_SIZE_Y+BORDERSIZE:
            meteorites.remove(met)
        else:
            for wall in walls:
                if wall.body.colliderect(met.body):
                    meteorites.remove(met)
        
        move_meteo(met)      

def ship_movement(ship, map_objects, key_pressed):
    #funktion bewegt die Position des Schiffs bezüglich der Eingabe
    #Das Schiff wird jedoch nicht bewegt, wenn die zukünftige Position mit der einem Element kollidiert
    #in map_objects wird eine Liste von Listen übergeben, Die listen jeweils enthalten Objekte einer Art,
    #z.B. eine Liste von Wänden
    if key_pressed[pygame.K_a] and ship.body.x>0: #left
        move_left=True #Wenn move_left==True ist dann wird das Schiff bewegt, 
        for obj in map_objects: #Es wird über alle Elemente iteriert, wenn ein Element mit dem SChiff 
            for element in obj: #kollidiert, dann wird move_left auf False gesetzt und das SChiff bewegt sich nicht
                if element.solid == True:
                    if element.body.colliderect(pygame.Rect(ship.body.x-ship.vel,ship.body.y,ship.body.width, ship.body.height)):
                        move_left = False
        if move_left==True:
            ship.body.x-=ship.vel
        ship.oriantation = 'left'
           
    if key_pressed[pygame.K_d] and ship.body.x < MAP_SIZE_X: #right
        move=True #Wenn move==True ist dann wird das Schiff bewegt, 
        for obj in map_objects: #Es wird über alle Elemente iteriert, wenn ein Element mit dem SChiff 
            for element in obj: #kollidiert, dann wird move auf False gesetzt und das SChiff bewegt sich nicht
                if element.solid == True:
                    if element.body.colliderect(pygame.Rect(ship.body.x +ship.vel,ship.body.y,ship.body.width,ship.body.height)):
                        move = False
        if move==True:
            ship.body.x+=ship.vel
        ship.oriantation = 'right'
           
    if key_pressed[pygame.K_w] and ship.body.y>0: #up
        move=True #Wenn move==True ist dann wird das Schiff bewegt, 
        for obj in map_objects: #Es wird über alle Elemente iteriert, wenn ein Element mit dem SChiff 
            for element in obj: #kollidiert, dann wird move auf False gesetzt und das SChiff bewegt sich nicht
                if element.solid == True:
                    if element.body.colliderect(pygame.Rect(ship.body.x,ship.body.y-ship.vel,ship.body.width,ship.body.height)):
                        move = False
        if move==True:
            ship.body.y-=ship.vel
        ship.oriantation = 'up'

    if key_pressed[pygame.K_s] and ship.body.y<MAP_SIZE_Y: #down
        move=True #Wenn move==True ist dann wird das Schiff bewegt, 
        for obj in map_objects: #Es wird über alle Elemente iteriert, wenn ein Element mit dem SChiff 
            for element in obj: #kollidiert, dann wird move auf False gesetzt und das SChiff bewegt sich nicht
                if element.solid == True:
                    if element.body.colliderect(pygame.Rect(ship.body.x,ship.body.y+ship.vel,ship.body.width,ship.body.height)):
                        move = False
        if move==True:
            ship.body.y+=ship.vel
        ship.oriantation = 'down'

def shoot(ship,key_pressed):
    if key_pressed[pygame.K_LEFT] and ship.weapon_cd[0]==0: #left
        ship.add_bullet(bullet(ship.body.x,ship.body.y+ship.body.height//2,5,5,ship.shotspeed,[-1,0],ship.shotrange))
        ship.weapon_cd[0]=ship.weapon_cd[1]
        ship.oriantation='left'
    if key_pressed[pygame.K_RIGHT] and ship.weapon_cd[0] ==0: #right
        ship.add_bullet(bullet(ship.body.x,ship.body.y+ship.body.height//2,5,5,ship.shotspeed,[1,0],ship.shotrange))
        ship.weapon_cd[0]=ship.weapon_cd[1]
        ship.oriantation='right'
    if key_pressed[pygame.K_UP] and ship.weapon_cd[0]==0: #up
        ship.add_bullet(bullet(ship.body.x+ship.body.width//2,ship.body.y,5,5,ship.shotspeed,[0,-1],ship.shotrange))
        ship.weapon_cd[0]=ship.weapon_cd[1]
        ship.oriantation='up'
    if key_pressed[pygame.K_DOWN] and ship.weapon_cd[0]==0: #down
        ship.add_bullet(bullet(ship.body.x+ship.body.width//2,ship.body.y+ship.body.height,5,5,ship.shotspeed,[0,1],ship.shotrange))
        ship.weapon_cd[0]=ship.weapon_cd[1]
        ship.oriantation='down'


def enemy_handler(ship,enemies,map_objects):
    for enemy in enemies:
        key_pressed= get_input([random.randint(0,7)])
        ship_movement(enemy, map_objects,key_pressed)
        shoot(enemy,key_pressed)

def main():
    global SCORE
    ship = spaceship(450,200,SHIP_HEIGHT-2,SHIP_WIDTH-2)
    enemy = spaceship(300,200,30,30)
    enemies=[enemy]

    ship_bullets=[]
    meteorites=[]
    met = meteo(300,300,10,10,1,[0,0])
    met2 = meteo(300,300,10,10,1,[0,0])
    meteorites.append(met)
    meteorites.append(met2)
    
    items=[]
    items.append(ship_item(50,50,10,10,fire_rate))
    items.append(ship_item(80,50,10,10,health_up))

    walls=[]
    walls.append(wall(50,50,150,150))
    portals = []
    portals.append(portal(0,1,200,200,10,50))

    hit_by_player_bullets=[meteorites,enemies]
    stops_bullets=[meteorites,walls,enemies]

    map_objects=[ship.bullets,meteorites,items,walls,portals]

    clock=pygame.time.Clock()
    run = True
    while run: 
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False            
        key_pressed = pygame.key.get_pressed()
        
        ###########Shooting##############
        #1.wenn schießen nicht auf cooldown ist, wird ein Schuss hinzugefügt mit der richtung in die geschossen wird
        #2.und anschließend wird der Cooldown hochgesetzt
        #3.orentation des ships soll abhängig der Schießrichtung sein
        
        shoot(ship,key_pressed)
        ##MOVEMENT############
        ship_movement(ship,map_objects, key_pressed)
             
        bullet_handler(ship,items, hit_by_player_bullets, stops_bullets) 

        #ITEMS
        item_handler(ship,items)
        
        #METEORITEN SPAWN
        spawn_met(meteorites, ship, 100)
        meteo_handler(meteorites, ship,walls)

        #ENEMIES
        enemy_handler(ship,enemies,map_objects)
        bullet_handler(enemy,items,[meteorites],[walls,meteorites,portals])
        if ship.health <=0:
            end_screen()
        else:
            draw_window(ship,map_objects+[enemies,enemy.bullets], SCORE)
    pygame.quit()


if __name__ == "__main__":
    main()