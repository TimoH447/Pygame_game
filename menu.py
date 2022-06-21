from main import main_game
import pygame
import globalVar as gv

WIN = pygame.display.set_mode((gv.WIDTH,gv.HEIGHT))

def main_menu():
    pygame.display.set_caption('Start_Menu')
    run = True
    clock=pygame.time.Clock()
    font_large= pygame.font.SysFont('Comic Sans MS', 50)
    font= pygame.font.SysFont('Comic Sans MS', 20)
    scene= 'start'
    while run:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                run = False
                

            if 400 + 100 > mouse[0] > 400 and 275 + 50 > mouse[1] > 275:
                pygame.draw.rect(WIN, gv.RED, (400, 275, 100, 50))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    scene= main_game()
                    
            else:
                pygame.draw.rect(WIN, gv.WHITE, (400, 275, 100, 50)) 
            if scene== 'start':
                WIN.blit(font_large.render("ASTROIDS", True, (255, 255, 255)), (325, 50)) 
                WIN.blit(font.render("Play", True, (0, 0, 0)), (417, 285))
            elif scene== 'lose':
                WIN.blit(font_large.render("You died!", True, gv.RED), (340, 50)) 
                WIN.blit(font.render("Try Again", True, (0, 0, 0)), (400, 285))
            


        pygame.display.flip() 
        clock.tick(gv.FPS)
        
main_menu()