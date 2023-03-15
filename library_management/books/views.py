from django.shortcuts import redirect, render
from .models import Book, IssuedItem
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import date
from django.core.paginator import Paginator

def home(request):
    return render(request,'home.html')

def login(request):
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if(user is not None):
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Invalid Credential')
            return redirect('login')
    else:
        return render(request,'login.html')

def register(request):
    if(request.method == 'POST'):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if(password1 == password2):
            if(User.objects.filter(username=username).exists()):
                messages.info(request,'Username already exist')
                return redirect('register')
            elif(User.objects.filter(email=email).exists()):
                messages.info(request,'Email already registered')
                return redirect('register')
            else:
                user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password1)
                user.save()
                print("User Created")
                return redirect('login')
        else:
            messages.info(request,'Password not matches')
            return redirect('register')
    else:
        return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required(login_url='login')
def issue(request):
    if(request.method == 'POST'):
        book_id = request.POST['book_id']
        current_book = Book.objects.get(id=book_id)
        book = Book.objects.filter(id=book_id)
        issue_item = IssuedItem.objects.create(user_id=request.user,book_id=current_book)
        issue_item.save()
        book.update(quantity = book[0].quantity-1)
        messages.success(request, 'Book issued successfully.')
    my_items = IssuedItem.objects.filter(user_id = request.user,return_date__isnull=True).values_list('book_id')
    books = Book.objects.exclude(id__in=my_items).filter(quantity__gt=0)
    return render(request,'issue_item.html',{'books':books})

@login_required(login_url='login')
def history(request):
    my_items = IssuedItem.objects.filter(user_id=request.user).order_by('-issue_date')
    paginator = Paginator(my_items,10) # object name, no of data
    page_number = request.GET.get('page')
    show_data_final = paginator.get_page(page_number)
    return render(request,'history.html',{'books':show_data_final})

@login_required(login_url='login')
def return_item(request):
    if(request.method == 'POST'):
        book_id = request.POST['book_id']
        current_book = Book.objects.get(id=book_id)
        book = Book.objects.filter(id=book_id)
        book.update(quantity = book[0].quantity+1)
        issue_item = IssuedItem.objects.filter(user_id=request.user,book_id=current_book,return_date__isnull=True)
        issue_item.update(return_date=date.today())
        messages.success(request, 'Book returned successfully.')
    my_items = IssuedItem.objects.filter(user_id = request.user,return_date__isnull=True).values_list('book_id')
    books = Book.objects.exclude(~Q(id__in=my_items))
    params = {'books':books}
    return render(request,'return_item.html',params)
