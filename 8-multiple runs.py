#!/usr/bin/env python
#
# Simpy Example - Multiple simulation runs with different seeds
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random


# Generic helper class to hold information regarding to resource
# This simplifies how we pass information from main program to entity process
class Server(object):
    def __init__(self, env, name, capacity, service_rate):
        self.name = name
        self.env = env
        self.service_rate = service_rate
        self.capacity = capacity
        self.resource = simpy.Resource(env, capacity=capacity)

    def print_stats(self):
        print('\t[{}] {} using, {} in queue'.format(self.name, self.resource.count, len(self.resource.queue)))

    def get_service_time(self):
        return random.expovariate(self.service_rate)


# passenger - Entity Process
# Describe how passenger performs at the ticket office
def passenger(env, name, server):
    print('[{:6.2f}:{}] - arrive at the station'.format(env.now, name))
    with server.resource.request() as request:
        yield request
        print('[{:6.2f}:{}] - begin buying ticket'.format(env.now, name))
        # random service time based on the service rate
        service_time = server.get_service_time()
        yield env.timeout(service_time)
        print('[{:6.2f}:{}] - finish buying ticket'.format(env.now, name))
    print('[{:6.2f}:{}] - depart from station'.format(env.now, name))


# generator - Supporting Process
# Create new passenger and then sleep for random amount of time
def passenger_generator(env, server, arrival_rate):
    i = 0
    while True:
        ename = 'Passenger#{}'.format(i)
        env.process(passenger(env, ename, server))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


# for simplicity, we define arrival and service rate as mean inter-arrival time and mean service time
MEAN_INTER_ARRIVAL_TIME = 5     # 5 time units between arrivals
MEAN_SERVICE_TIME = 8           # 8 time units for each service
SIMULATION_END_TIME = 50

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
service_rate = 1/MEAN_SERVICE_TIME


def model(seed=0):
    print('Running simulation with seed = {}'.format(seed))
    random.seed(seed)
    env = simpy.Environment()
    ticket_office = Server(env, 'office', capacity=1, service_rate=service_rate)
    env.process(passenger_generator(env, ticket_office, arrival_rate))
    env.run(until=SIMULATION_END_TIME)
    print('------------------')

seeds = [1234, 4567, 9721]
for seed in seeds:
    model(seed)