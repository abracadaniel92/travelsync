# TravelSync Mobile App

React Native iOS app for TravelSync - Sync your travel documents to your calendar.

## Setup

### Prerequisites
- Node.js (v16 or later)
- npm or yarn
- Expo CLI: `npm install -g expo-cli`
- iOS Simulator (for Mac) or physical iOS device

### Installation

1. Install dependencies:
```bash
cd mobile
npm install
```

2. Update API URL in `src/services/api.js`:
   - Change `API_BASE` to your backend server URL
   - For local development: `http://localhost:8001`
   - For production: Your production backend URL

3. Copy assets:
   - Copy `logo2.png` to `src/assets/logo2.png`
   - Copy `photo-1559627712-fa1c99c217a8.avif` (convert to JPG) to `src/assets/background.jpg`

### Running the App

```bash
# Start Expo development server
npm start

# Run on iOS simulator (Mac only)
npm run ios

# Run on physical device (scan QR code with Expo Go app)
```

## Building for iOS

### Using Expo

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Configure your app:
```bash
eas build:configure
```

3. Build for iOS:
```bash
eas build --platform ios
```

### Using Xcode (for TestFlight)

1. Generate native iOS project:
```bash
npx expo prebuild --platform ios
```

2. Open in Xcode:
```bash
cd ios
open TravelSync.xcworkspace
```

3. Configure signing and build settings in Xcode
4. Archive and upload to TestFlight

## Project Structure

```
mobile/
├── App.js                 # Main app entry point
├── src/
│   ├── screens/          # Screen components
│   │   ├── LandingScreen.js
│   │   ├── LoginScreen.js
│   │   └── MainScreen.js
│   ├── components/       # Reusable components
│   │   └── CollapsibleSection.js
│   ├── context/          # React context providers
│   │   └── AuthContext.js
│   ├── services/         # API services
│   │   └── api.js
│   └── assets/           # Images and assets
└── package.json
```

## Features

- ✅ Landing page with background image
- ✅ Login authentication
- ✅ Document upload (images and PDFs)
- ✅ Travel information extraction
- ✅ Google Calendar integration
- ✅ Email forwarding
- ✅ Collapsible test sections
- ✅ Dark blue theme matching web app

## Notes

- Update `API_BASE` in `src/services/api.js` to point to your backend
- Ensure backend CORS is configured to allow mobile app requests
- For production, use HTTPS for API calls
