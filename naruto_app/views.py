from django.views.generic import View
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import requests
import naruto_redis_store

crm_info_logger = logging.getLogger('crm_info_logger')


def convert_location_into_node(location):
    l = location.split("-")
    node_id = int(ord(l[1][0])-ord('A'))*360 + (int(l[1][1])-1)*40 + ((int(l[2])*2)-1) + int(ord(l[4])-ord('A'))+(int(l[3])-1)*1200
    return node_id


def tsp_rec_solve(start=0, intermediate_points={1, 2, 3}):
    def rec_tsp_solve(c, ts):

        # assert c not in ts (for debugging)
        if ts:
            int(get_distance_between_two_nodes(lc, c))
            return min((int(get_distance_between_two_nodes(lc, c)) + rec_tsp_solve(lc, ts - {lc})[0], lc)
                       for lc in ts)
        else:
            return int(get_distance_between_two_nodes(0, c)), 0


    best_tour = []
    start_dup = start
    # cs = set(range(1, len(d)))
    while True:
        l, lc = rec_tsp_solve(start, intermediate_points)
        if lc == 0:
            break
        best_tour.append(lc)
        start = lc
        intermediate_points = intermediate_points - {lc}

    best_tour = tuple(reversed(best_tour))

    print best_tour
    return best_tour


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

    return dist


def get_node_from_redis(product_id):
    product_id = str(product_id)
    item_node_mapping = get_item_node_mapping()
    node = int(item_node_mapping.get(product_id))
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
        warehouse = result.get("warehouse")
        if str(warehouse) == 'Bangalore':
            return str(result.get("location").get("location_name"))

    return "L0-C4-018-05-B"


def get_present_distance(list_at_present):
    prev_node = 0
    total_dist = 0
    for node in list_at_present:
        total_dist += int(get_distance_between_two_nodes(prev_node, node))
        prev_node = node
    return total_dist


class OrderList(View):

    @csrf_exempt
    def post(self, request):

        try:
            body = request.body
            crm_info_logger.info(str(body))
            order = body.get('order_id')
            order_to_consider = GrOrder.objects.get(id=order)
            if order_to_consider.actual_merchant_id == 25801:
                items = body.get('order').get('items')
                set = {}
                list_at_present = []
                for item in items:
                    mapping_id = item.get("mapping_id")
                    product_id = GrMerchantProductMapping.objects.get(id=mapping_id).product_id
                    item_code = get_item_code()
                    location = get_item_location(item_code)
                    node_at_present = convert_location_into_node(location)
                    node = get_node_from_redis(product_id)
                    set.add(node)
                    list_at_present.append(node_at_present)
                total_dist = apply_tsp(set)
                dist_at_present = get_present_distance(list_at_present)
                crm_info_logger.info("order:" + str(order) + "total_dist: " + total_dist + "dist_at_present" + dist_at_present)

        except Exception as e:
            print e

        return HttpResponse(status=200)
