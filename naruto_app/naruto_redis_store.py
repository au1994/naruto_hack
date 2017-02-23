import redis
import redis
import json

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def set_item_node_mapping():
    r.delete('item_node_mapping')
    f = open('final_answer', 'r')
    item_node_mapping = f.read()
    item_node_mapping = json.dumps(json.loads(item_node_mapping))
    return r.set('item_node_mapping', item_node_mapping)


def get_item_node_mapping():
    item_node_mapping = r.get('item_node_mapping')
    print type(item_node_mapping)
    return json.loads(item_node_mapping)


def set_distance_matrix(distance_matrix):
    prefix = 'dist:'
    i = 0
    for l in distance_matrix:
        key = prefix + str(i)
        r.delete(key)
        r.lpush(key, *l)
        i += 1


def get_distance_between_two_nodes(i, j):
    prefix = 'dist:'
    key = prefix + str(i)
    l = r.llen(key)
    return r.lindex(key, l-j-1)


def store_live_orders(order_id, best_tour, best_tour_coord, best_dist, current_tour, current_tour_coord, current_dist, ):
    prefix = 'new_order'
    key = prefix
    r.lpush(key, order_id)
    tmp_dict = {
        'best_tour': best_tour,
        'best_dist': best_dist,
        'best_tour_coord': best_tour_coord,
        'current_tour': current_tour,
        'current_dist': current_dist,
        'current_tour_coord': current_tour_coord
    }
    tmp_dict = json.dumps(tmp_dict)
    r.set(str(order_id), tmp_dict)


def get_live_orders():
    prefix = 'new_order'
    key = prefix
    order_id = r.lindex(prefix, 0)
    tmp_dict = r.get(str(order_id))
    return tmp_dict



