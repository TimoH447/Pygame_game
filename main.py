import pygame
import random
from classes import *
from utils import load_sprite
pygame.init()

#INITIALIZING THE WINDOW IN WHICH THE GAME IS PLAYED
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Platzhalter")

FPS = 60

#MAP AND PLAYER PROPERTIES
MAP_SIZE_X = 2000
MAP_SIZE_Y = 2000
BORDERSIZE = 100

COMET_CAP = 10

SHIP_HEIGHT, SHIP_WIDTH = 19, 19

#IMAGES and SPRITES
SHIP_IMG = load_sprite('Schiff', True)
SHIP_IMG = pygame.transform.scale(SHIP_IMG, (SHIP_HEIGHT,SHIP_WIDTH))
ASTEROID= load_sprite("asteroid2",True,'.jpg')
ASTEROID=pygame.transform.scale(ASTEROID, (15,15))
STONE=load_sprite("stone",False)
BACKGROUND = load_sprite('background2',False)
BACKGROUND=pygame.transform.scale(BACKGROUND, (2000,2000))
PORTAL_FLUID = load_sprite("portal_fluid",False)
BLUELINE = load_sprite("blueline",False)

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



def getClosest(pos, objects):
    index = 0
    
    dist = abs(pos[0]-objects[0][0])+abs(pos[1]-objects[0][1])
    for i in range(0,len(objects)):
        temp = abs(pos[0]-objects[i][0])+abs(pos[1]-objects[i][1])
        if temp<dist:
            dist = temp
            index = i
    return index

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
            met = Asteroid(x,random.randint(0,400),50,50,1,[random.randint(-5,5),random.randint(-5,5)],health=40)
            if not distance_rect(ship.body,met.body,d):
                meteorites.append(met)
        else:
            met = Asteroid(x,random.randint(0,400),10,10,random.randint(1,4),[random.randint(-5,5),random.randint(-5,5)])
            if not distance_rect(ship.body,met.body,d):
                meteorites.append(met)

def construct_portal(a,b,x,y,width,height,walls,portals):
    portals.append(Portal(a-x,b-y,x,y,width,height))
    portals.append(Portal(x-a,y-b,a,b,width,height))
    if height>width:
        walls.append(Wall(x-5,y-5,width+10,10))
        walls.append(Wall(x-5,y+height-5,10+width,10))
        walls.append(Wall(a-5,b-5,width+10,10))
        walls.append(Wall(a-5,b+height-5,10+width,10))
    else:
        walls.append(Wall(x-5,y-5,10,height+10))
        walls.append(Wall(x+width-5,y-5,10,height+10))
        walls.append(Wall(a-5,b-5,10,height+10))
        walls.append(Wall(a+width-5,b-5,10,height+10))


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
            if bullet.step>bullet.range:
                shooter.remove_bullet(bullet)
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
                        items.append(Ship_Item(element.body.x,element.body.y,10,10,random_ship_buff([fire_rate,speed_up,shotspeed_up,health_up])))
                del element

def item_handler(ship,items):
    for item in items:
        if ship.body.colliderect(item.body):
            item.On_ship_collision(ship)
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
                    break
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
#there are 0-7 possible keys
def emulateKeypress(input):
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
        key_pressed= emulateKeypress([random.randint(4,7)]) #generates random actions(moving,shooting)
        ship_movement(enemy, map_objects,key_pressed)
        shoot(enemy,key_pressed)
        

#PROCESSING EVENTS
def process_events():

    pass

def run_gamelogic():

    pass
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

    WIN.blit(BLUELINE,(1530+adjust_x,1000+adjust_y))
    WIN.blit(BLUELINE,(1530+adjust_x,1300+adjust_y))

    WIN.blit(BLUELINE,(450+adjust_x,300+adjust_y))
    WIN.blit(BLUELINE,(450+adjust_x,600+adjust_y))

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
def win_scene():
    run=True
    clock=pygame.time.Clock()
    font_large= pygame.font.SysFont('Comic Sans MS', 50)
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  
                quit()
        WIN.fill(BLACK)
        WIN.blit(font_large.render('YOU WIN',False, WHITE),(WIDTH//2,HEIGHT//2))
        pygame.display.flip()
        clock.tick(FPS)

def onDeath(ship,map_objects,enemies):
    draw_window(ship,map_objects,enemies)
    print('Ende')
    #win_scene()

def main_game(aicontrol=None, updateReward = None):
    pygame.display.set_caption("Astroids")
    next_scene='lose'
    #OBJECTS IN THE GAME
    ship = spaceship([],500,800,SHIP_HEIGHT-2,SHIP_WIDTH-2,YELLOW)
    enemy = spaceship([],300,200,30,30,RED,True)
    enemy2 = spaceship([],1750,1250,30,30,RED,True)
    enemies=[enemy,enemy2]

    meteorites=[]
    
    items=[]

    walls=[]
    walls.append(Wall(400,100,300,200))
    walls.append(Wall(700,130,950,150))
    walls.append(Wall(1400,280,250,620))
    walls.append(Wall(0,900,2000,100))
    walls.append(Wall(400,1000,150,800))
    walls.append(Wall(550,1650,1100,150))
    walls.append(Wall(1450,1550,200,300))
    walls.append(Wall(950,1000,50,300))

    portals = []
    
    construct_portal(750,1150,1100,650,5,50, walls, portals)
    
    hit_by_player_bullets=[meteorites,enemies]
    stops_bullets=[meteorites,walls,enemies]

    map_objects=[ship.bullet_list,meteorites,items,portals,walls]
    #Parameter für ai
    params= []
    #GAME LOOP
    clock=pygame.time.Clock()
    run = True
    while run: 
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  
                quit()
        params = {
            'health':ship.health,
            'player_posx':ship.body.x,
            'player_posy':ship.body.y,
            'asteroids': [[m.body.x,m.body.y] for m in meteorites]
        }          
        if aicontrol != None:
            key_pressed = emulateKeypress(aicontrol(params))
        else:
            key_pressed = pygame.key.get_pressed()

        process_events() 
        ###########Shooting##############
        #1.wenn schießen nicht auf cooldown ist, wird ein Schuss hinzugefügt mit der richtung in die geschossen wird
        #2.und anschließend wird der Cooldown hochgesetzt
        #3.orentation des ships soll abhängig der Schießrichtung sein
        shoot(ship,key_pressed)
        
        ##MOVEMENT############
        ship_movement(ship,map_objects+[[Line(450,300,6,600),Line(1530,1000,6,600)]], key_pressed)

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
        for asteroid in meteorites:
            asteroid.tick()
        
        #Check PlayerDeath
        if ship.health <=0:
            onDeath(ship,map_objects,enemies)
            try:
                updateReward(-10000)
            except:
                pass
            run = False
        else:
            draw_window(ship,map_objects,enemies)
    
    return next_scene

if __name__ == "__main__":
    main_game()