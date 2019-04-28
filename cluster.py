from haversine import haversine
import numpy as np
import random

# inputs[i] = (lat, long)

class Cluster():
    """ inputs:list(tuple)
        fixed_centers:list(tuple) 
        new_centers:list(tuple)
        num_new_centers:int
    """
    
    def __init__(self, inputs,
                 fixed_centers=[],
                 new_centers=[],
                 num_new_centers=2):
        
        self.fixed_centers = fixed_centers
        self.k_num_fixed = len(self.fixed_centers)
        
        if new_centers==[]:
            self.new_centers = random.sample(inputs, num_new_centers)
        else:
            self.new_centers = new_centers
        
        self.centers = self.fixed_centers+self.new_centers
        self.k_num = len(self.centers)
        

    def classify(self, input):
        """Return the index of the cluster closest to the input"""
        return min(range(self.k_num), key=lambda i: haversine(input, self.centers[i]))
        
        
    def train(self, inputs):
        assignments = [None,None]

        while True:
            # Find new assignments
            new_assignments = list(map(self.classify, inputs))

            # If no assignments have changed, we're done.
            if assignments == new_assignments:
                self.cluster_assign={i:a for i,a in zip(inputs,assignments)}
                return         
#             Otherwise keep the new assignments,
            assignments = new_assignments

            for i in range(self.k_num):
                i_points = [p for p, a in zip(inputs, new_assignments) if a == i]
                # avoid divide-by-zero if i_points is empty
                if i_points and i>=self.k_num_fixed:                        
                    self.centers[i] = tuple(np.mean(i_points, axis=0))
        print(self.centers)
            
    def cost(self, data_center_cost=2000):
        """aggregated sum of distances from corresponding cluster centers
        """
        self.total_cluster_cost = 0
        self.cluster_cost={}
        for point, k_num in self.cluster_assign.items():
            self.cluster_cost[point] = haversine(point,self.centers[k_num])
            self.total_cluster_cost += self.cluster_cost[point]
        self.total_center_cost = self.k_num * data_center_cost
        self.total_cost = self.total_center_cost + self.total_cluster_cost


def calculate_sunk_cost(current_cluster, new_cluster):
    """Calculating the sunk cost from expanding to next stage"""
    sunk_cost = 0
    for point, cluster_num in current_cluster.cluster_assign.items():
        #Check if cluster number match with new one
        if current_cluster.cluster_assign[point] != new_cluster.cluster_assign[point]:
            #If not add the old cluster-point cost to sunk cost
            sunk_cost += haversine(point,current_cluster.centers[cluster_num])
    return sunk_cost
    
    
def path_cost(path:list, inputs:list):
    cost = []
    c = None
    old_centers = []
    sunk_cost = 0
    centers=[]
    for k in path:
        if c is not None:
            old_centers = c.centers
            
        c1=Cluster(inputs, 
                   fixed_centers=old_centers,
                   num_new_centers=k)
        c1.train(inputs)
        c1.cost(data_center_cost=2000)
        cost.append(c1.total_cost + sunk_cost)
        centers.append(c1.centers)
        if c is not None:
            sunk_cost += calculate_sunk_cost(c, c1)
        c = c1
    return cost, centers