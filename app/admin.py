from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NutritionPlan
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserCreationForm
from django.utils.translation import gettext, gettext_lazy as _
import random
from .forms import NutritionPlanForm

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'user_type','goal','assigned_dietitian')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type','goal','assigned_dietitian', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('username', 'email', 'user_type', 'is_staff','assigned_dietitian')
    search_fields = ('username', 'email')
    ordering = ('username',)
    def save_model(self, request, obj, form, change):
        if obj.user_type == 2:  # client
            dietitians = CustomUser.objects.filter(user_type=1, goal=obj.goal)  # goal ile uyumlu diyetisyenler
            if dietitians.exists():
                assigned_dietitian = random.choice(dietitians)  # Rastgele bir diyetisyen seçme
                obj.assigned_dietitian = assigned_dietitian
                obj.save()
        super().save_model(request, obj, form, change)

    
    
class NutritionPlanAdmin(admin.ModelAdmin):
    model = NutritionPlan
    form=NutritionPlanForm
    list_display = ('title', 'dietitian', 'client', 'created_at')
    list_filter = ('dietitian', 'client')
    search_fields = ('title', 'dietitian__username', 'client__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(dietitian=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk and not request.user.is_superuser:
            obj.dietitian = request.user
        else:
            obj.dietitian = form.cleaned_data['dietitian']
        super().save_model(request, obj, form, change)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'dietitian' and request.user.user_type==1:
            kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        elif db_field.name == 'client':
            
            kwargs["queryset"] = CustomUser.objects.filter(assigned_dietitian=request.user)
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

@receiver(post_save, sender=get_user_model())
def assign_user_to_group(sender, instance, created, **kwargs):
    if created:
        user = instance
        if user.user_type == 1:
            group = Group.objects.get(name='dietitian')
            user.groups.add(group)
        elif user.user_type == 2:
            group = Group.objects.get(name='client')
            user.groups.add(group)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(NutritionPlan, NutritionPlanAdmin)
