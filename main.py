import sys
import utility as utility
import loader as loader
import numpy as np


def main():
    # Paths to the data and solution files.
    vrp_file = "data/n32-k5.vrp"  # "data/n80-k10.vrp"
    sol_file = "data/n32-k5.sol"  # "data/n80-k10.sol"

    # Loading the VRP data file.
    px, py, demand, capacity, depot = loader.load_data(vrp_file)

    # Displaying to console the distance and visualizing the optimal VRP solution.
    vrp_best_sol = loader.load_solution(sol_file)
    print(vrp_best_sol)
    best_distance = utility.calculate_total_distance(vrp_best_sol, px, py, depot)
    print("Best VRP Distance:", best_distance)
    utility.visualise_solution(vrp_best_sol, px, py, depot, "Optimal Solution")

    # Executing and visualizing the nearest neighbour VRP heuristic.
    # Uncomment it to do your assignment!

    nnh_solution = nearest_neighbour_heuristic(px, py, demand, capacity, depot)
    print(nnh_solution)
    nnh_distance = utility.calculate_total_distance(nnh_solution, px, py, depot)
    print("Nearest Neighbour VRP Heuristic Distance:", nnh_distance)
    utility.visualise_solution(nnh_solution, px, py, depot, "Nearest Neighbour Heuristic")

    # Executing and visualizing the saving VRP heuristic.
    # Uncomment it to do your assignment!

    sh_solution = savings_heuristic(px, py, demand, capacity, depot)
    print(sh_solution)
    sh_distance = utility.calculate_total_distance(sh_solution, px, py, depot)
    print("Saving VRP Heuristic Distance:", sh_distance)
    utility.visualise_solution(sh_solution, px, py, depot, "Savings Heuristic")


def nearest_neighbour_heuristic(px, py, demand, capacity, depot):
    """
    Algorithm for the nearest neighbour heuristic to generate VRP solutions.

    :param px: List of X coordinates for each node.
    :param py: List of Y coordinates for each node.
    :param demand: List of each nodes demand.
    :param capacity: Vehicle carrying capacity.
    :param depot: Depot.
    :return: List of vehicle routes (tours).
    """

    routes = []

    unvisited = list(range(0, len(px)))
    unvisited.remove(depot)

    current_capacity = 0

    current_node = depot
    nearest = -1
    min_dist = sys.maxsize

    route = []

    while len(unvisited) != 0:
        if current_capacity < capacity:
            for i in unvisited:
                dist = utility.calculate_euclidean_distance(px, py, current_node, i)
                if dist < min_dist and (current_capacity + demand[i]) <= capacity:
                    nearest = i
                    min_dist = dist
        if nearest == -1:
            routes.append(route)
            route = []
            current_node = depot
            min_dist = sys.maxsize
            current_capacity = 0
        else:
            route.append(nearest)
            current_node = nearest
            unvisited.remove(nearest)
            current_capacity += demand[nearest]
            nearest = -1
            min_dist = sys.maxsize

    routes.append(route)

    return routes


def savings_heuristic(px, py, demand, capacity, depot):
    """
    Algorithm for Implementing the savings heuristic to generate VRP solutions.

    :param px: List of X coordinates for each node.
    :param py: List of Y coordinates for each node.
    :param demand: List of each nodes demand.
    :param capacity: Vehicle carrying capacity.
    :param depot: Depot.
    :return: List of vehicle routes (tours).
    """

    routes = []
    demands = []

    fully_merged = False

    for i in range(1, len(px)):
        route = []
        route.append(i)
        routes.append(route)
        demands.append(demand[i])

    while not fully_merged:
        best_first_route = None
        best_second_route = None
        best_saving = 0
        for route in routes:
            for other_route in routes:
                if other_route != route and demands[routes.index(route)] + demands[routes.index(other_route)] <= capacity:
                    for i in range(4):

                        if i == 0: # head to tail route then other route
                            first_route = route
                            second_route = other_route
                        elif i == 1: # head to tail other route then route
                            first_route = other_route
                            second_route = route
                        elif i == 2: # head to head
                            reverse_route = route.copy()
                            first_route = reverse_route[::-1]
                            second_route = other_route
                        else: # tail to tail
                            reverse_route = route.copy()
                            first_route = other_route
                            second_route = reverse_route[::-1]

                        first_node = first_route[-1]
                        second_node = second_route[0]

                        saving = calculate_saving(first_node, second_node, px, py, depot)

                        if saving > best_saving:
                            best_saving = saving
                            best_first_route = first_route
                            best_second_route = second_route

        if best_first_route == None and best_second_route == None and best_saving == 0:
            fully_merged = True
        else:
            routes, demands = merge_routes(best_first_route, best_second_route, routes, demands)

    return routes


def calculate_saving(first_node, second_node, px, py, depot):

    return utility.calculate_euclidean_distance(px, py, first_node, depot) \
            + utility.calculate_euclidean_distance(px, py, depot, second_node) \
            - utility.calculate_euclidean_distance(px, py, first_node, second_node)


def merge_routes(best_first_route, best_second_route, routes, demands):

    if best_first_route not in routes:
        to_reverse = best_first_route.copy()
        first = to_reverse[::-1]
    else:
        first = best_first_route

    if best_second_route not in routes:
        to_reverse = best_second_route.copy()
        second = to_reverse[::-1]
    else:
        second = best_second_route

    index1 = routes.index(first)
    index2 = routes.index(second)

    new_route = []

    for node in best_first_route:
        new_route.append(node)
    for node in best_second_route:
        new_route.append(node)

    new_demand = demands[index1] + demands[index2]

    routes.remove(first)
    routes.remove(second)
    if index1 < index2:
        demands.pop(index2)
        demands.pop(index1)
    else:
        demands.pop(index1)
        demands.pop(index2)
    routes.append(new_route)
    demands.append(new_demand)

    return routes, demands


if __name__ == '__main__':
    main()
