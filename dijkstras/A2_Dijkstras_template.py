# Assignment 2 Dijkstra's Algorithm

# Author: Dr. Neha Karanjkar


import random
import math
import os
import numpy as np
from math import inf as INF # positive infinity


def generate_a_random_undirected_graph(num_nodes):
	""" 
	A function that randomly generates a graph
    given the number of nodes, and returns 
	the Adjacency matrix with edge costs.
	The edge cost is INF (infinity) if there is 
	no direct edge between two nodes
	"""

	G = [[] for i in range(num_nodes)]
	for i in range(num_nodes):
		for j in range(num_nodes):
			if(i==j):
				edge_cost=0
			elif (j<i):
				edge_cost=G[j][i]
			else:
				if (random.random()<0.5):
					edge_cost=INF
				else:
					edge_cost=random.randint(1,10)
			G[i].append(edge_cost)
	return G



def visualize_graph(G, show_edge_labels=False, node_labels=None):
	"""
	Given the graph connectivity matrix G,
	this function generates a visualization of the
	graph as a ".dot" file.
	
	NOTE: the ".dot" file can be viewed in a browser (http://www.webgraphviz.com/)
	OR converted into a pdf file using graphviz by running the command
		dot -Tpdf dot_file.dot -o plot.pdf
	"""
	if node_labels==None:
		node_labels = [str(i) for i in range(len(G))]
	with open("dot_file.dot","w") as f:
		print("graph  {", file=f)
		for i in range(len(G)): print(node_labels[i]+";",file=f)
		for i in range(len(G)): 
			for j in range(len(G)):
				if (G[i][j] != INF and j>i): 
					if show_edge_labels:
						print(f"{node_labels[i]} -- {node_labels[j]}  [weight={G[i][j]}, label=\"{G[i][j]}\"];",file=f)
					else:
						print(f"{node_labels[i]} -- {node_labels[j]}  [weight={G[i][j]}];",file=f)
		print("}",file=f)
	# ---- optional-----
	os.system("dot -Tpdf dot_file.dot -o plot.pdf")
	#-------------------

def minDistance(dist, sptSet):
    # Initialize minimum distance for next node
        min = 1e7

        # Search not nearest vertex not in the
        # shortest path tree

        for v in range(len(G)):
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v
        return min_index


def find_shortest_paths(source_node, graph, node_labels=None):
	
	# Find Shortest paths from source_node to 
	# all other nodes using Dijkstra's algorithm.
	#
	#
	# Returns lists D and p for every node v
	#
	# where D(v): shortest distance from source to v
	#   and p(v): previous node to v on the shortest path 
	# If v is not reachable from source, D(v)=INF and p(v)=None


	# function to return the label of a node(number)
	def label(node):
		if node_labels and (node!=None):
			return node_labels[node]
		else:
			return str(node)

	dist = [1e7] * len(G)
	dist[source_node] = 0
	sptSet = [False] * len(G)

	for cout in range(len(G)):
            # Pick the minimum distance vertex from
            # the set of vertices not yet processed.
            # u is always equal to source_node in first iteration

		u = minDistance(dist, sptSet)
            # Put the minimum distance vertex in the
            # shortest path tree

		sptSet[u] = True
            # Update dist value of the adjacent vertices
            # of the picked vertex only if the current
            # distance is greater than new distance and
            # the vertex in not in the shortest path tree
		donelist = []
		dict = {0 :'u',1 :'v',2:'w',3:'x',4:'y',5:'z'}
		for i in range(len(G)):
				if sptSet[i] == True :
					donelist.append(dict[i])

		
		for v in range(len(G)):
			if (graph[u][v] > 0 and
				sptSet[v] == False and
				dist[v] > dist[u] + graph[u][v]):
				dist[v] = dist[u] + graph[u][v]
			print(v+1," ",dist[0]," ",dist[1]," ",dist[2]," ",dist[3]," ",dist[4]," ",dist[5], donelist)
	
	return dist 
	
	# ---------------

    
	


#     u   v   w   x   y   z
G = [[0,  2,  5,  1,  INF,INF], #u
	 [2,  0,  3,  2,  INF,INF], #v
	 [5,  3,  0,  3,  1,  5  ], #w
	 [1,  2,  3,  0,  1,  INF], #x
	 [INF,INF,1,  1,  0,  2  ], #y
	 [INF,INF,5,  INF,2,  0  ]] #z

G = generate_a_random_undirected_graph(6)

print(np.matrix(G))
node_labels = ['u','v','w','x','y','z']
visualize_graph(G,show_edge_labels=True, node_labels=node_labels)
for s in range(len(G)):
	
	print("-------------------------------")
	print("Source node: ",s)
	print("Step D(u),p(u)   D(v),p(v)   D(w),p(w)   D(x),p(x)   D(y),p(y)   D(z),p(z)   Done Nodes ")
	find_shortest_paths(source_node=s, graph=G,node_labels=node_labels)

exit()



