from django.contrib import admin
from .models import (
    ProjectCategory, LGA, Contractor, Project, ProjectImage,
    CitizenPost, PostMedia, PostUpvote
)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'created_at']
    search_fields = ['name']


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration_number', 'contact_email', 'contact_phone']
    search_fields = ['name', 'registration_number']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'category', 'lga', 'contractor', 'budget_allocated', 'updated_at']
    list_filter = ['status', 'category', 'lga']
    search_fields = ['title', 'description', 'location_address']
    inlines = [ProjectImageInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'image_type', 'caption', 'uploaded_at']
    list_filter = ['image_type']


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1


@admin.register(CitizenPost)
class CitizenPostAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'category', 'status', 'upvotes', 'created_at']
    list_filter = ['status', 'category', 'lga']
    search_fields = ['title', 'description', 'reference_number']
    readonly_fields = ['reference_number', 'created_at', 'updated_at']
    inlines = [PostMediaInline]


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ['post', 'media_type', 'uploaded_at']
    list_filter = ['media_type']


@admin.register(PostUpvote)
class PostUpvoteAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
