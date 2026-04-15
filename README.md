# django-kaminarimon
## What is it?

`django-kaminarimon` (or just kaminarimon) is a library for integrating
kerberos authentication and ldap authorization into a Django/DRF application.

While users can independently choose to integrate one or the other, it is
designed to use both and use JWTs as interface for client<->server auth.

## How to use

### For Kerberos authentication

Set `kaminarimon.auth.KerberosAuthentication` as either:
* `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]`
* Individually at the view level

This will require the client to send a request with the header
`Authorization: Negotiate <token>` which will initiate the SPNEGO protocol.

If the client does not send the aforementioned header when requesting a view
that requires Kerberos authentication, the `WWW-Authenticate` is sent back to
the client, signaling that it should use SPNEGO protocol for authentication.

> [!TIP]
> By default the host or service principal will use the service's FQDN, but it
> can be overridden by setting the `KRB5_HOSTNAME` environment variable.

### For LDAP authorization

> [!NOTE]
> A lot of the behavior of this authentication backend is currently hardcoded
> to only work with Red Hat systems.

> [!NOTE]
> Anonymous user access to the LDAP server is required for querying user
> information.

> [!WARNING]
> Usage of LDAP authorization on its own withour Kerberos authentication is
> discouraged as it **only** handles authorization, it does not actually
> perform any sort of authentication of the user against the LDAP server,
> i.e. it simply loads the user's groups from the LDAP server.

Simply add the `kaminarimon.backend.LDAPRemoteUser` to the
`AUTHENTICATION_BACKENDS` django setting.

Required settings:
* `AUTH_LDAP_SERVER_URI` -- URI to the LDAP server
* `PUBLIC_READ_GROUPS` -- List of names of groups that, if the user is a member of,
  grant access to the application.
  `SERVICE_MANAGE_GROUP` -- Group that denotes a user as staff and/or superuser.

### Intended usage (kerberos authentication, ldap authorization)

The same settings, warnings, notes and tips for the previous sections apply.

Ensure `kaminarimon.backend.LDAPRemoteUser` is in `AUTHENTICATION_BACKENDS`,
and add `kaminarimon.views.krb5_obtain_token_pair_view` to your `urls.py`,
it is through this view that clients will obtain access and refresh JWT.

In order to protect other views with such authentication tokens, simply mark the
authentication method as `rest_framework_simplejwt.authentication.JWTAuthentication`
or similar as, or set it globally using `DEFAULT_AUTHENTICATION_CLASSES`.

### Middleware-based authentication

`django-restframework` and `drf-simplejwt` provide view-based authentication,
meaning that by default authentication is handled by DRF _after_ middleware has
run. This is usually not a big issue unless you have other middleware that
requires accessing e.g. the user object, this can happen when doing traceability
and you want to log the currently logged-in user for every request.

`django-kaminarimon` provides a way to authenticate the user using the
authentication class from `drf-simplejwt` in middleware, meaning that
request.user gets populated before reaching the corresponding DRF view.

The DRF view won't count the user as authenticated unless it also uses
the accompanying authentication class which can be set per-view or in
`DEFAULT_AUTHENTICATION_CLASSES`, like with any other DRF authentication
class.

To enable, add `kaminarimon.middleware.JWTAuthenticationMiddleware` to your
Django settings and `kaminarimon.auth.MiddlewareJWTAuthentication` either to
your `DEFAULT_AUTHENTICATION_CLASSES` or to individual views.

## Browser-based applications

If your service will be used by browser-based applications and security of tokens
is a concern, you can add `kaminarimon.views.refresh_token` to your
`urls.py`, this view will accept a cookie set by
`kaminarimon.views.krb5_obtain_token_pair_view` in order to provide a fresh
access token without requiring the client to store/handle the refresh token.

The cookie is by default httpOnly, secure and sameSite=Strict.

## Running tests

```bash
cd tests/
podman compose -f docker-compose.yml up -d
pytest .
```
