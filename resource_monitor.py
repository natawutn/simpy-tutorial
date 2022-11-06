#!/usr/bin/env python
#
# Simpy Example - Generic resource monitor
# for 2110636 Performance Evaluation and Analysis Class
# Natawut Nupairoj, Chulalongkorn University, Thailand
from functools import partial, wraps
import simpy
from simpy.util import start_delayed


def patch_resource(resource, func_name, pre=None, post=None):
    """Patch *resource* so that it calls the callable *pre* before each
    put/get/request/release operation and the callable *post* after each
    operation.  The only argument to these functions is the resource
    instance.
    """

    def get_wrapper(func):
        # Generate a wrapper for put/get/request/release
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This is the actual wrapper
            # Call "pre" callback
            if pre:
                pre(func_name, 'pre', resource)
            # Perform actual operation
            ret = func(*args, **kwargs)
            # Call "post" callback
            if post:
                post(func_name, 'post', resource)
            return ret

        return wrapper

    # Replace the original operations with our wrapper
    if hasattr(resource, func_name):
        setattr(resource, func_name, get_wrapper(getattr(resource, func_name)))


class Monitor:
    _resources = dict()

    def register(self, name, resource, capacity):
        data = []
        resource_logger = partial(Monitor.resource_logger, data)
        patch_resource(resource, 'request', pre=resource_logger, post=resource_logger)
        patch_resource(resource, 'release', pre=resource_logger, post=resource_logger)
        r = {
            'resource': resource,
            'capacity': capacity,
            'logs': data,
            'entity': []
        }
        self._resources[name] = r

    def get_resource(self, name):
        return self._resources[name]

    def entity_logger(self, name, e_name, stats):
        e = { 'name': e_name, 'stats': stats }
        self._resources[name]['entity'].append(e)

    @staticmethod
    def resource_logger(data, func_name, step, resource):
        d = { 'clock': resource._env.now, 'func': func_name, 'step': step,
              'stats': { 'count': resource.count, 'queue': len(resource.queue) } }
        data.append(d)

    @staticmethod
    def cleanup(data):
        # we will need to clean up the data such that
        # the stats of the current clock will come from the next clock
        # and for the last clock will use the final data
        clean_data = []
        cur_clock = -1
        for d in data:
            clock = d['clock']
            if cur_clock == -1:
                cur_clock = clock
                continue

            if cur_clock < clock:
                # change to the next one, we will use this stats for the previous clock
                o = { 'clock': cur_clock, 'stats': d['stats'] }
                clean_data.append(o)
                cur_clock = clock

        # handle the last clock
        d = data[-1]
        o = {'clock': d['clock'], 'stats': d['stats']}
        clean_data.append(o)
        return clean_data

    @staticmethod
    def seek(data, start, mark):
        n = len(data)
        index = start
        while index < n and data[index]['clock'] < mark:
            index += 1
        if index >= n:
            # beyond scope, use last
            index = n - 1
        else:
            if data[index]['clock'] > mark and index > 0:
                # use previous record
                index -= 1

        return index

    def get_stats(self, name, begin, end):
        if 'stats' not in self._resources[name]:
            self._resources[name]['stats'] = self.cleanup(self._resources[name]['logs'])

        capacity = self._resources[name]['capacity']
        log = self._resources[name]['stats']
        # seek the begin
        b_index = Monitor.seek(log, 0, begin)
        e_index = Monitor.seek(log, b_index, end)

        total_b = 0
        total_q = 0
        cur_t = begin
        cur_b = log[b_index]['stats']['count']
        cur_q = log[b_index]['stats']['queue']
        k = b_index + 1
        while k <= e_index:
            delta_t = log[k]['clock'] - cur_t
            total_b += cur_b * delta_t
            total_q += cur_q * delta_t
            cur_t = log[k]['clock']
            cur_b = log[k]['stats']['count']
            cur_q = log[k]['stats']['queue']
            k += 1
        # have to handle e_index
        delta_t = end - cur_t
        total_b += cur_b * delta_t
        total_q += cur_q * delta_t

        total_b /= 1.0*(end-begin)*capacity
        total_q /= 1.0*(end-begin)

        r = { 'begin': begin, 'end': end, 'stats': { 'util': total_b, 'queue': total_q }}
        return r


if __name__ == "__main__":
    def test_process(env, name, resource):
        print('[{:2d}:{}] pre request'.format(env.now, name))
        with resource.request() as req:
            print('[{:2d}:{}] post request'.format(env.now, name))
            yield req
            yield env.timeout(10)
            print('[{:2d}:{}] pre release'.format(env.now, name))
        print('[{:2d}:{}] post release'.format(env.now, name))

    env = simpy.Environment()
    capacity = 2
    resource = simpy.Resource(env, capacity=capacity)
    m = Monitor()
    m.register('test', resource, capacity)
    proc = env.process(test_process(env, 'P0', resource))
    proc = start_delayed(env, test_process(env, 'P1', resource), 5)
    proc = start_delayed(env, test_process(env, 'P2', resource), 10)
    env.run()
    print(m._resources['test']['logs'])
    print(m.cleanup(m._resources['test']['logs']))


    def test_stats(m, begin, end):
        print(begin, end, m.get_stats('test', begin, end))


    test_stats(m, 0, 10)
    test_stats(m, 1, 3)
    test_stats(m, 1, 9)
    test_stats(m, 7, 10)
    test_stats(m, 7, 9)
    test_stats(m, 10, 15)
    test_stats(m, 15, 20)
    test_stats(m, 20, 25)
    test_stats(m, 7, 25)
    test_stats(m, 10, 20)
    test_stats(m, 10, 25)
