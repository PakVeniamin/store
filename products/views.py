from django.shortcuts import render, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from products.models import Products, Categories, Basket


# Create your views here.

def index(request):
    context = {
        'title': 'Store'
    }
    return render(request, 'products/index.html', context)


def products(request, category_id=None, page_numbers=1):
    products = Products.objects.filter(category_id=category_id) if category_id else Products.objects.all()
    per_page = 2
    paginator = Paginator(products, per_page)
    products_paginator = paginator.page(page_numbers)

    context = {
        'title': 'Store - Каталог',
        'products': products_paginator,
        'category': Categories.objects.all(),
        'paginator': paginator
    }
    return render(request, 'products/products.html', context)


@login_required
def basket_add(request, product_id):
    product = Products.objects.get(id=product_id)
    baskets = Basket.objects.filter(user=request.user, product=product)
    if not baskets.exists():
        Basket.objects.create(user=request.user, product=product)
    else:
        basket = baskets.first()
        basket.quantity += 1
        basket.save()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
