from django.urls import path
from . import views
from .views import NutritionPlanCreateView, NutritionPlanListView, NutritionPlanDetailView

urlpatterns = [
    path("",views.index,name='index'),
    path("login/",views.login,name='login'),
    path("signup/",views.register,name='signup'),
    path('plans/', NutritionPlanListView.as_view(), name='nutritionplan-list'),
    path('plans/create/', NutritionPlanCreateView.as_view(), name='nutritionplan-create'),
    path('plans/<int:pk>/', NutritionPlanDetailView.as_view(), name='nutritionplan-detail'),

]