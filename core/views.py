from django.shortcuts import render

# View for the landing page
def landing_page(request):
  return render(request, 'core/landing_page.html')

# View for the about page
def about_page(request):
  return render(request, 'core/about.html')
