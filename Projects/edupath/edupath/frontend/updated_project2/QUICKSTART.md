# 🚀 EduPath Frontend - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Node.js Dependencies

```bash
npm install
```

### Step 2: Configure API URL

**Option A: Using app.json (Recommended)**

Edit `app.json`:
```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://localhost:5000"  // Change this for your backend
    }
  }
}
```

**Option B: For Different Environments**

- **Web Development**: `http://localhost:5000`
- **Android Emulator**: `http://10.0.2.2:5000`
- **iOS Simulator**: `http://localhost:5000`
- **Physical Device**: `http://YOUR_COMPUTER_IP:5000` (e.g., `http://192.168.1.100:5000`)

### Step 3: Add Razorpay Test Keys

Edit `src/config/constants.js`:

```javascript
export const RAZORPAY_CONFIG = {
  KEY_ID: 'rzp_test_xxxxxxxxxxxxx', // ← Add your Razorpay test key here
  THEME_COLOR: '#FFC107',
};
```

Get your test keys from: https://dashboard.razorpay.com/app/keys

### Step 4: Start the App

**For Web (Easiest):**
```bash
npm run web
```
Opens at: http://localhost:19006

**For Mobile (Expo Go):**
```bash
npm start
```
Then scan QR code with Expo Go app:
- Android: [Expo Go on Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- iOS: [Expo Go on App Store](https://apps.apple.com/app/expo-go/id982107779)

**For Android Emulator:**
```bash
npm run android
```

**For iOS Simulator (Mac only):**
```bash
npm run ios
```

## 📱 Testing the App

### Test Account Creation

1. Click "Sign Up"
2. Fill in details:
   - Full Name: `Test User`
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test@1234`

### Chat-Based Onboarding

After signup, you'll go through interactive onboarding:
1. AI asks for your name → Type it
2. AI asks learning goals → Type them
3. AI shows experience options → Select one
4. AI asks about time → Select one
5. AI asks motivation → Select one
6. Onboarding complete! → Start chatting

### Free Trial Messages

New users get **10 free messages**:
- Check balance in chat header
- Each message costs 1 token
- When free messages run out, you'll be prompted to buy tokens

### Testing Payments

1. Go to "Plans" tab
2. Select a token package (e.g., "Power Pack")
3. Click the plan card
4. Use Razorpay test credentials:
   - Card: `4111 1111 1111 1111`
   - CVV: `123`
   - Expiry: Any future date
   - Or UPI: `success@razorpay`
5. Complete payment
6. Tokens added automatically!

## 🔧 Common Issues & Fixes

### Issue: "Network request failed"

**Solution:**
- Make sure backend is running: `cd backend && python run_api.py`
- Check API URL in `app.json`
- For Android emulator: Use `http://10.0.2.2:5000`
- For physical device: Use your computer's local IP

### Issue: "Cannot connect to Metro"

**Solution:**
```bash
# Clear cache and restart
expo start -c
```

### Issue: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

### Issue: "Razorpay script not loading"

**Solution:**
- Razorpay checkout works best on **web**
- For mobile testing, use the web version
- For production mobile apps, implement Razorpay Standard Checkout SDK

## 🎯 Features to Try

### 1. Chat Interface
- Send messages to AI coach
- Get personalized responses
- See message history
- Watch typing indicator

### 2. Token Management
- View balance in header
- See free trial messages remaining
- Buy token packages
- Track token usage

### 3. Profile
- View account info
- See learning preferences from onboarding
- Clear chat history
- Logout

### 4. Payment Flow
- Browse token packages
- See "Most Popular" badge
- Complete test payment
- Get instant token credit

## 📊 Expected Behavior

### First Time User Flow:
```
Signup → Onboarding (5 chat questions) → Chat Screen → 10 free messages
```

### Returning User Flow:
```
Login → Chat Screen → Continue chatting
```

### Low Balance Flow:
```
Send message → No tokens → Alert → Navigate to Plans → Buy tokens → Continue
```

## 🎨 UI Elements

### Colors You'll See:
- **Yellow (`#FFC107`)**: Primary actions, user messages, headers
- **Orange (`#FF6F00`)**: Popular badges, accents
- **Green (`#4CAF50`)**: Free trial badges, success states
- **Gray (`#F5F5F5`)**: AI messages, backgrounds

### Components:
- **Chat Bubbles**: WhatsApp-style with timestamps
- **Token Header**: Shows balance or free messages
- **Gradient Backgrounds**: Yellow gradients on headers
- **Cards**: Clean cards with shadows for plans

## 🔐 Security Notes

- Never commit API keys to Git
- Use test keys for development
- Use production keys only for deployed apps
- Store sensitive data in secure storage

## 📱 Platform-Specific Notes

### Web
- ✅ Full Razorpay integration works
- ✅ All features available
- ✅ Fast development workflow

### Android
- ⚠️ Use `http://10.0.2.2:5000` for emulator
- ⚠️ Use device IP for physical device
- ℹ️ Razorpay needs native SDK for production

### iOS
- ⚠️ Mac required for iOS builds
- ⚠️ Xcode required for simulator
- ℹ️ Razorpay needs native SDK for production

## 🚀 Next Steps

1. ✅ Set up backend (if not already running)
2. ✅ Install frontend dependencies
3. ✅ Configure API URL
4. ✅ Add Razorpay keys
5. ✅ Start the app
6. ✅ Test signup/login
7. ✅ Complete onboarding
8. ✅ Send chat messages
9. ✅ Test payment flow

## 💡 Pro Tips

- Use **web version** for fastest development
- Keep backend running in separate terminal
- Check backend logs if API calls fail
- Use Expo DevTools for debugging
- Clear cache if you face issues: `expo start -c`

## 📚 Learn More

- [Full README](./README.md) - Complete documentation
- [Backend Setup](../backend/README.md) - Backend API setup
- [Expo Docs](https://docs.expo.dev/) - Expo framework
- [React Navigation](https://reactnavigation.org/) - Navigation

---

**Happy Coding! 🎉**

Need help? Check the [troubleshooting section](./README.md#-troubleshooting) in the main README.