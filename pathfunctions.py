"""
Hammad Jutt, Section EB1
Shivansh Singla, Seciton EB1
"""


from graph_v2 import Graph
import csv
import heapq
import queue

def read_directed_city_graph(filename):
	"""
	Reads the data in a comma-separated values (CSV) file that describes 
	a city's road network, and returns an instance of the Graph class 
	corresponding to the directed version of that road network.
	"""
	vertices = set()   #initialize set of vertices
	edges = []         #initialize list of edges
	data = open(filename, "r") #open the csv file
	reader = csv.reader(data) #create object that maps csv info to a dictionary

	for row in reader:
		if row[0] == 'V':
			vertices.add(row[1]) #add the ID of the vertex to set of vertices
		if row[0] == 'E':
			edges.append((row[1],row[2])) #add a tuple describing the edge to list of edges

	return Graph(vertices, edges)

def read_position(filename):
	"""
	Reads the data in a comma-separated values (CSV) file that describes 
	a city's road network, and returns a dictionary corresponding to the 
	latitude and longitude's of each vertex in the CSV file
	"""
	global position
	position = {}
	
	data = open(filename, "r") #open the csv file
	reader = csv.reader(data) #create object that maps csv info to a dictionary

	for row in reader:
		if row[0] == 'V':
			vertexid = row[1]
			latitude = int(float(row[2])*100000)
			longitude = int(float(row[3])*100000)
			position[vertexid] = [latitude, longitude]

def cost_distance(e):
	"""
	Computes and returns the straight-line distance between the two
	vertices at the endpoints of the edge e.
	Args:
	e: An indexable container where e[0] is the vertex id for the
	starting vertex of the edge, and e[1] is the vertex id for the
	ending vertex of the edge.
	Returns:
	numeric value: the distance between the two vertices.
	"""
	x = ((position[e[0]][0])-(position[e[1]][0]))**2 #(latitude of v1 - latitude of v2) ^ 2
	y = ((position[e[0]][1])-(position[e[1]][1]))**2 #(longitude of v1 - longitude of v2) ^ 2
	distance = (x + y)**(1/2) #calculate euclidian distance
	
	return int(distance*100000)

def closest_vertex(graph, lat, lon):
	"""
	Find and return the nearest vertex in graph corresponding to lat and lon
	"""

	dist = {}
	distheap = []

	for vertex in graph.vertices():
		x = (position[vertex][0] - lat)**2
		y = (position[vertex][1] - lon)**2
		z = (x + y)**(1/2)
		dist[z] = vertex

	for key in dist:
		heapq.heappush(distheap, key)

	lowestdist = heapq.heappop(distheap)
	closestV = dist[lowestdist]
	
	return closestV

def least_cost_path(graph, start, dest, cost):
	"""
	Find and return the least cost path in graph from start vertex to dest vertex.
	Efficiency: If E is the number of edges, the run-time is
	  O( E log(E) ).
	Args:
	  graph (Graph): The digraph defining the edges between the
		vertices.
	  start: The vertex where the path starts. It is assumed
		that start is a vertex of graph.
	  dest:  The vertex where the path ends. It is assumed
		that start is a vertex of graph.
	  cost:  A function, taking a single edge as a parameter and
		returning the cost of the edge. For its interface,
		see the definition of cost_distance.
	Returns:
	  list: A potentially empty list (if no path can be found) of
		the vertices in the graph. If there was a path, the first
		vertex is always start, the last is always dest in the list.
		Any two consecutive vertices correspond to some
		edge in graph.
	>>> graph = Graph({1,2,3,4,5,6}, [(1,2), (1,3), (1,6), (2,1),
			(2,3), (2,4), (3,1), (3,2), (3,4), (3,6), (4,2), (4,3),
			(4,5), (5,4), (5,6), (6,1), (6,3), (6,5)])
	>>> weights = {(1,2): 7, (1,3):9, (1,6):14, (2,1):7, (2,3):10,
			(2,4):15, (3,1):9, (3,2):10, (3,4):11, (3,6):2,
			(4,2):15, (4,3):11, (4,5):6, (5,4):6, (5,6):9, (6,1):14,
			(6,3):2, (6,5):9}
	>>> cost = lambda e: weights.get(e, float("inf"))
	>>> least_cost_path(graph, 1,5, cost)
	[1, 3, 6, 5]
	"""

	 
	R = {} #empty dictionary to hold reached vertices
	distances = {} #empty dictionary to hold distances for each vertex

	PQ = queue.PriorityQueue() #priority queue to hold distances to each neighbor
	PQ.put(((start, start), 0)) #put starting vertex with distance 0 into queue

	#get the closest vertex to the current vertex that hasnt been reached yet
	#and add it to reached and set it to the current vertex
	while not PQ.empty():
		node = PQ.get()
		prev = node[0][0]
		curr = node[0][1]
		val = node[1]

		if curr not in R:
			R[curr] = prev
			distances[curr] = val
			for succ in graph.neighbours(curr):
				PQ.put(((curr, succ), val + cost_distance((curr, succ))))
			if curr == dest:
				break

	#return an empty list if the destination vertex cant be reached
	if dest not in R:
		return []

	#map the path taken to get to destination into a list
	path = [dest]
	curr = dest
	while curr != start:
		curr = R[curr]
		path.append(curr)
	path.reverse()

	return path

