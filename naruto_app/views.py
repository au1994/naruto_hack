from django.views.generic import View
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

crm_info_logger = logging.getLogger('crm_info_logger')


class OrderList(View):

    @csrf_exempt
    def post(self, request):

        try:
            body = request.body
            crm_info_logger.info(str(body))
        except Exception as e:
            print e

        return HttpResponse(status=200)
