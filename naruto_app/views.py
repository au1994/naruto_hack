from django.views.generic import View
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import requests
from naruto_redis_store import *

crm_info_logger = logging.getLogger('crm_info_logger')


def convert_location_into_node(location):
    l = location.split("-")
    try:
        node_id = int(ord(l[1][0])-ord('A'))*360 + (int(l[1][1])-1)*40 + ((int(l[2])*2)-1) + int(ord(l[4])-ord('A'))+(int(l[3])-1)*1200
    except :
        node_id = 5676

    return node_id


def tsp_rec_solve(start=0, intermediate_points={1, 2, 3}):
    points = list(intermediate_points)
    if start is None:
        start = points[0]
    must_visit = points
    path = [start]
    while must_visit:
        nearest = min(must_visit, key=lambda x: int(get_distance_between_two_nodes(path[-1], x)))
        path.append(nearest)
        must_visit.remove(nearest)
    return path


def calculate_cost_of_best_tour(start, best_tour):
    min_dist = 0
    dup_start = start
    for node in best_tour:
        min_dist += int(get_distance_between_two_nodes(start, node))
        start = node

    min_dist += int(get_distance_between_two_nodes(start, dup_start))
    #print start, dup_start
    #print min_dist
    return min_dist


def apply_tsp(set):
    best_tour = tsp_rec_solve(0, set)
    dist = calculate_cost_of_best_tour(0, best_tour)

    return dist, best_tour


def get_node_from_redis(product_id):
    product_id = str(product_id)
    item_node_mapping = get_item_node_mapping()
    node = int(item_node_mapping.get(product_id, 1))
    return node


def get_item_code(product_id):
    url = "https://retail.grofers.com/rpc/v1/outlet-types/2/get-article-id-for-product/" + str(product_id)
    response = requests.get(url)
    response = response.json()
    item_code = response.get("data")
    return item_code


def get_item_location(item_code):
    url='https://retail.grofers.com/whl/v2/item-locations/?item_code=' + str(item_code)
    response = requests.get(url)
    response = response.json()
    data = response.get("data")
    results = data.get("results")
    for result in results:
        warehouse = result.get("warehouse").get("city")
        if str(warehouse) == 'Bangalore':
            return str(result.get("location").get("location_name"))

    return "L0-C4-018-05-B"


def get_present_distance(list_at_present):
    prev_node = 0
    total_dist = 0
    path = [0]

    for node in list_at_present:
        total_dist += int(get_distance_between_two_nodes(prev_node, node))
        prev_node = node
        path.append(node)
    total_dist += int(get_distance_between_two_nodes(prev_node, 0))
    path.append(0)
    return total_dist, path


def parse_file():
    f = open('graph_input_final_all', "r")
    f2 = open('result_final', 'w', 0)

    for line in f:
        words = line.split(" ")
        print words
        f2.write(words[0] + "," + words[1] + ',')
        words.pop(0)
        words.pop(0)
        a, b = my_func(words)
        print str(a) + str(b)
        f2.write(str(a) + "," + str(b))
        f2.write('\n')

    f2.close()
    return


def my_func(items):
    my_set = set([])
    list_at_present = []
    for item in items:
        product_id = item
        item_code = get_item_code(product_id)
        location = get_item_location(item_code)
        node_at_present = convert_location_into_node(location)
        node = get_node_from_redis(product_id)
        my_set.add(node)
        list_at_present.append(node_at_present)
    total_dist = apply_tsp(my_set)
    dist_at_present = get_present_distance(list_at_present)
    crm_info_logger.info("total_dist: " + str(total_dist) + "dist_at_present" + str(dist_at_present))
    return total_dist, dist_at_present


def two_dimension_from_single_node(node):
    node = int(node)
    if node == 0:
        return 0,0

    node = (node % 1200)
    if node == 0:
        node = 1200
    row = (node-1)/40 + 1
    column = node % 40
    if column == 0:
        column = 40
    return int(row), int(column)


class OrderList(View):

    @csrf_exempt
    def post(self, request):

        try:
            body = request.body
            crm_info_logger.info(str(body))
            order = body.get('order_id')
            if body.get('order', {}).get('actual_merchant', {}).get('id') == 25811:
                items = body.get('order').get('items')
                my_set = set([])
                list_at_present = []
                for item in items:
                    product_id = item.get("product_id")
                    item_code = get_item_code(product_id)
                    location = get_item_location(item_code)
                    node_at_present = convert_location_into_node(location)
                    node = get_node_from_redis(product_id)
                    my_set.add(node)
                    list_at_present.append(node_at_present)
                total_dist, best_tour = apply_tsp(my_set)
                dist_at_present, current_tour = get_present_distance(list_at_present)
                best_tour_coord = []
                current_tour_coord = []
                for node in best_tour:
                    coord = []
                    x,  y = two_dimension_from_single_node(node)
                    coord.append(x)
                    coord.append(y)
                    best_tour_coord.append(coord)

                for node in current_tour:
                    coord = []
                    x,  y = two_dimension_from_single_node(node)
                    coord.append(x)
                    coord.append(y)
                    current_tour_coord.append(coord)

                store_live_orders(order, best_tour, best_tour_coord, total_dist, current_tour, current_tour_coord,
                                  dist_at_present)

                crm_info_logger.info("total_dist: " + str(total_dist) + "dist_at_present" + str(dist_at_present))

        except Exception as e:
            print e

        return HttpResponse(status=200)
