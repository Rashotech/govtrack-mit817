from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from govtracker.models import (
    ProjectCategory, LGA, Contractor, Project, ProjectImage, 
    CitizenPost, PostMedia
)
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds the database with sample data for GovTrack'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@govtrack.ng', 'admin123')
            self.stdout.write(self.style.SUCCESS('✓ Admin user created'))

        # Seed Project Categories
        categories = [
            {'name': 'Road Construction', 'description': 'Road building and rehabilitation projects'},
            {'name': 'Drainage System', 'description': 'Drainage and flood control infrastructure'},
            {'name': 'Streetlight Installation', 'description': 'Street lighting and electrical infrastructure'},
            {'name': 'Water Supply', 'description': 'Water infrastructure and supply projects'},
            {'name': 'Waste Management', 'description': 'Waste collection and management facilities'},
            {'name': 'Bridge Construction', 'description': 'Bridge and overpass projects'},
        ]
        
        for cat_data in categories:
            ProjectCategory.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(categories)} categories created'))

        # Seed LGAs (Lagos State)
        lgas = [
            'Agege', 'Ajeromi-Ifelodun', 'Alimosho', 'Amuwo-Odofin', 'Apapa',
            'Badagry', 'Epe', 'Eti-Osa', 'Ibeju-Lekki', 'Ifako-Ijaiye',
            'Ikeja', 'Ikorodu', 'Kosofe', 'Lagos Island', 'Lagos Mainland',
            'Mushin', 'Ojo', 'Oshodi-Isolo', 'Shomolu', 'Surulere'
        ]
        
        for lga_name in lgas:
            LGA.objects.get_or_create(name=lga_name)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(lgas)} LGAs created'))

        # Seed Contractors
        contractors_data = [
            {'name': 'Julius Berger Nigeria PLC', 'registration_number': 'RC123456', 
             'contact_email': 'info@julius-berger.com', 'contact_phone': '+234-1-2345678'},
            {'name': 'RCC Limited', 'registration_number': 'RC234567',
             'contact_email': 'contact@rccnigeria.com', 'contact_phone': '+234-1-3456789'},
            {'name': 'Arab Contractors Nigeria Ltd', 'registration_number': 'RC345678',
             'contact_email': 'info@arabcontractors.ng', 'contact_phone': '+234-1-4567890'},
            {'name': 'Hitech Construction Company', 'registration_number': 'RC456789',
             'contact_email': 'info@hitechng.com', 'contact_phone': '+234-1-5678901'},
            {'name': 'Setraco Nigeria Limited', 'registration_number': 'RC567890',
             'contact_email': 'contact@setraco.com', 'contact_phone': '+234-1-6789012'},
        ]
        
        for contractor_data in contractors_data:
            Contractor.objects.get_or_create(
                registration_number=contractor_data['registration_number'],
                defaults=contractor_data
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(contractors_data)} contractors created'))

        # Seed Projects
        road_cat = ProjectCategory.objects.get(name='Road Construction')
        drainage_cat = ProjectCategory.objects.get(name='Drainage System')
        light_cat = ProjectCategory.objects.get(name='Streetlight Installation')
        water_cat = ProjectCategory.objects.get(name='Water Supply')
        bridge_cat = ProjectCategory.objects.get(name='Bridge Construction')

        projects_data = [
            # Completed Projects
            {
                'title': 'Lekki-Epe Expressway Rehabilitation (Phase 1)',
                'description': 'Complete rehabilitation of 10km stretch of Lekki-Epe Expressway including road resurfacing and drainage improvement.',
                'category': road_cat,
                'status': 'completed',
                'lga': LGA.objects.get(name='Eti-Osa'),
                'location_address': 'Lekki-Epe Expressway, Lekki Phase 1',
                'latitude': Decimal('6.4474'),
                'longitude': Decimal('3.5617'),
                'ministry': 'Ministry of Works and Infrastructure',
                'contractor': Contractor.objects.get(name='Julius Berger Nigeria PLC'),
                'budget_allocated': Decimal('2500000000'),
                'amount_disbursed': Decimal('2500000000'),
                'date_awarded': date(2023, 1, 15),
                'date_commenced': date(2023, 3, 1),
                'expected_completion_date': date(2024, 12, 31),
                'actual_completion_date': date(2024, 11, 20),
            },
            {
                'title': 'Ikeja GRA Drainage System Upgrade',
                'description': 'Installation of modern drainage channels to prevent flooding in Ikeja GRA residential area.',
                'category': drainage_cat,
                'status': 'completed',
                'lga': LGA.objects.get(name='Ikeja'),
                'location_address': 'Ikeja GRA, Lagos',
                'latitude': Decimal('6.5964'),
                'longitude': Decimal('3.3466'),
                'ministry': 'Ministry of Environment and Water Resources',
                'contractor': Contractor.objects.get(name='RCC Limited'),
                'budget_allocated': Decimal('850000000'),
                'amount_disbursed': Decimal('850000000'),
                'date_awarded': date(2023, 6, 10),
                'date_commenced': date(2023, 7, 15),
                'expected_completion_date': date(2024, 6, 30),
                'actual_completion_date': date(2024, 6, 15),
            },
            {
                'title': 'Badagry Expressway Streetlight Installation',
                'description': 'Installation of 500 solar-powered LED streetlights along Badagry Expressway.',
                'category': light_cat,
                'status': 'completed',
                'lga': LGA.objects.get(name='Badagry'),
                'location_address': 'Badagry Expressway',
                'latitude': Decimal('6.4167'),
                'longitude': Decimal('2.8833'),
                'ministry': 'Ministry of Energy and Mineral Resources',
                'contractor': Contractor.objects.get(name='Hitech Construction Company'),
                'budget_allocated': Decimal('450000000'),
                'amount_disbursed': Decimal('450000000'),
                'date_awarded': date(2023, 9, 1),
                'date_commenced': date(2023, 10, 1),
                'expected_completion_date': date(2024, 3, 31),
                'actual_completion_date': date(2024, 3, 10),
            },

            # Ongoing Projects
            {
                'title': 'Ikorodu-Sagamu Road Reconstruction',
                'description': 'Complete reconstruction of 15km Ikorodu-Sagamu road with dual carriageway and modern drainage.',
                'category': road_cat,
                'status': 'ongoing',
                'lga': LGA.objects.get(name='Ikorodu'),
                'location_address': 'Ikorodu-Sagamu Road',
                'latitude': Decimal('6.6194'),
                'longitude': Decimal('3.5106'),
                'ministry': 'Ministry of Works and Infrastructure',
                'contractor': Contractor.objects.get(name='Julius Berger Nigeria PLC'),
                'budget_allocated': Decimal('5200000000'),
                'amount_disbursed': Decimal('3120000000'),
                'date_awarded': date(2024, 2, 1),
                'date_commenced': date(2024, 4, 15),
                'expected_completion_date': date(2026, 4, 30),
            },
            {
                'title': 'Alimosho Water Supply Infrastructure',
                'description': 'Construction of water treatment plant and distribution network to serve 200,000 residents.',
                'category': water_cat,
                'status': 'ongoing',
                'lga': LGA.objects.get(name='Alimosho'),
                'location_address': 'Alimosho, Lagos',
                'latitude': Decimal('6.5833'),
                'longitude': Decimal('3.2833'),
                'ministry': 'Ministry of Environment and Water Resources',
                'contractor': Contractor.objects.get(name='Arab Contractors Nigeria Ltd'),
                'budget_allocated': Decimal('3800000000'),
                'amount_disbursed': Decimal('1900000000'),
                'date_awarded': date(2024, 1, 10),
                'date_commenced': date(2024, 3, 1),
                'expected_completion_date': date(2025, 12, 31),
            },
            {
                'title': 'Oshodi-Apapa Expressway Rehabilitation',
                'description': 'Major rehabilitation of Oshodi-Apapa expressway including bridge repairs and road expansion.',
                'category': road_cat,
                'status': 'ongoing',
                'lga': LGA.objects.get(name='Oshodi-Isolo'),
                'location_address': 'Oshodi-Apapa Expressway',
                'latitude': Decimal('6.5244'),
                'longitude': Decimal('3.3192'),
                'ministry': 'Ministry of Works and Infrastructure',
                'contractor': Contractor.objects.get(name='RCC Limited'),
                'budget_allocated': Decimal('4500000000'),
                'amount_disbursed': Decimal('2250000000'),
                'date_awarded': date(2024, 5, 1),
                'date_commenced': date(2024, 7, 1),
                'expected_completion_date': date(2026, 6, 30),
            },
            {
                'title': 'Victoria Island Drainage Expansion',
                'description': 'Expansion of drainage network in Victoria Island to address flooding issues.',
                'category': drainage_cat,
                'status': 'ongoing',
                'lga': LGA.objects.get(name='Eti-Osa'),
                'location_address': 'Victoria Island, Lagos',
                'latitude': Decimal('6.4281'),
                'longitude': Decimal('3.4219'),
                'ministry': 'Ministry of Environment and Water Resources',
                'contractor': Contractor.objects.get(name='Setraco Nigeria Limited'),
                'budget_allocated': Decimal('1200000000'),
                'amount_disbursed': Decimal('600000000'),
                'date_awarded': date(2024, 6, 15),
                'date_commenced': date(2024, 8, 1),
                'expected_completion_date': date(2025, 8, 31),
            },

            # Pending Projects
            {
                'title': 'Epe-Ijebu Ode Road Construction',
                'description': 'Construction of new 20km road connecting Epe to Ijebu Ode with modern specifications.',
                'category': road_cat,
                'status': 'pending',
                'lga': LGA.objects.get(name='Epe'),
                'location_address': 'Epe, Lagos',
                'latitude': Decimal('6.5833'),
                'longitude': Decimal('3.9833'),
                'ministry': 'Ministry of Works and Infrastructure',
                'contractor': Contractor.objects.get(name='Julius Berger Nigeria PLC'),
                'budget_allocated': Decimal('6500000000'),
                'amount_disbursed': Decimal('0'),
                'date_awarded': date(2025, 1, 15),
            },
            {
                'title': 'Surulere Streetlight Modernization',
                'description': 'Replacement of old streetlights with energy-efficient LED lights across Surulere LGA.',
                'category': light_cat,
                'status': 'pending',
                'lga': LGA.objects.get(name='Surulere'),
                'location_address': 'Surulere, Lagos',
                'latitude': Decimal('6.4969'),
                'longitude': Decimal('3.3603'),
                'ministry': 'Ministry of Energy and Mineral Resources',
                'contractor': Contractor.objects.get(name='Hitech Construction Company'),
                'budget_allocated': Decimal('320000000'),
                'amount_disbursed': Decimal('0'),
                'date_awarded': date(2025, 2, 1),
            },
            {
                'title': 'Ibeju-Lekki Bridge Construction',
                'description': 'Construction of new bridge to improve connectivity in Ibeju-Lekki area.',
                'category': bridge_cat,
                'status': 'pending',
                'lga': LGA.objects.get(name='Ibeju-Lekki'),
                'location_address': 'Ibeju-Lekki, Lagos',
                'latitude': Decimal('6.4333'),
                'longitude': Decimal('3.8667'),
                'ministry': 'Ministry of Works and Infrastructure',
                'contractor': Contractor.objects.get(name='Arab Contractors Nigeria Ltd'),
                'budget_allocated': Decimal('8900000000'),
                'amount_disbursed': Decimal('0'),
                'date_awarded': date(2025, 3, 1),
            },
            {
                'title': 'Mushin Drainage Network Rehabilitation',
                'description': 'Rehabilitation and expansion of drainage network in Mushin to prevent flooding.',
                'category': drainage_cat,
                'status': 'pending',
                'lga': LGA.objects.get(name='Mushin'),
                'location_address': 'Mushin, Lagos',
                'latitude': Decimal('6.5292'),
                'longitude': Decimal('3.3431'),
                'ministry': 'Ministry of Environment and Water Resources',
                'contractor': None,
                'budget_allocated': Decimal('950000000'),
                'amount_disbursed': Decimal('0'),
                'date_awarded': None,
            },
        ]

        for project_data in projects_data:
            Project.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(projects_data)} projects created'))

        # Seed Citizen Posts
        citizen_posts_data = [
            {
                'title': 'Pothole on Awolowo Road causing accidents',
                'description': 'There is a large pothole on Awolowo Road near the Falomo roundabout that has caused several accidents. The hole is about 2 feet deep and 3 feet wide. Urgent attention needed.',
                'category': 'road',
                'lga': LGA.objects.get(name='Eti-Osa'),
                'location_address': 'Awolowo Road, Ikoyi',
                'latitude': Decimal('6.4541'),
                'longitude': Decimal('3.4316'),
                'submitter_name': 'Adebayo Johnson',
                'submitter_email': 'adebayo.j@email.com',
                'status': 'approved',
                'upvotes': 45,
            },
            {
                'title': 'Blocked drainage causing flooding in Surulere',
                'description': 'The drainage system on Adeniran Ogunsanya Street is completely blocked with refuse and debris. During the last rain, water flooded into several shops and homes. Please help clear this drainage urgently.',
                'category': 'drainage',
                'lga': LGA.objects.get(name='Surulere'),
                'location_address': 'Adeniran Ogunsanya Street, Surulere',
                'latitude': Decimal('6.4969'),
                'longitude': Decimal('3.3603'),
                'submitter_name': 'Chioma Okafor',
                'submitter_email': 'chioma.ok@email.com',
                'status': 'approved',
                'upvotes': 78,
            },
            {
                'title': 'Non-functional streetlights on Agege Motor Road',
                'description': 'All streetlights along Agege Motor Road from Oshodi to Agege have not been working for over 3 months. This has made the area very dangerous at night with increased crime.',
                'category': 'streetlight',
                'lga': LGA.objects.get(name='Agege'),
                'location_address': 'Agege Motor Road',
                'latitude': Decimal('6.6167'),
                'longitude': Decimal('3.3167'),
                'submitter_name': 'Ibrahim Musa',
                'submitter_email': 'ibrahim.m@email.com',
                'status': 'approved',
                'upvotes': 92,
            },
            {
                'title': 'Water supply disruption in Alimosho',
                'description': 'Our community in Alimosho has not had water supply for 2 weeks. The water pipes appear to be damaged. We need urgent intervention.',
                'category': 'water',
                'lga': LGA.objects.get(name='Alimosho'),
                'location_address': 'Ipaja Road, Alimosho',
                'latitude': Decimal('6.5833'),
                'longitude': Decimal('3.2833'),
                'submitter_name': 'Fatima Abdullahi',
                'submitter_email': 'fatima.a@email.com',
                'status': 'approved',
                'upvotes': 63,
            },
            {
                'title': 'Uncollected waste on Ikorodu Road',
                'description': 'Waste has been piling up at the collection point on Ikorodu Road for over a week. The smell is unbearable and attracting rodents.',
                'category': 'waste',
                'lga': LGA.objects.get(name='Kosofe'),
                'location_address': 'Ikorodu Road, Ketu',
                'latitude': Decimal('6.5833'),
                'longitude': Decimal('3.3833'),
                'submitter_name': 'Oluwaseun Adeyemi',
                'submitter_email': 'seun.adeyemi@email.com',
                'status': 'approved',
                'upvotes': 34,
            },
            {
                'title': 'Damaged road at Apapa Port access',
                'description': 'The road leading to Apapa Port is severely damaged with multiple potholes. This is affecting cargo movement and causing delays.',
                'category': 'road',
                'lga': LGA.objects.get(name='Apapa'),
                'location_address': 'Apapa-Oshodi Expressway',
                'latitude': Decimal('6.4489'),
                'longitude': Decimal('3.3594'),
                'submitter_name': 'Emmanuel Okonkwo',
                'submitter_email': 'emma.ok@email.com',
                'status': 'pending',
                'upvotes': 21,
            },
        ]

        for post_data in citizen_posts_data:
            CitizenPost.objects.get_or_create(
                title=post_data['title'],
                defaults=post_data
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(citizen_posts_data)} citizen posts created'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('\nAdmin credentials:'))
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
