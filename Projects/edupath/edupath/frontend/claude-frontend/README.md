# EduPath Frontend - AI Learning Platform

A modern, WhatsApp-inspired learning platform built with React and GSAP animations.

## Features

- 🎨 Beautiful UI with smooth GSAP animations
- 📱 WhatsApp-like mentor list interface
- 💬 Real-time chat with AI mentors
- 📄 PDF/DOCX document upload
- 💰 Token-based system
- 🔐 Email OTP verification
- 📊 User dashboard and stats

## Tech Stack

- **React 18** - Modern React with hooks
- **GSAP 3.12+** - Smooth, professional animations
- **React Router v6** - Client-side routing
- **Axios** - API communication
- **React Toastify** - Toast notifications
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Clone the repository or extract the ZIP file

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory:
```env
REACT_APP_API_URL=http://localhost:5000
```

4. Start the development server:
```bash
npm start
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── TopNavbar.js    # Navigation bar with user menu
│   └── LoadingSpinner.js # Loading indicator
├── screens/            # Main app screens
│   ├── AuthScreen.js   # Login/Signup
│   ├── LibraryScreen.js # Mentor list
│   ├── ChatScreen.js   # Chat interface
│   ├── CreateMentorScreen.js # Upload & create mentor
│   ├── PlansScreen.js  # Token purchase
│   └── ProfileScreen.js # User profile
├── context/            # React context
│   └── AuthContext.js  # Authentication state
├── services/           # API services
│   └── api.js          # Axios configuration
├── config/             # Configuration
│   └── theme.js        # Theme colors & styles
├── utils/              # Utilities
│   └── animations.js   # GSAP animation presets
└── App.js              # Main app with routing
```

## Key Features

### Authentication Flow
- Step 1: Enter email
- Step 2: Verify OTP (sent to email)
- Step 3: Complete profile (username, password, name)

### Mentor Creation
- Step 1: Upload PDF/DOCX file
- Step 2: Configure topic and learning target
- Step 3: Processing with animated progress

### Chat Interface
- WhatsApp-style message bubbles
- Real-time typing indicator
- Source attribution (knowledge graph, web search)
- Auto-scroll to latest message

### Token System
- Balance displayed in navbar
- Purchase plans with bonus offers
- Featured plan with glow effect

## GSAP Animations

The app features smooth animations throughout:

- **Entrance**: Stagger animations for lists, scale-in for cards
- **Interactions**: Hover lifts, button ripples, input focus glows
- **Transitions**: Slide transitions between steps
- **Loading**: Spinning loaders, typing dots, progress bars
- **Special**: Confetti, pulse effects, glow animations

## API Integration

The app connects to a backend API with the following endpoints:

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Sign in
- `POST /api/auth/send-otp` - Send OTP to email
- `POST /api/auth/verify-otp` - Verify OTP

### Mentors
- `GET /api/mentors/list` - Get all mentors
- `POST /api/mentors/create-mentor` - Create new mentor

### Chat
- `POST /api/chat/chat` - Send message
- `GET /api/chat/history/:mentorId` - Get chat history

### Tokens
- `GET /api/tokens/balance` - Get token balance
- `GET /api/tokens/packages` - Get token packages
- `POST /api/tokens/create-order` - Create purchase order

## Customization

### Theme Colors

Edit `src/config/theme.js` to customize:
```javascript
colors: {
  primary: '#f5cb7d',    // Main accent color
  secondary: '#2f4954',  // Secondary color
  dark: '#1f3e4e',       // Dark text
  // ... more colors
}
```

### Animations

Modify `src/utils/animations.js` to adjust animation timings and easing.

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is part of the EduPath platform.

## Support

For issues or questions, please contact support.
