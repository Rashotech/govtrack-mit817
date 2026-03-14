from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Project Categories"

    def __str__(self):
        return self.name


class LGA(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, default="Lagos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Local Government Area"
        verbose_name_plural = "Local Government Areas"

    def __str__(self):
        return self.name


class Contractor(models.Model):
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(ProjectCategory, on_delete=models.PROTECT, related_name='projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    lga = models.ForeignKey(LGA, on_delete=models.PROTECT, related_name='projects')
    location_address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    ministry = models.CharField(max_length=255, blank=True)
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')

    budget_allocated = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    amount_disbursed = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    date_awarded = models.DateField(null=True, blank=True)
    date_commenced = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_projects')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def status_color(self):
        colors = {'pending': 'red', 'ongoing': 'yellow', 'completed': 'green'}
        return colors.get(self.status, 'gray')


class ProjectImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('before', 'Site Before Work'),
        ('progress', 'Work in Progress'),
        ('completed', 'Completed'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/%Y/%m/%d/')
    caption = models.CharField(max_length=255, blank=True)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='other')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['image_type', '-uploaded_at']

    def __str__(self):
        return f"{self.project.title} - {self.get_image_type_display()}"


class CitizenPost(models.Model):
    CATEGORY_CHOICES = [
        ('road', 'Road'),
        ('drainage', 'Drainage'),
        ('streetlight', 'Streetlight'),
        ('water', 'Water Supply'),
        ('waste', 'Waste Management'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    lga = models.ForeignKey(LGA, on_delete=models.PROTECT, related_name='citizen_posts', null=True, blank=True)
    location_address = models.CharField(max_length=500, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    submitter_name = models.CharField(max_length=255, blank=True)
    submitter_email = models.EmailField(blank=True)
    submitter_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')

    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    upvotes = models.IntegerField(default=0)

    moderation_notes = models.TextField(blank=True)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_posts')
    moderated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import random
            import string
            self.reference_number = 'CP' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class PostMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    post = models.ForeignKey(CitizenPost, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='citizen_posts/%Y/%m/%d/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Post Media"

    def __str__(self):
        return f"{self.post.reference_number} - {self.media_type}"


class PostUpvote(models.Model):
    post = models.ForeignKey(CitizenPost, on_delete=models.CASCADE, related_name='upvote_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['post', 'user'], ['post', 'session_key']]

    def __str__(self):
        return f"Upvote for {self.post.reference_number}"
