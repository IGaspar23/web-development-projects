from django.contrib import admin
from django.urls import path
from tareas import views 

from tareas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view),
    path('login/', views.login_view),
    path('signup/', views.signup),
    path('todopage/', views.todo),
    path('logout/', views.logout),
    path('edit_task/<int:srno>/', views.edit_task, name='edit_task'),
    path('delete_task/<int:srno>/', views.delete_task),
    path('signout/', views.signout, name='signout'),
]
