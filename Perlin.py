import pygame
from pygame.locals import *
import sys, os, random
from math import *
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

Screen = 512
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("Tileable Perlin Noise - Ian Mallett - 2009")
Surface = pygame.display.set_mode([Screen,Screen])

surface = pygame.Surface([Screen,Screen])

tiledim = 16   #In nodes
repeats = 1    #number of repetitions on screen

tilesize = float(Screen)/repeats
tilesize /= tiledim
def GetInput():
    key = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT or key[K_ESCAPE]:
            pygame.quit(); sys.exit()
        if event.type == KEYDOWN and event.key == K_F12:
            pygame.image.save(surface,"Perlin Noise.png")
def Draw():
    Surface.blit(surface,(0,0))
    pygame.display.flip()
    
def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)
def lerp(t, a, b):
    return a + t * (b - a)
def grad(hash, x, y, z):
    #CONVERT LO 4 BITS OF HASH CODE INTO 12 GRADIENT DIRECTIONS.
    h = hash & 15
    if h < 8: u = x
    else:     u = y
    if h < 4: v = y
    else:
        if h == 12 or h == 14: v = x
        else:                  v = z
    if h&1 == 0: first = u
    else:        first = -u
    if h&2 == 0: second = v
    else:        second = -v
    return first + second

p = []
for x in range(2*tiledim):
    p.append(0)
    
permutation = []
for value in range(0,tiledim):
    permutation.append(value)
random.shuffle(permutation)

for i in range(0,tiledim):
    p[i] = permutation[i]
    p[tiledim+i] = p[i]
    
def noise(x,y,z):
    #FIND UNIT CUBE THAT CONTAINS POINT.
    X = int(x)&(tiledim-1)
    Y = int(y)&(tiledim-1)
    Z = int(z)&(tiledim-1)
    #FIND RELATIVE X,Y,Z OF POINT IN CUBE.
    x -= int(x)
    y -= int(y)
    z -= int(z)
    #COMPUTE FADE CURVES FOR EACH OF X,Y,Z.
    u = fade(x)
    v = fade(y)
    w = fade(z)
    #HASH COORDINATES OF THE 8 CUBE CORNERS
    A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
    B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
    #AND ADD BLENDED RESULTS FROM 8 CORNERS OF CUBE
    return lerp(w,lerp(v,
                       lerp(u,grad(p[AA  ],x  ,y  ,z  ),
                              grad(p[BA  ],x-1,y  ,z  )),
                       lerp(u,grad(p[AB  ],x  ,y-1,z  ),
                              grad(p[BB  ],x-1,y-1,z  ))),
                  lerp(v,
                       lerp(u,grad(p[AA+1],x  ,y  ,z-1),
                              grad(p[BA+1],x-1,y  ,z-1)),
                       lerp(u,grad(p[AB+1],x  ,y-1,z-1),
                              grad(p[BB+1],x-1,y-1,z-1))))

def Generate():
    octaves = 8
    persistence = 0.8
    
    amplitude = 1.0
    maxamplitude = 1.0
    for octave in range(octaves):
        amplitude *= persistence
        maxamplitude += amplitude

    surface.lock()
    for x in range(0,Screen):
        for y in range(0,Screen):
            sc = float(Screen)/tilesize
            frequency = 1.0
            amplitude = 1.0
            color = 0.0
            for octave in range(0,octaves):
                sc *= frequency
                grey = noise(sc*float(x)/Screen,sc*float(y)/Screen,0.0)
                grey = (grey+1.0)/2.0
                grey *= amplitude
                color += grey
                frequency *= 2.0
                amplitude *= persistence
            color /= maxamplitude
            color = int(round(color*255.0))
            Surface.set_at((x,y),(color,color,color))
    surface.unlock()
def main():
    Generate()
    while True:
        GetInput()
        Draw()
if __name__ == '__main__': main()
