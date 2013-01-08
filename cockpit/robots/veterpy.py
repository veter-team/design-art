import  bpy
import  bge
import  mathutils
import  math

import datetime

from mathutils import Vector
from bge import texture
from bge import logic

def Pi():
    return 3.14159265

def getObject(object):
    return bge.logic.getCurrentScene().objects[object]

def Update_Robot(Sl,Sr,Rwl,Rwr,S,Zr):
	global TRS
	global WR
	global TB
	global Tl
	
	wheel_FR=getObject('wheel.FR')
	wheel_BR=getObject('wheel.BR')
	wheel_FL=getObject('wheel.FL')
	wheel_BL=getObject('wheel.BL')

	wheel_FR.applyRotation([-Rwr,0,0],1)
	wheel_BR.applyRotation([-Rwr,0,0],1)
	wheel_FL.applyRotation([-Rwl,0,0],1)
	wheel_BL.applyRotation([-Rwl,0,0],1)

	robot = getObject('robot')
	robot.applyMovement([0,S,0],True)
	robot.applyRotation([0,0,Zr],True)	

	nt = ['L','R']
	vt = [Sl,Sr]
	
	for t in range(0,2):
		for n in range(0,TRACKCOUNT):
			TRS[n][t] = TRS[n][t] + vt[t]
			name=nt[t]+"Track."+("000"+str(n)+"-")[-4:-1]
			base=getObject(name)
			p = track_sim(TRS[n][t])
			base.localPosition = (0,p[0],p[1])
			eul = mathutils.Euler((p[2], 0.0, 0.0), 'XYZ')
			base.localOrientation = eul
	
def recalc(Sl,Sr):
	global WR
	global TB
	global Tl

	k = 1
	Slk=Sl*k
	Srk=Sr*k
	S = (Slk+Srk)/2
	Rz = (Slk-Srk)/(TB*Pi())
	Rwl=Sr/WR
	Rwr=Sl/WR
	return [Slk,Srk,Rwl,Rwr,S,Rz]


    
def track_sim(fs):
	global WR
	global Tl
	global RD

	R = WR-RD
	L = TL
	
	k=1
	s = Pi()*R
	if fs<0:
		fs=-fs
		k=-1
	f = fs%(4*L+2*s)
	if f<L:
		d=f-(0)
		a=0
		return (d*k,R,a*k)
	if f<(L+s):
		d=f-(L)
		a=d/R
		return ((L+R*math.sin(a))*k,R*math.cos(a),-a*k)
	if f<(3*L+s):
		d=f-(L+s)
		a=s/R
		return ((L-d)*k,-R,a*k)
	if f<(3*L+2*s):
		d=f-(3*L+s)
		a=(s+d)/R
		return ((-L+R*math.sin(a))*k,R*math.cos(a),-a*k)
	d=f-(3*L+2*s)
	a=(2*s)/R
	return ((-L+d)*k,R,a*k)

### GLOBAL DATABASE
def gval(key):
	global gdb
	if hval(key):
		return gdb[key]
	return 0

def hval(key):
	global gdb
	return key in gdb

def sval(key,value):
	global gdb
	gdb[key] = value	

def svalsum(key,value):
	global gdb
	gdb[key] = gval(key)+value	

### CAMERA RENDER CAPTURE CODE 

def initCameraRender():
	pars = []
	pars.append(['Cam1','mainViewport','mainViewport'])
	pars.append(['Cam2','localViewport','localViewport'])
	pars.append(['Cam3','mapViewport','mapViewport'])
	
	for p in pars:
		Render2Texture(p[0],p[1],p[2])

def Render2Texture(ncam,nobj,nimg):
	scene = logic.getCurrentScene()
	obj = getObject(nobj)
	key = nobj + '_cam'

	if hval(key) == True:
		gval(key).refresh(True)
	else:
		print("Link(",key,"):",ncam,nobj,nimg)
		cam = getObject(ncam)
		matID = texture.materialID(obj,'IM'+nimg)
		if hasattr(obj,'channel') == True:
			ch = obj['channel']
		else:
			ch = 0
		tex = texture.Texture(obj, matID, ch)
		tex.source = texture.ImageRender(scene,cam)
		sval(key,tex)
	

def videopanel_update():
	pass
	
def setMainView():
	controller = bge.logic.getCurrentController()
	obj = controller.owner
	gameScreen = gameWindow()
	cams = getCameras()
	activeCamera(cams)
	viewportSize(gameScreen, cams)

def gameWindow():
	width = bge.render.getWindowWidth()
	height = bge.render.getWindowHeight()
	return (width, height)

def getCameras():
	scene = bge.logic.getCurrentScene()
	name_cams = ["Cam1","Cam3"]
	cams = []
	for name in name_cams:
		cams.append(scene.objects[name])
	return cams

def activeCamera(cams):
	scene = bge.logic.getCurrentScene()
	scene.active_camera = cams[0]


def viewportSize(gameScreen, cams):

	w = gameScreen[0]
	h = gameScreen[1]

	layout_cams = [[0,0,0.75,0.75],[0.5,0.75,0.75,1]]
	#,[0.75,0.75,1,1]]
	
	n = 0
	for p in layout_cams:
		cams[n].setViewport(int(w*p[0]),int(h*p[1]),int(w*p[2]),int(h*p[3]))
		cams[n].useViewport = True
		n = n + 1
		
def controllimit():
	head = getObject("head")
	eul = head.localOrientation
	#print(eul)

def camcap():
	scene = bge.logic.getCurrentScene()
	cams = getCameras()
	
	viewport = texture.ImageViewport()
#	viewport = texture.ImageRender(scene,cams[1])
###	viewport.depth = True
	buff = texture.imageToArray(viewport,'RGB1')
	writearray(buff,"imagetest")
	
	
def writearray(inputlist, filename):
	pass

def setup():
	global Pmaterial
	global Ptexture

	Pmaterial = "material"
	Ptexture = "_texture"

	#obj = cont.owner
	obj = getObject('Plane')
	
	print("setup:",obj)
	
	scene = logic.getCurrentScene()
	camera = scene.objects['Cam2']
	
	#matID = texture.materialID(obj, 'MAVideo' )
	#video = texture.Texture(obj, matID)
	#video.source = texture.ImageRender(scene, camera)
	#video.source.capsize = [256,256]
	#obj[Ptexture] = video
	return True

def refresh(cont):
	global Ptexture
	
	obj = cont.owner
	print("refresh:",obj)
	
	if (not Ptexture in obj and not setup(cont)):
		return
	obj[Ptexture].refresh(True)
	
	
def initialize():
	print("---")
	print("Initialize module")
	print("")
	
	global gdb
	gdb = {}

	global RD
	global WR
	global TB
	global TL
	global TRS
	global TRACKCOUNT

	portal_init = False

	RD = 1
	WR = 30
	TB = 93
	TL = 89
	TRACKCOUNT = 48
	TRS = []
	s=4*TL+2*(WR-RD)*Pi()
	s=s/(TRACKCOUNT-1)
	for i in range(0,TRACKCOUNT):
		TRS.append([i*s,i*s])

def Bx_Control():
	sens = bge.logic.getCurrentController().sensors[0]
	if len(sens.bodies)>0:
		msg = sens.bodies[0]
		lv = 0
		rv = 0
		if msg == 'up_arrow':
			lv = 0.5
			rv = 0.5
		if msg == 'left_arrow':
			lv = 0.5
			rv = -0.5
		if msg == 'down_arrow':
			lv = -0.5
			rv = -0.5
		if msg == 'right_arrow':
			lv = -0.5
			rv = 0.5
		svalsum('motor_left',lv)
		svalsum('motor_right',rv)	
	

def Bx_RadarDetect():
	radar = bge.logic.getCurrentController().sensors[0]
	obj = radar.owner
	key = obj.name
	pos = Vector(obj.worldPosition)
	hit = Vector(radar.hitPosition)
	dis = (pos-hit).length
	sval(key,dis)

def Init_Motors():
	sl = sval('motor_left',0)
	sr = sval('motor_right',0)

def limit_sr(a):
	m = 1
	if a>m:
		a = m
	if a<-m:
		a = -m
	return a

def Update_Motors():
	sl = limit_sr(gval('motor_left'))
	sr = limit_sr(gval('motor_right'))
	
	slm = sl / 10
	srm = sr / 10
	
	msg = 'motors:'+str(sl)+":"+str(sr)
	logic.sendMessage('motors',msg)
	sl *= 0.5
	sr *= 0.5			
	sval('motor_left',sl)
	sval('motor_right',sr)

	for i in range(0,10):
		v =  recalc(slm*3,srm*3)
		Update_Robot(v[0],v[1],v[2],v[3],v[4],v[5])
		
	
def Init_DateTime():
	pass
	
def Update_DateTime():
	from time import gmtime, strftime
	msg = strftime('time:%H:%M:%S',gmtime())
	logic.sendMessage('time',msg)

def Init_Compas():
	pass
	
def Update_Compas():
	robot = getObject('robot')
	value = abs(robot.localOrientation.to_euler('XYZ').z/Pi()*180+180)
	msg = 'compas:'+str(value)
	logic.sendMessage('compas',msg)

def Init_Radar():
	keys = ['radar.000','radar.001','radar.002','radar.003']
	for key in keys:
		sval(key,0)
	
def Update_Radar():
	keys = ['radar.000','radar.001','radar.002','radar.003']
	msg = 'radar'
	for key in keys:
		value = gval(key)
		msg += ':' + str(value)
		value += 10
		sval(key,value)
	logic.sendMessage('radar',msg)
	
def debugx(s):
	print(s)
	
def Init():
	Init_DateTime()
	Init_Compas()
	Init_Radar()
	Init_Motors()

def Update():
	initCameraRender()

	Update_DateTime()
	Update_Compas()
	Update_Radar()
	Update_Motors()
    
def main():
	initialize()
	camcap()
	    
main()
