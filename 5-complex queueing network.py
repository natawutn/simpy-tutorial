#!/usr/bin/env python
#
# Simpy Example - Complex Queueing Network
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
# Describe how passenger performs at the station
# - 80% buy tickets from machine, 20% buy from office
# - after bought tickets, go to the gate
def passenger(env, name, ticket_machine, ticket_office, gate):
    print('[{:6.2f}:{}] - arrive at the station'.format(env.now, name))

    # 80% of passengers go to ticket machine with 2 machines
    # and 20% go to ticket office with 1 counter
    # we randomly choose the destination
    if random.random() < 0.8:
        # this is the 80% that go to ticket machine
        t_arrival = env.now
        print('[{:6.2f}:{}] - join queue at ticket machine'.format(t_arrival, name))
        ticket_machine.print_stats()
        with ticket_machine.resource.request() as request:
            yield request
            t_queue = env.now - t_arrival
            print('[{:6.2f}:{}] - reach machine after waiting for {:4.2f} time units'.format(env.now, name, t_queue))
            service_time = ticket_machine.get_service_time()
            yield env.timeout(service_time)
            print('[{:6.2f}:{}] - finish buying ticket after {:4.2f} time units'.format(env.now, name, service_time))
    else:
        # this is the 20% that go to ticket office
        t_arrival = env.now
        print('[{:6.2f}:{}] - join queue at ticket office'.format(t_arrival, name))
        ticket_office.print_stats()
        with ticket_office.resource.request() as request:
            yield request
            t_queue = env.now - t_arrival
            print('[{:6.2f}:{}] - reach counter after waiting for {:4.2f} time units'.format(env.now, name, t_queue))
            service_time = ticket_office.get_service_time()
            yield env.timeout(service_time)
            print('[{:6.2f}:{}] - finish buying ticket after {:4.2f} time units'.format(env.now, name, service_time))

    # those finish buying tickets from either machine or office go to the gate
    t_arrival = env.now
    print('[{:6.2f}:{}] - join queue at the gates'.format(t_arrival, name))
    gate.print_stats()
    with gate.resource.request() as request:
        yield request
        t_queue = env.now - t_arrival
        print('[{:6.2f}:{}] - reach the gate after waiting for {:4.2f} time units'.format(env.now, name, t_queue))
        service_time = gate.get_service_time()
        yield env.timeout(service_time)
        print('[{:6.2f}:{}] - pass the gate after {:4.2f} time units'.format(env.now, name, service_time))

    print('[{:6.2f}:{}] - depart from station'.format(env.now, name))


# generator - Supporting Process
# Create new passenger and then sleep for random amount of time
def passenger_generator(env, ticket_machine, ticket_office, gate, arrival_rate):
    i = 0
    while True:
        ename = 'Passenger#{}'.format(i)
        env.process(passenger(env, ename, ticket_machine, ticket_office, gate))
        next_entity_arrival = random.expovariate(arrival_rate)
        yield env.timeout(next_entity_arrival)
        i += 1


# for simplicity, we define arrival and service rate as mean inter-arrival time and mean service time
MEAN_INTER_ARRIVAL_TIME = 10     # 10 time units between arrivals
TO_MEAN_SERVICE_TIME = 20        # 20 time units for each service at the ticket office
TM_MEAN_SERVICE_TIME = 15        # 15 time units for each service at the ticket machine
GA_MEAN_SERVICE_TIME = 10        # 10 time units for each service at the gate
SIMULATION_END_TIME = 50

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
to_service_rate = 1/TO_MEAN_SERVICE_TIME
tm_service_rate = 1/TM_MEAN_SERVICE_TIME
ga_service_rate = 1/GA_MEAN_SERVICE_TIME

env = simpy.Environment()
ticket_office = Server(env, 'ticket_office', 1, to_service_rate)
ticket_machine = Server(env, 'ticket_machine', 2, tm_service_rate)
gate = Server(env, 'gate', 1, ga_service_rate)
env.process(passenger_generator(env, ticket_machine, ticket_office, gate, arrival_rate))
env.run(until=SIMULATION_END_TIME)
