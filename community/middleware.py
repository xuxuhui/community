from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x


class Interceptor(MiddlewareMixin):
    def process_request(self, request):
        print(request.get_full_path(), "path...................")
        pass

    # def process_response(self, request, response):
    #     pass
