from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def home_page(request):
    # if request.method == 'POST':
    #     Item.objects.create(text=request.POST['text'])
    #     return redirect('/lists/the-only-list-in-the-world/')
    
    return render(request, 'home.html', {'form' : ItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list' : list_, 'form' : form})

# def new_list(request):
#     form = ItemForm(data=request.POST)

#     if form.is_valid():
#         # list_ = List.objects.create()
#         list_ = List()
#         if request.user.is_authenticated:
#             list_.owner = request.user
#         list_.save()
#         form.save(for_list=list_)
#         return redirect(str(list_.get_absolute_url()))
#     else:
#         return render(request, 'home.html', {'form' : form})

def new_list(request):
    form = NewListForm(data=request.POST)

    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(str(list_.get_absolute_url()))
    
    return render(request, 'home.html', {'form' : form},)


def my_lists(request, email):
    owner = User.objects.get(email=email)
    lists = List.objects.filter(shared_with=owner)
    return render(
        request, 
        'my_lists.html',
        {'owner' : owner, 'shared_lists' : lists}
    )

def share_list(request, list_id):

    list_ = List.objects.get(id=list_id)
    try:
        user = User.objects.get(email=request.POST.get('sharee'))
    except User.DoesNotExist:
        user = User.objects.create(email=request.POST.get('sharee'))
    
    list_.shared_with.add(user)
    return redirect(str(list_.get_absolute_url()))
