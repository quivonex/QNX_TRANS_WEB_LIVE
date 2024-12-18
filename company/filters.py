from django.db.models import Q

def apply_filters(model, filters):
    """
    Apply dynamic filters to a Django model queryset.

    Args:
        model: The Django model to filter.
        filters: A dictionary where keys are field names with operators, and values are the filter values.

    Returns:
        Filtered queryset.
    """
    query = Q()
    
    # Iterate over the filters dictionary
    for field, value in filters.items():
        # Apply the filter directly if it contains a valid field name and operator
        if hasattr(model, field.split('__')[0]):  # Ensure the field exists in the model
            query &= Q(**{field: value})  # Apply dynamic field filter

    return model.objects.filter(query)
