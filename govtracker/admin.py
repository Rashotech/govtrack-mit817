from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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


class GovTrackerAdminSite(admin.AdminSite):
    site_header = "GovTracker Administration"
    site_title = "GovTracker Admin"
    index_title = "Dashboard"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard-export/', self.admin_view(self.export_dashboard), name='dashboard_export'),
            path('dashboard-export-pdf/', self.admin_view(self.export_dashboard_pdf), name='dashboard_export_pdf'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if not date_from and not date_to:
            date_to = datetime.now().date()
            date_from = date_to - timedelta(days=30)
        
        projects_qs = Project.objects.all()
        posts_qs = CitizenPost.objects.filter(status='approved')
        
        if date_from:
            projects_qs = projects_qs.filter(created_at__date__gte=date_from)
            posts_qs = posts_qs.filter(created_at__date__gte=date_from)
        if date_to:
            projects_qs = projects_qs.filter(created_at__date__lte=date_to)
            posts_qs = posts_qs.filter(created_at__date__lte=date_to)
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_projects': projects_qs.count(),
            'pending_count': projects_qs.filter(status='pending').count(),
            'ongoing_count': projects_qs.filter(status='ongoing').count(),
            'completed_count': projects_qs.filter(status='completed').count(),
            'total_posts': posts_qs.count(),
            'most_supported_posts': posts_qs.order_by('-upvotes')[:5],
            'date_from': date_from,
            'date_to': date_to,
        })
        
        return super().index(request, extra_context)
    
    def export_dashboard(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dashboard_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Dashboard Report'])
        writer.writerow(['Date Range:', f'{date_from or "All"} to {date_to or "All"}'])
        writer.writerow([])
        
        projects_qs = Project.objects.all()
        if date_from:
            projects_qs = projects_qs.filter(created_at__date__gte=date_from)
        if date_to:
            projects_qs = projects_qs.filter(created_at__date__lte=date_to)
        
        writer.writerow(['Projects Summary'])
        writer.writerow(['Status', 'Count'])
        writer.writerow(['Pending', projects_qs.filter(status='pending').count()])
        writer.writerow(['Ongoing', projects_qs.filter(status='ongoing').count()])
        writer.writerow(['Completed', projects_qs.filter(status='completed').count()])
        writer.writerow(['Total', projects_qs.count()])
        writer.writerow([])
        
        posts_qs = CitizenPost.objects.filter(status='approved')
        if date_from:
            posts_qs = posts_qs.filter(created_at__date__gte=date_from)
        if date_to:
            posts_qs = posts_qs.filter(created_at__date__lte=date_to)
        
        writer.writerow(['Citizen Posts Summary'])
        writer.writerow(['Total Approved Posts', posts_qs.count()])
        writer.writerow([])
        
        writer.writerow(['Most Supported Posts'])
        writer.writerow(['Reference', 'Title', 'Upvotes', 'Category'])
        for post in posts_qs.order_by('-upvotes')[:10]:
            writer.writerow([post.reference_number, post.title, post.upvotes, post.get_category_display()])
        
        return response
    
    def export_dashboard_pdf(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dashboard_report.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1565c0'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        elements.append(Paragraph('GovTracker Dashboard Report', title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Date Range
        date_range_text = f"Date Range: {date_from or 'All'} to {date_to or 'All'}"
        elements.append(Paragraph(date_range_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Projects Summary
        projects_qs = Project.objects.all()
        if date_from:
            projects_qs = projects_qs.filter(created_at__date__gte=date_from)
        if date_to:
            projects_qs = projects_qs.filter(created_at__date__lte=date_to)
        
        elements.append(Paragraph('Projects Summary', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        project_data = [
            ['Status', 'Count'],
            ['Pending', str(projects_qs.filter(status='pending').count())],
            ['Ongoing', str(projects_qs.filter(status='ongoing').count())],
            ['Completed', str(projects_qs.filter(status='completed').count())],
            ['Total', str(projects_qs.count())],
        ]
        
        project_table = Table(project_data, colWidths=[3*inch, 2*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#417690')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(project_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Citizen Posts Summary
        posts_qs = CitizenPost.objects.filter(status='approved')
        if date_from:
            posts_qs = posts_qs.filter(created_at__date__gte=date_from)
        if date_to:
            posts_qs = posts_qs.filter(created_at__date__lte=date_to)
        
        elements.append(Paragraph('Citizen Posts Summary', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        post_summary_data = [
            ['Metric', 'Value'],
            ['Total Approved Posts', str(posts_qs.count())],
        ]
        
        post_summary_table = Table(post_summary_data, colWidths=[3*inch, 2*inch])
        post_summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#417690')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(post_summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Most Supported Posts
        elements.append(Paragraph('Most Supported Posts (Top 10)', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        supported_posts_data = [['Reference', 'Title', 'Upvotes', 'Category']]
        for post in posts_qs.order_by('-upvotes')[:10]:
            title = post.title[:40] + '...' if len(post.title) > 40 else post.title
            supported_posts_data.append([
                post.reference_number,
                title,
                str(post.upvotes),
                post.get_category_display()
            ])
        
        if len(supported_posts_data) == 1:
            supported_posts_data.append(['No posts found', '', '', ''])
        
        supported_table = Table(supported_posts_data, colWidths=[1.2*inch, 2.5*inch, 0.8*inch, 1*inch])
        supported_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#417690')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(supported_table)
        
        doc.build(elements)
        return response

admin_site = GovTrackerAdminSite(name='govtracker_admin')

admin_site.register(ProjectCategory, ProjectCategoryAdmin)
admin_site.register(LGA, LGAAdmin)
admin_site.register(Contractor, ContractorAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(ProjectImage, ProjectImageAdmin)
admin_site.register(CitizenPost, CitizenPostAdmin)
admin_site.register(PostMedia, PostMediaAdmin)
admin_site.register(PostUpvote, PostUpvoteAdmin)
