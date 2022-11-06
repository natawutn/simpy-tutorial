#!/usr/bin/env python
import simpy
import random


def find_shortest_queues(servers):
    min_n = -1
    min_s = None
    for s in servers:
        n_in_server = s.count + len(s.queue)
        if n_in_server < min_n or min_n == -1:
            min_n = n_in_server
            min_s = s
    return min_s, min_n


def customer(env, name, servers, service_rate):
    server, num_in_server = find_shortest_queues(servers)
    with server.request() as request:
        yield request
        service_time = random.expovariate(service_rate)
        yield env.timeout(service_time)


def customer_generator(env, servers, arrival_rate, service_rate):
    i = 0
    while True:
        ename = 'Customer#{}'.format(i)
        env.process(customer(env, ename, servers, service_rate))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


env = simpy.Environment()
nurse1 = simpy.Resource(env, capacity=1)
nurse2 = simpy.Resource(env, capacity=1)
nurse3 = simpy.Resource(env, capacity=1)
nurses = [nurse1, nurse2, nurse3]
env.process(customer_generator(env, nurses, 4, 10))
env.run(until=100)


