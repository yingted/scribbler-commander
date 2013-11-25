#!usr/bin/env python
#XXX ^ must change to fit environment
import numpy
from math import hypot
from heapq import *


#grid = [[-1 for i in xrange(10)] for j in xrange(10)]

"""
Returns the equivalent distance between two given points.
Currently assumes equivalent distance is Euclidean norm.

XXX Here is where the obstacle sensor comes in
"""
def cost((x1,y1),(x2,y2)): 
#	return abs(x1-x2) + abs(y1-y2)
	return hypot(x1-x2,y1-y2)

"""
Generates all neighbors of input location.
We use a genexpr to produce neighbors because there may be important 
edge cases best handled before the neighbors are even created

XXX another place the sensors can come in
"""
def neighbors(x,y=None):
  if isinstance(x,tuple): x,y = x[0], x[1]
  yield (x+1, y)
  yield (x-1, y)
	yield (x, y+1)
	yield (x, y-1)


start = (0,0) #XXX
finish = (10,10) #XXX

openset = [(cost(start, finish), start)]
closedset = set([])
camefrom = {}
g_score = {start:0} # best known cost from start
f_score = {start:cost(start,finish)} # estimated total cost to target

"""
Reset the A* search space to do another search
"""
def resetAstar(new_start, new_finish):
	start, finish = new_start, new_finish
	openset = heapify([(cost(start, finish), start)])
	closedset = set([])
	camefrom = {}
	g_score = {start:0} # best known cost from start
	f_score = {start:cost(start,finish)} # estimated total cost to target



# will have to yield some value in between iterations 
# (to pause and allow other calculations)
# but what value would be useful?

# this A* is completely transparent in its workings so it can be 
# interrupted with incomplete path if need be
"""
computes A* over an arbitrary graph generated by neighbors() 
and weighted by cost()
"""
def astar():
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

"""

"""
def trace_path(src, dest):
	path = [dest]
	cur = camefrom[dest]
	while cur != src:
		#print cur
		path.append(cur)
		cur = camefrom[cur]
  return reversed(path)

def findloops(graph):
	for i in graph.keys():
		j = graph[i]
		l = []
		while j in graph.keys():
			if j in l:
				print "AHAHA " + str(l)
				break
			l.append(j)
			j = graph[j]

# testing below
pathfinder = astar()
for i in pathfinder:
#	print i
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


