import json
from collections import OrderedDict
from urllib import urlencode

from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponse
from django.http import JsonResponse
from django.views.generic import View


class LoginAPIView(View):

    def post(self, request, *args, **kwargs):
        from django.contrib.admin.forms import AdminAuthenticationForm

        auth_form = AdminAuthenticationForm(data=json.loads(request.body))
        if not auth_form.is_valid():
            response_data = {
                "authenticated": False
            }
            return JsonResponse(response_data, 401)

        response_data = {
            "authenticated": True,
        }
        return JsonResponse(response_data)


class LogoutAPIView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse("logout")


class PasswordChangeAPIView(View):

    def post(self, request, *args, **kwargs):
        return HttpResponse("pasword_change")


class APIView(View):

    def json_response(self, data, *args, **kwargs):
        return JsonResponse(data, safe=False, *args, **kwargs)


class ChangeListRetrieveAPIView(APIView):

    def get_api_next_url(self, request, cl):
        page_num = cl.page_num
        if page_num and page_num is not int or not cl.multi_page:
            return None
        info = self.model._meta.app_label, self.model._meta.model_name
        url = reverse_lazy("admin:%s_%s_api_list" % info)
        host = request.get_host()
        params = cl.params
        params["p"] = page_num + 1
        return "%s://%s%s?%s" % (request.scheme, host, url, urlencode(params))

    def get_api_previous_url(self, request, cl):
        page_num = cl.page_num
        if page_num == 0 or not cl.multi_page:
            return None

        info = self.model._meta.app_label, self.model._meta.model_name
        url = reverse_lazy("admin:%s_%s_api_list" % info)
        host = request.get_host()
        params = cl.params
        params["p"] = page_num - 1
        return "%s://%s%s?%s" % (request.scheme, host, url, urlencode(params))

    def get(self, request, model_admin, admin_cl, *args, **kwargs):
        self.model = admin_cl.model
        results = []
        for obj in admin_cl.result_list:
            results.append(model_admin.serialize_obj(request, obj))

        data = OrderedDict()
        data["count"] = admin_cl.result_count
        data["next"] = self.get_api_next_url(request, admin_cl)
        data["previous"] = self.get_api_previous_url(request, admin_cl)
        data["results"] = results
        return self.json_response(data)


class AdminDetailRetrieveAPIView(APIView):

    def get(self, request, model_admin, admin_cl, *args, **kwargs):
        return self.json_response("ok")
