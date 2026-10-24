from .models import CaseFile, DetectiveProfile

def global_case_context(request):
    """
    Supplies global template context such as active profile and available cases.
    Includes defensive exception handling during migrations or early boot.
    """
    context = {}
    try:
        context['all_cases_nav'] = list(CaseFile.objects.filter(is_published=True).order_by('order')[:5])
    except Exception:
        context['all_cases_nav'] = []

    if request.user.is_authenticated:
        try:
            profile, created = DetectiveProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'badge_number': f"DET-{request.user.id:04d}",
                    'rank': 'Rookie Investigator'
                }
            )
            context['current_profile'] = profile
        except Exception:
            context['current_profile'] = None
    else:
        context['current_profile'] = None

    return context
