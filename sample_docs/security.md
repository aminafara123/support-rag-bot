# Account Security

## Resetting your password

If you forgot your password, click "Forgot password" on the login page and enter your email. We'll send a reset link that is valid for 1 hour. For security, the link can only be used once.

## Two-factor authentication (2FA)

We strongly recommend enabling 2FA. Go to Settings > Security > Two-factor authentication and scan the QR code with an authenticator app such as Google Authenticator or 1Password. Save your backup codes somewhere safe; each code can be used once if you lose your device.

## Single sign-on (SSO)

Business plan workspaces can enable SAML SSO with providers like Okta, Azure AD, and Google Workspace. Go to Settings > Security > SSO, upload your identity provider's metadata, and assign the Nimbus app to your users. When SSO is enforced, password login is disabled for all members.

## Sessions and devices

You can view active sessions under Settings > Security > Sessions and revoke any you don't recognize. Sessions expire automatically after 30 days of inactivity.

## Data privacy

Nimbus encrypts data in transit with TLS 1.2+ and at rest with AES-256. We are SOC 2 Type II audited and never sell your data.
