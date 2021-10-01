#!/usr/bin/env python
#
# Simpy Example - Processes
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
import random


# entity - Entity Process
# Describe how entity performs for the entire simulation
def entity(env, name, waitfor=50):
    print('[{:6.2f}:{}] - begin process'.format(env.now, name))
    yield env.timeout(waitfor)
    print('[{:6.2f}:{}] - end process'.format(env.now, name))


# generator - Supporting Process
# Create new entity and then sleep for random amount of time
def generator(env, arrival_rate):
    i = 0
    while True:
        ename = 'Entity#{}'.format(i)
        print('[{:6.2f}:Generator] Generate {}'.format(env.now, ename))
        env.process(entity(env, ename))
        next_entity_arrival = random.expovariate(arrival_rate)
        print('[{:6.2f}:Generator] next generation is {} seconds away'.format(env.now, next_entity_arrival))
        yield env.timeout(next_entity_arrival)
        i += 1


env = simpy.Environment()
env.process(generator(env, 0.1))
env.run(until=100)


