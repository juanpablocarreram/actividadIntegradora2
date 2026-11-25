#TODO Agregar el chequeo de que se escoja la edge mas barata entre la misma ruta de dos mismas ciudades
#TODO Agregar father para el mejor camino

import numpy as np
import sys

class Edge:
    def __init__(self, 
                 from_stop_id,
                 from_stop_name,
                 to_stop_id,
                 to_stop_name,
                 route_id, 
                 route_short_name, 
                 route_long_name, 
                 mean_travel_time_min
                 ):
        self.from_stop_id = from_stop_id
        self.from_stop_name = from_stop_name
        self.to_stop_id = to_stop_id
        self.to_stop_name = to_stop_name
        self.route_id = route_id
        self.route_short_name = route_short_name
        self.route_long_name = route_long_name
        self.mean_travel_time_min = mean_travel_time_min
        self.mean_travel_time_min *=60





class Graph:
    def __init__(self, matrix, edges, cities, name_to_idx, idx_to_name):
        self.original_matrix = np.copy(matrix)
        self.matrix = matrix
        self.edges = edges
        self.cities = cities
        self.name_to_idx = name_to_idx
        self.idx_to_name = idx_to_name
        self.parent = np.full((len(cities), len(cities)), -1, dtype = int)
        self.build_parent()
        self.floyd_war()
        




    def floyd_war(self):
        n = len(self.cities)
        for k in range(n):
            for fr in range(n):
                for tt in range(n):
                    if self.matrix[fr][tt] > self.matrix[fr][k] + self.matrix[k][tt]:
                        self.matrix[fr][tt] = min(self.matrix[fr][tt], self.matrix[fr][k] + self.matrix[k][tt])
                        self.parent[fr][tt] = self.parent[k][tt]


    def build_parent(self):
        n = len(self.cities)
        for i in range(n):
            for j in range(n):
                if i != j and self.matrix[i][j] != np.inf:
                    self.parent[i][j] = i

    def get_path_cost(self, A_, B_):
        A = self.name_to_idx[A_]
        B = self.name_to_idx[B_]
        path_costo = {}
        path = []

        current = B

        path.append(current)


        while(current != A):
            current = self.parent[A][current]
            path.append(current)


        path.reverse()
        for i in range(len(path)):
           path[i] = idx_to_name[path[i]]

        path_costo['p'] = path
        path_costo['c'] = self.matrix[A][B]
        return path_costo


#la matriz de adjacencia
adj_ma = {}
#las edges para guardar toda info
edges = {}
#guardar el numero unico de ciudades
cities = set()
#mapea nombre a un indice
name_to_idx = {}

idx_to_name = {}


with open("metro_cdmx_aristas.csv", mode = 'r') as file:
    i = 0
    flag = False
    for line in file:
        if flag == False:
            flag = True
            continue
        e = line.strip().split(',')
        cities.add(e[1])
        cities.add(e[3])

        # Actualizar el mapa para que cada nombre este mapeado a un numero
        if name_to_idx.get(e[1], -1) == -1:
            name_to_idx[e[1]] = i
            idx_to_name[i] = e[1]
            i+=1

        if name_to_idx.get(e[3], -1) == -1: 
            name_to_idx[e[3]] = i
            idx_to_name[i] = e[3]
            i+=1
        
        
        f = name_to_idx[e[1]]
        to = name_to_idx[e[3]]

        if f not in adj_ma:
            adj_ma[f] = []

        adj_ma[f].append(to)
        #--------------------------------Aca el chequeo---------------------------
        edges[(f, to)] = Edge(e[0], e[1], e[2], e[3], e[4], e[5], e[6], float(e[7]))
file.close()

matrix = np.full((len(cities), len(cities)), np.inf, dtype = float)

for city in cities:
    fr = name_to_idx[city]
    if fr not in adj_ma:
        continue
    for tt in adj_ma[fr]:
        matrix[fr][tt] = edges[(fr,tt)].mean_travel_time_min


g = Graph(matrix, edges, cities, name_to_idx, idx_to_name)


result = g.get_path_cost("Balbuena", "Gómez Farías")
print(result["p"])

