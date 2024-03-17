from register.models import UserProfile, OnlineAccount, BankAccount
from django.core.exceptions import ObjectDoesNotExist
from payapp.models import TransactionHistory


# function for  account
def account_context(request):
    """
    Retrieves the user's account information and context for rendering in a template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the user's account information and context.
            The dictionary may contain the following keys:
                - 'online_account' (OnlineAccount): The user's online account information.
                - 'user_profile' (UserProfile): The user's profile information.
                - 'bank_accounts' (QuerySet): The user's bank accounts.
    """
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


def transaction_history_context(request):
    context = {}
    if request.user.is_authenticated:
        transaction_history = TransactionHistory.objects.filter(sender=request.user).order_by('-created_at')
        context['transaction_history'] = transaction_history
    return context