# Public GitHub preparation notes

This repository is a cleaned copy of the student's original coursework archive, not a live deployment.

Changes made before public sharing:

1. **Removed** the original `webapps.db` file, which can contain account data and password hashes.
2. **Removed** `localhost.key` and `localhost.crt` (local TLS key/certificate).
3. **Removed** the hard-coded Django `SECRET_KEY` default and replaced it with environment-driven configuration plus a temporary locally-generated key when debug is enabled.
4. **Removed** the insecure automatic superuser with a publicly known password from `register/apps.py`; developers can run `python manage.py createsuperuser` instead.
5. **Removed** the original test that asserted the insecure automatic admin credentials existed.
6. **Restricted** the payment request approval and rejection endpoints to POST requests (the existing forms already use POST).
7. **Updated** `.gitignore` to exclude databases, private keys, credentials, virtual environments and generated files.
8. **Added** a README and an example environment configuration file.

Most application functionality and other tests are retained from the uploaded source code. No personal or business data from the excluded files is included.

**Important:** If any of the excluded credentials were used on a deployed service, replace or revoke them there. Removing them from a public ZIP does not invalidate them elsewhere. This is still educational code; do not treat it as secure production software.
