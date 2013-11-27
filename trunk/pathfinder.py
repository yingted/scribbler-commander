#!/usr/bin/env python
import numpy # currently unused, should be used for optimization
from math import hypot
from heapq import *
import threading # might not be necessary if thread not started here
import util # needed for state object

def set_target(xy):
	'''sets the target to x, y
	returns immediately'''
	newtarget = xy
	pass

# NOTES:
# - start `pathfinder_thread` in a thread, process or whatever
# - then use `set_target` to set the target of the A*
#
# - `cost` and `neighbors` do special things based on the map data -- 
#	that stuff still needs integration, currently each function is a 
#	dummy for a blank, infinitely large 8-connected square grid
#

"""
newtarget is None when there is no A* to do, 
is equal to finish when the A* is being done,
and is not equal to finish when the A* has to 
be restarted with a new target.
"""
newtarget = None

start = (0,0) # XXX Must get from state
finish = (10,10) # XXX Must get from state

# XXX all of these should probably be stored in state
openset = [(cost(start, finish), start)]
closedset = set([])
camefrom = {}
g_score = {start:0} # best known cost from start
f_score = {start:cost(start,finish)} # estimated total cost to target

# probably too ugly of a hack to work
def nullGenerator():
	raise StopIteration

def resetAstar(new_start, new_finish):
	"""
	Reset the A* search space to do a search from given start position 
	to given end position, return the generator object
	"""
	if new_finish is None or new_start is None:
		return nullGenerator # stops iterating immediately
    start, finish = new_start, new_finish
    openset = heapify([(cost(start, finish), start)])
    closedset = set([])
    camefrom = {}
    g_score = {start:0} # best known cost from start
    f_score = {start:cost(start,finish)} # estimated total cost to target
    return astar().next # returns generator's next function

def pathfinder_thread():
	"""The thread that continually waits on target change and 
	runs A* whenever a new target is set"""
	iterastar = nullGenerator
	while True:
		# stuff happens
		if newtarget != finish:
			start = (0,0) # XXX GET CURRENT POSITION FROM STATE
			# is it start = util.state["position"] ? probably.
			# we currently scrap partial paths, which might be useful, 
			# but that's okay.
			iterastar = resetAstar(start,newtarget)
		if newtarget != None:
			try:
				# step once thru A*
				iterastar()
			except StopIteration:
				# A* finished, so we update state
				util.state["pathpoints"] = trace_path(start, finish)
				newtarget = None

def cost((x1,y1),(x2,y2)): 
	"""
	Returns the equivalent distance between two given points.
	Currently assumes equivalent distance is Euclidean norm.

	XXX Here is where the obstacle sensor comes in
	"""
	# XXX needs to check obstacle probability to evaluate cost
    return hypot(x1-x2,y1-y2)


# XXX Needs updating to use real coords
neighbor_step = 1

def neighbors(x,y=None):
	"""
	Generates all neighbors of input location.
	We use a genexpr to produce neighbors because there may be important 
	edge cases best handled before the neighbors are even created

	XXX another place the sensors can come in
	"""
	if isinstance(x,tuple): x,y = x[0], x[1]
    # XXX needs to check bounds to decide which neighbors get yielded
    
    yield (x + neighbor_step, y - neighbor_step)
    yield (x + neighbor_step, y)
    
    yield (x + neighbor_step,y + neighbor_step)
    yield (x, y + neighbor_step)
    
    yield (x - neighbor_step, y + neighbor_step)
    yield (x - neighbor_step, y)
    
    yield (x - neighbor_step, y - neighbor_step)
    yield (x, y - neighbor_step)


# will have to yield some value in between iterations 
# (to pause and allow other calculations)
# but what value would be useful?

# this A* is completely transparent in its workings so it can be 
# interrupted with incomplete path if need be

def astar():
    """
	computes A* over an arbitrary graph generated by neighbors() 
	and weighted by cost()
	"""
	done = 0
    while openset and not done:
        current = heappop(openset)
        yield current # produces current best target, and distance to final target
        if current[1] == finish:
            #DONE DONE DONE
            done = True
            continue
            #break
        closedset.add(current[1])
        for i in neighbors(current[1]):
            tentative_g = g_score[current[1]] + cost(current[1],i)
            tentative_f = tentative_g + cost(i,finish)
            if i in closedset and tentative_f >= f_score[i]:
                continue
            if i not in openset or tentative_f < f_score[i]:
                camefrom[i] = current[1]
                g_score[i] = tentative_g
                f_score[i] = tentative_f
                if i not in openset:
                    heappush(openset, (tentative_f,i))
    
    pass #FAIL

def trace_path(src, dest):
	"""
	Iterate backwards from dest, following came-from links until 
	reaching src. Returns list of points on the path, starting at src, 
	ending at dest.
	"""
    path = [dest]
    cur = camefrom[dest]
    while cur != src:
        #print cur
        path.append(cur)
        cur = camefrom[cur]
    return list(reversed(path))

def findloops(graph):
	"""
	A utility function for checking for problems in an A* came-from tree
	"""
    for i in graph.keys():
        j = graph[i]
        l = []
        while j in graph.keys():
            if j in l:
                print "AHAHA " + str(l)
                break
            l.append(j)
            j = graph[j]

"""
pathfinder = astar()
for i in pathfinder:
#   print i
    pass
print "##"
for i in trace_path(start, finish):
    print i
print "###"
#print camefrom[(4,3)]
#print camefrom[(4,4)]
#print camefrom[(0,0)]
print "####"
findloops(camefrom)
"""
