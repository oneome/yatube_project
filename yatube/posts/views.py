from django.http import HttpResponse
# Create your views here.


def index(request):
    return HttpResponse('Слава пиву, алкашам слава')


def group_posts(request, slug):
    return HttpResponse('Ты не туда защел пацанчик это наш район')