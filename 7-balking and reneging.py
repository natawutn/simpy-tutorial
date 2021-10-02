#!/usr/bin/env python
#
# Simpy Example - Balking (not enter queue) and reneging (leave queue)
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random


# Generic helper class to hold information regarding to resource
# This simplifies how we pass information from main program to entity process
class Server(object):
    def __init__(self, env, name, capacity, service_rate, queue_limit):
        self.name = name
        self.env = env
        self.service_rate = service_rate
        self.capacity = capacity
        self.queue_limit = queue_limit
        self.resource = simpy.Resource(env, capacity=capacity)

    def print_stats(self):
        print('\t[{}] {} using, {} in queue'.format(self.name, self.resource.count, len(self.resource.queue)))

    def get_service_time(self):
        return random.expovariate(self.service_rate)

    def is_available_spaces(self):
        return len(self.resource.queue) < self.queue_limit


# passenger - Entity Process
# Describe how passenger performs at the ticket office
def passenger(env, name, server, wait_limit):
    print('[{:6.2f}:{}] - arrive at the station'.format(env.now, name))
    server.print_stats()
    if not server.is_available_spaces():
        # queue is full, passenger does not join the queue --> balking
        print('\t[{}] - queue is full, not enter the queue'.format(name))
    else:
        # some spaces left, join the queue
        t_arrival = env.now
        with server.resource.request() as request:
            print('\t[{}] - join the queue'.format(name))
            server.print_stats()
            results = yield request | env.timeout(wait_limit)
            if request in results:
                # we got the queue
                t_queue = env.now - t_arrival
                print('[{:6.2f}:{}] - begin buying ticket after waiting for {:4.2f} time units'.format(env.now, name, t_queue))
                # random service time based on the service rate
                service_time = server.get_service_time()
                yield env.timeout(service_time)
                print('[{:6.2f}:{}] - finish buying ticket'.format(env.now, name))
            else:
                # waiting for too long, reneging
                print('[{:6.2f}:{}] - wait for too long, leave the queue'.format(env.now, name))
    print('[{:6.2f}:{}] - depart from station'.format(env.now, name))


# generator - Supporting Process
# Create new passenger and then sleep for random amount of time
def passenger_generator(env, server, arrival_rate, wait_limit):
    i = 0
    while True:
        ename = 'Passenger#{}'.format(i)
        env.process(passenger(env, ename, server, wait_limit))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


# for simplicity, we define arrival and service rate as mean inter-arrival time and mean service time
MEAN_INTER_ARRIVAL_TIME = 5     # 5 time units between arrivals
MEAN_SERVICE_TIME = 8           # 8 time units for each service
WAIT_LIMIT = 6
QUEUE_LIMIT = 2
SIMULATION_END_TIME = 50

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
service_rate = 1/MEAN_SERVICE_TIME

env = simpy.Environment()
ticket_office = Server(env, 'office', capacity=1, service_rate=service_rate, queue_limit=QUEUE_LIMIT)
env.process(passenger_generator(env, ticket_office, arrival_rate, WAIT_LIMIT))
env.run(until=SIMULATION_END_TIME)


