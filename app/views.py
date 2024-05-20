from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView
from .models import NutritionPlan
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login
from .models import *
import random
class DietitianRequiredMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.user_type == 1

class ClientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 2

class NutritionPlanCreateView(LoginRequiredMixin, DietitianRequiredMixin, CreateView):
    model = NutritionPlan
    fields = ['client', 'title', 'description']
    template_name = 'nutrition/nutritionplan_form.html'

    def form_valid(self, form):
        form.instance.dietitian = self.request.user
        return super().form_valid(form)

class NutritionPlanListView(LoginRequiredMixin, ListView):
    model = NutritionPlan
    template_name = 'nutrition/nutritionplan_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            return NutritionPlan.objects.filter(dietitian=self.request.user)
        elif self.request.user.user_type == 2:
            return NutritionPlan.objects.filter(client=self.request.user)

class NutritionPlanDetailView(LoginRequiredMixin, ClientRequiredMixin, DetailView):
    model = NutritionPlan
    template_name = 'nutrition/nutritionplan_detail.html'

def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 2  # client
            user.is_staff=True
            user.save()

            # Goal alanına göre uygun bir diyetisyen atama
            if user.user_type == 2:  # client
                dietitians = CustomUser.objects.filter(user_type=1, goal=user.goal)  # goal ile uyumlu diyetisyenler
                if dietitians.exists():
                    assigned_dietitian = random.choice(dietitians)  # Rastgele bir diyetisyen seçme
                    user.assigned_dietitian = assigned_dietitian
                    user.save()  # Diyetisyen atandıktan sonra tekrar kaydet

            return redirect('index')  # veya uygun bir yönlendirme URL'si
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})