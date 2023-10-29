from django.contrib import admin
from products.models import Categories, Products, Basket

admin.site.register(Categories)


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'category')
    fields = ('name', 'description', ('price', 'quantity'), 'image', 'category')
    readonly_fields = ('description', )
    search_fields = ('name', )
    ordering = ('name', )


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity')
    extra = 0