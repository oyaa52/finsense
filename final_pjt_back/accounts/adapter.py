from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def _get_ott_from_sociallogin_or_request(self, request, sociallogin=None):
        """Helper to get OTT from sociallogin (primary) or request (fallback)."""
        ott = None
        if sociallogin and hasattr(sociallogin, 'one_time_token_for_redirect'):
            ott = sociallogin.one_time_token_for_redirect
            if ott:
                print(f"[DEBUG] CustomSocialAccountAdapter: OTT '{ott}' found in sociallogin object.")
                return ott
        
        # Fallback or if sociallogin not directly available in this adapter method context
        # Some adapter methods might only have `request`.
        # We rely on `pre_social_login` or other upstream code to potentially store it on `request`
        # if it also stored it on `sociallogin`.
        # However, the primary source should be `sociallogin` if available.
        ott_req = getattr(request, 'one_time_token_for_redirect', None)
        if ott_req:
            print(f"[DEBUG] CustomSocialAccountAdapter: OTT '{ott_req}' found in request object (fallback or primary for this context).")
            return ott_req
        
        # If sociallogin was passed but OTT was not on it, and also not on request, then no OTT.
        # Or if sociallogin was not passed, and OTT not on request.
        print(f"[DEBUG] CustomSocialAccountAdapter: OTT not found in sociallogin or request object.")
        return None

    def _add_ott_to_url(self, url, ott):
        """Helper to add OTT to a URL's query parameters."""
        if not ott:
            return url
        
        print(f"[DEBUG] CustomSocialAccountAdapter: Adding OTT '{ott}' to URL: {url}")
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params['ott'] = [ott]
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query))
        print(f"[DEBUG] CustomSocialAccountAdapter: Redirect URL with OTT: {new_url}")
        return new_url

    def get_connect_redirect_url(self, request, sociallogin):
        assert request.user.is_authenticated
        url = getattr(settings, 'LOGIN_REDIRECT_URL', "/")
        
        # sociallogin is directly available here
        ott = self._get_ott_from_sociallogin_or_request(request, sociallogin)
        return self._add_ott_to_url(url, ott)

    def get_login_redirect_url(self, request):
        # This method from DefaultAccountAdapter is called by allauth for general logins
        # and can also be a fallback for social logins if specific redirects aren't set.
        # We need to check if `sociallogin` is available on the request, often set by allauth middleware/views.
        url = super().get_login_redirect_url(request) # Gets LOGIN_REDIRECT_URL or 'next'
        
        sociallogin_on_request = getattr(request, 'sociallogin', None)
        if sociallogin_on_request:
            print(f"[DEBUG] CustomSocialAccountAdapter (get_login_redirect_url): sociallogin object found on request.")
            ott = self._get_ott_from_sociallogin_or_request(request, sociallogin_on_request)
        else:
            print(f"[DEBUG] CustomSocialAccountAdapter (get_login_redirect_url): sociallogin object NOT found on request. Checking request directly for OTT.")
            ott = self._get_ott_from_sociallogin_or_request(request) # Pass only request
            
        return self._add_ott_to_url(url, ott)


class CustomAccountAdapter(DefaultAccountAdapter):
    # This adapter is for general account actions, not specifically social.
    # If a social login flow somehow ends up calling this for its redirect URL,
    # we should try to get OTT if available (e.g., from request.sociallogin).
    def get_login_redirect_url(self, request):
        url = super().get_login_redirect_url(request)
        ott = None
        sociallogin_on_request = getattr(request, 'sociallogin', None)

        if sociallogin_on_request and hasattr(sociallogin_on_request, 'one_time_token_for_redirect'):
            ott = sociallogin_on_request.one_time_token_for_redirect
            if ott:
                print(f"[DEBUG] CustomAccountAdapter (get_login_redirect_url): OTT '{ott}' found in request.sociallogin.")
        else:
            # Fallback if sociallogin not on request or no OTT on it.
            # This might be a non-social login, or OTT was not set as expected.
            ott_req = getattr(request, 'one_time_token_for_redirect', None)
            if ott_req:
                ott = ott_req
                print(f"[DEBUG] CustomAccountAdapter (get_login_redirect_url): OTT '{ott}' found directly in request (fallback).")

        if ott:
            print(f"[DEBUG] CustomAccountAdapter (get_login_redirect_url): Adding OTT '{ott}' to URL: {url}")
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            query_params['ott'] = [ott]
            new_query = urlencode(query_params, doseq=True)
            url = urlunparse(parsed_url._replace(query=new_query))
            print(f"[DEBUG] CustomAccountAdapter (get_login_redirect_url): Redirect URL with OTT: {url}")
        return url 