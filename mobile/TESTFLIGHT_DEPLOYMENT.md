# Deploy TravelSync to TestFlight (Mac)

Step-by-step guide to deploy the TravelSync React Native (Expo) app to TestFlight.

## Prerequisites

- **Apple Developer account** ($99/year) — [developer.apple.com](https://developer.apple.com)
- **Expo account** (free) — [expo.dev](https://expo.dev)
- **Mac** with Node.js installed

---

## Option 1: EAS Build (Recommended — No Xcode Required)

EAS Build runs in the cloud. You don't need Xcode on your Mac.

### 1. Install EAS CLI

```bash
cd mobile
npm install -g eas-cli
```

### 2. Log in to Expo

```bash
eas login
```

Create an account at [expo.dev](https://expo.dev) if needed.

### 3. Configure the Project

```bash
eas build:configure
```

This creates `eas.json`. When prompted:
- **Build profile:** Choose "Production" or create one for TestFlight
- **iOS:** Yes
- **Automatically manage credentials:** Yes (recommended)

### 4. Configure app.json for iOS

Ensure `app.json` has:
- `ios.bundleIdentifier`: e.g. `com.travelsync.app` (must be unique, register in App Store Connect)
- `ios.buildNumber`: Increment for each upload (e.g. `"1"`, `"2"`, `"3"`)

### 5. Build for iOS

```bash
eas build --platform ios --profile production
```

- First build: EAS will prompt to create/use an Apple Developer account and set up credentials
- You may need to provide your Apple ID and app-specific password
- Build runs in the cloud (~10–20 min)

### 6. Submit to TestFlight

After the build completes:

```bash
eas submit --platform ios --profile production
```

Or submit the latest build:

```bash
eas submit --platform ios --latest
```

---

## Option 2: Local Build with Xcode

Use this if you prefer building on your Mac with Xcode.

### 1. Install Xcode

- Install from Mac App Store
- Open Xcode once and accept the license
- Install Command Line Tools: `xcode-select --install`

### 2. Generate Native iOS Project

```bash
cd mobile
npx expo prebuild --platform ios
```

This creates the `ios/` folder.

### 3. Open in Xcode

```bash
cd ios
open TravelSync.xcworkspace
```

### 4. Configure Signing in Xcode

1. Select the **TravelSync** project in the left sidebar
2. Select the **TravelSync** target
3. Open **Signing & Capabilities**
4. Check **Automatically manage signing**
5. Select your **Team** (Apple Developer account)
6. Ensure **Bundle Identifier** matches App Store Connect (e.g. `com.travelsync.app`)

### 5. Archive and Upload

1. Select **Any iOS Device (arm64)** as the run destination (not a simulator)
2. **Product** → **Archive**
3. When the Organizer opens: **Distribute App**
4. Choose **App Store Connect** → **Upload**
5. Follow the prompts (default options are fine)
6. Wait for upload to finish

### 6. In App Store Connect

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Select your app (or create it if first time)
3. **TestFlight** tab → Build will appear after processing (10–30 min)
4. Add **Internal Testers** (your team) or **External Testers** (requires Beta App Review)
5. Testers install via the TestFlight app

---

## App Store Connect Setup (First Time)

If this is your first deployment:

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. **My Apps** → **+** → **New App**
3. Fill in:
   - **Platform:** iOS
   - **Name:** TravelSync
   - **Primary Language:** English
   - **Bundle ID:** Select or create `com.travelsync.app`
   - **SKU:** e.g. `travelsync-ios`

---

## EAS Configuration (eas.json)

If using EAS Build, your `eas.json` might look like:

```json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "production": {
      "ios": {
        "resourceClass": "m1-medium"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@email.com",
        "ascAppId": "YOUR_APP_STORE_CONNECT_APP_ID"
      }
    }
  }
}
```

Run `eas build:configure` to generate this.

---

## Common Issues

### "No valid signing identity"
- Ensure your Apple Developer account has a valid distribution certificate
- In EAS: Let EAS manage credentials, or regenerate in Apple Developer Portal

### "Bundle identifier already in use"
- Use a unique bundle ID (e.g. `com.yourname.travelsync`)
- Update `app.json` and `ios/` project

### "App Store Connect processing"
- First upload can take 30+ minutes to process
- Check email for any metadata or compliance questions

### API URL in production
- Update `src/services/api.js` so `API_BASE` points to your production backend (HTTPS)
- Rebuild and re-submit after changing

---

## Quick Reference

| Step | EAS Build | Xcode |
|------|-----------|-------|
| Install | `npm i -g eas-cli` | Xcode from App Store |
| Setup | `eas build:configure` | `npx expo prebuild --platform ios` |
| Build | `eas build --platform ios` | Product → Archive |
| Submit | `eas submit --platform ios --latest` | Distribute App in Organizer |
