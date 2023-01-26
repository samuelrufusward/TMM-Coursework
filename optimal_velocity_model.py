import random
import pygame
import numpy as np
import time

pygame.init()

# Set up the drawing window
screenWidth = 1000
screenLength = 500
screen = pygame.display.set_mode([screenWidth, screenLength])


def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key


class create_car:

    def __init__(self, x_pos=0, y_pos=255):
        self.type = "car"
        self.v_ideal = 10 + random.randint(-2, 2)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.d_c = 8 # car length in pixels
        self.v = 10 # car velocity
        self.tau = 5
        self.color = (0, 0, 255) # color to display car as
        self.id = time.time() # unique id

class create_bicycle:

    def __init__(self, x_pos=0, y_pos=230):
        self.type = "bike"
        self.v_ideal = 8 + random.randint(-1, 1)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.d_c = 4 # bike length in pixels
        self.v = 8
        self.tau = 3
        self.color = (255, 0, 0) # color to display bike as
        self.id  = time.time() # unique id


def run_single_lane_sim(tmax=500):
    dt = 0.1
    t = 0

    # Font to display flow rate
    font = pygame.font.SysFont('chalkduster.ttf', 30)

    car_spawn_rate = 0.01
    bike_spawn_rate = 0.005

    counter = 0

    # Initiate with some vehicles
    cars = [create_car(x_pos=50)]
    bikes = [create_bicycle(x_pos=140, y_pos=255)]

    # Create list of all vehicles on the road
    vehicles = cars + bikes

    running = True
    while running:

        # Fill the background with white
        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (0, 0, 0), (0, 235), (1000, 235))
        pygame.draw.line(screen, (0, 0, 0), (0, 275), (1000, 275))

        # Randomly spawn cars
        if random.random() < car_spawn_rate:
            # Get list of all cars
            cars = [vehicle for vehicle in vehicles if vehicle.type == "car"]
            # Check to see if space at start of road
            if not (True in (c.x_pos < c.d_c for c in cars)):
                vehicles.append(create_car(x_pos=0, y_pos=255))
        # Randomly spawn bikes
        if random.random() < bike_spawn_rate:
            bikes = [vehicle for vehicle in vehicles if vehicle.type == "bike"]
            # Check to see if space at start of road
            if not (True in (c.x_pos < c.d_c for c in bikes)):
                vehicles.append(create_bicycle(x_pos=0, y_pos=255))

        # Iterate through vehicles and update positions/ speeds
        for vehicle in vehicles:
            # Calculate relative distance between vehicles, only keeping positive distances
            relative_dists = {str(other_vehicle.type): other_vehicle.x_pos - vehicle.x_pos for other_vehicle in vehicles
                              if other_vehicle.x_pos - vehicle.x_pos > 0}

            # Car in front does not have to consider slowing down for other cars
            if len(relative_dists) > 0:
                # Get distance to vehicle in front
                d_alpha = min(list(relative_dists.values()))
                # Get type of vehicle in front
                alpha_type = get_key(relative_dists, d_alpha)

                # Define car behaviours
                if vehicle.type == "car":
                    # If car in front of car
                    if alpha_type == "car":
                        v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                        acc = (v_e - vehicle.v) / vehicle.tau
                        vehicle.v += dt * acc
                    # If bike in front of car
                    if alpha_type == "bike":
                        v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                        acc = (v_e - vehicle.v) / (0.5 * vehicle.tau)
                        vehicle.v += dt * acc

                # Define bike behaviours
                if vehicle.type == "bike":
                    # If car in front of bike
                    if alpha_type == "car":
                        v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                        acc = (v_e - vehicle.v) / vehicle.tau
                        vehicle.v += dt * acc
                    # If bike in front of bike
                    if alpha_type == "bike":
                        v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                        acc = (v_e - vehicle.v) / (2 * vehicle.tau)
                        vehicle.v += dt * acc

            else:
                # If no car in front then dist_infront is infinite
                d_alpha = np.inf
                v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                acc = (v_e - vehicle.v) / vehicle.tau
                vehicle.v += dt * acc

            # Update position
            vehicle.x_pos += vehicle.v * dt

            # Draw a solid blue circle in the center
            pygame.draw.circle(screen, vehicle.color, (vehicle.x_pos, vehicle.y_pos), vehicle.d_c)

            # Count vehicles that have fully traversed road
            if vehicle.x_pos > screenWidth:
                counter += 1
                for i, o in enumerate(vehicles):
                    if o.id == vehicle.id:
                        del vehicles[i]
                        break

        t += dt
        if t > tmax:
            running = False

        avg_flow = round(counter / t, 2)

        img = font.render("Average flow: "+str(avg_flow), True, (0, 0, 0))
        screen.blit(img, (20, 20))
        pygame.display.update()
        pygame.time.wait(10)


def run_two_lane_sim(tmax=500):

    dt = 0.1
    t = 0

    # Font to display average flow
    font = pygame.font.SysFont('chalkduster.ttf', 30)

    car_spawn_rate = 0.01
    bike_spawn_rate = 0.005

    counter = 0

    # Initiate with some vehicles
    cars = [create_car(x_pos=50), create_car(x_pos=100)]
    bikes = [create_bicycle(x_pos=140, y_pos=230)]

    # Create list of all vehicles on the road
    vehicles = cars + bikes

    running = True
    while running:

        # Fill the background with white
        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (0, 0, 0), (0, 220), (1000, 220))
        pygame.draw.line(screen, (0, 0, 0), (0, 240), (1000, 240))
        pygame.draw.line(screen, (0, 0, 0), (0, 270), (1000, 270))

        # Randomly spawn cars
        if random.random() < car_spawn_rate:
            # Get list of all cars
            cars = [vehicle for vehicle in vehicles if vehicle.type == "car"]
            # Check to see if space at start of road
            if not (True in (c.x_pos < c.d_c for c in cars)):
                vehicles.append(create_car(x_pos=0, y_pos=255))
        # Randomly spawn bikes
        if random.random() < bike_spawn_rate:
            bikes = [vehicle for vehicle in vehicles if vehicle.type == "bike"]
            # Check to see if space at start of road
            if not (True in (c.x_pos < c.d_c for c in bikes)):
                vehicles.append(create_bicycle(x_pos=0, y_pos=230))

        # Iterate through vehicles and update positions/ speeds
        for vehicle in vehicles:
            # Calculate relative distance between vehicles, only keeping positive distances (and only considering same
            # vehicle types as they have separate lanes and therefore do not affect each other's speed)
            relative_dists = {str(other_vehicle.type): other_vehicle.x_pos - vehicle.x_pos for other_vehicle in vehicles
                              if other_vehicle.x_pos - vehicle.x_pos > 0 and vehicle.type == other_vehicle.type}

            # Car in front does not have to consider slowing down for other cars
            if len(relative_dists) > 0:
                # Get distance to vehicle in front
                d_alpha = min(list(relative_dists.values())) - vehicle.d_c

                v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                acc = (v_e - vehicle.v) / vehicle.tau
                vehicle.v += dt * acc

            else:
                # If no car in front then dist_infront is infinite
                d_alpha = np.inf
                v_e = vehicle.v_ideal / 2 * (np.tanh(d_alpha - vehicle.d_c) + np.tanh(vehicle.d_c))
                acc = (v_e - vehicle.v) / vehicle.tau
                vehicle.v += dt * acc

            # Update position
            vehicle.x_pos += vehicle.v * dt

            # Draw a solid blue circle in the center
            pygame.draw.circle(screen, vehicle.color, (vehicle.x_pos, vehicle.y_pos), vehicle.d_c)

            # Count vehicles that have fully traversed road
            if vehicle.x_pos > screenWidth:
                counter += 1
                # remove vehicle
                for i, o in enumerate(vehicles):
                    if o.id == vehicle.id:
                        del vehicles[i]
                        break

        t += dt
        if t > tmax:
            running = False

        avg_flow = round(counter / t, 2)

        img = font.render("Average flow: "+str(avg_flow), True, (0, 0, 0))
        screen.blit(img, (20, 20))
        pygame.display.update()
        pygame.time.wait(10)


if __name__ == "__main__":
    run_single_lane_sim(tmax=250)
    run_two_lane_sim(tmax=250)
