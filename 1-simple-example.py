#!/usr/bin/env python
#
# First Simpy Example
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
import simpy
from simpy.util import start_delayed


def simple_process(env, name, waitfor=50):
    print('{:6.2f}:{} - begin process'.format(env.now, name))
    yield env.timeout(waitfor)
    print('{:6.2f}:{} - end process'.format(env.now, name))

env = simpy.Environment()
proc = env.process(simple_process(env, 'P0'))
proc2 = start_delayed(env, simple_process(env, 'P1', waitfor=35), 8)
env.run()

