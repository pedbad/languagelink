from django.shortcuts import render

def landing_page(request):
    return render(request, 'core/landing_page.html')

def about_page(request):
    return render(request, 'core/about.html')
