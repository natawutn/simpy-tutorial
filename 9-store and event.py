#!/usr/bin/env python
#
# Simpy Example - Store and Event
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random


# Helper class to
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
        return random.expovariate(self.service_rate)+0.1


# passenger - Entity Process
# Describe how passenger performs at the station
# - 80% buy tickets from machine, 20% buy from office
# - after bought tickets, go to the gate
# - wait until the train arrives and broad the train
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

    # register to wait for a train on the platform
    train_arrival_event = env.event()
    yield platform.put(train_arrival_event)
    yield train_arrival_event
    print('[{:6.2f}:{}] - board the train'.format(env.now, name))


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


def train(env, on_board, remaining, platform):
    n_pax_wait = len(platform.items)
    print('[{:6.2f}:Train] - train has arrived with {} pax on board, {} seats remaining, and {} pax waiting on the platform'.format(env.now, on_board, remaining, n_pax_wait))
    if n_pax_wait < remaining:
        remaining = n_pax_wait
    for i in range(remaining):
        passenger_ev = yield platform.get()
        # inform the passenger to board the train
        passenger_ev.succeed()
        on_board += 1

    yield env.timeout(0.1)
    print('[{:6.2f}:Train] - train leaves the platform with {} pax ({} still waiting on platform)'.format(env.now, on_board, len(platform.items)))


def train_generator(env, duration, capacity, platform):
    while True:
        yield env.timeout(duration)
        # random remaining capacity
        remaining = random.randint(0, capacity)
        on_board = capacity - remaining
        env.process(train(env, on_board, remaining, platform))


# for simplicity, we define arrival and service rate as mean inter-arrival time and mean service time
MEAN_INTER_ARRIVAL_TIME = 5     # 10 time units between arrivals
TO_MEAN_SERVICE_TIME = 20        # 20 time units for each service at the ticket office
TM_MEAN_SERVICE_TIME = 10        # 15 time units for each service at the ticket machine
GA_MEAN_SERVICE_TIME = 5        # 10 time units for each service at the gate

TRAIN_INTERVAL = 20
TRAIN_CAPACITY = 5
SIMULATION_END_TIME = 80

arrival_rate = 1/MEAN_INTER_ARRIVAL_TIME
to_service_rate = 1/TO_MEAN_SERVICE_TIME
tm_service_rate = 1/TM_MEAN_SERVICE_TIME
ga_service_rate = 1/GA_MEAN_SERVICE_TIME

env = simpy.Environment()
ticket_office = Server(env, 'ticket_office', 1, to_service_rate)
ticket_machine = Server(env, 'ticket_machine', 2, tm_service_rate)
gate = Server(env, 'gate', 1, ga_service_rate)
platform = simpy.Store(env, capacity=1000)
env.process(passenger_generator(env, ticket_machine, ticket_office, gate, arrival_rate))
env.process(train_generator(env, TRAIN_INTERVAL, TRAIN_CAPACITY, platform))
env.run(until=SIMULATION_END_TIME)
