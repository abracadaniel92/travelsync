# TravelSync Mobile App Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   cd mobile
   npm install
   ```

2. **Set up assets:**
   - Copy `logo2.png` from `../frontend/images/` to `src/assets/logo2.png` (already done)
   - Convert `photo-1559627712-fa1c99c217a8.avif` to JPG format and save as `src/assets/background.jpg`
     - You can use an online converter or ImageMagick: `magick convert photo-1559627712-fa1c99c217a8.avif background.jpg`

3. **Configure API URL:**
   - Open `src/services/api.js`
   - Update `API_BASE` to your backend server URL:
     - Local development: `http://localhost:8001` or `http://YOUR_IP:8001`
     - Production: Your production backend URL

4. **Run the app:**
   ```bash
   npm start
   # Then press 'i' for iOS simulator or scan QR code with Expo Go app
   ```

## Building for iOS TestFlight

### Option 1: Using Expo EAS Build (Recommended)

1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   ```

2. Login to Expo:
   ```bash
   eas login
   ```

3. Configure build:
   ```bash
   eas build:configure
   ```

4. Build for iOS:
   ```bash
   eas build --platform ios
   ```

5. Submit to App Store:
   ```bash
   eas submit --platform ios
   ```

### Option 2: Using Xcode (For TestFlight)

1. Generate native iOS project:
   ```bash
   npx expo prebuild --platform ios
   ```

2. Open in Xcode:
   ```bash
   cd ios
   open TravelSync.xcworkspace
   ```

3. In Xcode:
   - Select your development team in Signing & Capabilities
   - Update Bundle Identifier if needed (currently `com.travelsync.app`)
   - Update version and build number
   - Select your device/simulator
   - Product → Archive
   - Distribute App → App Store Connect → Upload

4. In App Store Connect:
   - Wait for processing
   - Add to TestFlight
   - Invite testers

## Important Notes

- **API URL**: Make sure your backend allows CORS from mobile app
- **HTTPS**: For production, use HTTPS for API calls
- **Network**: For local testing, ensure your phone and computer are on the same network
- **Permissions**: Camera and photo library permissions are configured in `app.json`

## Troubleshooting

- **Can't connect to API**: Check that `API_BASE` is correct and backend is running
- **Build errors**: Run `npx expo install --fix` to fix dependency versions
- **Image not found**: Ensure all assets are in `src/assets/` directory
