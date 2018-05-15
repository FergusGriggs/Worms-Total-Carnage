#lemmings
import pygame, sys, math, random,os ,ctypes, webbrowser, pygame.midi, Perlin
from pygame.locals import *
from ctypes import wintypes
from operator import itemgetter
windowed=True
if not windowed:
    os.environ['SDL_VIDEO_WINDOW_POS'] = str(0)+","+str(0)
pygame.init()
pygame.display.set_caption('Worms!')
screenDetails = pygame.display.Info()
if not windowed:
    screenW,screenH = int(screenDetails.current_w),int(screenDetails.current_h)
else:
    screenW=1000
    screenH=800
screen = pygame.display.set_mode((screenW, screenH))

user32 = ctypes.WinDLL("user32")

user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = (
    wintypes.LPCWSTR,
    wintypes.LPCWSTR)

user32.ShowWindow.argtypes = (
    wintypes.HWND,
    ctypes.c_int)

playerID = random.randint(0,10000)
class point():
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.velocityx=0
        self.velocityy=0
class barrel():
    def __init__(self,x,y,damage,radius,ID):
        self.x=x
        self.y=y
        self.damage=damage
        self.radius=radius
        self.ID=ID
    def explode(self):
        global worms, selectedWorm, hitcount, hpToRemove
        pygame.draw.circle(bitmap, (255, 0, 255), (int(self.x),int(self.y)), self.radius)
        playExplosionSound(self.radius)
        createExplosion(self.x,self.y,self.radius,(255,0,0))
        for worm in worms:
            dx=worm.x-self.x
            dy=worm.y+5-self.y
            dist=math.sqrt((dx)**2+(dy)**2)
            if dist<self.radius+5:
                damage=(1-(dist/self.radius))*self.damage
                damage=abs(damage)
                hpToRemove.append([worm.ID,damage,worms[selectedWorm].name,False])
                hitcount+=1
                if worm.x>self.x:
                    worm.velocityx+=damage/10
                else:
                    worm.velocityx-=damage/10
                if worm.y<self.y+1:
                    worm.velocityy-=damage/10
                else:
                    worm.velocityy+=damage/10
            for barrel in barrels:
                if barrel.ID==self.ID:
                    barrels.remove(barrel)
        for barrel in barrels:
            if barrel.ID!=self.ID:
                dx=barrel.x-self.x
                dy=barrel.y-self.y
                dist=math.sqrt((dx)**2+(dy)**2)
                if dist<self.radius+5:
                    barrel.explode()

                
            
class worm():
    def __init__(self,x,y,hp,team,name):
        self.x=x
        self.y=y
        self.velocityx=0
        self.velocityy=0
        self.hp=hp
        self.team=team
        self.name=name
        self.grounded=False
        self.jumping=False
        self.direction=1
        self.ID=random.randint(0,10000)
    def showCoords(self):
        print(self.x,self.y)
    def explode(self):
        global worms, barrels, hpToRemove, hitcount, gameState, hpTick
        pygame.draw.circle(bitmap, (255, 0, 255), (int(self.x),int(self.y)), 25)
        playExplosionSound(25)
        createExplosion(self.x,self.y,25,(255,0,0))
        for worm in worms:
            dx=worm.x-self.x
            dy=worm.y+5-self.y
            dist=math.sqrt((dx)**2+(dy)**2)
            if dist<25:
                damage=(1-(dist/25))*10#max damage of 10
                damage=abs(damage)
                hpToRemove.append([worm.ID,damage,self.name,False])
                hitcount+=1
                hpTick=0
                if worm.x>self.x:
                    worm.velocityx+=damage/10
                else:
                    worm.velocityx-=damage/10
                if worm.y<self.y+1:
                    worm.velocityy-=damage/10
                else:
                    worm.velocityy+=damage/10
                gameState="waiting"
            for barrel in barrels:
                if barrel.ID==self.ID:
                    barrels.remove(barrel)
        for barrel in barrels:
            if barrel.ID!=self.ID:
                dx=barrel.x-self.x
                dy=barrel.y-self.y
                dist=math.sqrt((dx)**2+(dy)**2)
                if dist<20:
                    barrel.explode()
def domordea(name,prevname):
    global message, announcerTimer
    announcerTimer=100
    domordea=random.randint(0,1)
    if name==prevname:
        message=name+" killed himself, idiot"
    if domordea==0:
        randomNum1=random.randint(0,len(announcerDeathLines)-1)
        if randomNum1==0:
            message=name+announcerDeathLines[randomNum1][random.randint(0,len(announcerDeathLines[randomNum1])-1)]
        elif randomNum1==1:
            message=announcerDeathLines[randomNum1][random.randint(0,len(announcerDeathLines[randomNum1])-1)]+name
        else:
            message=announcerDeathLines[randomNum1][random.randint(0,len(announcerDeathLines[randomNum1])-1)]
            
    else:
        randomNum1=random.randint(0,len(announcerDominationLines)-1)
        if randomNum1==0:
            message=announcerDominationLines[randomNum1][random.randint(0,len(announcerDominationLines[randomNum1])-1)]+prevname
        elif randomNum1==1:
            message=prevname+announcerDominationLines[randomNum1][random.randint(0,len(announcerDominationLines[randomNum1])-1)]
        else:
            message=announcerDominationLines[randomNum1][random.randint(0,len(announcerDominationLines[randomNum1])-1)]
def createGroundBlock():
    global tileSize, bitmap, screenW, screenH
    groundTexture=pygame.image.load("groundTextureSeamless.jpg")
    groundTexture=pygame.transform.scale(groundTexture,(tileSize,tileSize))
    for i in range(0,(screenW//tileSize)+1):
        for j in range(1,(screenH//tileSize)+1):
            bitmap.blit(groundTexture,(i*tileSize,100+j*tileSize))
    bitmap.set_alpha()
    bitmap.set_colorkey((255,0,255))
def groundWorms():
    global worms, genType
    for i in range(len(worms)):
        while not worms[i].grounded:
            worms[i].y+=1
            if bitmap.get_at((int(worms[i].x),int(worms[i].y)+5))!=(255,0,255):
                worms[i].grounded=True
            if worms[i].y>screenH-10:
                worms[i].y=0
                worms[i].x=random.randint(10,screenW-10)
                if genType==3:
                    worms[i].x=random.randint(10,screenW-10)
                    worms[i].y=random.randint(10,screenH-10)
        if worms[i].y>screenH-5:
            worms[i].x=random.randint(10,screenW-10)
            worms[i].y=random.randint(10,screenH-10)
        while bitmap.get_at((int(worms[i].x),int(worms[i].y)+4))!=(255,0,255):
            worms[i].y-=1
            if worms[i].y<5:
                worms[i].x=random.randint(10,screenW-10)
                worms[i].y=random.randint(10,screenH-10)
def loadWorldFromSave(saveName):
    global bitmap, screenW, screenH
    worldImage=pygame.image.load("saved terrain/"+str(saveName)+".png")
    worldImage=pygame.transform.scale(worldImage,(screenW,screenH))
    bitmap.blit(worldImage,(0,0))
    bitmap.set_alpha()
    bitmap.set_colorkey((255,0,255))
def createWorm(x,y,hp,team,name):
    global worms
    worm0=worm(x,y,hp,team,name)
    worms.append(worm0)
def spawnWorms(numOfTeams,wormsPerTeam,hp):
    global wormStats, worms, wormNames, startHp, genType
    wormNum=numOfTeams*wormsPerTeam
    startHp=wormsPerTeam*hp
    for i in range(0,wormNum):
        for j in range(0,numOfTeams):
            if i%numOfTeams==j:
                team=j+1
        x=random.randint(10,screenW-10)
        y=random.randint(10,screenH-10)
        if genType==2:
            if team%2==1:
                x=random.randint(10,450)
            else:
                x=random.randint(550,screenW)
        createWorm(x,y,hp,team,wormNames[random.randint(0,len(wormNames)-1)])
        wormStats.append([worms[i].ID,worms[i].name,0,0,0,0,0])#id, name, total dmg, max dmg in one shot,misses,totalShotNum,hpLost
def updateWorm(ID):
    global worms, gravity, aiming, selectedWorm, message, announcerTimer, movingWormLeft, movingWormRight, gameState, timer, timing, hpToRemove, windSpeed
    if ID<len(worms):
        worms[ID].y+=worms[ID].velocityy
        worms[ID].x+=worms[ID].velocityx
        checkWormBoundaries(worms[selectedWorm])
        if worms[ID].velocityy<-5:
            worms[ID].velocityy=-5
        if not worms[ID].grounded:
            worms[ID].velocityy+=gravity
            worms[ID].velocityx+=windSpeed/1500
            if bitmap.get_at((int(worms[ID].x),int(worms[ID].y)+5))!=(255,0,255):
                worms[ID].grounded=True
                if worms[ID].velocityy>13:
                    hpToRemove.append([worms[ID].ID,int(worms[ID].velocityy/1.5),worms[selectedWorm].name,False])
                    checkEnded()
                    timing=True
                    timer=0
                    gameState="waiting"
                    worms[ID].velocityx=0
                    movingWormLeft=False
                    movingWormRight=False
                worms[ID].velocityy=0
        else:
            worms[ID].velocityx*=0.8
            if bitmap.get_at((int(worms[ID].x),int(worms[ID].y)+4))!=(255,0,255):
                starty=worms[ID].y
                while bitmap.get_at((int(worms[ID].x),int(worms[ID].y)+4))!=(255,0,255):
                    worms[ID].y-=1
                    if starty-worms[ID].y>2:
                        if bitmap.get_at((int(worms[ID].x-3),int(worms[ID].y)))==(255,0,255):
                            worms[ID].x-=1
                        elif bitmap.get_at((int(worms[ID].x+3),int(worms[ID].y)))==(255,0,255):
                            worms[ID].x+=1
                    
            if bitmap.get_at((int(worms[ID].x),int(worms[ID].y)+5))==(255,0,255):
                worms[ID].grounded=False
        if worms[ID].direction==1:
            if bitmap.get_at((int(worms[ID].x+5),int(worms[ID].y)-5))!=(255,0,255):
                worms[ID].velocityx*=-1
        if worms[ID].direction==-1:
            if bitmap.get_at((int(worms[ID].x-5),int(worms[ID].y)-5))!=(255,0,255):
                worms[ID].velocityx*=-1
        if bitmap.get_at((int(worms[ID].x),int(worms[ID].y)-10))!=(255,0,255):
            worms[ID].velocityy+=1
            worms[ID].velocityx=0
        if worms[selectedWorm].direction==-1:
            if bitmap.get_at((int(worms[selectedWorm].x-3),int(worms[selectedWorm].y)))==(255,0,255):
                if worms[selectedWorm].jumping:
                    if worms[selectedWorm].grounded:
                        worms[selectedWorm].velocityy-=5
                        worms[selectedWorm].velocityx+=2*worms[selectedWorm].direction
                        worms[selectedWorm].jumping=False
            elif bitmap.get_at((int(worms[ID].x),int(worms[ID].y)-20))==(255,0,255):
                if worms[selectedWorm].jumping:
                    worms[selectedWorm].velocityy-=5
                    worms[selectedWorm].jumping=False
            else:
                jumping=False
        if worms[selectedWorm].direction==1:
            if bitmap.get_at((int(worms[selectedWorm].x-3),int(worms[selectedWorm].y)))==(255,0,255):
                if worms[selectedWorm].jumping:
                    if worms[selectedWorm].grounded:
                        worms[selectedWorm].velocityy-=5
                        worms[selectedWorm].velocityx+=2*worms[selectedWorm].direction
                        worms[selectedWorm].jumping=False
            elif bitmap.get_at((int(worms[ID].x),int(worms[ID].y)-20))==(255,0,255):
                if worms[selectedWorm].jumping:
                    worms[selectedWorm].velocityy-=5
                    worms[selectedWorm].jumping=False
            else:
                jumping=False
        if worms[selectedWorm].velocityx<0.5 and worms[selectedWorm].velocityy<0.5 and gameState=="playing":
            aimWeapon()
            drawRecticle()
            aiming=True
def updateAllWorms():
    global worms, selectedWorm, message, announcerTimer, projectiles, hpToRemove, timer, timing
    for worm in worms:
        worm.y+=worm.velocityy
        worm.x+=worm.velocityx
        checkWormBoundaries(worm)
        if not worm.grounded:
            worm.velocityy+=gravity
            if bitmap.get_at((int(worm.x),int(worm.y)+5))!=(255,0,255):
                worm.grounded=True
                if worm.velocityy>15:
                    hpToRemove.append([worm.ID,int(worm.velocityy/1.5),worms[selectedWorm].name,False])
                    timing=True
                    timer=0
                worm.velocityy=0
        else:
            worm.velocityx*=0.8
            if bitmap.get_at((int(worm.x),int(worm.y)+4))!=(255,0,255):
                while bitmap.get_at((int(worm.x),int(worm.y)+4))!=(255,0,255):
                    worm.y-=1
            if bitmap.get_at((int(worm.x),int(worm.y)+5))==(255,0,255):
                worm.grounded=False
        if bitmap.get_at((int(worm.x)+5,int(worm.y-5)))!=(255,0,255):
            worm.velocityx=0
        if bitmap.get_at((int(worm.x)-5,int(worm.y-5)))!=(255,0,255):
            worm.velocityx=0
        if bitmap.get_at((int(worm.x),int(worm.y)-10))!=(255,0,255):
            worm.velocityy=1
            worm.velocityx=0
def selectWorm(ID):
    global selectedWorm
    selectedWorm=ID
def handleWormMovement():
    global worms, selectedWorm, movingWormLeft, movingWormRight, gameState, jumpTimer
    try:
        if movingWormLeft:
            if bitmap.get_at((int(worms[selectedWorm].x-3),int(worms[selectedWorm].y)))==(255,0,255):
                worms[selectedWorm].x-=1.5
                worms[selectedWorm].velocityx*=0.5
                if bitmap.get_at((int(worms[selectedWorm].x+1),int(worms[selectedWorm].y+4)))!=(255,0,255):
                    worms[selectedWorm].y-=0.5
            elif bitmap.get_at((int(worms[selectedWorm].x-5),int(worms[selectedWorm].y-3)))!=(255,0,255):
                if gameState=="thinking" and worms[selectedWorm].grounded:
                    if jumpTimer==0:
                        startjumpWorm()
                    
                
                
        if movingWormRight:
            if bitmap.get_at((int(worms[selectedWorm].x+3),int(worms[selectedWorm].y)))==(255,0,255):
                worms[selectedWorm].x+=1.5
                worms[selectedWorm].velocityx*=0.5
                if bitmap.get_at((int(worms[selectedWorm].x-1),int(worms[selectedWorm].y+4)))!=(255,0,255):
                    worms[selectedWorm].y-=0.5
        elif bitmap.get_at((int(worms[selectedWorm].x+5),int(worms[selectedWorm].y-3)))!=(255,0,255):
            if gameState=="thinking"and worms[selectedWorm].grounded:
                if jumpTimer==0:
                        startjumpWorm()
        if jumpTimer>0:
            jumpTimer-=1
        if selectedWorm<len(worms):
            checkWormBoundaries(worms[selectedWorm])
    except:
        None
def checkWormBoundaries(worm):
    global worms
    if worm.x<6:
        worm.x=6
        worm.velocityx=0
    elif worm.x>screenW-6:
        worm.x=screenW-6
        worm.velocityx=0
    if worm.y<6:
        worm.y=6
    elif worm.y>screenH-6:
        worm.y=screenH-6
        for i in range(0,len(worms)):
            if worm.ID==worms[i].ID:
                domordea(worm.name,"The arena")
                worms.remove(worm)
                endTurn()
                gameState="waiting"
                break
def aimWeapon():
    global aimAngle, aimingUp, aimingDown, recticlePoint, worms, selectedWorm
    if aimingUp:
        if aimAngle>-88:
            aimAngle-=2
    if aimingDown:
        if aimAngle<88:
            aimAngle+=2
    recticlePoint.x=worms[selectedWorm].x+(math.cos((aimAngle*math.pi)/180)*50)*worms[selectedWorm].direction
    recticlePoint.y=worms[selectedWorm].y+(math.sin((aimAngle*math.pi)/180)*50)
def fireWeapon():
    global weaponHold, firing, weapons, currentWeapon, aimAngle, worms, selectedWorm, projectiles, gameState
    if firing:
        weaponHold+=2
        if weaponHold>weapons[currentWeapon][3]-1:
            firing=False
    if not firing:
        if currentWeapon==0:
            speed=(weaponHold/weapons[currentWeapon][3])*weapons[currentWeapon][2]
            projectile=point(worms[selectedWorm].x,worms[selectedWorm].y)
            projectile.velocityx=(math.cos((aimAngle*math.pi)/180)*worms[selectedWorm].direction)*speed
            projectile.velocityy=(math.sin((aimAngle*math.pi)/180))*speed
            projectiles.append([projectile,50,weapons[currentWeapon][0],weapons[currentWeapon][4],worms[selectedWorm].name,False])
            weaponHold=0
            gameState="waiting"
def updateProjectiles():
    global projectiles, worms, message, announcerTimer, selectedWorm, hitcount, trailDelay, hpToRemove, windSpeed
    listOfRemoves=[]
    for projectile in projectiles:
        if trailDelay>1:
            createTrail(projectile[0].x,projectile[0].y,(20,20,20))
            trailDelay=0
        else:
            trailDelay+=1
        if onScreen(projectile[0]):
            if bitmap.get_at((int(projectile[0].x),int(projectile[0].y)))!=(255,0,255):
                while bitmap.get_at((int(projectile[0].x),int(projectile[0].y)))!=(255,0,255):
                    projectile[0].x-=projectile[0].velocityx*0.1
                    projectile[0].y-=projectile[0].velocityy*0.1
                playExplosionSound(projectile[3])
                pygame.draw.circle(bitmap, (255, 0, 255), (int(projectile[0].x),int(projectile[0].y)), projectile[3])
                createExplosion(projectile[0].x,projectile[0].y,projectile[3],(255,0,0))
                hitcount=0
                for barrel in barrels:
                    dx=barrel.x-projectile[0].x
                    dy=barrel.y-projectile[0].y
                    dist=math.sqrt((dx)**2+(dy)**2)
                    if dist<projectile[3]+5:
                        barrel.explode()
                for worm in worms:
                    dx=worm.x-projectile[0].x
                    dy=worm.y+5-projectile[0].y
                    dist=math.sqrt((dx)**2+(dy)**2)
                    if dist<projectile[3]:
                        damage=(1-(dist/projectile[3]))*projectile[1]
                        hpToRemove.append([worm.ID,damage,projectile[4],False])
                        hitcount+=1
                        if worm.x>projectile[0].x:
                            worm.velocityx+=damage/10
                        else:
                            worm.velocityx-=damage/10
                        if worm.y<projectile[0].y+1:
                            worm.velocityy-=damage/10
                        else:
                            worm.velocityy+=damage/10
                        
                
                if hitcount==0:
                    announcerTimer=100
                    randomNum1=random.randint(0,len(announcerMissLines)-1)
                    if randomNum1==0:
                        message=announcerMissLines[randomNum1][random.randint(0,len(announcerMissLines[randomNum1])-1)]+projectile[4]
                    elif randomNum1==1:
                        message=projectile[4]+announcerMissLines[randomNum1][random.randint(0,len(announcerMissLines[randomNum1])-1)]
                    else:
                        message=announcerMissLines[randomNum1][random.randint(0,len(announcerMissLines[randomNum1])-1)]         
                            
                listOfRemoves.append(projectile)
        if projectile[2]:
            projectile[0].velocityy+=gravity/2
            projectile[0].velocityx+=windSpeed/600
        projectile[0].x+=projectile[0].velocityx
        projectile[0].y+=projectile[0].velocityy
        if projectile[0].x<0:
            listOfRemoves.append(projectile)
        elif projectile[0].x>screenW:
            listOfRemoves.append(projectile)
        elif projectile[0].y>screenH:
            listOfRemoves.append(projectile)
        for i in range(0,len(listOfRemoves)):
            if listOfRemoves[i] in projectiles:
                projectiles.remove(listOfRemoves[i])
def onScreen(p):
    global screenW, screenH
    if p.x>0 and p.x<screenW and p.y>0 and p.y<screenH:
        return True
    else:
        return False
def checkEnded():
    global projectiles, selectedWorm, gameState, timer, timing, movingWormLeft, movingWormRight, aimingUp, aimingDown, worms
    if len(projectiles)==0:
        counter=0
        if len(worms)>0:
            for i in range(len(worms)):
                if worms[i].grounded:
                    counter+=1
            if counter==len(worms):
                if not timing:
                    timer=0
                    timing=True
        else:
            timing=True
            timer=0
    if timer>50 and timing:
        timer=0
        timing=False
        movingWormLeft=False
        movingWormRight=False
        aimingUp=False
        aimingDown=False
        gameState="damaging"
        try:
            worms[selectedWorm].grounded=True
        except:
            print("selected worm out of range")
    if timing:
        timer+=1
def updateWormHp():
    global worms, hpToRemove, gameState, selectedWorm, hpTick, wormDeathDelay, playerControlledTeam
    for i in range(0,len(hpToRemove)):
        for worm in worms:
            if not hpToRemove[i][3]:
                if worm.ID==hpToRemove[i][0]:
                    worm.hp-=hpToRemove[i][1]*0.02
                    if worm.hp<=0:
                        worm.hp=0
                    

    if hpTick>100:
        toRemove=[]
        for i in range(0,len(hpToRemove)):
            hpToRemove[i][3]=True
            for j in range(0,len(worms)):
                worms[j].hp=int(worms[j].hp)
                if worms[j].hp<=0:
                    place=0
                    if selectedWorm>j:
                        selectedWorm-=1
                    toRemove.append(worms[j].ID)
                    wormDeathDelay=0
        for i in range(0,len(toRemove)):
            for worm in worms:
                if worm.ID==toRemove[i]:
                    if wormDeathDelay<=0:
                        worm.explode()
                        domordea(worm.name,hpToRemove[i][2])
                        worms.remove(worm)
                        wormDeathDelay=50
                    else:
                        wormDeathDelay-=1
        if len(toRemove)==0:
            endTurn()
        hpTick=0
    else:
        hpTick+=2
        updateHealthBars()
    
    
def updateTimer():
    global turnTimeLeft, turnTiming, selectedWorm, gameState, worms, deltaTime, movingWormRight, movingWormLeft
    if turnTimeLeft<0:
        turnTimeLeft=10000
        gameState="damaging"
        hpTick=0
        movingWormRight=False
        movingWormLeft=False
    elif turnTiming:
        turnTimeLeft-=deltaTime
def drawTurnTimer():
    global turnTimeLeft, turnTiming
    if turnTiming:
        timerFont = pygame.font.Font(None,35)
        turnTimerText=timerFont.render(str(round(turnTimeLeft/1000)),True,(0,0,0))
        screen.blit(turnTimerText,(0,100))
        
        
def endTurn():
    global selectedWorm, gameState, worms, playerControlledTeam, turnTimeLeft, arrowTimer
    testWorm=selectedWorm
    teams=[]
    currentTeam=worms[selectedWorm].team-1
    nextTeam=0
    for i in range(0,len(worms)):
        if worms[i].team-1 not in teams:
            teams.append(worms[i].team-1)
    teams.sort()
    if currentTeam<len(teams)-1:
        for i in range(0,len(teams)):
            if teams[i]==currentTeam:
                nextTeam=teams[i+1]
    else:
        nextTeam=teams[0]
    while worms[testWorm].team-1!=nextTeam:
        if testWorm<len(worms)-1:
            testWorm+=1
        else:
            testWorm=0
    selectedWorm=testWorm
    gameState="playing"
    updateWind()
    checkGameEnded()
    if nextTeam!=playerControlledTeam:
        for i in range(len(teams)):
            teams[i]+=1
        teams.remove(nextTeam+1)
        startThinking(worms[selectedWorm],teams)
    turnTimeLeft=10000
    arrowTimer=0
def tryToShoot(worm,teams):
    global firing, aimAngle, weaponHold, worms, wormThinkState, moveTime
    if len(teams)>0:
        shot=calculateShot(worms[selectedWorm],teams,1)
        if shot[0]:
            worms[selectedWorm].direction=shot[1]
            weaponHold=shot[2]
            aimAngle=shot[3]
            firing=False
            fireWeapon()
        else:
            wormThinkState="moving"
            moveTime=random.randint(1,50)
def drawProjectiles():
    for projectile in projectiles:
        pygame.draw.circle(screen,(0,0,0),(int(projectile[0].x),int(projectile[0].y)),2,0)
        
def drawRecticle():
    global worms, selectedWorm, recticlePoint, weaponHold, weapons, currentWeapon
    charge=weaponHold/weapons[currentWeapon][3]
    chargePoint.x=worms[selectedWorm].x+(recticlePoint.x-worms[selectedWorm].x)*charge
    chargePoint.y=worms[selectedWorm].y+(recticlePoint.y-worms[selectedWorm].y)*charge
    pygame.draw.line(screen,(255*charge,255-255*charge,0),(worms[selectedWorm].x,worms[selectedWorm].y),(chargePoint.x,chargePoint.y),int(5*charge))
    pygame.draw.circle(screen,(0,0,0),(int(recticlePoint.x),int(recticlePoint.y)),10,1)
    pygame.draw.line(screen,(0,0,0),(int(recticlePoint.x-10),int(recticlePoint.y)),(int(recticlePoint.x+10),int(recticlePoint.y)),1)
    pygame.draw.line(screen,(0,0,0),(int(recticlePoint.x),int(recticlePoint.y-10)),(int(recticlePoint.x),int(recticlePoint.y+10)),1)
    
def drawWorms():
    global worms, teamColours, showHealthBars, showNames, playerFont
    for selectedWorm in worms:
        pygame.draw.circle(screen,(0,0,0),(int(selectedWorm.x),int(selectedWorm.y)),6,2)
        pygame.draw.circle(screen,(0,0,0),(int(selectedWorm.x),int(selectedWorm.y-6)),5,2)
        pygame.draw.circle(screen,(255,224,189),(int(selectedWorm.x),int(selectedWorm.y)),5,0)
        pygame.draw.circle(screen,(255,224,189),(int(selectedWorm.x),int(selectedWorm.y-6)),4,0)
        screen.set_at((int(selectedWorm.x-2),int(selectedWorm.y-7)),(0,0,0))
        screen.set_at((int(selectedWorm.x+1),int(selectedWorm.y-7)),(0,0,0))
        if showHealthBars or showNames: 
            if showHealthBars:
                hpText=playerFont.render(str(int(selectedWorm.hp)),True,teamColours[selectedWorm.team-1])
                screen.blit(hpText,(selectedWorm.x-hpText.get_width()/2,selectedWorm.y-40))
            if showNames:
                nameText=playerFont.render(selectedWorm.name,True,teamColours[selectedWorm.team-1])
                screen.blit(nameText,(selectedWorm.x-nameText.get_width()/2,selectedWorm.y-30))
def announce():
    global announcerTimer, message
    if announcerTimer>0:
        announcerFont = pygame.font.Font(None,40)
        announceText=announcerFont.render(message,True,(0,0,0))
        screen.blit(announceText,(screenW/2-announceText.get_width()/2,30))
        announcerTimer-=1
def checkGameEnded():
    global worms, announcerTimer, message
    if len(worms)==1 and announcerTimer==0:
        announcerTimer=10000
        message="Victory for "+str(worms[0].name)+"!"
    counter=0
    for i in range(len(teamColours)):
        for j in range(len(worms)):
            if worms[j].team==i:
                counter+=1
            if counter==len(worms):
                announcerTimer=10000
                message="Victory for team "+str(worms[j].team-1)+"!"
                gameState="ended"
        counter=0
    if len(worms)==0:
        print("noone wins")
        announcerTimer=10000
        message="No-one wins"
        
def showCurrentWorm():
    global worms, selectedWorm, selectedWormText1
    HUDFont = pygame.font.Font(None,35)
    selectedWormText0=HUDFont.render("Now up is: ",True,(0,0,0))
    try:
        selectedWormText1=HUDFont.render(worms[selectedWorm].name,True,teamColours[worms[selectedWorm].team-1])
    except:
        selectedWormText1=HUDFont.render("",True,(0,0,0))
    screen.blit(selectedWormText0,(0,0))
    screen.blit(selectedWormText1,(130,0))
def spawnPictureObjects(pictureObjectNum):
    picturePoints=[]
    picturePoint=point(0,0)
    for i in range(0,pictureObjectNum):
        picturePoint.x=random.randint(0,screenW)
        picturePoint.y=0
        while bitmap.get_at((int(picturePoint.x),int(picturePoint.y)))==(255,0,255):
            picturePoint.y+=1
        object1=pygame.image.load("object"+str(random.randint(0,1))+".png")
        object1=pygame.transform.scale(object1,(150,150))
        object1=pygame.transform.rotozoom(object1,random.randint(0,4)*90,1)
        picturePoints.append([picturePoint.x,picturePoint.y,object1])
    bitmap.set_alpha()
    bitmap.set_colorkey((255,0,255))
    for i in range(0,len(picturePoints)):           
        bitmap.blit(picturePoints[i][2],(picturePoints[i][0]-75,picturePoints[i][1]-75))
def spawnBarrel(x,y,damage,radius):
    global barrels
    barrels.append(barrel(x,y,damage,radius,random.randint(0,100000)))
def spawnBarrels():
    global barrelNum, barrels, screenW, screenH
    for i in range(barrelNum):
        spawnBarrel(random.randint(10,screenW-10),0,50,50)
    for barrel in barrels:
        while bitmap.get_at((int(barrel.x),int(barrel.y)+8))==(255,0,255):
            barrel.y+=1
            if barrel.y>screenH-10:
                barrel.x=random.randint(10,screenW-10)
                barrel.y=0
        barrelImage=pygame.image.load("barrel.png")
        bitmap.blit(barrelImage,(int(barrel.x)-5,int(barrel.y)-8))
        #pygame.draw.rect(bitmap,(35, 158, 70),(int(barrel.x)-5,int(barrel.y)-8,10,16),0)

def startjumpWorm():
    global selectedWorm, worm
    worms[selectedWorm].jumping=True
def hideTaskbar():
    hWnd = user32.FindWindowW(u"Shell_traywnd", None)
    user32.ShowWindow(hWnd, 0)

def unhideTaskbar():
    hWnd = user32.FindWindowW(u"Shell_traywnd", None)
    user32.ShowWindow(hWnd, 5)
def drawExplosions():
    global explosions
    for i in range(0,len(explosions)):
        pygame.draw.circle(screen,explosions[i][3],(int(explosions[i][0].x),int(explosions[i][0].y)),int(explosions[i][1]))
def drawTrails():
    global trails
    for i in range(0,len(trails)):
        pygame.draw.circle(screen,trails[i][2],(int(trails[i][0].x),int(trails[i][0].y)),int(trails[i][1]))
def updateExplosions():
    toRemove=[]
    for i in range(0,len(explosions)):
        if explosions[i][1]>1:
            explosions[i][2]+=0.1
            explosions[i][1]-=explosions[i][2]
            if explosions[i][1]<1:
                toRemove.append(explosions[i])
    for i in range(0,len(toRemove)):
        explosions.remove(toRemove[i])
def updateTrails():
    global trails
    toRemove=[]
    for i in range(0,len(trails)):
        trails[i][3]-=0.1
        trails[i][1]+=trails[i][3]
        if trails[i][1]<1:
            trails[i][1]=1
            toRemove.append(trails[i])
        col=trails[i][2][0]
        col+=4
        if col>255:
            col=255
        trails[i][2]=(col,col,col)
    for i in range(0,len(toRemove)):
        trails.remove(toRemove[i])
def createExplosion(x,y,radius,colour):
    global explosions
    explosionPoint=point(x,y)
    explosions.append([explosionPoint,radius,0,colour])
def createTrail(x,y,colour):
    global trails
    trailPoint=point(x,y)
    trails.append([trailPoint,1,colour,1.25])
def rickRoll():
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
def playExplosionSound(radius):
    global sounds
    #116,120,47,108,33,38,15,105,10,32 for win
    #sounds.append([random.randint(20,50),127,100,100])
    low=100-radius*2
    if low<0:
        low=0
    if low>107:
        low=107
    sounds.append([random.randint(low,low+20),118,100,100])
def handleSounds():
    global sounds
    toRemove=[]
    for sound in sounds:
        if sound[3]==sound[2]:
            player.set_instrument(sound[1],1)
            player.note_on(sound[0],127,1)
        if sound[3]>0:
            sound[3]-=1
        elif sound[3]==0:
            player.set_instrument(sound[1],1)
            player.note_off(sound[0],127,1)
            toRemove.append(sound)
    for item in toRemove:
        sounds.remove(item)
def updateHealthBars():
    global worms, startHp, teamHps
    teams=[]
    teamHps=[]
    for worm in worms:
        if worm.team-1 not in teams:
            teams.append(worm.team-1)
    teamHps=[[0,teams[i]] for i in range(len(teams))]
    for teamNo in range(0,len(teamHps)):
        for worm in worms:
            if worm.team-1==teamHps[teamNo][1]:
                teamHps[teamNo][0]+=worm.hp
    teamHps=sorted(teamHps, key=itemgetter(0),reverse=True)
def drawHeathBars():
    global worms, startHp, teamHps, screenH
    for i in range(len(teamHps)):
        pygame.draw.rect(screen,teamColours[teamHps[i][1]],(40,screenH-20-15*len(teamHps)+15*i,200*(teamHps[i][0]/startHp),10),0)
        hpFont = pygame.font.Font(None,20)
        hpText=hpFont.render(str(int(teamHps[i][0])),True,teamColours[teamHps[i][1]])
        screen.blit(hpText,(20-hpText.get_width()/2,screenH-20-len(teamHps)*15+i*15))
def drawHud():
    global teamHps, selectedWormText, teamColours, gameState
    pygame.draw.rect(screen, (0,0,0),(0,0,selectedWormText1.get_width()+142,31),2)
    pygame.draw.rect(screen, (255,255,255),(0,0,selectedWormText1.get_width()+141,30),0)
    if gameState=="damaging":
        pygame.draw.rect(screen,(255,255,255),(0,screenH-30-len(teamHps)*15,250,20+len(teamHps)*15),0)
    #pygame.draw.rect(screen,(0,0,0),(-2,screenH-53-len(teamHps)*15,253,52+len(teamHps)*15),2)
    #HUDFont = pygame.font.Font(None,35)
    #HUDTextObject1=HUDFont.render("Leader is team ",True,(0,0,0))
    #try:
    #    HUDTextObject2=HUDFont.render(str(teamHps[0][1]),True,teamColours[teamHps[0][1]])
    #except:
    #    HUDTextObject2=HUDFont.render("",True,(0,0,0))
    #screen.blit(HUDTextObject1,(10,screenH-50-len(teamHps)*15))
    #screen.blit(HUDTextObject2,(200,screenH-50-len(teamHps)*15))
def saveAllData():
    global worms, bitmap, barrels, selectedWorm
    pygame.image.save(bitmap,"multiplayer data/map.png")
    f=open("multiplayer data/worm data.txt","w")
    for i in range(len(worms)):
        string=str(worms[i].x)+","+str(worms[i].y)+","+str(worms[i].hp)+","+str(worms[i].team)+","+str(worms[i].name)+","+str(worms[i].direction)+","+str(worms[i].grounded)+","+str(worms[i].ID)+"\n"
        f.write(string)
    f.close()
    f=open("multiplayer data/barrel data.txt","w")
    for i in range(len(barrels)):
        string=str(barrels[i].x)+","+str(barrels[i].y)+","+str(barrels[i].damage)+","+str(barrels[i].radius)+","+str(barrels[i].ID)+"\n"
        f.write(string)
    f.close()
    f=open("multiplayer data/general data.txt","w")
    string=str(selectedWorm)
    f.write(string)
    f.close()
def loadAllData():
    global bitmap, worms, barrels, selectedWorm
    worms=[]
    barrels=[]
    bitmap=pygame.image.load("multiplayer data/map.png")
    bitmap.set_alpha()
    bitmap.set_colorkey((255,0,255))
    f=open("multiplayer data/worm data.txt","r")
    wormData=f.readlines()
    for i in range(0,len(wormData)):
        singleWorm = wormData[i].split(",")
        worm1=worm(float(singleWorm[0]),float(singleWorm[1]),float(singleWorm[2]),int(singleWorm[3]),singleWorm[4])
        worm1.direction=int(singleWorm[5])
        worm1.grounded=bool(singleWorm[6])
        worm1.ID=int(singleWorm[7])
        worms.append(worm1)
    f.close()
    f=open("multiplayer data/barrel data.txt","r")
    barrelData=f.readlines()
    for i in range(0,len(barrelData)):
        singleBarrel = barrelData[i].split(",")
        barrel1=barrel(float(singleBarrel[0]),float(singleBarrel[1]),float(singleBarrel[2]),int(singleBarrel[3]),int(singleBarrel[4]))
        barrels.append(barrel1)
    f.close()
    f=open("multiplayer data/general data.txt","r")
    generalData=f.readlines()
    selectedWorm=int(generalData[0])
    updateHealthBars()
def addToServer():
    global playerID
    f=open("multiplayer data/new player.txt","w")
    f.write(str(playerID))
def generateTerrain():
    global bitmap, screenW, screenW, tilesize, genType, data, labels, nextLabel
    bitmap=pygame.image.load("black.png")
    bitmap=pygame.transform.scale(blank,(screenW,screenH))
    groundTexture=pygame.image.load("groundTextureSeamless.jpg")
    groundTexture=pygame.transform.scale(groundTexture,(tileSize,tileSize))
    for i in range(0,(screenW//tileSize)+1):
        for j in range(0,(screenH//tileSize)+1):
            bitmap.blit(groundTexture,(i*tileSize,j*tileSize))
    if genType==0:
        acc=0
        num=random.randint(200,500)
        for i in range(screenW):
            acc+=random.randint(-100,100)/500
            num+=acc
            if abs(acc)>1:
                acc*=0.5
            if num<100:
                acc+=0.1
            if num>screenH-100:
                acc-=0.1
            for j in range(screenH):
                #if j<screenH/2+math.sin((i*math.pi)/180)*300:
                   # bitmap.set_at((i,j),(255,0,255))
                if j< num+math.sin((i*math.pi)*10/180)*3:
                    bitmap.set_at((i,j),(255,0,255))
        for i in range(2):
            tunnel=random.randint(0,screenH)
            tunnelAcc=0
            tunnelRadius=0
            tunnelRadiusAcc=0
            for j in range(screenW):
                tunnelAcc+=random.randint(-100,100)/500
                tunnel+=tunnelAcc
                tunnelRadiusAcc+=random.randint(-100,100)/500
                tunnelRadius+=tunnelRadiusAcc
                if abs(tunnelAcc)>1.5:
                    tunnelAcc*=0.5
                if tunnel<200:
                    tunnelAcc+=0.1
                if tunnel>screenH-100:
                    tunnelAcc-=0.1
                if abs(tunnelRadiusAcc)>0.5:
                    tunnelRadiusAcc*=0.5
                if tunnelRadius<10:
                    tunnelRadius=10
                    tunnelRadiusAcc+=0.1
                if tunnelRadius>35:
                    tunnelRadiusAcc-=0.05
                if tunnelRadius<0:
                    tunnelRadius=0
                pygame.draw.circle(bitmap,(255,0,255),(j,int(tunnel)),int(tunnelRadius),0)
    if genType==1:
        bitmap.fill((255,0,255))
        for i in range(50):
            radius=random.randint(10,50)
            posx=random.randint(0,screenW)
            posy=random.randint(0,screenH)
            pygame.draw.circle(bitmap,(128,128,0),(posx,posy),radius,0)
            for i in range(10):
                pygame.draw.circle(bitmap,(i*12.8,128-i*12.8,0),(posx,posy),int(radius-(radius/(11-i))),0)
    if genType==2:
        bitmap.fill((255,0,255))
        fort=pygame.image.load("fort1.png")
        bitmap.blit(fort,(0,250))
        fort=pygame.transform.flip(fort,True,False)
        bitmap.blit(fort,(400,250))
    if genType==3:
        maxi=0
        mini=10000000
        for i in range(screenW):
            for j in range(screenH):
                n=Perlin.noise(i/75,j/75,2)
                if n>maxi:
                    maxi=n
                if n<mini:
                    mini=n
                if n<0:
                    bitmap.set_at((i,j),(255,0,255))
        print(maxi,mini)
    if genType==4:
        #bitmap.fill((255,0,255))
        num=random.randint(100,500)/1000
        print(num)
        data= [[0 for i in range(screenH)] for i in range(screenW)]
        labels= [[-1 for i in range(screenH)] for i in range(screenW)]
        print("Creating Noise Map")
        for i in range(screenW):
            for j in range(screenH):
                n=Perlin.noise(i/30,j/30,num)
                n=abs(n)
                n*=255
                if n<20:
                    n=0
                else:
                    n=1
##                if n<20:
##                    n=0
##                else:
##                    n=255
##                bitmap.set_at((i,j),(n,n,n))
                data[i][j]=n
##        for i in range(screenW):
##            for j in range(screenH):
##                if data[i][j]==0:
##                    bitmap.set_at((i,j),(0,0,0))
##                else:
##                    bitmap.set_at((i,j),(255,255,255))
        print("Creating Distinct Islands")
        passOverImage()
        print("Choosing Islands")
        regionsToShow=[]
        for i in range(screenW):
            if labels[i-1][screenH-400] != 0 and labels[i-1][screenH-400]:
                randnum=random.randint(0,1000)
                if randnum<250 and labels[i][screenH-400] not in regionsToShow:
                    regionsToShow.append(labels[i][screenH-125])
                else:
                    if labels[i][screenH-125] in regionsToShow:
                        regionsToShow.remove(labels[i][screenH-125])
                    
        for i in range(screenW):
            if labels[i-1][screenH-100] != 0 and labels[i-1][screenH-100] not in regionsToShow:
                randnum=random.randint(0,1000)
                if randnum<500:
                    regionsToShow.append(labels[i][screenH-100])
        for i in range(screenW):
            if labels[i-1][screenH-75] != 0 and labels[i-1][screenH-75] not in regionsToShow:
                regionsToShow.append(labels[i][screenH-75])
        for i in range(screenW):
            if labels[i-1][screenH-50] != 0 and labels[i-1][screenH-50] not in regionsToShow:
                regionsToShow.append(labels[i][screenH-50])
        for i in range(screenW):
            if labels[i-1][screenH-25] != 0 and labels[i-1][screenH-25] not in regionsToShow:
                regionsToShow.append(labels[i][screenH-25])
        for i in range(screenW):
            if labels[i-1][screenH-1] != 0 and labels[i-1][screenH-1] not in regionsToShow:
                regionsToShow.append(labels[i][screenH-1])
        #dilate
        if 0 in regionsToShow:
            regionsToShow.remove(0)
        print("Dilating Chosen Islands")
        toAdd=[]
        for x in range(10):
            for i in range(screenW):
                for j in range(screenH):
                    try:
                        if labels[i][j] in regionsToShow and labels[i][j]!=0:
                            if labels[i-1][j] not in regionsToShow:
                                labels[i-1][j]=8999+x
                            if labels[i+1][j] not in regionsToShow:
                                labels[i+1][j]=8999+x
                            if labels[i][j-1] not in regionsToShow:
                                labels[i][j-1]=8999+x
                            if labels[i][j+1] not in regionsToShow:
                                labels[i][j+1]=8999+x
                    except:
                        None
            regionsToShow.append(999999+x)
        print("Blitting to Surface")
        for i in range(screenW):
            for j in range(screenH):
                if labels[i][j] not in regionsToShow:
                    bitmap.set_at((i,j),(255,0,255))
            print(i)
        print("done")
        f=open("Procedurally generated terrain/0.txt","r")
        num=f.read()
        pygame.image.save(bitmap,"Procedurally generated terrain/number"+str(num)+".png")
        f.close()
        f=open("Procedurally generated terrain/0.txt","w")
        intNum=int(num)
        intNum+=1
        f.write(str(intNum))
        f.close()
        #pygame.draw.rect(bitmap,(255,0,255),(0,0,screenW,250),0)
##        colours = [(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for i in range(nextLabel)]
##        for i in range(screenW):
##            for j in range(screenH):
##                try:
##                    if labels[i][j]!=0:
##                        bitmap.set_at((i,j),colours[labels[i][j]])#if labels is zero and data is 1, run fill island
##                except:
##                    None
def fillIsland(x,y):
    global data, labels, nextLabel
    if data[x][y]==1 and labels[x][y]==0:
        expandFill(x,y,nextLabel,50)
        nextLabel+=1

def passOverImage():
    global data, labels, screenW, nextLabel
    #linked=[[] for j in range(1000)]
    for x in range(1):
        for i in range(screenW):
            for j in range(screenH):
                if data[i][j]==0:
                    labels[i][j]=0
                if data[i][j]==1:
                    neighbors=[]
                    try:
                        if data[i-1][j]==1 and labels[i-1][j]!=-1:
                            neighbors.append(labels[i-1][j])
                        if data[i-1][j-1]==1 and labels[i-1][j-1]!=-1:
                            neighbors.append(labels[i-1][j-1])
                        if data[i-1][j+1]==1 and labels[i-1][j+1]!=-1:
                            neighbors.append(labels[i-1][j+1])
                        if data[i+1][j+1]==1 and labels[i+1][j+1]!=-1:
                            neighbors.append(labels[i+1][j+1])
                        if data[i+1][j-1]==1 and labels[i+1][j-1]!=-1:
                            neighbors.append(labels[i+1][j-1])
                        if data[i+1][j]==1 and labels[i+1][j]!=-1:
                            neighbors.append(labels[i+1][j])
                        if data[i][j-1]==1 and labels[i][j-1]!=-1:
                            neighbors.append(labels[i][j-1])
                        if data[i][j+1]==1 and labels[i][j+1]!=-1:
                            neighbors.append(labels[i][j+1])
                    except:
                        None
                    if len(neighbors)>0:
                        neighbors=sorted(neighbors)
                        labels[i][j]=neighbors[0]
                    else:
                        labels[i][j]=nextLabel
                        #linked[nextLabel].append((i,j))
                        nextLabel+=1
                
                
                
def startSinglePlayer():
    global bitmap, background, pictureObjectNum, screenW, screenH, gameState, wormHP
    randomSaveNo=random.randint(0,3)
    loadWorldFromSave("save"+str(randomSaveNo))
    #createGroundBlock()
    generateTerrain()
    spawnPictureObjects(pictureObjectNum)
    spawnBarrels()
    spawnWorms(teamNum,wormsPerTeam,wormHP)
    groundWorms()
    updateHealthBars()
    gameState="playing"
def drawMenuAssets():
    global titleText,subTitleText, textData, singlePlayerRect, multiPlayerRect, singleColour,menuScreenState, initialSound, currentMenuPitch, currentMenuInstrument, menuOffset
    global screenH, screenW, backButtonRect, startButtonRect, teamNum, wormsPerTeam, barrelNum, wormHP, pictureObjectNum
    
    titleFont = pygame.font.Font("Fonts/TEXAT BOLD PERSONAL USE___.otf",200)
    titleSubFont = pygame.font.Font("Fonts/TEXAT BOLD PERSONAL USE___.otf",50)
    buttonFont = pygame.font.Font("Fonts/TEXAT BOLD PERSONAL USE___.otf",80)
    smallButtonFont = pygame.font.Font("Fonts/TEXAT BOLD PERSONAL USE___.otf",40)
    if menuScreenState=="main":
        #main title
        for i in range(len(titleText)):
            title=titleFont.render(titleText[i],True,(29+i*10,46+i*10,14+i*10))
            screen.blit(title,(100+150*i,-250+menuOffset*3+math.sin((textData[i]*math.pi)/180)*30))
            textData[i]+=10
        subTitle=titleSubFont.render(subTitleText,True,(40+(215/255)*singleColour,57,25))
        screen.blit(subTitle,(-472+menuOffset*7.22,300))
        if singlePlayerRect.collidepoint(pygame.mouse.get_pos()):
            if not initialSound:
                player.set_instrument(currentMenuInstrument,1)
                currentMenuPitch=random.randint(40,50)
                player.note_on(currentMenuPitch,127,1)
                initialSound=True
            if singleColour<255:
                singleColour+=5
                if singleColour>255:
                    singleColour=255
            pygame.draw.rect(screen,(0,0,0),singlePlayerRect,0)
            pygame.draw.rect(screen,(40,57,25),multiPlayerRect,0)
        elif multiPlayerRect.collidepoint(pygame.mouse.get_pos()):
            if not initialSound:
                currentMenuPitch=random.randint(40,50)
                player.set_instrument(currentMenuInstrument,1)
                player.note_on(currentMenuPitch,127,1)
                initialSound=True
            if singleColour<255:
                singleColour+=10
                if singleColour>255:
                    singleColour=255
            pygame.draw.rect(screen,(0,0,0),multiPlayerRect,0)
            pygame.draw.rect(screen,(40,57,25),singlePlayerRect,0)
        else:
            if singleColour>0:
                singleColour-=10
                if singleColour<0:
                    singleColour=0
            initialSound=False
            player.set_instrument(currentMenuInstrument,1)
            player.note_off(currentMenuPitch,127,1)
            pygame.draw.rect(screen,(40,57,25),singlePlayerRect,0)
            pygame.draw.rect(screen,(40,57,25),multiPlayerRect,0)
        single=buttonFont.render("single",True,(255,255,255))
        multi=buttonFont.render("multi",True,(255,255,255))
        screen.blit(single,(singlePlayerRect.left,singlePlayerRect.top))
        screen.blit(multi,(multiPlayerRect.left,multiPlayerRect.top))
        if menuDirection=="in" or menuDirection=="out":
            singlePlayerRect=Rect(-300+menuOffset*4,singlePlayerRect.top,300,110)
            multiPlayerRect=Rect(screenW-menuOffset*4,multiPlayerRect.top,270,110)
    elif menuScreenState=="singleConfig":
        pygame.draw.rect(screen,(40,57,25),(-350+menuOffset*4,50,350,100),0)
        pygame.draw.rect(screen,(40,57,25),(-350+menuOffset*4,180,350,100),0)
        pygame.draw.rect(screen,(40,57,25),(-350+menuOffset*4,310,350,100),0)
        pygame.draw.rect(screen,(40,57,25),(-350+menuOffset*4,440,350,100),0)
        pygame.draw.rect(screen,(40,57,25),(-350+menuOffset*4,570,350,100),0)
        pygame.draw.rect(screen,(40,57,25),(450,-650+menuOffset*7,100,100),0)
        pygame.draw.rect(screen,(40,57,25),(450,-520+menuOffset*7,100,100),0)
        pygame.draw.rect(screen,(40,57,25),(450,-390+menuOffset*7,100,100),0)
        pygame.draw.rect(screen,(40,57,25),(450,-260+menuOffset*7,100,100),0)
        pygame.draw.rect(screen,(40,57,25),(450,-130+menuOffset*7,100,100),0)
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,50,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,180,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,310,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,440,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,570,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,105,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,235,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,365,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,495,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(screenW-menuOffset*4,625,350,45),0)#
        pygame.draw.rect(screen,(40,57,25),(startButtonRect),0)
        pygame.draw.rect(screen,(40,57,25),(backButtonRect),0)
        if Rect(screenW-menuOffset*4,50,350,45).collidepoint(pygame.mouse.get_pos()):#teamup
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,50,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,180,350,45).collidepoint(pygame.mouse.get_pos()):#wormspteamup
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,180,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,310,350,45).collidepoint(pygame.mouse.get_pos()):#barrelsup
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,310,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,570,350,45).collidepoint(pygame.mouse.get_pos()):#hpup
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,570,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,440,350,45).collidepoint(pygame.mouse.get_pos()):#picturesdown
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,440,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,105,350,45).collidepoint(pygame.mouse.get_pos()):#teamdown
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,105,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,235,350,45).collidepoint(pygame.mouse.get_pos()):#wormsperteamdown
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,235,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,365,350,45).collidepoint(pygame.mouse.get_pos()):#barrelsdown
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,365,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,495,350,45).collidepoint(pygame.mouse.get_pos()):#wormhpdown
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,495,350,45),0)
            hoverSound()
        elif Rect(screenW-menuOffset*4,625,350,45).collidepoint(pygame.mouse.get_pos()):#picturesdown
            pygame.draw.rect(screen,(0,0,0),(screenW-menuOffset*4,625,350,45),0)
            hoverSound()
        elif backButtonRect.collidepoint(pygame.mouse.get_pos()):#back
            pygame.draw.rect(screen,(0,0,0),(backButtonRect),0)
            hoverSound()
        elif startButtonRect.collidepoint(pygame.mouse.get_pos()):#start
            pygame.draw.rect(screen,(0,0,0),(startButtonRect),0)
            hoverSound()
        else:
            initialSound=False
            player.set_instrument(currentMenuInstrument,1)
            player.note_off(currentMenuPitch,127,1)
            
        
        
        back=buttonFont.render("back",True,(255,255,255))
        start=buttonFont.render("start!",True,(255,255,255))
        teamsText=buttonFont.render("teams",True,(255,255,255))
        wormsTeamText=smallButtonFont.render("worms/team",True,(255,255,255))
        barrelsText=smallButtonFont.render("barrels",True,(255,255,255))
        hpText=smallButtonFont.render("worm hp",True,(255,255,255))
        pictureObject=smallButtonFont.render("pictures",True,(255,255,255))
        teamNumText=numberFont.render(str(teamNum),True,(255,255,255))
        wormsPerTeamText=numberFont.render(str(wormsPerTeam),True,(255,255,255))
        barrelNumText=numberFont.render(str(barrelNum),True,(255,255,255))
        hpNumText=smallNumberFont.render(str(wormHP),True,(255,255,255))
        upArrow=smallButtonFont.render("/\\",True,(255,255,255))
        downArrow=smallButtonFont.render("\\/",True,(255,255,255))
        pictureObjectNumText=numberFont.render(str(pictureObjectNum),True,(255,255,255))
        screen.blit(back,(backButtonRect.left+80,backButtonRect.top-18))
        screen.blit(teamsText,(-325+menuOffset*4,50))
        screen.blit(wormsTeamText,(-325+menuOffset*4,200))
        screen.blit(barrelsText,(-275+menuOffset*4,330))
        screen.blit(hpText,(-275+menuOffset*4,460))
        screen.blit(pictureObject,(-275+menuOffset*4,590))
        screen.blit(start,(startButtonRect.left+55,startButtonRect.top-18))
        screen.blit(teamNumText,(475,-640+menuOffset*7))
        screen.blit(wormsPerTeamText,(500-wormsPerTeamText.get_width()/2,-510+menuOffset*7))
        screen.blit(barrelNumText,(500-barrelNumText.get_width()/2,-380+menuOffset*7))
        screen.blit(hpNumText,(500-hpNumText.get_width()/2,-235+menuOffset*7))
        screen.blit(pictureObjectNumText,(500-pictureObjectNumText.get_width()/2,-120+menuOffset*7))
        for i in range(5):
            screen.blit(upArrow,(screenW+155-menuOffset*4,45+130*i))
            screen.blit(downArrow,(screenW+155-menuOffset*4,100+130*i))
        if menuDirection=="in" or menuDirection=="out":
            backButtonRect=Rect(50,screenH+150-menuOffset*2.5,400,75)
            startButtonRect=Rect(550,screenH+150-menuOffset*2.5,400,75)
def updateShrapnel():
    global shrapnel, screenW, screenH, nextMenu
    for piece in shrapnel:
        if nextMenu=="start":
            piece[0].velocityy+=10
        else:
            piece[0].velocityy+=0.2
        piece[0].x+=piece[0].velocityx
        piece[0].y+=piece[0].velocityy
        if piece[0].y>screenH and nextMenu!="start":
            randomSide=random.randint(0,1)
            piece[0].y=random.randint(0,screenH)
            piece[0].velocityy=random.randint(-10,5)
            if randomSide==0:
                piece[0].x=0
                piece[0].velocityx=random.randint(0,10)
            if randomSide==1:
                piece[0].x=screenW
                piece[0].velocityx=random.randint(-10,0)
        if piece[1]<0:
            createTrail(piece[0].x,piece[0].y,(20,20,20))
            piece[1]=1
        else:
            piece[1]-=1
    
def initialiseShrapnel(num):
    global shrapnel
    shrapnel=[[point(random.randint(0,screenW),random.randint(-200,0)),0]for i in range(num)]
def changeMenuOffset():
    global menuOffset, menuDirection, menuVelocity
    if menuDirection=="in":
        if menuOffset<100:
            menuVelocity-=0.1
            menuOffset+=menuVelocity
        else:
            menuDirection=""
            menuOffset=100
            menuVelocity=0
    elif menuDirection=="out":
        if menuOffset>0:
            menuVelocity+=0.1
            menuOffset-=menuVelocity
        else:
            menuDirection=""
            menuOffset=0
            menuVelocity=4.55
def hoverSound():
    global initialSound, currentMenuPitch
    if not initialSound:
        player.set_instrument(currentMenuInstrument,1)
        currentMenuPitch=random.randint(40,50)
        player.note_on(currentMenuPitch,127,1)
        initialSound=True
def drawWindspeed():
    global windSpeed, windHudDelta
    col=abs(windSpeed)*2.55
    if windHudDelta<100:
        windHudDelta+=1
    else:
        windHudDelta=0
    pygame.draw.rect(screen,(col,255-col,0),(screenW-125,10,windSpeed,15),0)
    pygame.draw.rect(screen,(255,255,255),(screenW-125+windSpeed*(windHudDelta/100),10,1,15),0)
    pygame.draw.rect(screen,(255,255,255),(screenW-125+windSpeed*(((windHudDelta+25)%100)/100),10,1,15),0)
    pygame.draw.rect(screen,(255,255,255),(screenW-125+windSpeed*(((windHudDelta+50)%100)/100),10,1,15),0)
    pygame.draw.rect(screen,(255,255,255),(screenW-125+windSpeed*(((windHudDelta+75)%100)/100),10,1,15),0)
    pygame.draw.rect(screen,(0,0,0),(screenW-127,10,4,15),0)
def updateWind():
    global windSpeed
    windSpeed=random.randint(-100,100)
def takeRandomShot():
    global worms, aimAngle, selectedWorm, firing, weaponHold
    if random.randint(0,1)==0:
        worms[selectedWorm].direction=-1
    else:
        worms[selectedWorm].direction=1
    aimAngle=random.randint(-90,0)
    weaponHold=random.randint(30,100)
    firing=False
    fireWeapon()
targetPoint=point(0,0)
def calculateShot(worm,teams,targetRadius):
    global targetPoint
    startDirection=random.randint(0,1)
    if startDirection==0:
        startDirection=-1
    for direction in range(0,2):
        if direction==0:
            direction=-1*startDirection
        for power in range(50,100):
            for angle in range(-90,90):
                if inRadiusOf(endPoint(worm,direction,power,angle),teams,targetRadius):
                    wp=point(worm.x,worm.y)
                    if distance(endPoint(worm,direction,power,angle),wp)>50:
                        targetPoint=endPoint(worm,direction,power,angle)
                        return [True,direction,power,angle]
    return [False]
def endPoint(worm,direction,power,angle):
    global gravity, windSpeed, screenW, screenH, intendedTrajectory
    speed=(power/100)*11.75
    p=point(worm.x,worm.y)
    p.velocityx=(math.cos((angle*math.pi)/180)*direction)*speed
    p.velocityy=(math.sin((angle*math.pi)/180))*speed
    intendedTrajectory=[]
    while 1:
        p.x+=p.velocityx
        p.y+=p.velocityy
        p.velocityy+=gravity/2
        p.velocityx+=windSpeed/600
        intendedTrajectory.append((p.x,p.y))
        if onScreen(p):
            if bitmap.get_at((int(p.x),int(p.y)))!=(255,0,255):
                while bitmap.get_at((int(p.x),int(p.y)))!=(255,0,255):
                    p.x-=p.velocityx*0.1
                    p.y-=p.velocityy*0.1
                    if not onScreen(p):
                       p.x+=p.velocityx*0.1
                       p.y+=p.velocityy*0.1
                       break
                if len(intendedTrajectory)<2:
                    intendedTrajectory=[(0,0),(1,1)]
                return p
        else:
            return point(-100,-100)
    
def inRadiusOf(p,teams,targetRadius):
    for worm in worms:
        if worm.team in teams:
            wp=point(worm.x,worm.y+5)
            if distance(wp,p)<=targetRadius:
                return True
def distance(p0,p1):
    return math.sqrt((p1.x-p0.x)**2+(p1.y-p0.y)**2)
def startThinking(worm,teams):
    global wormThinkData, gameState, wormThinkState
    wormThinkState="moving"
    gameState="thinking"
    wormThinkData=[worm,teams]
def drawCurrentWormArrow():
    global worms, selectedWorm, teamColours, arrowTimer, deltaTime
    if arrowTimer<3000:
        p=worms[selectedWorm]
        pygame.draw.polygon(screen,teamColours[worms[selectedWorm].team-1],[(p.x-5,p.y-70),(p.x+5,p.y-70),(p.x+5,p.y-60),(p.x+8,p.y-60),(p.x,p.y-50),(p.x-8,p.y-60),(p.x-5,p.y-60)],0)
        arrowTimer+=deltaTime
def drawTrajectory():
    global weaponHold, aimAngle, gravity, windSpeed, screenW, screenH, worms, selectedWorm
    speed=(weaponHold/100)*12
    p=point(worms[selectedWorm].x,worms[selectedWorm].y)
    p.velocityx=(math.cos((aimAngle*math.pi)/180)*worms[selectedWorm].direction)*speed
    p.velocityy=(math.sin((aimAngle*math.pi)/180))*speed
    #points=[]
    while onScreen(p):
        if bitmap.get_at((int(p.x),int(p.y)))==(255,0,255):
            p.x+=p.velocityx
            p.y+=p.velocityy
            p.velocityy+=gravity/2
            p.velocityx+=windSpeed/600
            #points.append((p.x,p.y))
        else:
            break
    #pygame.draw.lines(screen,(0,0,0),False,points,1)
def generalPoint(teams):
    global worms
    xtot=0
    ytot=0
    count=0
    for worm in worms:
        if worm.team in teams:
            xtot+=worm.x
            ytot+=worm.y
            count+=1
    if count>0:
        return point(xtot/count,ytot/count)
    else:
        return point(-100,-100)
    
###int
tileSize=250
selectedWorm=0
currentWeapon=0
aimAngle=0
weaponHold=0
timer=0
announcerTimer=0
pictureObjectNum=0
hitcount=0
trailDelay=0
hpTick=0
wormDeathDelay=0
startHp=0
currentMenuInstrument=92
currentMenuPitch=0
singleColour=0
menuOffset=0
menuDirection="in"
menuVelocity=4.55
teamNum=2
wormsPerTeam=4
barrelNum=0
wormHP=100
initialLoadDelay=0
initialLoadTick=0
genType=4
windSpeed=random.randint(-100,100)
windHudDelta=0
playerControlledTeam=0

moveTime=0
wormThinkAngle=0
wormThinkPower=0
WormThinkDirection=0
turnTimeLeft=10000
jumpTimer=0
arrowTimer=3000
nextLabel=2
###float
gravity=0.5
###string
gameState="menuScreen"
message=""
titleText="Worms!"
subTitleText="total carnage!"
menuScreenState="main"
nextMenu=""
wormThinkState=""
###array
wormThinkData=[]
worms=[]
barrels=[]
data=[]
labels=[]
weapons=[
        [True,50,12,100,50]#bazooka not affected by gravity, max damage of 50, max speed of 10, max hold time of 100 crator radius 50
        ]
intendedTrajectory=[(0,0),(1,1)]
projectiles=[]
explosions=[]
trails=[]
shrapnel=[]
hpToRemove=[]
textData=[ i*30 for i in range(len(titleText))]
teamColours=[(255,0,0),(0,0,255),(147,9,252),(255,0,200),(0,255,0),(254,131,10),(50,50,50),(57,240,190)]
announcerDeathLines=[[" takes one in the kisser!"," is no more...",", may he live on in our hearts...", ],#after name
                     ["Unlucky for ","Aww, poor ",],#before name
                     ["Round up the usual suspects.","offf, that must have hurt!","Gone with the wind..."," is that in the rules?"]]#standalone
announcerDominationLines=[["Somebody stop ","Who is this ","Holy hell ","A kill in the bag for " ],#before name
                          [" is out of control!"," takes another"," is going ham!"],#after name
                          ["Domination!","Carnage!","Now this is what i live for!","What just happened?","Who did this?"]#standalone
                          ]
announcerMissLines=[["Solid miss by ","Who doesn't love a good miss. Eh ","It's a miss by ","Yeah, nice one "],#before name
                    [" 1, ground 0"," strikes the dirt"," clearly has a disliking of my arena..."],#after name
                    ["The ground shuddered","My beautiful arena!","What a waste of ammo","The arena is taking some fire"]#standalone
                    ]

wormNames=["Mr Ti-T",
           "Succ off",
           "Johnny two memes",
           "Micheal jenkins",
           "MeMe Big Boy",
           "Dat Boi",
           "Jimmy Saas",
           "Szechuan Sauce",
           "Fergus",
           "The Geek",
           "Muselk",
           "Leggy Boi",
           "Your Mum",
           "Pop Culture Refrence",
           "Jackspedicey 2",
           "High IQ R&M Fan",
           "Milly Bays",
           "Aye Aye",
           "<worm.object>",
           "Propane",
           "Propane Accessories",
           "Big G",
           "Earthquake",
           "Donkey",
           "Shrek",
           "edups",
           "Her Majesty",
           "name placeholder",
           "Rick Astley",
           "Slim Shady",
           "The Real Slim Shady",
           "Wubba Lubba Dub Dub",
           "Pickle Rick",
           
           
           ]
sounds=[]
teamHps=[]
wormStats=[]
###bool
movingWormLeft=False
movingWormRight=False
aimingUp=False
aimingDown=False
aiming=False
firing=False
timing=False
showHealthBars=True
initialSound=False
showNames=True
pressing=False
initialLoad=False
initialMove=False
turnTiming=True
###other
targetPoint=point(-100,-100)
playerFont = pygame.font.Font(None,20)
selectedWormText1=playerFont.render("",True,(0,0,0))
numberFont = pygame.font.Font(None,125)
smallNumberFont = pygame.font.Font(None,75)
pygame.midi.init()
player= pygame.midi.Output(0)
blank=pygame.image.load("black.png")
blank=pygame.transform.scale(blank,(screenW,screenH))
bitmap = blank
background= pygame.image.load("background.png")
background=pygame.transform.scale(background,(screenW+200,screenH))
recticlePoint=point(-100,-100)
chargePoint=point(-100,-100)
singlePlayerRect=Rect(100,500,300,110)
multiPlayerRect=Rect(600,500,270,110)
backButtonRect=Rect(-1000,0,0,0)
startButtonRect=Rect(-1000,0,0,0)
initialRect=Rect(0,0,0,0)
initialiseShrapnel(10)
oldTime=0
currentTime=0
#hideTaskbar()
while 1:
    oldTime=currentTime
    currentTime=pygame.time.get_ticks()
    deltaTime=currentTime-oldTime
    screen.blit(background,(-100,0))
    #pygame.draw.lines(screen,(0,0,0),False,intendedTrajectory,1)
    if gameState=="thinking":
        if wormThinkState=="moving":
            if not initialMove:
                initialMove=True
                moveTime=random.randint(1,50)
                rand=random.randint(0,10)
                if rand<6:
                    if wormThinkData[0].x<generalPoint(wormThinkData[1]).x:
                        movingWormRight=True
                    else:
                        movingWormLeft=True
                else:
                    rand=random.randint(0,1)
                    if rand==0:
                        movingWormLeft=True
                    else:
                        movingWormRight=True
            if moveTime>0:
                moveTime-=1
            else:
                initialMove=False
                movingWormRight=False
                movingWormLeft=False
                if worms[selectedWorm].grounded:
                    wormThinkState="firing"
        elif wormThinkState=="firing":
            tryToShoot(wormThinkData[0],wormThinkData[1])
        updateTimer()
    if gameState=="waiting"or gameState=="playing" or gameState=="damaging":
        screen.blit(bitmap, (0, 0))
        if firing:
            fireWeapon()
            drawTrajectory()
        if gameState=="waiting":
            updateAllWorms()
            checkEnded()
            updateProjectiles()
            updateTrails()
            #pygame.draw.circle(screen,(255,0,0),(int(targetPoint.x),int(targetPoint.y)),5,0)
        if gameState=="damaging":
            updateWormHp()
            updateAllWorms()
        if len(worms)>0:
            if gameState=="playing":
                drawCurrentWormArrow()
                updateWorm(selectedWorm)
                updateTimer()
        handleWormMovement()
        updateExplosions()
        drawProjectiles()
        drawWorms()
        drawTrails()
        drawExplosions()
        drawWindspeed()
        #if len(projectiles)>0:
            #pygame.draw.circle(screen,(255,0,0),(int(targetPoint.x),int(targetPoint.y)),5,0)
        if not initialLoad:
            drawHud()
            if gameState=="damaging":
                drawHeathBars()
            showCurrentWorm()
        
        announce()
        handleSounds()
        if pygame.mouse.get_pressed()[2]:
            pygame.draw.circle(bitmap, (255, 0, 255), pygame.mouse.get_pos(), 50)
            createExplosion(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],50,(255,0,0))
            playExplosionSound(50)
            updateAllWorms()
        drawTurnTimer()
    elif gameState=="thinking":
        screen.blit(bitmap, (0, 0))
        updateWorm(selectedWorm)
        handleWormMovement()
        drawWorms()
        drawHud()
        drawWindspeed()
        showCurrentWorm()
        drawTurnTimer()
        drawCurrentWormArrow()
    elif gameState=="menuScreen":
        updateTrails()
        updateShrapnel()
        drawTrails()
        handleSounds()
        changeMenuOffset()
        if menuOffset==0:
            if nextMenu=="start":
                startSinglePlayer()
                trails=[]
                player.set_instrument(currentMenuInstrument,1)
                player.note_off(currentMenuPitch,127,1)
                initialLoad=True
                initialRect=Rect(0,screenH-10,screenW,10)
            else:
                menuDirection="in"
                menuScreenState=nextMenu
        drawMenuAssets()
        if menuScreenState == "main":
            if singlePlayerRect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    menuDirection="out"
                    nextMenu="singleConfig"
        elif menuScreenState == "singleConfig":
            if pygame.mouse.get_pressed()[0]:
                if backButtonRect.collidepoint(pygame.mouse.get_pos()):
                    menuDirection="out"
                    nextMenu="main"
                if Rect(screenW-menuOffset*4,50,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if teamNum<8:
                            teamNum+=1
                elif Rect(screenW-menuOffset*4,105,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if teamNum>2:
                            teamNum-=1
                elif Rect(screenW-menuOffset*4,180,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if wormsPerTeam<10:
                            wormsPerTeam+=1
                elif Rect(screenW-menuOffset*4,235,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if wormsPerTeam>1:
                            wormsPerTeam-=1
                elif Rect(screenW-menuOffset*4,310,350,45).collidepoint(pygame.mouse.get_pos()):
                    if barrelNum<99:
                        barrelNum+=1
                elif Rect(screenW-menuOffset*4,365,350,45).collidepoint(pygame.mouse.get_pos()):
                    if barrelNum>0:
                        barrelNum-=1
                elif Rect(screenW-menuOffset*4,440,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if wormHP<200:
                            wormHP+=10
                elif Rect(screenW-menuOffset*4,495,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if wormHP>10:
                            wormHP-=10
                elif Rect(screenW-menuOffset*4,570,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if pictureObjectNum<10:
                            pictureObjectNum+=1
                elif Rect(screenW-menuOffset*4,625,350,45).collidepoint(pygame.mouse.get_pos()):
                    if not pressing:
                        pressing=True
                        if pictureObjectNum>0:
                            pictureObjectNum-=1
                elif startButtonRect.collidepoint(pygame.mouse.get_pos()):
                    menuDirection="out"
                    nextMenu="start"
                    
            if not pygame.mouse.get_pressed()[0]:
               pressing=False
    if len(labels)>0:
        testf = pygame.font.Font(None,20)
        testt=testf.render(str(labels[pygame.mouse.get_pos()[0]][pygame.mouse.get_pos()[1]]),True,(0,0,0))
        screen.blit(testt,(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]+30))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.mouse.set_visible(True)
            unhideTaskbar()
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.mouse.set_visible(True)
                unhideTaskbar()
                pygame.quit()
                sys.exit()
            if gameState=="waiting"or gameState=="playing" or gameState=="damaging":
                if event.key==K_RETURN:
                    object1=pygame.image.load("object"+str(random.randint(0,3))+".png")
                    object1=pygame.transform.scale(object1,(150,150))
                    bitmap.blit(object1,(pygame.mouse.get_pos()[0]-150,pygame.mouse.get_pos()[1]-150))
                if event.key==K_k:
                    pygame.image.save(bitmap,"saved terrain/save3.png")
                if event.key==K_l:
                    randomSaveNo=random.randint(0,3)
                    loadWorldFromSave("save"+str(randomSaveNo))
                    bitmap.set_alpha()
                    bitmap.set_colorkey((255,0,255))
                if event.key==K_v:
                    saveAllData()
                if event.key==K_b:
                    loadAllData()
                if gameState=="playing" or gameState=="waiting":
                    if event.key==K_m:
                        if showHealthBars:
                            showHealthBars=False
                        else:
                            showHealthBars=True
                    if event.key==K_n:
                        if showNames:
                            showNames=False
                        else:
                            showNames=True
                if gameState=="playing":
                    arrowTimer=3000
                    if event.key==K_a:
                        movingWormLeft=True
                        worms[selectedWorm].direction=-1
                    if event.key==K_p:
                        spawnBarrels()
                    if event.key==K_g:
                        worms[selectedWorm].grounded=True
                    if event.key==K_d:
                        movingWormRight=True
                        worms[selectedWorm].direction=1
                    if event.key==K_LSHIFT:
                        startjumpWorm()
                    if event.key==K_w:
                        aimingUp=True
                    if event.key==K_s:
                        aimingDown=True
                    if event.key==K_LEFT:
                        movingWormLeft=True
                        worms[selectedWorm].direction=-1
                    if event.key==K_RIGHT:
                        movingWormRight=True
                        worms[selectedWorm].direction=1
                    if event.key==K_COMMA:
                        if selectedWorm<len(worms)-1:
                            selectedWorm+=1
                        else:
                            selectedWorm=0
                    if event.key==K_PERIOD:
                        if selectedWorm!=0:
                            selectedWorm-=1
                        else:
                            selectedWorm=len(worms)-1
                    if aiming:
                        if event.key==K_UP:
                            aimingUp=True
                        if event.key==K_DOWN:
                            aimingDown=True
                        if worms[selectedWorm].grounded:
                            if event.key==K_SPACE:
                                weaponHold=0
                                firing=True
                                fireWeapon()
            else:
                if event.key==K_o:
                    menuDirection="in"
                if event.key==K_p:
                    menuDirection="out"
                    
        if event.type == KEYUP:
            if gameState=="playing":
                if event.key==K_a:
                    movingWormLeft=False
                if event.key==K_d:
                    movingWormRight=False
                if event.key==K_w:
                    aimingUp=False
                if event.key==K_s:
                    aimingDown=False
                if event.key==K_LEFT:
                    movingWormLeft=False
                if event.key==K_RIGHT:
                    movingWormRight=False
                if aiming:
                    if event.key==K_UP:
                        aimingUp=False
                    if event.key==K_DOWN:
                        aimingDown=False
                    if event.key==K_SPACE:
                        if weaponHold!=0:
                            firing=False
                            fireWeapon()
    if initialLoad:
        if initialLoadTick>1:
            initialLoadTick=0
            newval=initialRect.top-15
            initialRect=Rect(0,newval,screenW,screenH-newval)
            if newval<0:
                initialLoad=False
        else:
            initialLoadTick+=1
        pygame.display.update(initialRect)
    else:
        pygame.display.update()
        pygame.display.flip()
