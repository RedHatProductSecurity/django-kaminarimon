# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
