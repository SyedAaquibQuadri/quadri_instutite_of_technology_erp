from django.shortcuts import render
from accounts.decorators import admin_required
# Create your views here.
@admin_required
def dashboard(request):
    return render(request, 'admin_panel/dashboard.html')