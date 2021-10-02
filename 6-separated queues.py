#!/usr/bin/env python
#
# Simpy Example - Multiple servers with separated queues
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


def find_shortest_queues(servers):
    min_n = -1
    min_s = None
    for s in servers:
        n_in_server = s.resource.count + len(s.resource.queue)
        if n_in_server < min_n or min_n == -1:
            min_n = n_in_server
            min_s = s
    return min_s, min_n


# passenger - Entity Process
# Describe how passenger performs at the ticket office
def passenger(env, name, servers):
    print('[{:6.2f}:{}] - arrive at the station'.format(env.now, name))
    # passenger will choose a server with the shorest queue
    server, num_in_server = find_shortest_queues(servers)
    for s in servers:
        s.print_stats()
    print('[{:6.2f}:{}] - chooses {} with {} pax in the office'.format(env.now, name, server.name, num_in_server))
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
def passenger_generator(env, servers, arrival_rate):
    i = 0
    while True:
        ename = 'Passenger#{}'.format(i)
        env.process(passenger(env, ename, servers))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


# for simplicity, we define arrival and service rate as mean inter-arrival time and mean service time
MEAN_INTER_ARRIVAL_TIME = 5     # 5 time units between arrivals
MEAN_SERVICE_TIME = 8           # 8 time units for each service
SIMULATION_END_TIME = 50

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
service_rate = 1/MEAN_SERVICE_TIME

env = simpy.Environment()
ticket_office1 = Server(env, 'office-1', capacity=1, service_rate=service_rate)
ticket_office2 = Server(env, 'office-2', capacity=1, service_rate=service_rate)
ticket_offices = [ticket_office1, ticket_office2]
env.process(passenger_generator(env, ticket_offices, arrival_rate))
env.run(until=SIMULATION_END_TIME)


