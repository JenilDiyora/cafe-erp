from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'product_count')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'is_available',
        'is_featured', 'is_bestseller', 'vegetarian', 'display_order'
    )
    list_editable = ('price', 'is_available', 'is_featured', 'is_bestseller', 'display_order')
    list_filter = ('category', 'is_available', 'is_featured', 'is_bestseller', 'vegetarian', 'spicy')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category', 'display_order', 'name')
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'price', 'image')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'description')
        }),
        ('Attributes & Flags', {
            'fields': ('is_available', 'is_featured', 'is_bestseller', 'vegetarian', 'spicy', 'allergen_information')
        }),
        ('Display & Ordering', {
            'fields': ('display_order',)
        }),
    )

