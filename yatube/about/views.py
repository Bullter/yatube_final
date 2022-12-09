from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'app_name/author.html'


class AboutTech(TemplateView):
    template_name = 'app_name/tech.html'
