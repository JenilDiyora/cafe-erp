from django.contrib import admin
from .models import GalleryCategory, GalleryImage


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'image_count')
    list_editable = ('is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = "Images"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'display_order', 'created_at')
    list_editable = ('is_active', 'display_order')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'caption')
    ordering = ('display_order', '-created_at')

