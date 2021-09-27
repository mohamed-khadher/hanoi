import pygame, sys
import pygame_gui, colorsys
from pygame.locals import *
import random


#displayInit

pygame.init()
displaySurface = pygame.display.set_mode((1024,768))
pygame.display.set_caption("Hanoi")
framePerSec = pygame.time.Clock()
w,h = pygame.display.get_surface().get_size()

#myTowerDimensions
towerTop = 100
towerWidth = 300
towerHeight = 400
towerACoord = (w/3 -(towerWidth+25), towerTop)
towerBCoord = (2*w/3 -(towerWidth+25), towerTop)
towerCCoord = (w-(towerWidth+25), towerTop)
TowerAAxisCoord = towerACoord[0] + towerWidth/2
TowerBAxisCoord = towerBCoord[0] + towerWidth/2
TowerCAxisCoord = towerCCoord[0] + towerWidth/2

#DISK COLORS

diskColors = [(16, 52, 68), (26, 26, 26), (105, 105, 105), (104, 120, 140), (201, 201, 201), (242, 155, 136)
, (214, 135, 96), (242, 212, 61), (232, 255, 182), (62, 181, 149), (96, 191, 191), (75, 196, 207)
, (50, 153, 217), (146, 130, 190), (233, 139, 192), (115, 32, 62), (242, 73, 87)]

#game STATES

moves = 0
slow = False
animationDelay = 0.1
movingDisk = False
currentDisk = None

#GUI manager

manager = pygame_gui.UIManager((1024,768))

#GUI elements

btnMoreDisks = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 700), (80, 50)),text='More',manager=manager)

btnLessDisks = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 700), (80, 50)),text='Less',manager=manager)

btnSolve = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 700), (80, 50)),text='Solve',manager=manager)

btnAnimate = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 700), (80, 50)),text='Animate',manager=manager)

btnReset = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((450, 700), (80, 50)),text='Reset',manager=manager)

speedLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((550, 725), (160, 30)),text='Speed',manager=manager)

stopLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((550, 695), (160, 30)),text='Hold Space to Stop',manager=manager)

btnFaster = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((570, 725), (30, 30)),text='+',manager=manager)

btnSlower = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((660, 725), (30, 30)),text='-',manager=manager)

diskCountLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((40, 0), (150, 20)),text='DiskCount : 0',manager=manager)

animationDelayLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((590, 0), (400, 20))
													,text='Animation Delay (secs) : ' + str(animationDelay) + 's'
													,manager=manager)

minMoves = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((190, 0), (400, 20)),text='Minimal number of moves (2^diskcount -1) : ',manager=manager)

credits = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((836, 748), (190, 20)),text='Mohamed Khadher GCR2',manager=manager)


class Disk(pygame.sprite.Sprite):
	
	def __init__(self, width, height, color, pos):
		super().__init__()
		self.surf = pygame.Surface((width,height), pygame.SRCALPHA, 32)
		self.rect = self.surf.get_rect()
		pygame.draw.rect(self.surf, color, self.rect, 0, border_radius=4)
		self.width = width
		self.height = height
		self.pos = [pos[0], pos[1]]
		self.offset = [0,0]
		self.isPileTop = False
		self.tower = None
		self.originalPosition = [pos[0], pos[1]]

	def __lt__(self, other):
		if(self.width < other.width):
			return True
		return False

	def __gt__(self, other):
		if(self.width > other.width):
			return True
		return False

	def draw(self, surface, pos):
		surface.blit(self.surf, (self.pos[0]-self.width/2, self.pos[1]))
		
	
	def move(self, pos):
		if self.isPileTop:
			self.pos = [pos[0], pos[1]]

	def containsCursor(self,pos):
		if(self.pos[0] - self.width/2 < pos[0] < self.pos[0] + self.width/2):
			if(self.pos[1] < pos[1] < self.pos[1] + self.height):
				return True
		return False

	def snap(self, towers, pos):
		if not self.isPileTop:
			return
		for tower in towers:
			if(tower.pos[0] < pos[0] < tower.pos[0] + towerWidth):
				if(towerTop < pos[1] < towerTop + towerHeight):
					if(self.tower != tower and (not tower.disks or self < tower.disks[-1])):
						tower.updateTop()
						self.move((tower.pos[0]+towerWidth/2, tower.topDiskY))
						if(tower.disks):
							tower.disks[-1].isPileTop = False
						tower.disks.append(self)
						self.tower.removeDisk(self)
						self.tower.updateTop()
						self.tower = tower
						global moves
						moves += 1
					else:
						self.tower.updateTop(-1)
						self.move((self.tower.pos[0]+towerWidth/2, self.tower.topDiskY))
					return tower

	def reset(self):
		self.pos = self.originalPosition
		self.offset = [0,0]
		self.isPileTop = False
		self.tower = None


class Tower(pygame.sprite.Sprite):
	
	def __init__(self, width, height, color, pos):
		super().__init__()
		self.surf = pygame.Surface((width, height))
		self.rect = self.surf.get_rect()
		self.surf.fill((255,255,255,0))
		self.color = color
		self.width = width
		self.height = height
		self.pos = pos
		self.topDiskY = self.height + towerTop - 25
		self.disks = []

	def draw(self, surface, pos):
		#base
		pygame.draw.rect(self.surf, self.color, pygame.Rect(0,self.height-10, self.width, 10), border_radius=2)
		#tower
		pygame.draw.rect(self.surf, self.color, pygame.Rect(self.width/2 - 5,0, 10, self.height), border_radius=2)
		surface.blit(self.surf, pos)

	def updateTop(self, offset = 0, diskThickness = 15):
		self.topDiskY = self.height + towerTop -25 - diskThickness*(len(self.disks)+offset)

	def removeDisk(self, disk):
		self.disks = self.disks[:-1]
		if(self.disks):
			self.disks[-1].isPileTop = True

	def reset(self):
		self.topDiskY = self.height + towerTop - 25
		self.disks = []


#intialization

diskCount = 6
towerA = Tower(towerWidth,towerHeight,(0,10,0), towerACoord)
towerB = Tower(towerWidth,towerHeight,(0,10,0), towerBCoord)
towerC = Tower(towerWidth,towerHeight,(0,10,0), towerCCoord)
towers = [towerA, towerB, towerC]
disks = [Disk(300-10*i, 15 ,diskColors[i],(TowerAAxisCoord,towerTop + towerHeight - 10 - 15*i))
	for i in range(1,diskCount)]
towerA.disks = disks
for i in disks:
	i.tower = towerA
	i.snap([towerA],(TowerAAxisCoord, towerTop+1))
disks[-1].isPileTop = True
diskCountLabel.set_text('DiskCount : ' + str(diskCount-1))
minMoves.set_text('Minimal number of moves (2^diskcount -1) : ' + str(2**(diskCount-1) - 1))
font = pygame.font.SysFont('Calibri', 32)
movesTextSurface = font.render('Moves : 0', True,(0,0,0))

#add a disk and restart

def addOneDisk():
	global moves
	moves = 0
	movesTextSurface = font.render('Moves : 0', True,(0,0,0))
	if(len(disks) >= 16):
		return
	for tower in towers:
		tower.reset()
	for disk in disks:
		disk.reset()
	global diskCount
	currentDiskCount = len(disks)
	disks.append(Disk(300-10*(currentDiskCount+1), 15 ,diskColors[diskCount]
		,(TowerAAxisCoord,towerTop + towerHeight - 10 - 15*(currentDiskCount+1))))
	towerA.disks = disks
	for i in disks:
		i.tower = towerA
		i.snap([towerA],(TowerAAxisCoord, towerTop+1))
	disks[-1].isPileTop = True
	diskCount += 1
	diskCountLabel.set_text('DiskCount : ' + str(diskCount-1))
	minMoves.set_text('Minimal number of moves (2^diskcount -1) : ' + str(2**(diskCount-1) - 1))

#remove a disk and restart

def removeOneDisk():
	global moves
	moves = 0
	movesTextSurface = font.render('Moves : 0', True,(0,0,0))
	if(len(disks) < 3):
		return
	for tower in towers:
		tower.reset()
	for disk in disks:
		disk.reset()
	currentDiskCount = len(disks)
	disks.pop(len(disks)-1)
	towerA.disks = disks
	for i in disks:
		i.tower = towerA
		i.snap([towerA],(TowerAAxisCoord, towerTop+1))
	disks[-1].isPileTop = True
	global diskCount
	diskCount -= 1
	diskCountLabel.set_text('DiskCount : ' + str(diskCount-1))
	minMoves.set_text('Minimal number of moves (2^diskcount -1) : ' + str(2**(diskCount-1) - 1))

#solve using recursive method

def solve(diskCount, towerA, towerB, towerC):
	if(slow):
		if(redraw(animationDelay)):
			return
	if(diskCount > 0):
		solve(diskCount-1,towerA,towerC,towerB)
		#movement part (have to add animation)
		if towerA.disks:
			towerA.disks[-1].snap([towerA, towerB, towerC], (towerC.pos[0]+1, towerTop+1))
		#------------
		solve(diskCount-1,towerB,towerA,towerC)

#this is meant to redraw the game each solve move

def redraw(delay):
	#should use multithreading for this (in a revisit)
	#because holding space should go for a 'delay-long' hold and this is an inconvenience
	displaySurface.fill((255,255,255))
	towerA.draw(displaySurface, towerACoord)
	towerB.draw(displaySurface, towerBCoord)
	towerC.draw(displaySurface, towerCCoord)
	for disk in disks:
		disk.draw(displaySurface, (TowerCAxisCoord,towerTop + towerHeight - 25))
	delta = framePerSec.tick(1/delay)
	manager.draw_ui(displaySurface)
	movesTextSurface = font.render('Moves : ' + str(moves), True,(0,0,0))
	displaySurface.blit(movesTextSurface,(420,570))
	pygame.display.update()
	if pygame.key.get_pressed()[K_SPACE]:
		return True
	for event in pygame.event.get():              
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

#increase speed by decreasing delay

def faster():
	global animationDelay
	if(animationDelay < 0.11):
		return
	animationDelay -= 0.1
	animationDelayLabel.set_text('Animation Delay (secs) : ' + str(round(animationDelay,1)) + 's')

#decrease speed by increasing delay

def slower():
	global animationDelay
	animationDelay += 0.1
	animationDelayLabel.set_text('Animation Delay (secs) : ' + str(round(animationDelay,1)) + 's')

#resets disks into position and moves counter to 0

def reset():
	global moves,movesTextSurface
	for tower in towers:
		tower.reset()
	for disk in disks:
		disk.reset()
	towerA.disks = disks
	towerA.disks[-1].isPileTop = True
	for disk in towerA.disks:
		disk.tower = towerA
		disk.snap([towerA],(TowerAAxisCoord, towerTop+1))
	moves = 0
	movesTextSurface = font.render('Moves : 0', True,(0,0,0))

while True:
	delta = framePerSec.tick(75)
	displaySurface.fill((255,255,255))
	movesTextSurface = font.render('Moves : ' + str(moves), True,(0,0,0))
	displaySurface.blit(movesTextSurface,(420,570))

	for event in pygame.event.get():              
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == MOUSEBUTTONDOWN:
			for disk in disks:
				if(disk.containsCursor(event.pos)):
					movingDisk = True
					currentDisk = disk
		elif event.type == MOUSEBUTTONUP and currentDisk:
			movingDisk = False
			currentDisk.snap(towers, event.pos)
		elif event.type == MOUSEMOTION and movingDisk:
			currentDisk.move(event.pos)
		elif event.type == pygame.USEREVENT:
			if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
				if event.ui_element == btnMoreDisks:
					addOneDisk()
				elif event.ui_element == btnLessDisks:
					removeOneDisk()
				elif event.ui_element == btnSolve:
					slow = False
					reset()
					solve(diskCount-1, towerA, towerB, towerC)
				elif event.ui_element == btnAnimate:
					slow = True
					#can't go/carry on from n-th position unfortunetly
					reset()
					solve(diskCount-1, towerA, towerB, towerC)
				elif event.ui_element == btnReset:
					reset()
				elif event.ui_element == btnFaster:
					faster()
				elif event.ui_element == btnSlower:
					slower()
		manager.process_events(event)

	towerA.draw(displaySurface, towerACoord)
	towerB.draw(displaySurface, towerBCoord)
	towerC.draw(displaySurface, towerCCoord)
	for disk in disks:
		disk.draw(displaySurface, (TowerCAxisCoord,towerTop + towerHeight - 25))
	manager.update(delta)
	manager.draw_ui(displaySurface)
	pygame.display.update()
