from .models import Donor, Hospital

def user_role(request):
    if request.user.is_authenticated:
        return {
            'is_donor': Donor.objects.filter(user=request.user).exists(),
            'is_hospital': Hospital.objects.filter(user=request.user).exists()
        }
    return {}