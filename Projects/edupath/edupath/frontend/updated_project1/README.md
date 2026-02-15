# 🎓 EduPath Frontend - Universal React App

A beautiful, professional WhatsApp-like chat interface for the EduPath AI Learning Coach. Built with React Native (Expo) for **universal deployment** on Web, iOS, and Android.

## ✨ Features

- 🎨 **Modern Yellow Theme** - Professional WhatsApp-inspired UI
- 💬 **Chat Interface** - Real-time messaging with AI coach
- 🚀 **Chat-Based Onboarding** - Interactive setup through conversation
- 💰 **Payment Integration** - Razorpay for secure payments
- 🎁 **Free Trial** - 10 free messages for new users
- 📊 **Token Management** - Track balance and usage
- 👤 **User Profile** - View preferences and account details
- 🌐 **Universal** - Works on Web, iOS, and Android

## 🛠️ Tech Stack

- **React Native** with Expo SDK 49
- **React Navigation** for routing
- **AsyncStorage** for local data
- **Axios** for API calls
- **Expo Linear Gradient** for beautiful gradients
- **date-fns** for date formatting

## 📋 Prerequisites

- Node.js 16+ and npm/yarn
- Expo CLI (`npm install -g expo-cli`)
- Backend API running at `http://localhost:5000`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Backend URL

Edit `app.json` and update the API URL if different:

```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://localhost:5000"
    }
  }
}
```

For Android emulator, use: `http://10.0.2.2:5000`
For iOS simulator, use: `http://localhost:5000`
For physical device on same network, use: `http://YOUR_COMPUTER_IP:5000`

### 3. Update Razorpay Keys

Edit `src/config/constants.js` and add your Razorpay test keys:

```javascript
export const RAZORPAY_CONFIG = {
  KEY_ID: 'rzp_test_xxxxxxxxxxxxx', // Your Razorpay test key
  THEME_COLOR: '#FFC107',
};
```

### 4. Run the App

**For Web:**
```bash
npm run web
```
Open http://localhost:19006 in your browser.

**For Android:**
```bash
npm run android
```
Requires Android Studio and emulator or physical device.

**For iOS (Mac only):**
```bash
npm run ios
```
Requires Xcode and iOS simulator.

**Universal Development:**
```bash
npm start
```
Opens Expo DevTools - scan QR code with Expo Go app.

## 📱 App Structure

```
src/
├── screens/
│   ├── LoginScreen.js         # User login
│   ├── SignupScreen.js        # User registration
│   ├── OnboardingScreen.js    # Chat-based onboarding
│   ├── ChatScreen.js          # Main chat interface
│   ├── PlansScreen.js         # Token packages
│   ├── PaymentScreen.js       # Razorpay integration
│   └── ProfileScreen.js       # User profile
├── components/
│   ├── ChatBubble.js          # WhatsApp-like message bubble
│   └── TokenBalanceHeader.js  # Token balance display
├── context/
│   └── AuthContext.js         # Authentication state
├── services/
│   └── api.js                 # API service with Axios
├── navigation/
│   └── AppNavigator.js        # Navigation configuration
└── config/
    ├── theme.js               # Yellow theme colors
    └── constants.js           # App constants
```

## 🎨 Color Palette

The app uses a professional yellow color scheme:

- **Primary**: `#FFC107` (Bright Yellow)
- **Primary Dark**: `#FFA000` (Dark Yellow)
- **Primary Light**: `#FFECB3` (Light Yellow)
- **Secondary**: `#FF6F00` (Orange)
- **Success**: `#4CAF50` (Green)

## 🔐 API Endpoints Used

The app connects to these backend endpoints:

```
✅ POST /api/auth/signup       - User registration
✅ POST /api/auth/login        - User login
✅ POST /api/chat              - Send chat message
✅ GET  /api/payments/plans    - Get token packages
✅ POST /api/payments/create-order/tokens - Create Razorpay order
✅ POST /api/payments/verify-payment - Verify payment
✅ GET  /api/payments/balance  - Get token balance
```

## 💳 Payment Testing

### Razorpay Test Credentials:

**Test Cards:**
- Card Number: `4111 1111 1111 1111`
- CVV: `123`
- Expiry: Any future date

**Test UPI:**
- UPI ID: `success@razorpay`

**Test Net Banking:**
- Select any bank and use `success` as credentials

## 📦 Free Trial

New users get **10 free messages** to try EduPath:
- Each chat message costs 1 token
- Free messages are tracked in `AuthContext`
- Users are prompted to buy tokens when free messages run out

## 🎯 User Flow

1. **Signup/Login** → User creates account
2. **Onboarding** → Chat-based setup (name, goals, experience, etc.)
3. **Chat** → Main interface with AI coach
4. **Token Management** → View balance, buy tokens
5. **Profile** → View account info and preferences

## 🚀 Deployment

### Web Build

```bash
npm run build:web
```

Output in `web-build/` - deploy to any static hosting (Netlify, Vercel, etc.)

### Android APK

```bash
expo build:android
```

### iOS IPA (Mac only)

```bash
expo build:ios
```

## 🐛 Troubleshooting

### "Network request failed"
- Check if backend is running at `http://localhost:5000`
- For Android emulator, use `http://10.0.2.2:5000`
- For physical device, use your computer's IP address

### "Cannot connect to Metro bundler"
```bash
# Clear cache
expo start -c
```

### "Module not found"
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

### Razorpay not working on mobile
- Razorpay checkout requires additional native setup for mobile
- Use web version for testing payments
- For production, implement Razorpay Standard Checkout SDK

## 📝 Environment Variables

Create a `.env` file (optional):

```env
API_URL=http://localhost:5000
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
```

Note: Expo doesn't natively support `.env` files. Use `app.json` → `extra` for config.

## 🔄 State Management

The app uses **React Context API** for state:

- **AuthContext**: User authentication, token balance, free messages
- **AsyncStorage**: Local persistence for tokens, messages, preferences

## 🎉 Key Features Implementation

### Chat-Based Onboarding
All onboarding happens through chat - no forms!
- AI asks questions one by one
- User responds via text or options
- Smooth conversational flow

### WhatsApp-Like UI
- Message bubbles with timestamps
- User messages on right (yellow)
- AI messages on left (gray)
- Typing indicator
- Auto-scroll to bottom

### Token System
- Display balance in header
- Show free trial messages
- Deduct tokens on chat
- Prompt to buy when low

### Payment Flow
1. User selects plan
2. Razorpay checkout opens
3. Payment processed
4. Tokens credited automatically
5. Balance updated in real-time

## 📚 Additional Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Razorpay Docs](https://razorpay.com/docs/)
- [EduPath Backend API](../backend/README.md)

## 🙏 Credits

Built with:
- React Native & Expo
- React Navigation
- Razorpay
- Axios
- AsyncStorage

---

**Made with ❤️ in India 🇮🇳**

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend API status
3. Check Expo logs: `expo start --dev-client`

Happy Learning! 🎓✨