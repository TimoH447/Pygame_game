import pygame
import random

pygame.init()

#INITIALIZING THE WINDOW IN WHICH THE GAME IS PLAYED
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Platzhalter")

FPS = 90

#MAP AND PLAYER PROPERTIES
MAP_SIZE_X = 2000
MAP_SIZE_Y = 2000
BORDERSIZE = 100

COMET_CAP = 10

SHIP_HEIGHT, SHIP_WIDTH = 19, 19

#IMAGES and SPRITES
SHIP_IMG = pygame.image.load("Schiff.png")
SHIP_IMG = pygame.transform.scale(SHIP_IMG, (SHIP_HEIGHT,SHIP_WIDTH))
ASTEROID= pygame.image.load('asteroid2.jpg')
ASTEROID=pygame.transform.scale(ASTEROID, (15,15))
STONE=pygame.image.load('stone.png')
BACKGROUND = pygame.image.load('background2.png')
BACKGROUND=pygame.transform.scale(BACKGROUND, (2000,2000))
PORTAL_FLUID = pygame.image.load('portal_fluid.png')

#COLORS
BLACK = (0,0,0)
LIGHTGREY=(200,200,200)
GREEN = (0,255,0)
BLUE = (0,0,255)
BROWN = (139,69,20)
YELLOW=(255,255,0)
WHITE=(255,255,255)
LILA=(130,0,130)
RED=(255,0,0)

SCREEN_COLOR = BLACK

#OBJECTS USED THE GAME
class Moveable:
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

class Portal:
    color=LILA
    solid=False
    def __init__(self,x_change,y_change, x,y, height, width):
        self.x_change = x_change
        self.y_change = y_change
        self.body = pygame.Rect(x,y,height, width)
        self.sprite = pygame.transform.scale(PORTAL_FLUID,(height, width))

class Astroid(Moveable,Portable):
    n=0
    item_drop = True
    solid=False
    color=BROWN
    sprite= ASTEROID
    def __init__(self,x,y,height,width,vel=5,dir=[1,0], health= 1):
        Moveable.__init__(self,x,y,height,width,dir,vel)
        Portable.__init__(self,False)
        self.health= health

class Bullet(Moveable,Portable):
    solid=False
    def __init__(self, x,y,height, width, vel,dir,range,color=YELLOW,step=0):
        Moveable.__init__(self,x,y,height,width,dir,vel)
        Portable.__init__(self,False)
        self.range = range
        self.step= step
        self.color=color
        
    
class ship_item:
    solid= False
    color=GREEN
    def __init__(self,x,y,width,height,func):
        self.body = pygame.Rect(x,y,height,width)
        self.effect = func
        
class Wall:
    solid = True
    color=WHITE
    def __init__(self,x,y,width,height,sprite=STONE):
        self.body=pygame.Rect(x,y,width,height)
        self.sprite =pygame.transform.scale(sprite,(width,height))

class spaceship(Portable,Weaponized):
    color=LILA
    solid=True
    def __init__(self,bullet_list, x,y,height,width,bullet_color,item_drop=False,vel=3, health=50,shotspeed = 3,shotrange=100, shotdamage= 10,ori='right', score=0):
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

#ITEM FUNCTIONS
def speed_up(obj):
    obj.vel+=1

def shotspeed_up(ship):
    ship.weapon.shotspeed+=1

def fire_rate(obj):
    obj.weapon.cd[1]/=2

def health_up(obj):
    obj.health+=10

def random_ship_buff(liste):
    return liste[random.randint(0,len(liste)-1)]

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
            met = Astroid(x,random.randint(0,400),50,50,1,[random.randint(-5,5),random.randint(-5,5)],health=40)
            if not distance_rect(ship.body,met.body,d):
                meteorites.append(met)
        else:
            met = Astroid(x,random.randint(0,400),10,10,random.randint(1,4),[random.randint(-5,5),random.randint(-5,5)])
            if not distance_rect(ship.body,met.body,d):
                meteorites.append(met)

def construct_portal(x_change,y_change,x,y,width,height,walls,portals):
    portals.append(Portal(x_change,y_change,x,y,width,height))
    if height>width:
        walls.append(Wall(x-5,y-5,width+10,10))
        walls.append(Wall(x-5,y+height-5,10+width,10))
    else:
        walls.append(Wall(x-5,y-5,10,height+10))
        walls.append(Wall(x+width-5,y-5,10,height+10))


def portation(obj,x,y):
    obj.body.x+=x
    obj.body.y+=y
    obj.timer_change(obj.change_ported,obj.ported,True,120)
    obj.ported=True
    
#HANDLING THE INTERACTION OF OBJECTS IN THE GAME

def portal_handler(portals, obj_list):
    for portal in portals:
        for obj in obj_list:
            if obj.body.colliderect(portal.body) and not obj.ported:
                portation(obj,portal.x_change,portal.y_change)

def bullet_handler(shooter,items,hit_by_player_bullets, stops_bullets):
    if shooter.weapon.cd[0] > 0:
        shooter.weapon.cd[0] -=1
    for bullet in shooter.bullet_list:
            bullet.move_obj()
            bullet.step+=1
    for obj in hit_by_player_bullets:
        for element in obj:
            for bullet in shooter.bullet_list:
                if bullet.body.colliderect(element.body):
                    element.health-=shooter.weapon.shotdamage
                    shooter.change_score(shooter.score+10)
        
    for obj in stops_bullets:
        for element in obj:
            for bullet in shooter.bullet_list:
                if bullet.body.colliderect(element.body):
                    shooter.remove_bullet(bullet)

    for obj in hit_by_player_bullets:
        for element in obj:
            if element.health<=0:
                obj.remove(element)
                if element.item_drop==True:
                    if random.randint(0,100)>5:
                        items.append(ship_item(element.body.x,element.body.y,10,10,random_ship_buff([fire_rate,speed_up,shotspeed_up,health_up])))
                del element

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
        met.move_obj()      

#FUNCTIONS HANDLING USER INPUT AND COMPUTER CONTROLLED ENEMIES

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

def shoot(actor,key_pressed):
    if key_pressed[pygame.K_LEFT] and actor.weapon.cd[0]==0: #left
        actor.add_bullet(Bullet(actor.body.x,actor.body.y+actor.body.height//2,5,5,actor.weapon.shotspeed,[-1,0],actor.weapon.shotrange,actor.bullet_color))
        actor.weapon.cd[0]=actor.weapon.cd[1]
        actor.oriantation='left'
    if key_pressed[pygame.K_RIGHT] and actor.weapon.cd[0] ==0: #right
        actor.add_bullet(Bullet(actor.body.x,actor.body.y+actor.body.height//2,5,5,actor.weapon.shotspeed,[1,0],actor.weapon.shotrange,actor.bullet_color))
        actor.weapon.cd[0]=actor.weapon.cd[1]
        actor.oriantation='right'
    if key_pressed[pygame.K_UP] and actor.weapon.cd[0]==0: #up
        actor.add_bullet(Bullet(actor.body.x+actor.body.width//2,actor.body.y,5,5,actor.weapon.shotspeed,[0,-1],actor.weapon.shotrange,actor.bullet_color))
        actor.weapon.cd[0]=actor.weapon.cd[1]
        actor.oriantation='up'
    if key_pressed[pygame.K_DOWN] and actor.weapon.cd[0]==0: #down
        actor.add_bullet(Bullet(actor.body.x+actor.body.width//2,actor.body.y+actor.body.height,5,5,actor.weapon.shotspeed,[0,1],actor.weapon.shotrange,actor.bullet_color))
        actor.weapon.cd[0]=actor.weapon.cd[1]
        actor.oriantation='down'

#ENEMY CONTROL

#Turn numbers into keyboard input, so that the computer can use the same functions
#as the player
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

def enemy_handler(enemies,map_objects):
    for enemy in enemies:
        key_pressed= get_input([random.randint(4,7)]) #generates random actions(moving,shooting)
        ship_movement(enemy, map_objects,key_pressed)
        shoot(enemy,key_pressed)
        

#SZENES OF THE GAME

#not really an endscreen yet since the game still continues just without being
#seen by the player -> find a better solution
def end_screen(): 
    WIN.fill(SCREEN_COLOR)
    myfont= pygame.font.SysFont('Comic Sans MS', 40)
    end= myfont.render('GAME OVER',False,WHITE)
    WIN.blit(end,(300,220))
    pygame.display.update()

#VISUALISING THE GAME

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

def draw_window(ship,map_objects,enemies):
    
    #Text written on the screen
    myfont= pygame.font.SysFont('Comic Sans MS', 40)
    score = myfont.render('Score: '+str(ship.score),False,(255,255,255))
    health= myfont.render('Health: '+str(ship.health),False,(255,255,255))
    
    #Ship is in the center of the Screen, moving on an underlying grid
    adjust_x = WIDTH//2-ship.body.x-ship.body.width
    adjust_y = HEIGHT//2-ship.body.y-ship.body.height

    WIN.fill(BLUE)
    central_draw(SCREEN_COLOR, pygame.Rect(-500,-500,MAP_SIZE_X,MAP_SIZE_Y), adjust_x, adjust_y)
    WIN.blit(BACKGROUND,(adjust_x,adjust_y))
    #Drawing enemies and their bullets:
    for enemy in enemies:
        try:
            WIN.blit(enemy.sprite,(enemy.body.x+adjust_x,enemy.body.y+adjust_y))
        except:
            central_draw(enemy.color,enemy.body,adjust_x,adjust_y)
        
        for bullet in enemy.bullet_list:
            try:
                WIN.blit(bullet.sprite,(bullet.body.x+adjust_x,bullet.body.y+adjust_y))
            except:
                central_draw(bullet.color,bullet.body,adjust_x,adjust_y)

    #Drawing all map_objects on the screen
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

# MAIN ############################################################################

def main_game():
    pygame.display.set_caption("Astroids")
    #OBJECTS IN THE GAME
    ship = spaceship([],750,600,SHIP_HEIGHT-2,SHIP_WIDTH-2,YELLOW)
    enemy = spaceship([],300,200,30,30,RED,True)
    enemy2 = spaceship([],800,800,30,30,RED,True)
    enemies=[enemy,enemy2]

    meteorites=[]
    
    items=[]

    walls=[]
    walls.append(Wall(50,50,150,150))
    portals = []
    
    construct_portal(100,100,200,200,5,50, walls, portals)
    construct_portal(-100,-100,300,300,5,50,walls,portals)
    hit_by_player_bullets=[meteorites,enemies]
    stops_bullets=[meteorites,walls,enemies]

    map_objects=[ship.bullet_list,meteorites,items,portals,walls]
    
    #GAME LOOP
    clock=pygame.time.Clock()
    run = True
    while run: 
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  
                quit()          
        key_pressed = pygame.key.get_pressed()
        
        ###########Shooting##############
        #1.wenn schießen nicht auf cooldown ist, wird ein Schuss hinzugefügt mit der richtung in die geschossen wird
        #2.und anschließend wird der Cooldown hochgesetzt
        #3.orentation des ships soll abhängig der Schießrichtung sein
        shoot(ship,key_pressed)
        
        ##MOVEMENT############
        ship_movement(ship,map_objects, key_pressed)

        ##PORTALS########
        all_obj = [ship]+portals + walls + items+ enemies+meteorites+ship.bullet_list + enemy.bullet_list + enemy2.bullet_list
        portables = []
        for p in all_obj:
            if isinstance(p,Portable):
                portables.append(p)
        
        portal_handler(portals,portables)
        
        ##BULLETS#######
        bullet_handler(ship,items, hit_by_player_bullets, stops_bullets) 
        
        ##ITEMS########
        item_handler(ship,items)
        
        #METEORITEN SPAWN
        spawn_met(meteorites, ship, 100)
        meteo_handler(meteorites, ship,walls)

        #ENEMIES
        enemy_handler(enemies,map_objects)
        for e in enemies:
            bullet_handler(e,items,[meteorites,[ship]],[[ship],walls,meteorites,portals])
        
        ship.tick()
        for bullet in ship.bullet_list:
            bullet.tick()
        for astroid in meteorites:
            astroid.tick()
        
        
        if ship.health <=0:
            draw_window(ship,map_objects,enemies)
            run=False
        else:
            draw_window(ship,map_objects,enemies)
    

def main_menu():
    pygame.display.set_caption('Start_Menu')
    run = True
    clock=pygame.time.Clock()
    font_large= pygame.font.SysFont('Comic Sans MS', 50)
    font= pygame.font.SysFont('Comic Sans MS', 20)
    First_time=True

    while run:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                run = False
                

            if 400 + 100 > mouse[0] > 400 and 275 + 50 > mouse[1] > 275:
                pygame.draw.rect(WIN, RED, (400, 275, 100, 50))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    main_game()
                    First_time=False
            else:
                pygame.draw.rect(WIN, WHITE, (400, 275, 100, 50)) 
            if First_time:
                WIN.blit(font_large.render("ASTROIDS", True, (255, 255, 255)), (325, 50)) 
                WIN.blit(font.render("Play", True, (0, 0, 0)), (417, 285))
            else:
                WIN.blit(font_large.render("You died!", True, RED), (340, 50)) 
                WIN.blit(font.render("Try Again", True, (0, 0, 0)), (400, 285))


        pygame.display.flip() 
        clock.tick(FPS)       


if __name__ == "__main__":
    main_menu()