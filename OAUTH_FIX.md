# Fixing OAuth 403 Access Denied Error

If you're getting `Error 403: access_denied`, follow these steps:

## Quick Fix: Add Yourself as a Test User

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/
   - Select your project

2. **Open OAuth Consent Screen**:
   - Go to **APIs & Services** → **OAuth consent screen**

3. **Add Test Users**:
   - Scroll down to **"Test users"** section
   - Click **"+ ADD USERS"**
   - Enter your Google email address (the one you're signing in with)
   - Click **"ADD"**

4. **Save Changes**:
   - Click **"SAVE AND CONTINUE"** at the bottom

5. **Try Again**:
   - Go back to your app
   - Click "Test Calendar Connection" again
   - Sign in with the email you just added

## Alternative: Publish Your App (For Personal Use)

If you want to use it without test users:

1. **Go to OAuth Consent Screen**:
   - https://console.cloud.google.com/apis/credentials/consent

2. **Publish App**:
   - Click **"PUBLISH APP"** button at the top
   - Confirm you want to publish
   - Note: This makes it available to anyone, but for personal use it's fine

3. **Try Again**:
   - Go back to your app and try authentication again

## Common Issues

### "App is in testing mode"
- **Solution**: Add your email as a test user (see above)

### "This app isn't verified"
- **Solution**: For personal use, you can ignore this warning and click "Advanced" → "Go to [Your App] (unsafe)"

### "Access blocked"
- **Solution**: Make sure you're using the same Google account that you added as a test user

## Step-by-Step with Screenshots Guide

### Step 1: Navigate to OAuth Consent Screen
1. Go to https://console.cloud.google.com/
2. Select your project
3. Click **"APIs & Services"** in the left menu
4. Click **"OAuth consent screen"**

### Step 2: Check App Status
- Look at the top - it should say **"Testing"** or **"In production"**
- If it says "Testing", you need to add test users

### Step 3: Add Test User
1. Scroll down to **"Test users"** section
2. Click **"+ ADD USERS"**
3. Enter the Google email you'll use to sign in
4. Click **"ADD"**
5. Click **"SAVE AND CONTINUE"** at the bottom

### Step 4: Retry Authentication
1. Go back to your app
2. Try the calendar connection again
3. When you see the consent screen, you should see your email listed

## Still Having Issues?

### Check These:
- ✅ OAuth consent screen is configured (not just credentials)
- ✅ Your email is added as a test user
- ✅ You're signing in with the same email you added
- ✅ Google Calendar API is enabled
- ✅ You're using the correct project

### For Development/Testing:
- Keep the app in "Testing" mode
- Add all emails that will use the app as test users
- This is the recommended approach for personal projects

### For Production:
- Publish the app (makes it available to anyone)
- Or keep in testing mode and manage test users


