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
            pre_data = None
            if pre:
                pre_data = pre(resource)
            # Perform actual operation
            ret = func(*args, **kwargs)
            # Call "post" callback
            if post:
                post(resource, pre_data)
            return ret

        return wrapper

    # Replace the original operations with our wrapper
    if hasattr(resource, func_name):
        setattr(resource, func_name, get_wrapper(getattr(resource, func_name)))


class Monitor:
    _resources = dict()

    def register(self, name, resource):
        data = []
        monitor_post = partial(Monitor.monitor_post_request, data)
        patch_resource(resource, 'request', pre=Monitor.monitor_pre, post=monitor_post)
        monitor_post = partial(Monitor.monitor_post_release, data)
        patch_resource(resource, 'release', pre=Monitor.monitor_pre, post=monitor_post)
        r = {
            'resource': resource,
            'logs': data
        }
        self._resources[name] = r

    @staticmethod
    def monitor_pre(resource):
        """This is our monitoring callback."""
        q0 = len(resource.queue)
        u0 = resource.count
        return {'q': q0, 'u': u0}

    @staticmethod
    def monitor_post_request(data, resource, pre_data):
        """This is our monitoring callback."""
        now = resource._env.now
        q0 = pre_data['q']
        u0 = pre_data['u']
        q1 = len(resource.queue)
        u1 = resource.count
        data.append((now, Monitor.checkBusy(q0, u0, q1, u1), q1))

    @staticmethod
    def monitor_post_release(data, resource, pre_data):
        """This is our monitoring callback."""
        now = resource._env.now
        q0 = pre_data['q']
        u0 = pre_data['u']
        q1 = len(resource.queue)
        u1 = resource.count
        if q0 == q1 > 0:
            q1 -= 1
        data.append((now, Monitor.checkBusy(q0, u0, q1, u1), q1))

    @staticmethod
    def checkBusy(q0, u0, q1, u1):
        busy = u1
        if q0 > 0 or q1 > 0:
            busy = u0
        return busy


def test_process(env, resource):
    with resource.request() as req:
        yield req
        yield env.timeout(10)

env = simpy.Environment()
resource = simpy.Resource(env)
m = Monitor()
m.register('test', resource)
proc = env.process(test_process(env, resource))
proc = start_delayed(env, test_process(env, resource), 5)
proc = start_delayed(env, test_process(env, resource), 10)
env.run()
print(m._resources)