#!/usr/bin/env python
#
# Simpy Example - Simple monitors
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random
from resource_monitor import Monitor
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt


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
MEAN_INTER_ARRIVAL_TIME = 10     # 5 time units between arrivals
MEAN_SERVICE_TIME = 8            # 8 time units for each service
SIMULATION_END_TIME = 20000

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
service_rate = 1/MEAN_SERVICE_TIME


env = simpy.Environment()
ticket_office = Server(env, 'office', capacity=1, service_rate=service_rate)
m = Monitor()
m.register('office', ticket_office.resource, ticket_office.capacity)
env.process(passenger_generator(env, ticket_office, arrival_rate))
env.run(until=SIMULATION_END_TIME)

step = 20
clocks = []
util_stats = []
queue_stats = []
raw_util_stats = []
raw_queue_stats = []
for i in range(step, SIMULATION_END_TIME, step):
    stats = m.get_stats('office', 0, i)
    raw_stats = m.get_stats('office', i, i+step)
    print(stats)
    clocks.append(i)
    util_stats.append(stats['stats']['util'])
    queue_stats.append(stats['stats']['queue'])
    raw_util_stats.append(raw_stats['stats']['util'])
    raw_queue_stats.append(raw_stats['stats']['queue'])

plt.plot(clocks, util_stats, color="blue", linewidth=2.5, linestyle="-")
plt.ylim(0, 1)
plt.show()


# calculate CI every n_ci_points
n_ci_points = 5
n = len(queue_stats)
for i in range(0, n-n_ci_points, n_ci_points):
    data = queue_stats[i:i+n_ci_points]
    mean = np.mean(data)
    sem = st.sem(data)
    if sem != 0:
        (low, high) = st.t.interval(alpha=0.95, df=n_ci_points-1, loc=mean, scale=sem)
        width = high - low
    else:
        width = 0
    width_pct = width / mean
    print(mean, width, width_pct)
