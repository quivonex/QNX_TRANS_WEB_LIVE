# your_project/context_processors.py

from company.models import FinancialYears
from django.conf import settings


def financial_year_processor(request):
    financial_year_id = request.session.get('financial_year_id')
    if financial_year_id:
        try:
            financial_year = FinancialYears.objects.get(id=financial_year_id)
        except FinancialYears.DoesNotExist:
            financial_year = None
    else:
        financial_year = None

    return {'financial_year': financial_year}
# Example data structure in your view or context processor


def get_sidebar_data():
    custom_app_list = [
        {
            'name': 'Custom Option 1',
            'label': 'custom-option-1',
            'apps': [
                {
                    'app_label': 'app1',
                    'app_url': '/admin/app1/',
                    'name': 'App 1',
                    'models': [
                        {'object_name': 'Model1', 'admin_url': '/admin/app1/model1/',
                            'name': 'Model 1', 'add_url': '/admin/app1/model1/add/'},
                        # More models...
                    ]
                },
                # More apps...
            ]
        },
        {
            'name': 'Custom Option 2',
            'label': 'custom-option-2',
            'apps': [
                {
                    'app_label': 'app2',
                    'app_url': '/admin/app2/',
                    'name': 'App 2',
                    'models': [
                        {'object_name': 'Model2', 'admin_url': '/admin/app2/model2/',
                            'name': 'Model 2', 'add_url': '/admin/app2/model2/add/'},
                        # More models...
                    ]
                },
                # More apps...
            ]
        },
        # More custom options...
    ]
    return {'custom_app_list': custom_app_list}

def media_absolute_url(request):
    return {
        'MEDIA_URL': request.build_absolute_uri(settings.MEDIA_URL),
    }