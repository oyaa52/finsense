from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, User
from allauth.account.signals import user_signed_up, user_logged_in as allauth_user_logged_in
from allauth.socialaccount.signals import pre_social_login
from rest_framework.authtoken.models import Token
from django.core.cache import cache
import uuid


# 새로운 사용자가 생성될 때 또는 기존 사용자가 저장될 때 Profile 객체를 보장 (get_or_create 사용)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile_on_user_save(sender, instance, created, **kwargs):
    profile, profile_created_flag = Profile.objects.get_or_create(user=instance)
    if created and profile_created_flag:
        print(f"[DEBUG] ProfileAutoCreate: Profile CREATED for new user '{instance.username}'.")
    elif not created and profile_created_flag:
        # 이 경우는 User는 기존에 있었지만 Profile이 없어서 생성된 경우
        print(f"[DEBUG] ProfileAutoCreate: Profile was MISSING and CREATED for existing user '{instance.username}'.")
    # else: Profile이 이미 존재하고 User도 기존에 있었거나, User가 새로 생성되면서 Profile도 잘 생성된 경우(위의 created and profile_created_flag)


# user_signed_up 시그널은 소셜 가입 포함, 일반 가입 시에도 발생할 수 있음.
# 여기서는 주로 소셜 가입 시 추가 정보(프로필 이미지) 업데이트에 초점.
@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    print(f"[DEBUG] UserSignedUp: User '{user.username}' (ID: {user.pk}) signed up.")
    # post_save 핸들러(ensure_profile_on_user_save)에 의해 Profile은 이미 생성/보장됨.
    # 여기서는 해당 프로필을 가져와서 소셜 정보로 업데이트.
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        # 이론적으로는 발생하면 안되지만, 방어적으로 get_or_create 사용 가능
        profile, _ = Profile.objects.get_or_create(user=user)
        print(f"[DEBUG] UserSignedUp: Profile was missing for user {user.pk}, get_or_create fallback executed.")
    
    print(f"[DEBUG] UserSignedUp: Profile ensured/retrieved for user {user.pk}.")

    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        print(f"[DEBUG] UserSignedUp: Social sign up detected for user {user.pk}. Provider: {sociallogin.account.provider}")
        profile_image_url = None
        extra_data = sociallogin.account.extra_data
        provider_id = sociallogin.account.provider

        if provider_id == 'google':
            profile_image_url = extra_data.get('picture')
        elif provider_id == 'kakao':
            kakao_properties = extra_data.get('properties', {})
            profile_image_url = kakao_properties.get('profile_image')
        
        if profile_image_url:
            if profile.social_profile_image_url != profile_image_url:
                profile.social_profile_image_url = profile_image_url
                profile.save()
                print(f"[DEBUG] UserSignedUp: Updated social profile image for user {user.pk} from {provider_id}.")
            # else:
                # print(f"[DEBUG] UserSignedUp: Social profile image is already up-to-date for user {user.pk}.")
        else:
            print(f"[DEBUG] UserSignedUp: No profile image URL found in social account data for user {user.pk} from {provider_id}.")
    else:
        print(f"[DEBUG] UserSignedUp: Standard (non-social) sign up for user {user.pk}.")


@receiver(pre_social_login)
def handle_pre_social_login(sender, request, sociallogin, **kwargs):
    if sociallogin: 
        one_time_token = str(uuid.uuid4())
        # request 객체 대신 sociallogin 객체에 OTT 저장
        sociallogin.one_time_token_for_redirect = one_time_token 
        print(f"[DEBUG] PreSocialLogin: Generated OTT '{one_time_token}' for social login. Stored in sociallogin object.")
        

@receiver(allauth_user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    print(f"[DEBUG] AllauthUserLoggedIn: User '{user.username}' (ID: {user.pk}) logged in via allauth signal.")
    
    sociallogin = kwargs.get('sociallogin', None) 
    one_time_token = None

    if sociallogin:
        one_time_token = getattr(sociallogin, 'one_time_token_for_redirect', None)
        if one_time_token:
            print(f"[DEBUG] AllauthUserLoggedIn: OTT '{one_time_token}' found in sociallogin object.")
        else:
            # allauth의 user_logged_in 시그널은 sociallogin이 있을 때 OTT도 있어야 정상.
            # request fallback은 큰 의미가 없을 수 있으나, 디버깅을 위해 남겨둘 수 있음.
            print(f"[DEBUG] AllauthUserLoggedIn: OTT not found in sociallogin object. This might be unexpected for social logins.")
            one_time_token = getattr(request, 'one_time_token_for_redirect', None) # Fallback (less likely to work if sociallogin is present)
            if one_time_token:
                 print(f"[DEBUG] AllauthUserLoggedIn: OTT '{one_time_token}' found in request object (fallback).")
    else:
        print(f"[DEBUG] AllauthUserLoggedIn: No sociallogin object in kwargs. This is likely a non-social login.")

    if one_time_token and sociallogin:
        print(f"[DEBUG] AllauthUserLoggedIn: Social login with OTT '{one_time_token}'. Creating/getting API token for user {user.pk}.")
        api_token, created = Token.objects.get_or_create(user=user)
        if created:
            print(f"[DEBUG] AllauthUserLoggedIn: New API token created for user {user.pk}.")
        else:
            print(f"[DEBUG] AllauthUserLoggedIn: Existing API token retrieved for user {user.pk}.")

        cache_key = f"ott_{one_time_token}"
        token_data = {
            'api_token': api_token.key,
            'user_id': user.pk
        }
        cache.set(cache_key, token_data, timeout=300) 
        print(f"[DEBUG] AllauthUserLoggedIn: API token and user ID for user {user.pk} cached with key '{cache_key}'. Token: {api_token.key[:5]}...")
        
        if hasattr(sociallogin, 'one_time_token_for_redirect'):
            delattr(sociallogin, 'one_time_token_for_redirect')
            print(f"[DEBUG] AllauthUserLoggedIn: OTT removed from sociallogin object after use.")

    elif sociallogin and not one_time_token:
        print(f"[DEBUG] AllauthUserLoggedIn: Social login detected, but no OTT found. API token not cached via OTT.")
    elif not sociallogin:
        # 일반 로그인 (username/password)의 경우. 세션 기반 토큰을 사용하거나 다른 처리를 할 수 있음.
        # 현재 OTT 방식에 집중하므로, 여기서는 특별한 처리를 하지 않음.
        print(f"[DEBUG] AllauthUserLoggedIn: Standard (non-social) login flow for user '{user.username}'. No OTT processing.")


# 아래 ensure_profile_exists 함수는 ensure_profile_on_user_save 로 대체되었으므로 주석 처리 또는 삭제합니다.
# @receiver(post_save, sender=User)
# def ensure_profile_exists(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#         print(f"[DEBUG] PostSaveUser: Profile CREATED for new user '{instance.username}'.")
#     else:
#         # 기존 사용자의 경우, Profile이 없을 때만 생성 (user_signed_up에서 이미 처리할 수도 있음)
#         profile, profile_created = Profile.objects.get_or_create(user=instance)
#         if profile_created:
#             print(f"[DEBUG] PostSaveUser: Profile GET_OR_CREATED for existing user '{instance.username}'.")
#         pass

# 나머지 불필요한 시그널 핸들러들 (social_account_added, social_account_updated 등)은
# 이전 단계에서 이미 주석 처리되었으므로 그대로 둡니다.

