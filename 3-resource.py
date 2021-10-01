#!/usr/bin/env python
#
# Simpy Example - Processes
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random


def print_stats(resource):
    print('\t[Resource] {} using, {} in queue'.format(resource.count, len(resource.queue)))


# passenger - Entity Process
# Describe how passenger performs at the ticket office
def passenger(env, name, server, service_rate):
    print('[{:6.2f}:{}] - arrive at the station'.format(env.now, name))
    print_stats(server)
    with server.request() as request:
        yield request
        print('[{:6.2f}:{}] - begin buying ticket'.format(env.now, name))
        print_stats(server)
        # random service time based on the service rate
        service_time = random.expovariate(service_rate)
        yield env.timeout(service_time)
        print('[{:6.2f}:{}] - finish buying ticket'.format(env.now, name))
        print_stats(server)
    print('[{:6.2f}:{}] - depart from station'.format(env.now, name))
    print_stats(server)


# generator - Supporting Process
# Create new passenger and then sleep for random amount of time
def passenger_generator(env, server, arrival_rate, service_rate):
    i = 0
    while True:
        ename = 'Passenger#{}'.format(i)
        env.process(passenger(env, ename, server, service_rate))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


# for simplicity, we define arrival and service rate as mean inter-arrival time and mean service time
MEAN_INTER_ARRIVAL_TIME = 5     # 5 time units between arrivals
MEAN_SERVICE_TIME = 4           # 4 time units for each service
SIMULATION_END_TIME = 50

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
service_rate = 1/MEAN_SERVICE_TIME

env = simpy.Environment()
ticket_office = simpy.Resource(env, capacity=1)
env.process(passenger_generator(env, ticket_office, arrival_rate, service_rate))
env.run(until=SIMULATION_END_TIME)


