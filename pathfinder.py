import heapq
from math import sqrt

class AdvancedPathFinder:
    @staticmethod
    
    def heuristic(a, b):
        """Euclidean distance heuristic for A* algorithm"""
        return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    @staticmethod
    def find_path(start, end, width, height, hazards):
        """
        Find the safest and shortest path using A* algorithm with hazard avoidance
        """
        
        hazard_map = {}
        hazard_weights = {
            'fire': 3.0, 
            'smoke': 2.0, 
            'blocked': 100.0, 
            'water': 1.5, 
            'chemical': 5.0,
            'structural': 50.0
        }
        
        for hazard in hazards:
            hazard_map[(hazard.x, hazard.y)] = {
                'type': hazard.type,
                'intensity': hazard.intensity
            }

        
        open_set = []
        heapq.heappush(open_set, (0, 0, start, [start]))
        visited = set()
        g_costs = {start: 0}

        while open_set:
            current_f, current_g, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in visited:
                continue
            visited.add(current_pos)

            
            if current_pos == end:
                return path, current_g

           
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                neighbor = (current_pos[0] + dx, current_pos[1] + dy)
                
                
                if (neighbor[0] < 0 or neighbor[0] >= width or 
                    neighbor[1] < 0 or neighbor[1] >= height):
                    continue

               
                move_cost = 1.4 if (dx != 0 and dy != 0) else 1.0
                
                
                hazard_cost = 0
                if neighbor in hazard_map:
                    hazard_data = hazard_map[neighbor]
                   
                    if (hazard_data['type'] == 'blocked' or 
                        hazard_data['intensity'] >= 4 or
                        (hazard_data['type'] == 'structural' and hazard_data['intensity'] >= 2)):
                        continue
                    hazard_cost = hazard_weights.get(hazard_data['type'], 1) * hazard_data['intensity'] * 2
                
                total_cost = current_g + move_cost + hazard_cost

                
                if neighbor not in g_costs or total_cost < g_costs[neighbor]:
                    g_costs[neighbor] = total_cost
                    f_cost = total_cost + AdvancedPathFinder.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_cost, total_cost, neighbor, path + [neighbor]))

        
        return None, float('inf')
