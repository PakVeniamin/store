from django.shortcuts import render, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from products.models import Products, Categories, Basket
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView


# Create your views here.

class IndexView(TemplateView):
    template_name = 'products/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data()
        context['title'] = 'Store'
        return context


class ProductsListView(ListView):
    model = Products
    template_name = 'products/products.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = super(ProductsListView, self).get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id) if category_id else queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsListView, self).get_context_data()
        context['title'] = 'Store - Каталог'
        context['categories'] = Categories.objects.all()
        return context


class BasketAddView(View):
    model = Basket
    template_name = 'products/products.html'

    def post(self, request, product_id):
        product = Products.objects.get(id=product_id)
        baskets = Basket.objects.filter(user=request.user, product=product)
        if not baskets.exists():
            Basket.objects.create(user=request.user, product=product)
        else:
            basket = baskets.first()
            basket.quantity += 1
            basket.save()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class BasketRemoveView(View):
    def post(self, request, basket_id):
        basket = Basket.objects.get(id=basket_id)
        basket.delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
