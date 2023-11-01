
from django.urls import path

from products.views import ProductsListView, BasketAddView, BasketRemoveView

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='product'),
    path('category/<int:category_id>/', ProductsListView.as_view(), name='category'),
    path('page/<int:page>/', ProductsListView.as_view(), name='paginator'),
    path('basket/add/<int:product_id>/', BasketAddView.as_view(), name='basket_add'),
    path('basket/remove/<int:basket_id>/', BasketRemoveView.as_view(), name='basket_remove'),
]
