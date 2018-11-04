#!BPY

"""
Name: 'Create Circular Curve'
Blender: 249
Group: 'Mesh'
Tip: 'Can create circular curves with changeable resolutions.'
"""

__bpydoc__ = """\
It is possible to create circlular curves and change their resolutions all at once.

Warning: To work nicely with the "change resolution" function
do not edit or move points around in edit mode.

Tip: Press 'N' to view and edit the "Transform Properties" window.

Tip: Hold 'Shift' and press 'S' for functions to position the curve.
"""



from Blender import *
import math
import bpy



degrees1_TEXT = "0"
degrees2_TEXT = "90"
radius1_TEXT = "1"
radius2_TEXT = "1"
cuts_TEXT = "8"

create_HDL = 1
degrees1_HDL = 2
degrees2_HDL = 3
radius1_HDL = 4
radius2_HDL = 5
cuts_HDL = 6
change_HDL = 7



def getPtRadDeg(x, y):
	rad = math.sqrt(x * x + y * y)

	if x < 0:
		deg = -math.acos(y / rad) / (math.pi * 2.0 / 360.0)
	else:
		deg = math.acos(y / rad) / (math.pi * 2.0 / 360.0)
	
	return rad, deg


def getTurnDir(xA, yA, xB, yB):
	
	turnDir = 0
	
	# shrink or extend the line so that one of its ends is on an axis
	if (abs(xB) < abs(xA)):
		yB = yA - float(xA) / (xA - xB) * (yA - yB)
		xB = 0
	
	if (abs(yB) < abs(yA)):
		xB = xA - float(yA) / (yA - yB) * (xA - xB)
		yB = 0
	
	if (abs(xA) < abs(xB)):
		yA = yB - float(xB) / (xB - xA) * (yB - yA)
		xA = 0
	
	if (abs(yA) < abs(yB)):
		xA = xB - float(yB) / (yB - yA) * (xB - xA)
		yA = 0
	
	# find the turn direction
	if (abs(xB - xA) > abs(yB - yA)):
		if (yA > 0 or yB > 0):
			if xB - xA > 0:
				turnDir = 1
			if xB - xA < 0:
				turnDir = -1
		
		if (yA < 0 or yB < 0):
			if xB - xA > 0:
				turnDir = -1
			if xB - xA < 0:
				turnDir = 1
	else:
		if (xA > 0 or xB > 0):
			if yB - yA < 0:
				turnDir = 1
			if yB - yA > 0:
				turnDir = -1
		
		if (xA < 0 or xB < 0):
			if yB - yA < 0:
				turnDir = -1
			if yB - yA > 0:
				turnDir = 1
	
	return turnDir


def getHalfTurnCnt(xPts, yPts, pointCnt):
	
	if pointCnt < 2:
		return 0
	
	# initalize
	if xPts[0] < 0:
		side = -1
	else:
		side = 1
	
	sidePrior = side
	
	# get the turn count
	turnCnt = 0
	for i in range(1, pointCnt):
		if xPts[i] < 0:
			side = -1
		else:
			side = 1
		
		if side != sidePrior:
			turnCnt += 1
		
		sidePrior = side
	
	# offset turn count
	if turnCnt != 0:
		turnCnt -= 1
	
	return turnCnt


def getDegreesSum(xPts, yPts, pointCnt, degA, degB, direction):
	
	halfTurns = getHalfTurnCnt(xPts, yPts, pointCnt)

	if halfTurns == 0:
		if direction > 0:
			if xPts[0] >= 0 and xPts[-1] >= 0:
				degreesSum = -degA + degB
				
			if xPts[0] < 0 and xPts[-1] < 0:
				degreesSum = -degA + degB
			
			if xPts[0] >= 0 and xPts[-1] < 0:
				degreesSum = 360 - (degA - degB)
			
			if xPts[0] < 0 and xPts[-1] >= 0:
				degreesSum = (degB - degA)
		else:
			if xPts[0] >= 0 and xPts[-1] >= 0:
				degreesSum = degA + -degB
				
			if xPts[0] < 0 and xPts[-1] < 0:
				degreesSum = degA + -degB
			
			if xPts[0] >= 0 and xPts[-1] < 0:
				degreesSum = (degA - degB)
			
			if xPts[0] < 0 and xPts[-1] >= 0:
				degreesSum = (degA - degB) + 360
	else:
		if direction > 0:
			if xPts[0] >= 0:
				degA = 180 - abs(degA)
			else:
				degA = abs(degA)

			if xPts[-1] >= 0:
				degB = abs(degB)
			else:
				degB = 180 - abs(degB)
		else:
			if xPts[0] >= 0:
				degA = abs(degA)
			else:
				degA = 180 - abs(degA)

			if xPts[-1] >= 0:
				degB = 180 - abs(degB)
			else:
				degB = abs(degB)

		degreesSum = halfTurns * 180 + degA + degB

	return degreesSum


def getCurveParameters(xPts, yPts):

	if xPts[0] == 0 and yPts[0] == 0:
		radA = 0
		degA = 0
	else:
		radA, degA = getPtRadDeg(xPts[0], yPts[0])

	if xPts[-1] == 0 and yPts[-1] == 0:
		radB = 0
		degB = 0
	else:
		radB, degB = getPtRadDeg(xPts[-1], yPts[-1])

	if radA > radB:
		direction = getTurnDir(xPts[0], yPts[0], xPts[1], yPts[1])
	else:
		direction = getTurnDir(xPts[-2], yPts[-2], xPts[-1], yPts[-1])

	pointCnt = len(xPts)
	degreesSum = getDegreesSum(xPts, yPts, pointCnt, degA, degB, direction)

	degB = degA + degreesSum * direction 

	return radA, degA, radB, degB



def createCurve(deg1, deg2, rad1, rad2, cuts):
	
	if rad1 <= 0 or rad2 <= 0:
		Draw.PupMenu("Radiuses must be greater than 0.")
		#Draw.PupStrInput("Radiuses must be greater than 0.", "", 1)
		return
	
	if deg1 == deg2:
		Draw.PupMenu("Degrees can not be equal.")
		return
	
	#convert the number of cuts into points
	rightAngleCnt = int(abs(deg2 - deg1) / 90.0)
	
	if rightAngleCnt == 0:
		rightAngleCnt = 1
	
	pts = rightAngleCnt * (int(abs(cuts)) + 1.0) + 1.0
	
	
	degInc = (deg2 - deg1) / (pts-1.0)
	radInc = (rad2 - rad1) / (pts-1.0)

	c = math.cos(-degInc / 360.0 * math.pi * 2.0);
	s = math.sin(-degInc / 360.0 * math.pi * 2.0);

	vPrior = math.cos(deg1 / 360.0 * math.pi * 2.0);
	hPrior = math.sin(deg1 / 360.0 * math.pi * 2.0);

	y = vPrior*rad1;
	x = hPrior*rad1;

	verts = []
	edges = []
	verts.append((x, y, 0.0))
	
	for i in range(1, int(pts)):
		
		v = hPrior * s + vPrior * c;
		h = vPrior * -s + hPrior * c;
		y = v*(rad1+radInc*i);
		x = h*(rad1+radInc*i);

		verts.append((x, y, 0.0))
		edges.append((i-1, i))

		vPrior = v;
		hPrior = h;
	
	
	editmode = Window.EditMode()
	if editmode: Window.EditMode(0)

	cu = bpy.data.meshes.new('cuEdges') # create a new mesh
	cu.verts.extend(verts)
	cu.edges.extend(edges)
	
	# link object to current scene
	scn = bpy.data.scenes.active
	ob = scn.objects.new(cu, 'curve')
	ob.setLocation(Window.GetCursorPos())

	if editmode: Window.EditMode(1)
	Window.RedrawAll()

	return


def chgCurveRes(cuts):

	scene = Scene.GetCurrent()
	
	# make sure the radiuses are greater than zero
	for ob in scene.objects.selected:
		if ob.type == "Mesh":
			cu = ob.data
			if cu.verts[0][0] == 0 and cu.verts[0][1] == 0:
				Draw.PupMenu("Error, "+ob.name+" x,y end point == 0,0")
				return
			if cu.verts[-1][0] == 0 and cu.verts[-1][1] == 0:
				Draw.PupMenu("Error, "+ob.name+" x,y end point == 0,0")
				return
	
	for ob in scene.objects.selected:
		if ob.type == "Mesh":
			cu = ob.data
			
			xCurvePts = []
			yCurvePts = []
			for i in range(0, len(cu.verts)):
				xCurvePts.append(cu.verts[i][0])
				yCurvePts.append(cu.verts[i][1])
			
			print xCurvePts
			
			rad1, deg1, rad2, deg2 = getCurveParameters(xCurvePts, yCurvePts)
			
			if deg1 == deg2:
				continue;
			
			
			#convert the number of cuts into points
			rightAngleCnt = int(abs(deg2 - deg1) / 90.0)
			
			if rightAngleCnt == 0:
				rightAngleCnt = 1
			
			pts = rightAngleCnt * (int(abs(cuts)) + 1.0) + 1.0
			
			
			degInc = (deg2 - deg1) / (pts-1.0)
			radInc = (rad2 - rad1) / (pts-1.0)
		
			c = math.cos(-degInc / 360.0 * math.pi * 2.0);
			s = math.sin(-degInc / 360.0 * math.pi * 2.0);
		
			vPrior = math.cos(deg1 / 360.0 * math.pi * 2.0);
			hPrior = math.sin(deg1 / 360.0 * math.pi * 2.0);

			y = vPrior*rad1;
			x = hPrior*rad1;
		
			verts = []
			edges = []
			verts.append((xCurvePts[0], yCurvePts[0], 0.0))
			edges.append((0, 1))
			
			for i in range(1, int(pts-1)):
				
				v = hPrior * s + vPrior * c;
				h = vPrior * -s + hPrior * c;
				y = v*(rad1+radInc*i);
				x = h*(rad1+radInc*i);
		
				verts.append((x, y, 0.0))
				edges.append((i, i+1))
		
				vPrior = v;
				hPrior = h;
			
			verts.append((xCurvePts[-1], yCurvePts[-1], 0.0))
			
			
			editmode = Window.EditMode()
			if editmode: Window.EditMode(0)
		
			cuChg = bpy.data.meshes.new('cuEdges') # create a new mesh
			cuChg.verts.extend(verts)
			cuChg.edges.extend(edges)
			
			# link mesh to object
			ob.link(cuChg)
			cu.update()
			
			if editmode: Window.EditMode(1)
			Window.RedrawAll()
			
	return


# handle input events
def event(evt, val):
	# exit when user presses Q
	if evt == Draw.QKEY:
		Draw.Exit()

# text edit events
def textEdit_ev(evt, val):
	global degrees1_TEXT
	global degrees2_TEXT
	global radius1_TEXT
	global radius2_TEXT
	global cuts_TEXT
	
	if evt == degrees1_HDL:
		degrees1_TEXT = val

	if evt == degrees2_HDL:
		degrees2_TEXT = val

	if evt == radius1_HDL:
		radius1_TEXT = val

	if evt == radius2_HDL:
		radius2_TEXT = val

	if evt == cuts_HDL:
		cuts_TEXT = val

# handle button events
def button_event(evt):
	global degrees1_TEXT
	global degrees2_TEXT
	global radius1_TEXT
	global radius2_TEXT
	global cuts_TEXT
	
	if evt == create_HDL:
		createCurve(float(degrees1_TEXT), float(degrees2_TEXT), float(radius1_TEXT), float(radius2_TEXT), float(cuts_TEXT))

	if evt == change_HDL:
		chgCurveRes(float(cuts_TEXT))


# draw to screen
def gui():
	global degrees1_TEXT
	global degrees2_TEXT
	global radius1_TEXT
	global radius2_TEXT
	global cuts_TEXT
	
	
	BGL.glClearColor(0.72,0.7,0.7,1)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

	BGL.glColor3f(0.25,0.25,0.25)
	
	
	x = 10
	y = 5
	Draw.Button("Create", create_HDL, x, y, 155, 25, "Add a circular path to the scene.")

	y += 30
	ret = Draw.String("DegrA:", degrees1_HDL, x,    y, 76, 25, degrees1_TEXT, 9, "The amount of degrees the first point will be around the circle.", textEdit_ev)
	ret = Draw.String("DegrB:", degrees2_HDL, x+80, y, 76, 25, degrees2_TEXT, 9, "The amount of degrees the second point will be around the circle.", textEdit_ev)

	y += 30
	ret = Draw.String("RadiusA:", radius1_HDL, x,    y, 76, 25, radius1_TEXT, 9, "The length from the center of the circle to the first point.", textEdit_ev)
	ret = Draw.String("RadiusB:", radius2_HDL, x+80, y, 76, 25, radius2_TEXT, 9, "The length from the center of the circle to the second point.", textEdit_ev)


	y += 30
	BGL.glRasterPos2i(x, y)
	Draw.Text("CREATE CIRCULAR CURVE")
	
	y += 20
	ret = Draw.String("Cuts:", cuts_HDL, x, y, 76, 25, cuts_TEXT, 9, "The number of cuts per quadrant.", textEdit_ev)
	Draw.Button("Change", change_HDL, x+80, y, 76, 25, "Change the resolution of a curve.")

	y += 30
	BGL.glRasterPos2i(x, y)
	Draw.Text("Change resolution:")
	
	
	y = 130
	BGL.glRasterPos2i(180, y)
	Draw.Text("Warning: To work nicely with the \"change resolution\" function")
	y -= 15
	BGL.glRasterPos2i(180, y)
	Draw.Text("do not edit or move points around in edit mode.")
	
	y = 90
	BGL.glRasterPos2i(180, y)
	Draw.Text("Note: Same radius is a circular path.")
	y -= 15
	BGL.glRasterPos2i(180, y)
	Draw.Text("Different radius makes a spiral segment.")
	y -= 15
	BGL.glRasterPos2i(180, y)
	Draw.Text("Press 'Q' to exit.")


# registering the 3 callbacks
Draw.Register(gui, event, button_event)