import simpy


def print_stats(id, t, et, q, b, stats):
    stats['out-count'] += 1
    s = '{:3d} [{}, {}, {}] q={}, b={}, in-q={}, in-s={}, P={}, N={}, sum-wq={}, sum-ts={}, area-q={}, area-b={}, stack={}'.format(
        stats['out-count'], id, t, et, q, b, stats['in-q'], stats['in-s'], stats['P'], stats['N'], stats['sum-wq'], stats['sum-ts'], stats['a-q'], stats['a-b'], stats['stack'])
    print(s)


def caller(env, id, callcenter, svc_list, stats):
    pop_stack(stats)
    t_arrival = env.now
    # print('[{:3d}:{}] arrive at call center'.format(t_arrival, name))
    server_idle = True
    if callcenter.count >= 2:
        stats['in-q'].append((id, t_arrival))
        server_idle = False
    with callcenter.request() as req:
        if not server_idle:
            print_stats(id, env.now, 'Arr', len(callcenter.queue), callcenter.count, stats)
        yield req

        # this call is about to be served
        in_s = (id, env.now)
        server = 0
        if stats['in-s'][server] != '-':
            server += 1
        stats['in-s'][server] = in_s
        stats['sum-wq'] += env.now - t_arrival
        stats['N'] += 1
        push_stack(stats, (id, env.now+svc_list[id-1], 'Dep'))
        if server_idle:
            print_stats(id, env.now, 'Arr', len(callcenter.queue), callcenter.count, stats)
        yield env.timeout(svc_list[id-1])

        # we are done
        pop_stack(stats)
        # print('[{:3d}:{}] complete service'.format(env.now, name))
        stats['sum-ts'] += env.now - t_arrival
        stats['P'] += 1
        server = 0
        if stats['in-s'][0] == '-' or stats['in-s'][0][0] != id:
            server = 1

        if len(stats['in-q']) > 0:
            o = stats['in-q'].pop(0)
            stats['in-s'][server] = (o[0], env.now)
            push_stack(stats, (o[0], env.now + svc_list[o[0]-1], 'Dep'))
        else:
            print('server = ', server)
            stats['in-s'][server] = '-'

        print_stats(id, env.now, 'Dep', len(callcenter.queue), callcenter.count, stats)


def push_stack(stats, item):
    for o in stats['stack']:
        if item[0] == o[0]:
            # already in the stack, ignore!
            return

    stats['stack'].append(item)
    stats['stack'] = sorted(stats['stack'], key=lambda x: x[1])


def pop_stack(stats):
    return stats['stack'].pop(0)


def caller_generator(env, callcenter, iat_list, svc_list, stats):
    n = len(iat_list)
    push_stack(stats, (1, 0, 'Arr'))
    for i in range(n):
        env.process(caller(env, (i+1), callcenter, svc_list, stats))
        # print('Next arrival {} at {}'.format(i+2, env.now + iat_list[i]))
        push_stack(stats, (i+2, env.now + iat_list[i], 'Arr'))
        yield env.timeout(iat_list[i])


iats = [5, 3, 2, 4, 14, 7, 4, 5, 11, 8]
svcs = [12, 8, 10, 6, 15, 9, 4, 8, 5, 14]
env = simpy.Environment()
cc = simpy.Resource(env, capacity=2)
stats = {'in-q': [], 'in-s': ['-', '-'], 'P': 0, 'N': 0, 'sum-wq': 0, 'sum-ts': 0, 'a-q': 0, 'a-b': 0, 'out-count': 0, 'stack': []}
env.process(caller_generator(env, cc, iats, svcs, stats))
push_stack(stats, ('-', 20, 'End'))
env.run(until=20)
print(stats)
print('avg wq', 1.0*stats['sum-wq']/stats['N'])
print('avg w', 1.0*stats['sum-ts']/stats['P'])
