import main
import numpy as np
import random
from collections import defaultdict

rewardAlive = -1
rewardDeath = -10000
rewardHploss= -1000
alpha = 0.2
gamma = 0.9

#Q[state] = [w,a,s,d,up,down,left,right]
Q = defaultdict(lambda: [0 for i in range(0,8)])

def paramsToState(params):
    x = params['player_posx']
    y = params['player_posy']
    
    if params['asteroids'] !=[]:
        close_ast = main.getClosest((x,y),params['asteroids'])
        dist = str(int((x-params['asteroids'][close_ast][0])/20))+str(int((y-params['asteroids'][close_ast][0])/20))
    else:
        dist = str(1000)+'_'+str(1000)


    return str(int(round(x/10))*10)+str(int(round(y/10))*10) + dist
        


oldState = None
oldAction = None

def updateReward(reward):
    global oldState
    global oldAction

    #vorherige Aktion/State bewerten
    if oldState != None:
        prevReward = Q[oldState]
        prevReward[oldAction] = (1-alpha)*prevReward[oldAction] + alpha * reward
        Q[oldState]= prevReward   

    

def aicontrol(params):
    global oldState
    global oldAction

    state = paramsToState(params)
    estReward = Q[state]

    #vorherige Aktion/State bewerten
    if oldState != None:
        prevReward = Q[oldState]
        prevReward[oldAction] = (1-alpha)*prevReward[oldAction] + alpha * (rewardAlive + gamma * max(estReward))   

    oldState=state
        
    if set(estReward)==set([0]):
        oldAction= random.randint(0,7)
        
        return [oldAction]
    else:
        oldAction = np.argmax(estReward)
        return [oldAction]


main.main_game(aicontrol)

