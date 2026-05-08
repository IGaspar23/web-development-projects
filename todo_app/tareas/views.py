from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from tareas import models
from tareas.models import Task
from django.contrib.auth import authenticate, login as new_login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.generic import TemplateView

class TaskForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a new task...',
            'class': 'task-input'
            })
    )
     

def signup(request):
    if request.method == 'POST':
        # Aquí puedes agregar la lógica para manejar el formulario de registro
        # Por ejemplo, puedes crear un nuevo usuario con los datos del formulario
        # y luego redirigir al usuario a otra página después del registro exitoso.
        fnm = request.POST.get('fnm')
        email_id = request.POST.get('email')
        pwd = request.POST.get('pwd')
        print(fnm, email_id, pwd)
        my_user = User.objects.create_user(fnm, email_id, pwd)
        my_user.save()
        return redirect('/login')  # Redirige a la página principal después del registro
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        pwd = request.POST.get('pwd')
        print(fnm, pwd)  # Solo para verificar que los datos se reciben correctamente
        user = authenticate(request, username=fnm, password=pwd)
        print(user)
        if user is not None:
            new_login(request, user)
            return redirect('/todopage')  # Redirige a la página principal después del inicio de sesión
        else: 
            return redirect('/login', {'error': 'Invalid credentials'})  # Redirige a la página de registro si las credenciales son incorrectas
    return render(request, 'login.html')

@login_required(login_url='/login/')
def todo(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        print(title)
        obj = models.Task(title=title, user=request.user)
        obj.save()
        res=models.Task.objects.filter(user=request.user).order_by('-created_at')  # Obtiene las tareas del usuario actual
        print(res)
        return redirect('/todopage', {'res': res})
    res = models.Task.objects.filter(user=request.user).order_by('-created_at')  
    return render(request, 'todo.html', {'res': res})


def edit_task(request, srno):
    # Aquí puedes agregar la lógica para editar una tarea específica
    # Por ejemplo, puedes obtener la tarea por su ID, mostrar un formulario de edición
    # y luego actualizar la tarea con los nuevos datos después de que el usuario envíe el formulario.
    if request.method == 'POST':
        title = request.POST.get('title')
        print(title)
        obj = models.Task.objects.get(srno=srno)
        obj.title = title
        obj.save()
        return redirect('/todopage',{'obj': obj})
    obj = models.Task.objects.get(srno=srno)  
    return render(request, 'edit_task.html', {'obj': obj})

def delete_task(request, srno):
    # Aquí puedes agregar la lógica para eliminar una tarea específica
    # Por ejemplo, puedes obtener la tarea por su ID y luego eliminarla de la base de datos.
    obj = models.Task.objects.get(srno=srno)
    obj.delete()    
    return redirect('/todopage')


def signout(request):
    logout(request)
    return redirect('/login')