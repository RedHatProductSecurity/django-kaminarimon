# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-08-14

### Added

- Simple bind fallback for test/dev environments without Kerberos
- `KAMINARIMON_LDAP_BASE_DN` setting to configure base DN (defaults to IPA)
- `KAMINARIMON_LDAP_TIMEOUT` setting for LDAP operation timeouts (defaults to
  10 seconds)
- `escape_filter_chars` to LDAP search filters to prevent injection

### Changed

- Migrated LDAP directory from legacy Red Hat LDAP (`dc=redhat,dc=com`) to IPA
  LDAP (`dc=ipa,dc=redhat,dc=com`)
- Replaced anonymous LDAP bind with GSSAPI (Kerberos) as default
  authentication method to LDAP server
- Renamed settings:
  - `AUTH_LDAP_SERVER_URI` (single string) → `KAMINARIMON_LDAP_SERVERS` (list)
  - New: `KAMINARIMON_LDAP_BIND_DN`, `KAMINARIMON_LDAP_BIND_PASSWORD`
- Single LDAP connection per authentication request instead of one per query
- Group search uses `groupOfNames`/`member` to match the IPA group schema,
  instead of the legacy directory's `groupOfUniqueNames`/`uniqueMember`
- User search uses `uid` attribute under `cn=users,cn=accounts` (IPA structure)

### Removed

- Removed service account fallback search in separate `ou=serviceaccounts`
  container (IPA stores all accounts in `cn=users`)
- Removed anonymous LDAP bind support

## [0.2.2] - 2026-04-07

### Fixed

- Remove invalid 'in: header' field from Kerberos OpenAPI security scheme definition

## [0.2.1] - 2025-06-03

### Fixed

- The refresh token view explicitly requires no authentication/authorization so
  that it can be a drop-in replacement for the django_rest_framework_simplejwt
  library view that it replaces.
- The refresh token view now contains the proper OpenAPI annotations.

## [0.2.0] - 2025-06-02

### Added

- Cookies are now issued when authenticating via `/auth/token`
  and will be accepted in lieu of an explicit payload in
  `/auth/token/refresh` via GET request (OSIDB-4243)

## [0.1.0] - 2025-05-29

### Added

- LDAPRemoteUser backend for LDAP authorization
- KerberosAuthentication authentication class
- krb5_obtain_token_pair_view for issuing JWT
