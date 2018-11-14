#!BPY

"""
Name: 'g-code (.ngc)...'
Blender: 249
Group: 'Export'
Tip: 'Export mesh edges to g-code.'
"""

__bpydoc__ = """\
	Note: This program exports 'mesh' vertex lines to g-code not 'paths'.

	It might be a good idea to use "reorder_vertex_line.py" before exporting.

	Use "reorder_vertex_line.py" to untangle the vertex sequence and give a starting point.
"""


from Blender import *
import math


relCoord_TOG = 0
setZero_TOG = 0
addG0_TOG = 1
feedRate_TEXT = "120"


exit_HDL = 1
chooseDir_HDL = 2
blendDir_HDL = 3
feedRate_HDL = 4
addG0_HDL = 5
setZero_HDL = 6
relCoord_HDL = 7


# rotate point using degrees
def degRot(horiP, vertP, degrees):

	hUc = math.cos(degrees * (math.pi * 2.0 / 360.0))
	vUc = math.sin(degrees * (math.pi * 2.0 / 360.0))

	hLine1 = hUc
	vLine1 = vUc
	hLine2 = -vUc
	vLine2 = hUc

	h = vertP * hLine2 + horiP * vLine2
	v = horiP * vLine1 + vertP * hLine1
	horiP = h
	vertP = v

	return (horiP, vertP)


def applyTrans(x, y, z, meshData):
	
	# apply object size
	x *= meshData.size[0]
	y *= meshData.size[1]
	z *= meshData.size[2]
	
	# apply object x axis rotation
	vertsRot = degRot(y, z, meshData.rot[0] / (math.pi * 2.0 / 360.0))
	y = vertsRot[0]
	z = vertsRot[1]
	
	# apply object y axis rotation
	vertsRot = degRot(x, z, -meshData.rot[1] / (math.pi * 2.0 / 360.0))
	x = vertsRot[0]
	z = vertsRot[1]
	
	# apply object z axis rotation
	vertsRot = degRot(x, y, meshData.rot[2] / (math.pi * 2.0 / 360.0))
	x = vertsRot[0]
	y = vertsRot[1]
	
	# apply object location
	x += meshData.loc[0]
	y += meshData.loc[1]
	z += meshData.loc[2]
	
	return (x, y, z)


# script main function
def ExportToGcode(file_name):
	
	# add up the selected layers after converting to binary
	selectedLayers = Window.ViewLayers()
	selectedLayersMask = 0
	for aL in selectedLayers:
		selectedLayersMask += 1<<(aL-1)
	
	# get a list of meshes
	scene = Scene.GetCurrent()
	meshes = []
	for ob in scene.objects:
		if selectedLayersMask & ob.Layer: # use only meshes in selected layers
			obtype = ob.type
			if obtype == "Mesh":
				meshes.append(ob)
	
	# return if found no meshes
	if meshes == []:
		print("No meshes found.")
		return

	# sort meshes alphabetically
	meshNames = []
	sortedMeshNames = []
	for mesh in meshes:
		meshNames.append(mesh.getName().split('-')[-1])
		sortedMeshNames.append(mesh.getName().split('-')[-1])
	
	sortedMeshNames.sort()
	
	sortedMeshes = []
	for sortedMeshName in sortedMeshNames:
		sortedMeshes.append(meshes[meshNames.index(sortedMeshName)])
	meshes = sortedMeshes

	# change to object mode
	in_editmode = Window.EditMode()
	if in_editmode: Window.EditMode(0)

	
	feedRate = float(feedRate_TEXT)
	xPrior = 0.0
	yPrior = 0.0
	zPrior = 0.0
	
	file = open(file_name, "w")
	
	if (relCoord_TOG):
		file.write("( Using relative coordinates )\n")
		file.write("G91\n")
		file.write("\n")
	else:
		file.write("G90\n")
		file.write("\n")
	
	if (setZero_TOG):
		file.write("( Set current position as 0,0,0 )\n")
		file.write("G92 X%f Y%f Z%f\n" % (0.0, 0.0, 0.0))
		file.write("\n")
	
	for mesh in meshes:
		file.write("( %s )\n" % (mesh.name))
		
		edges = list(mesh.getData().edges)
		
		x = mesh.data.verts[edges[0].v1.index][0]
		y = mesh.data.verts[edges[0].v1.index][1]
		z = mesh.data.verts[edges[0].v1.index][2]
		
		x, y, z = applyTrans(x, y, z, mesh)
		
		# find relative coordinates if true
		if (relCoord_TOG):
			xRel = x - xPrior
			yRel = y - yPrior
			zRel = z - zPrior
			xPrior, yPrior, zPrior = x, y, z
			x, y, z = xRel, yRel, zRel
		
		# write positioning code if true
		if (addG0_TOG):
			file.write("G0 X%f\n" % (x))
			file.write("G0 Y%f\n" % (y))
			file.write("G0 Z%f\n" % (z))
			xRel = x - xPrior
			yRel = y - yPrior
			zRel = z - zPrior
			xPrior, yPrior, zPrior = x, y, z
			x, y, z = xRel, yRel, zRel
		
		file.write("G1 F%f X%f Y%f Z%f\n" % (feedRate, x, y, z))
		
		for edge in edges:
			
			x = mesh.data.verts[edge.v2.index][0]
			y = mesh.data.verts[edge.v2.index][1]
			z = mesh.data.verts[edge.v2.index][2]
			
			x, y, z = applyTrans(x, y, z, mesh)
			
			# find relative coordinates if true
			if (relCoord_TOG):
				xRel = x - xPrior
				yRel = y - yPrior
				zRel = z - zPrior
				xPrior, yPrior, zPrior = x, y, z
				x, y, z = xRel, yRel, zRel
			
			file.write("G1 X%f Y%f Z%f\n" % (x, y, z))
		
		file.write("\n")

	# write positioning code if true
	if (addG0_TOG):
		file.write("G0 Z%f\n" % (0.0))
		file.write("G0 Y%f\n" % (0.0))
		file.write("G0 X%f\n" % (0.0))
	
	file.write("M2\n")
	file.close()



def FileSelectorCB(file_name):
	if not file_name.lower().endswith('.ngc'):
		file_name += '.ngc'
	ExportToGcode(file_name)

# handle input events
def event(evt, val):
	# exit when user presses Q
	if evt == Draw.QKEY:
		Draw.Exit()

# text edit events
def textEdit_ev(evt, val):
	global feedRate_TEXT
	
	if evt == feedRate_HDL:
		feedRate_TEXT = val

# handle button events
def button_event(evt):
	global relCoord_TOG
	global setZero_TOG
	global addG0_TOG
	
	if evt == relCoord_HDL:
		relCoord_TOG = 1^relCoord_TOG
		
	if evt == setZero_HDL:
		setZero_TOG = 1^setZero_TOG
		
	if evt == addG0_HDL:
		addG0_TOG = 1^addG0_TOG
		
	if evt == blendDir_HDL:
		ExportToGcode(sys.makename(ext='.ngc'))
	
	if evt == chooseDir_HDL:
		Window.FileSelector(FileSelectorCB, "Export to g-code", sys.makename(ext='.ngc'))

	if evt == exit_HDL:
		Draw.Exit()
	


# draw to screen
def gui():
	global relCoord_TOG
	global setZero_TOG
	global addG0_TOG
	global feedRate_TEXT
	
	
	BGL.glClearColor(0.72,0.7,0.7,1)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

	BGL.glColor3f(0.25,0.25,0.25)
	
	
	x = 10
	y = 5
	Draw.Button("Exit", exit_HDL, x, y, 155, 25, "End this python script.")

	y += 30
	Draw.Button("Choose a directory...", chooseDir_HDL, x, y, 155, 25, "Choose a directory to save the g-code.")
	
	y += 30
	Draw.Button("Save to .blend file path", blendDir_HDL, x, y, 155, 25, "Save g-code in the same directory as this .blend file.")

	y += 30
	BGL.glRasterPos2i(x, y)
	Draw.Text("EXPORT TO G-CODE")
	
	y += 20
	ret = Draw.String("Feed Rate:", feedRate_HDL, x, y, 155, 25, feedRate_TEXT, 9, "Feed rate to use for 'G1' code.", textEdit_ev)

	y += 30
	Draw.Toggle("Add 'G0' positioning code", addG0_HDL, x, y, 155, 20, addG0_TOG, "Add extra 'G0' code at the start and end of each path.")

	y += 25
	Draw.Toggle("Add set zero code", setZero_HDL, x, y, 155, 20, setZero_TOG, "Add 'G92' to set current position to 0,0,0.")
	
	y += 25
	Draw.Toggle("Use relative coordinates", relCoord_HDL, x, y, 155, 20, relCoord_TOG, "Use relative instead of absolute coordinates.")
	
	
	y = 90
	BGL.glRasterPos2i(180, y)
	Draw.Text("Note: This program exports 'mesh' vertex lines to g-code not 'paths'.")
	y -= 15
	BGL.glRasterPos2i(180, y)
	Draw.Text("It might be a good idea to use \"reorder_vertex_line.py\" before exporting.")
	y -= 15
	BGL.glRasterPos2i(180, y)
	Draw.Text("Use \"reorder_vertex_line.py\" to untangle the vertex sequence and give a starting point.")


# registering the 3 callbacks
Draw.Register(gui, event, button_event)
