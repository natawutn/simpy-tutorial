#!/usr/bin/env python
#
# Simpy Example - Processes
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random


def entity(env, name, waitfor=50):
    print('{:4}:{} - begin process'.format(env.now, name))
    yield env.timeout(waitfor)
    print('{}:{} - end process'.format(env.now, name))


def generator_process(env, name, arrival_rate):
    i = 0
    while True:
        ename = 'Entity#{}'.format(i)
        print('Generate {}'.format(ename))
        env.process(entity(env, ename))
        next_entity_arrival = random.expovariate(arrival_rate)
        print('next generation is {} seconds away'.format(next_entity_arrival))
        yield env.timeout(next_entity_arrival)
        i += 1



env = simpy.Environment()
env.process(generator_process(env, 'Generator', 1))
env.run(until=100)


