# Azure AD Authentication Setup — Odoo 19 CE (Path 2: Implicit Flow)

## Overview

This guide configures Odoo to allow users to sign in with their Microsoft Azure AD accounts using OAuth2 implicit flow. No custom module is required — configuration is done entirely in Azure Portal and Odoo settings.

**What users will see:** A "Sign in with Microsoft" button on the Odoo login page alongside the normal username/password form.

**Limitations of this approach:**
- Uses implicit flow (Azure AD considers this legacy but still supports it)
- Requires IT to enable "Access tokens" implicit grant on the App Registration
- For a more secure alternative, see Path 3 (authorization code flow)

---

## Part 1 — Azure AD Setup (IT)

### Step 1: Create an App Registration

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Fill in:
   - **Name:** `Odoo Dev` (or `Odoo ERP` for production)
   - **Supported account types:** `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI:** Leave blank for now
4. Click **Register**
5. **Copy and save:**
   - `Application (client) ID` — shown on the Overview page
   - `Directory (tenant) ID` — shown on the Overview page

---

### Step 2: Add Redirect URI

1. In the App Registration, go to **Authentication**
2. Under **Platform configurations**, click **Add a platform** → **Web**
3. Add the Redirect URI:

   **Development:**
   ```
   http://localhost:8072/auth_oauth/signin
   ```

   **Production (add later):**
   ```
   https://yourdomain.com/auth_oauth/signin
   ```

4. Click **Configure**

---

### Step 3: Enable Implicit Grant

Still under **Authentication**, scroll to **Implicit grant and hybrid flows**:

```
☑ Access tokens (used for implicit flows)
☑ ID tokens (used for implicit and hybrid flows)
```

Click **Save**.

> **Note for IT:** This enables the legacy implicit flow. Azure AD still supports it but recommends authorization code flow for new applications. This can be changed to Path 3 later without affecting the Odoo-side user accounts.

---

### Step 4: Add API Permissions

1. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**
2. Search and add:
   - `openid`
   - `profile`
   - `email`
3. Click **Add permissions**
4. Click **Grant admin consent for [your organization]** → **Yes**

Status should show green checkmarks for all three permissions.

---

### Step 5: Hand off to Odoo admin

Provide these two values:

| Value | Where to find |
|---|---|
| Directory (tenant) ID | App Registration → Overview |
| Application (client) ID | App Registration → Overview |

No client secret is needed for Path 2.

---

## Part 2 — Odoo Setup (Admin)

### Step 1: Install auth_oauth module

1. Go to **Settings** → **Apps**
2. Search for `OAuth Authentication`
3. Click **Install**

> If already installed, skip this step.

---

### Step 2: Enable OAuth in Settings

1. Go to **Settings** → **General Settings**
2. Scroll to **Integrations** section
3. Enable **OAuth Authentication**
4. Click **Save**

---

### Step 3: Set Authorization Header parameter

This is required for Azure AD — without it, token validation will fail.

1. Go to **Settings** → **Technical** → **Parameters** → **System Parameters**
2. Click **New**
3. Fill in:
   - **Key:** `auth_oauth.authorization_header`
   - **Value:** `1`
4. Click **Save**

> **Why this matters:** Azure AD's userinfo endpoint requires the access token in the `Authorization: Bearer <token>` header. By default Odoo sends it as a URL query parameter, which Azure AD rejects.

---

### Step 4: Create the Azure AD OAuth Provider

1. Go to **Settings** → **Technical** → **OAuth Providers**
2. Click **New**
3. Fill in the fields:

   | Field | Value |
   |---|---|
   | **Provider Name** | `Microsoft Azure AD` |
   | **Client ID** | *(paste Application client ID from Azure)* |
   | **Authorization URL** | `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize` |
   | **UserInfo URL** | `https://graph.microsoft.com/oidc/userinfo` |
   | **Scope** | `openid profile email` |
   | **Login button label** | `Sign in with Microsoft` |
   | **Allowed** | ☑ checked |

   Replace `{tenant_id}` with your actual Directory (tenant) ID, for example:
   ```
   https://login.microsoftonline.com/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/oauth2/v2.0/authorize
   ```

4. Click **Save**

---

### Step 5: (Optional) Style the login button

To use the Microsoft icon on the login button, set the **CSS class** field:

```
fa fa-windows
```

For a more branded look, you can add a custom CSS class in a theme module later.

---

## Part 3 — Testing

### First login test

1. Open a private/incognito browser window
2. Navigate to `http://localhost:8072/web/login`
3. You should see a **"Sign in with Microsoft"** button below the login form
4. Click it — you will be redirected to Microsoft's login page
5. Sign in with your Azure AD credentials
6. If MFA is required by your Azure AD policy, complete MFA
7. Microsoft redirects back to Odoo and logs you in

### Expected first-time behavior

- If the user **does not exist** in Odoo: a new Odoo user is automatically created using the name and email from Azure AD
- If the user **already exists** in Odoo with the same email: the accounts are linked automatically on first OAuth login

### Superuser / password login

Users with local password access are **not affected**. The Microsoft button is additive — password login remains available. Superusers can continue to use username/password at any time.

---

## Part 4 — Troubleshooting

### "Sign in with Microsoft" button does not appear

- Check that `auth_oauth` module is installed
- Check that **OAuth Authentication** is enabled in General Settings
- Check that the provider has **Allowed** = checked

### Redirected back with `oauth_error=2`

Generic error. Check Odoo server logs (`docker logs ggglue-odoo-1`) for the real exception. Common causes:

- `auth_oauth.authorization_header` system parameter not set → Azure AD returns 401 on userinfo call
- Wrong **UserInfo URL** — must be `https://graph.microsoft.com/oidc/userinfo`
- Scope missing `openid` — Azure AD won't return a valid token without it

### Redirected back with `oauth_error=3`

Access denied — user exists in Azure AD but Odoo rejected the login. Possible causes:

- User is inactive in Odoo
- User is archived — reactivate in Settings → Users

### "AADSTS50011: The redirect URI does not match"

The Redirect URI in Azure App Registration does not exactly match what Odoo is sending. Verify:
- Protocol: `http` vs `https`
- Port: `:8072` included
- Path: `/auth_oauth/signin` exactly
- No trailing slash

### Token validation fails silently

Confirm admin consent was granted on the API permissions. In Azure Portal → App Registration → API permissions — all three permissions (`openid`, `profile`, `email`) should show a green checkmark under **Status**.

---

## Reference

| Item | Value |
|---|---|
| Dev Odoo URL | `http://localhost:8072` |
| Redirect URI (dev) | `http://localhost:8072/auth_oauth/signin` |
| Azure auth endpoint | `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize` |
| Azure userinfo endpoint | `https://graph.microsoft.com/oidc/userinfo` |
| Scope | `openid profile email` |
| System parameter key | `auth_oauth.authorization_header` = `1` |
| OAuth flow type | Implicit (response_type=token) |
