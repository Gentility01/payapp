from register.models import UserProfile, OnlineAccount, BankAccount
from django.core.exceptions import ObjectDoesNotExist


def account_context(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # If UserProfile does not exist, create one
            user_profile = UserProfile.objects.create(user=user)
        except ObjectDoesNotExist:
            # Handle other ObjectDoesNotExist exceptions if necessary
            pass

        try:
            online_account = OnlineAccount.objects.get(user=user)
            context['online_account'] = online_account
        except OnlineAccount.DoesNotExist:
            pass
        
        bank_accounts = BankAccount.objects.filter(user=user)
        context['user_profile'] = user_profile
        context['bank_accounts'] = bank_accounts
    return context