# 🚀 EduPath Frontend - Deployment Guide

## 📦 Deployment Options

### 1. Web Deployment (Recommended for MVP)

#### Option A: Netlify (Free, Easy)

```bash
# Build for production
npm run build:web

# Deploy to Netlify
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd web-build
netlify deploy --prod
```

**Or use Netlify UI:**
1. Push code to GitHub
2. Go to https://netlify.com
3. Click "New site from Git"
4. Select your repo
5. Build command: `npm run build:web`
6. Publish directory: `web-build`

#### Option B: Vercel (Free, Fast)

```bash
# Install Vercel CLI
npm install -g vercel

# Build
npm run build:web

# Deploy
vercel --prod
```

**Or use Vercel UI:**
1. Push code to GitHub
2. Go to https://vercel.com
3. Import your repo
4. Framework preset: Other
5. Build command: `npm run build:web`
6. Output directory: `web-build`

#### Option C: Firebase Hosting (Free)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Build
npm run build:web

# Initialize Firebase
firebase init hosting

# Deploy
firebase deploy
```

### 2. Android Deployment

#### Build APK (For Testing)

```bash
# Build APK
eas build --platform android --profile preview

# Download APK from Expo dashboard
# Share APK with testers
```

#### Publish to Google Play Store

```bash
# Build AAB (Android App Bundle)
eas build --platform android --profile production

# Submit to Google Play
eas submit --platform android
```

**Steps:**
1. Create Google Play Developer account ($25 one-time)
2. Create app in Play Console
3. Upload AAB
4. Fill app details, screenshots, etc.
5. Submit for review

### 3. iOS Deployment

#### Build IPA (For Testing)

```bash
# Build IPA
eas build --platform ios --profile preview

# Install on device via TestFlight
```

#### Publish to App Store

```bash
# Build for App Store
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

**Steps:**
1. Create Apple Developer account ($99/year)
2. Create app in App Store Connect
3. Upload IPA
4. Fill app details, screenshots, etc.
5. Submit for review

## 🔧 Pre-Deployment Checklist

### ✅ Environment Configuration

- [ ] Update API URL to production backend
- [ ] Add production Razorpay keys
- [ ] Remove test/debug code
- [ ] Test all features end-to-end

### ✅ Code Quality

- [ ] Run linter: `npm run lint` (if configured)
- [ ] Fix all warnings
- [ ] Test on multiple devices/browsers
- [ ] Optimize images and assets

### ✅ Security

- [ ] Never commit `.env` with real keys
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS for production API
- [ ] Implement proper error handling

### ✅ Performance

- [ ] Minimize bundle size
- [ ] Optimize images
- [ ] Enable production builds
- [ ] Test on slow networks

## 📝 Production Environment Variables

### For Web Deployment

Create `.env.production`:

```env
API_URL=https://api.yourdomain.com
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
```

### For Mobile (EAS Build)

Create `eas.json`:

```json
{
  "build": {
    "production": {
      "env": {
        "API_URL": "https://api.yourdomain.com",
        "RAZORPAY_KEY_ID": "rzp_live_xxxxxxxxxxxxx"
      }
    },
    "preview": {
      "env": {
        "API_URL": "https://staging-api.yourdomain.com",
        "RAZORPAY_KEY_ID": "rzp_test_xxxxxxxxxxxxx"
      }
    }
  }
}
```

## 🌐 Domain & DNS Setup

### Custom Domain for Web

**Netlify:**
1. Go to Site settings → Domain management
2. Add custom domain
3. Update DNS records at your domain registrar

**Vercel:**
1. Go to Project settings → Domains
2. Add domain
3. Configure DNS as instructed

### Deep Linking for Mobile

Add to `app.json`:

```json
{
  "expo": {
    "scheme": "edupath",
    "android": {
      "intentFilters": [
        {
          "action": "VIEW",
          "data": {
            "scheme": "https",
            "host": "edupath.app"
          }
        }
      ]
    },
    "ios": {
      "associatedDomains": ["applinks:edupath.app"]
    }
  }
}
```

## 📊 Analytics & Monitoring

### Add Google Analytics

```bash
npm install expo-firebase-analytics
```

### Add Sentry for Error Tracking

```bash
npm install @sentry/react-native
```

## 🔄 CI/CD Setup

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Web

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build:web
      - uses: netlify/actions/cli@master
        with:
          args: deploy --prod
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## 🚀 Deployment Commands Summary

### Web

```bash
# Build
npm run build:web

# Deploy to Netlify
netlify deploy --prod

# Deploy to Vercel
vercel --prod

# Deploy to Firebase
firebase deploy
```

### Android

```bash
# Preview build
eas build --platform android --profile preview

# Production build
eas build --platform android --profile production

# Submit to Play Store
eas submit --platform android
```

### iOS

```bash
# Preview build
eas build --platform ios --profile preview

# Production build
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

## 📱 App Store Assets Needed

### Screenshots

- **Android**: 1080x1920px (portrait), 5-8 screenshots
- **iOS**: Various sizes for different devices, 5-10 screenshots

### App Icon

- **Android**: 512x512px PNG
- **iOS**: 1024x1024px PNG

### Feature Graphic (Android)

- 1024x500px PNG

### App Description

Prepare:
- Short description (80 chars)
- Full description (4000 chars)
- Keywords for ASO
- Privacy policy URL
- Support URL

## 🔐 Store Listing Example

### App Name
EduPath - AI Learning Coach

### Short Description
Learn anything with your personal AI coach. Daily motivation, progress tracking, and adaptive learning paths.

### Full Description
```
🎓 EduPath - Your Personal AI Learning Coach

Transform your learning journey with EduPath, the AI-powered learning companion that adapts to your goals, keeps you motivated, and tracks your progress.

✨ KEY FEATURES:
• 🤖 AI Coach powered by GPT-4
• 💬 Chat-based interface - like talking to a friend
• 📅 Daily check-ins for motivation
• 🎯 Personalized learning paths
• 📊 Progress tracking and analytics
• 🔥 Streak system to build habits
• 💰 Flexible token-based pricing

🚀 PERFECT FOR:
• Students preparing for exams
• Professionals learning new skills
• Anyone wanting to stay consistent
• Self-learners needing accountability

💡 HOW IT WORKS:
1. Tell us your learning goals
2. Chat with your AI coach daily
3. Get personalized guidance
4. Track your progress
5. Achieve your goals!

🎁 FREE TRIAL:
New users get 10 free messages to experience the power of AI-guided learning.

🔒 SECURE & PRIVATE:
Your data is encrypted and secure. We never share your information.

📧 SUPPORT:
Questions? Email us at support@edupath.app

Made with ❤️ in India 🇮🇳
```

### Keywords (iOS)
edupath, learning, ai, coach, study, education, tutor, courses, skills

### Category
- Primary: Education
- Secondary: Productivity

## 📈 Post-Deployment Monitoring

### Metrics to Track

1. **User Engagement**
   - Daily active users
   - Average session length
   - Messages sent per user
   - Retention rate

2. **Technical Performance**
   - App crashes
   - API response times
   - Loading times
   - Error rates

3. **Business Metrics**
   - Conversion rate (free → paid)
   - Average revenue per user
   - Token purchase frequency
   - Churn rate

### Tools

- **Analytics**: Google Analytics, Mixpanel
- **Error Tracking**: Sentry
- **Performance**: Firebase Performance
- **User Feedback**: In-app feedback form

## 🎉 Launch Checklist

Final checks before launch:

- [ ] All features tested on prod environment
- [ ] API is stable and scalable
- [ ] Payment flow tested end-to-end
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Support email set up
- [ ] App store listings complete
- [ ] Screenshots uploaded
- [ ] Beta testers given feedback
- [ ] Marketing materials ready
- [ ] Social media accounts created
- [ ] Press release prepared (optional)

## 🚀 Launch Day!

1. Submit apps to stores (can take 1-7 days for review)
2. Deploy web version
3. Announce on social media
4. Email early users
5. Monitor analytics and errors
6. Be ready for support requests
7. Celebrate! 🎉

---

**Good luck with your launch! 🚀**

For issues, check [troubleshooting](./README.md#troubleshooting) or contact support.