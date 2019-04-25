#!BPY

"""
Name: 'Reorder Vertex Line'
Blender: 249
Group: 'Mesh'
Tip: 'Reorder vertex lines so they can be used as paths.'
"""

__bpydoc__ = """\
This tool will make it easy to use vertex lines as paths by reording them end to end.

All that is needed is a double indicating the beginning.

Create a double at the beginning of a vertex line by going into "Edit Mode", right clicking a vertex, pressing 'E', and right clicking to let go of the vertex.

Tip: Paths can be converted to edges by holding 'Alt' and pressing 'C' in object mode.

Tip: Doubles can be removed by pressing 'W' and clicking remove doubles in edit mode.

"""



from Blender import *
import bpy



#find path head
def findPathHead(ptsX, ptsY, ptsZ, linesA, linesB):
	
	#find which 2 connected points are in the same location
	noLengthLines = []
	for i in range(0, len(linesA)):
		if ptsX[linesA[i]] == ptsX[linesB[i]]:
			noLengthLines.append(i)
	
	
	#find the connection count for each of the "noLengthLines"
	connectionCnts = [0] * len(noLengthLines)
	for i in range(0, len(noLengthLines)):
		for j in range(0, len(linesA)):
			headLineA = linesA[noLengthLines[i]]
			headLineB = linesB[noLengthLines[i]]
			lineA = linesA[j]
			lineB = linesB[j]
			
			if (headLineA == lineA) or (headLineB == lineB) or (headLineA == lineB) or (headLineB == lineA):
				
				# don't count its self
				if noLengthLines[i] != j:
					connectionCnts[i] += 1;
	
	
	#find the path head
	pathHeadCnt = 0
	for i in range(0, len(noLengthLines)):
		if connectionCnts[i] == 1:
			pathHead = noLengthLines[i]
			pathHeadCnt += 1
	
	#if there is no path head then return -1
	if pathHeadCnt == 0:
		return -1
	
	return pathHead



def reorderPathVerts(ptsX, ptsY, ptsZ, linesA, linesB, pathHead):
	linesCnt = len(linesA)
	roCnt = 0
	roLinesA = []
	roLinesB = []
	usedLines = [0] * linesCnt
	loc = pathHead
	
	roLinesA.append(linesA[loc])
	roLinesB.append(linesB[loc])
	usedLines[loc] = 1
	roCnt += 1
	priorLoc = loc
	loc += 1
	foundConnection = 1
	
	#repeat until all possible connections are found
	while (foundConnection):
		
		#reset
		foundConnection = 0
		
		if loc == -1:
			loc += 2
		
		#move location forwards and find connected lines
		while loc < linesCnt:
			if usedLines[loc] != 1:
				if (linesA[loc] == linesA[priorLoc]) or (linesB[loc] == linesB[priorLoc]) or (linesA[loc] == linesB[priorLoc]) or (linesB[loc] == linesA[priorLoc]):
					roLinesA.append(linesA[loc])
					roLinesB.append(linesB[loc])
					usedLines[loc] = 1
					roCnt += 1
					priorLoc = loc
					foundConnection = 1
			
			loc += 1
		
		if loc == linesCnt:
			loc -= 2
		
		#move location backwards and find connected lines
		while loc >= 0:
			if usedLines[loc] != 1:
				if (linesA[loc] == linesA[priorLoc]) or (linesB[loc] == linesB[priorLoc]) or (linesA[loc] == linesB[priorLoc]) or (linesB[loc] == linesA[priorLoc]):
					roLinesA.append(linesA[loc])
					roLinesB.append(linesB[loc])
					usedLines[loc] = 1
					roCnt += 1
					priorLoc = loc
					foundConnection = 1
			
			loc -= 1
	
	#switch line directions if going the wrong way
	if (linesCnt >= 2):
		if (roLinesA[0] == roLinesA[1]) or (roLinesA[0] == roLinesB[1]):
			roLinesA[0], roLinesB[0] = roLinesB[0], roLinesA[0]
	
	for i in range(1, roCnt):
		if roLinesA[i] != roLinesB[i-1]:
			roLinesA[i], roLinesB[i] = roLinesB[i], roLinesA[i]
	
	return roLinesA, roLinesB



def mainFunc():
	
	scene = Scene.GetCurrent()
	ob = scene.objects.active
	
	if ob == None:
		return

	if ob.type != "Mesh":
		return

	xPts = []
	yPts = []
	zPts = []
	for i in range(0, len(ob.data.verts)):
		xPts.append(ob.data.verts[i][0])
		yPts.append(ob.data.verts[i][1])
		zPts.append(ob.data.verts[i][2])

	linesA = []
	linesB = []
	for edges in ob.getData().edges:
		linesA.append(edges.v1.index)
		linesB.append(edges.v2.index)


	pathHead = findPathHead(xPts, yPts, zPts, linesA, linesB)
	
	
	if pathHead == -1:
		Draw.PupMenu("Create double at beginning (Edit Mode: RMB, Press 'E', RMB)")
		return


	roLinesA, roLinesB = reorderPathVerts(xPts, yPts, zPts, linesA, linesB, pathHead)

	
	verts = []
	edges = []
	edgesCnt = len(roLinesA)
	
	for i in range(0, edgesCnt):
		verts.append((xPts[roLinesB[i]], yPts[roLinesB[i]], zPts[roLinesB[i]]))

	for i in range(1, edgesCnt):
		edges.append((i-1, i))


	editmode = Window.EditMode()
	if editmode: Window.EditMode(0)
	
	roChg = bpy.data.meshes.new('roEdges') # create a new mesh
	roChg.verts.extend(verts)
	roChg.edges.extend(edges)
	
	# link mesh to object
	ob.link(roChg)
	ob.data.update()
	
	if editmode: Window.EditMode(1)
	Window.RedrawAll()


mainFunc()