from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Project, CitizenPost, ProjectCategory, LGA, PostUpvote
from decimal import Decimal


# US-01: View All Government Projects
class ProjectListView(ListView):
    model = Project
    template_name = 'govtracker/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        queryset = Project.objects.select_related('category', 'lga', 'contractor').prefetch_related('images')
        
        # US-16: Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location_address__icontains=search) |
                Q(contractor__name__icontains=search)
            )
        
        # US-17: Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # US-17: Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # US-17: Filter by LGA
        lga = self.request.GET.get('lga')
        if lga:
            queryset = queryset.filter(lga_id=lga)
        
        # Filter by budget range
        budget_min = self.request.GET.get('budget_min')
        budget_max = self.request.GET.get('budget_max')
        if budget_min:
            queryset = queryset.filter(budget_allocated__gte=budget_min)
        if budget_max:
            queryset = queryset.filter(budget_allocated__lte=budget_max)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProjectCategory.objects.all()
        context['lgas'] = LGA.objects.all()
        context['status_choices'] = Project.STATUS_CHOICES
        
        # Count by status
        context['ongoing_count'] = Project.objects.filter(status='ongoing').count()
        context['pending_count'] = Project.objects.filter(status='pending').count()
        context['completed_count'] = Project.objects.filter(status='completed').count()
        
        return context


# US-03: View Project Details
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'govtracker/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.select_related('category', 'lga', 'contractor').prefetch_related('images')


# US-13: View Community-Submitted Reports
class CitizenPostListView(ListView):
    model = CitizenPost
    template_name = 'govtracker/citizen_post_list.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        queryset = CitizenPost.objects.filter(status='approved').select_related('lga').prefetch_related('media')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by LGA
        lga = self.request.GET.get('lga')
        if lga:
            queryset = queryset.filter(lga_id=lga)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Sort by most supported
        sort = self.request.GET.get('sort')
        if sort == 'most_supported':
            queryset = queryset.order_by('-upvotes', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lgas'] = LGA.objects.all()
        context['category_choices'] = CitizenPost.CATEGORY_CHOICES
        return context


# US-13: View Citizen Post Detail
class CitizenPostDetailView(DetailView):
    model = CitizenPost
    template_name = 'govtracker/citizen_post_detail.html'
    context_object_name = 'post'
    slug_field = 'reference_number'
    slug_url_kwarg = 'reference_number'

    def get_queryset(self):
        return CitizenPost.objects.filter(status='approved').select_related('lga').prefetch_related('media')


# US-11: Submit a Community Report
class CitizenPostCreateView(CreateView):
    model = CitizenPost
    template_name = 'govtracker/citizen_post_create.html'
    fields = ['title', 'description', 'category', 'lga', 'location_address', 'latitude', 'longitude', 'submitter_name', 'submitter_email']

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle media uploads
        files = self.request.FILES.getlist('media_files')
        for file in files[:5]:  # Max 5 files
            from .models import PostMedia
            media_type = 'image' if file.content_type.startswith('image/') else 'video'
            PostMedia.objects.create(post=self.object, file=file, media_type=media_type)
        
        messages.success(self.request, f'Report submitted successfully! Reference number: {self.object.reference_number}')
        return response

    def get_success_url(self):
        return '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lgas'] = LGA.objects.all()
        context['category_choices'] = CitizenPost.CATEGORY_CHOICES
        return context


# US-14: Upvote a Community Report
@require_POST
def upvote_post(request, reference_number):
    post = get_object_or_404(CitizenPost, reference_number=reference_number, status='approved')
    
    # Check if user already upvoted (using session)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    # Check if already upvoted
    existing_upvote = PostUpvote.objects.filter(post=post, session_key=session_key).first()
    
    if existing_upvote:
        return JsonResponse({'success': False, 'message': 'Already upvoted', 'upvotes': post.upvotes})
    
    # Create upvote
    PostUpvote.objects.create(
        post=post,
        session_key=session_key,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Increment upvotes
    post.upvotes += 1
    post.save()
    
    return JsonResponse({'success': True, 'upvotes': post.upvotes})


# Homepage
def home(request):
    context = {
        'pending_projects': Project.objects.filter(status='pending').select_related('category', 'lga')[:6],
        'ongoing_projects': Project.objects.filter(status='ongoing').select_related('category', 'lga')[:6],
        'completed_projects': Project.objects.filter(status='completed').select_related('category', 'lga')[:6],
        'recent_posts': CitizenPost.objects.filter(status='approved').select_related('lga')[:6],
        'total_projects': Project.objects.count(),
        'ongoing_count': Project.objects.filter(status='ongoing').count(),
        'completed_count': Project.objects.filter(status='completed').count(),
        'pending_count': Project.objects.filter(status='pending').count(),
        'total_posts': CitizenPost.objects.filter(status='approved').count(),
    }
    return render(request, 'govtracker/home.html', context)
