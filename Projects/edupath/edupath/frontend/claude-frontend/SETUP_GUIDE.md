# EduPath Frontend - Complete Setup Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd edupath-frontend
npm install
```

This will install all required packages:
- react & react-dom
- react-router-dom
- gsap (animations)
- axios (API calls)
- react-toastify (notifications)
- framer-motion (optional animations)
- lucide-react (icons)

### Step 2: Configure Environment

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and set your backend API URL:
```
REACT_APP_API_URL=http://localhost:5000
```

### Step 3: Start Development Server

```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## 📋 Complete File Structure

```
edupath-frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/             # Reusable components
│   │   ├── LoadingSpinner.js   # Animated loading spinner
│   │   └── TopNavbar.js        # Navigation bar with user menu
│   ├── screens/                # Main application screens
│   │   ├── AuthScreen.js       # Login & Signup (3-step OTP)
│   │   ├── LibraryScreen.js    # WhatsApp-style mentor list
│   │   ├── ChatScreen.js       # Chat interface with AI mentor
│   │   ├── CreateMentorScreen.js # Upload files & create mentor
│   │   ├── PlansScreen.js      # Token purchase plans
│   │   └── ProfileScreen.js    # User profile & stats
│   ├── context/
│   │   └── AuthContext.js      # Global authentication state
│   ├── services/
│   │   └── api.js              # Axios instance & API methods
│   ├── config/
│   │   └── theme.js            # Colors, fonts, spacing
│   ├── utils/
│   │   └── animations.js       # GSAP animation presets
│   ├── App.js                  # Main app with routing
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
├── package.json                # Dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # Documentation
└── SETUP_GUIDE.md              # This file
```

## 🎨 Key Features & Animations

### 1. Authentication Flow (AuthScreen.js)
- **Login**: Email + Password with smooth card entrance
- **Signup** (3 steps):
  - Step 1: Email input with send OTP
  - Step 2: 6-digit OTP verification with countdown
  - Step 3: Profile completion (username, password, name)
- **Animations**: Rotate-in logo, slide-up cards, shake on error

### 2. Library Screen (LibraryScreen.js)
- WhatsApp-inspired mentor list
- Staggered card entrance animations
- Hover lift effects
- Empty state with pulsing "Create Mentor" button
- Badge displays for streak and scroll count

### 3. Chat Screen (ChatScreen.js)
- WhatsApp-style message bubbles
- User messages: Right-aligned, gold background
- AI messages: Left-aligned, white background
- Typing indicator with bouncing dots
- Auto-scroll to bottom on new messages
- Source chips for knowledge graph & web search

### 4. Create Mentor Screen (CreateMentorScreen.js)
- **Step 1**: Drag & drop file upload (PDF/DOCX)
- **Step 2**: Configure topic and target days
- **Step 3**: Animated processing with checklist:
  - ✓ Extracting text...
  - ✓ Analyzing content...
  - ✓ Creating learning plan...
  - ✓ Building knowledge graph...
- Success celebration and auto-redirect to chat

### 5. Plans Screen (PlansScreen.js)
- Token balance card with pulse animation
- Grid of token packages
- Featured plan with glow effect
- Staggered card entrance

### 6. Profile Screen (ProfileScreen.js)
- Rotating avatar entrance
- Stats cards with stagger animation
- Action buttons for profile management
- Logout button with shake warning

## 🔧 Customization Guide

### Changing Colors

Edit `src/config/theme.js`:

```javascript
colors: {
  primary: '#f5cb7d',     // Change to your brand color
  secondary: '#2f4954',   // Secondary accent
  dark: '#1f3e4e',        // Text color
  // ... more colors
}
```

### Adjusting Animations

Edit `src/utils/animations.js`:

```javascript
// Example: Make cards slide in faster
staggerSlideIn: (elements, options = {}) => {
  const defaults = { 
    x: -100, 
    opacity: 0, 
    duration: 0.4,  // Changed from 0.6
    stagger: 0.1, 
    ease: 'power2.out' 
  };
  return gsap.from(elements, { ...defaults, ...options });
}
```

### Adding New Screens

1. Create file in `src/screens/NewScreen.js`
2. Add route in `src/App.js`:
```javascript
<Route
  path="/new-screen"
  element={
    <ProtectedRoute>
      <AppLayout title="New Screen">
        <NewScreen />
      </AppLayout>
    </ProtectedRoute>
  }
/>
```

## 🌐 API Integration

The app uses Axios with interceptors for:
- Auto-adding auth tokens
- Handling 401 (redirect to login)
- Error toast notifications

### Example API Call

```javascript
import { apiService } from '../services/api';

const loadData = async () => {
  try {
    const response = await apiService.mentors.list();
    setMentors(response.data.mentors);
  } catch (error) {
    // Error handled by interceptor
  }
};
```

## 📱 Responsive Design

The app is mobile-first and responsive:

- **Mobile (<768px)**: Single column, touch-optimized
- **Tablet (768-1024px)**: Optimized layouts
- **Desktop (>1024px)**: Max-width containers, hover effects

## 🐛 Troubleshooting

### Issue: "Module not found" errors

```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: GSAP animations not working

Ensure GSAP is imported:
```javascript
import gsap from 'gsap';
```

### Issue: API calls failing

1. Check `.env` file has correct API URL
2. Verify backend is running
3. Check browser console for CORS errors

### Issue: Routes not working

Ensure `BrowserRouter` is wrapping the app in `App.js`

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

This creates optimized files in `build/` folder.

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

1. Connect repository
2. Build command: `npm run build`
3. Publish directory: `build`

### Environment Variables

Set in deployment platform:
- `REACT_APP_API_URL` - Your production API URL

## 🎯 Next Steps

1. **Connect to Backend**: Update API URL in `.env`
2. **Test Authentication**: Sign up and verify OTP flow
3. **Create a Mentor**: Upload a PDF and test chat
4. **Customize Theme**: Adjust colors in `theme.js`
5. **Add Analytics**: Integrate Google Analytics or similar

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [GSAP Documentation](https://greensock.com/docs/)
- [React Router](https://reactrouter.com)
- [Axios](https://axios-http.com)

## 💡 Tips for Development

1. **Use React DevTools**: Install browser extension for debugging
2. **Check Console**: Always monitor for errors
3. **Hot Reload**: Changes auto-refresh during development
4. **Component Reusability**: Extract common patterns into components
5. **Animation Performance**: Use `will-change` CSS for smooth animations

## 🔐 Security Notes

- Auth tokens stored in localStorage
- API interceptor handles token refresh
- CORS configured in backend
- OTP verification for email
- Protected routes require authentication

## 📊 Performance Tips

1. **Code Splitting**: React Router handles this automatically
2. **Image Optimization**: Use WebP format when possible
3. **Lazy Loading**: Import screens lazily if needed
4. **Memoization**: Use React.memo for expensive components
5. **GSAP Cleanup**: Animations auto-cleanup on unmount

## ✅ Checklist Before Going Live

- [ ] Update API URL to production endpoint
- [ ] Test all authentication flows
- [ ] Verify file upload works
- [ ] Check responsive design on mobile
- [ ] Test error handling
- [ ] Optimize bundle size
- [ ] Add loading states
- [ ] Test payment integration
- [ ] Set up error tracking (Sentry)
- [ ] Configure analytics

---

**Happy Coding! 🚀**

For questions or support, refer to the main README.md or API documentation.
