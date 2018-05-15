# server file
import os, time

players=[]
newTeamNo=0
def updatePlayers():
    global players, newTeamNo
    players=[]
    f=open("players.txt","r")
    playerData = f.readline().split(":")
    for i in range(len(playerData)):
        player = playerData[i].split(",")
        player[0]=int(player[0])
        player[1]=int(player[1])
        players.append(player)
        newTeamNo+=1
def checkNewPlayer():
    global players, newTeamNo
    try:
        f=open("new player.txt","r")
        player = f.readline().split(",")
        if len(player)>0:
            newTeamNo+=1
            player[0]=int(player[0])
            if len(player)==1:
                player.append(newTeamNo)
            player[1]=int(player[1])
            players.append(player)
            
        f.close()
        if len(player)>0:
            os.remove("new player.txt")
            f=open("players.txt","w")
            string=""
            for i in range(len(players)):
                string+=str(players[i][0])+","+str(players[i][1])+":"
            string=string[:-1]
            f.write(string)
    except:
        None
def showPlayers():
    global players
    print(players)
updatePlayers()
showPlayers()
while 1:
    time.sleep(2)
    checkNewPlayer()
    showPlayers()
