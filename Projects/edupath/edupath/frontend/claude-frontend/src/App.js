import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Screens
import AuthScreen from './screens/AuthScreen';
import LibraryScreen from './screens/LibraryScreen';
import CreateMentorScreen from './screens/CreateMentorScreen';
import ChatScreen from './screens/ChatScreen';
import PlansScreen from './screens/PlansScreen';
import ProfileScreen from './screens/ProfileScreen';

// Components
import TopNavbar from './components/TopNavbar';
import LoadingSpinner from './components/LoadingSpinner';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// App Layout with Navbar
const AppLayout = ({ children, title }) => {
  return (
    <div style={{ paddingTop: '64px' }}>
      <TopNavbar title={title} />
      {children}
    </div>
  );
};

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/library" replace /> : <AuthScreen />}
        />
        <Route
          path="/signup"
          element={isAuthenticated ? <Navigate to="/library" replace /> : <AuthScreen />}
        />

        {/* Protected Routes */}
        <Route
          path="/library"
          element={
            <ProtectedRoute>
              <AppLayout title="Library">
                <LibraryScreen />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/create-mentor"
          element={
            <ProtectedRoute>
              <AppLayout title="Create Mentor">
                <CreateMentorScreen />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat/:mentorId"
          element={
            <ProtectedRoute>
              <AppLayout title="Chat">
                <ChatScreen />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/plans"
          element={
            <ProtectedRoute>
              <AppLayout title="Plans">
                <PlansScreen />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <AppLayout title="Profile">
                <ProfileScreen />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/library" replace />} />
        <Route path="*" element={<Navigate to="/library" replace />} />
      </Routes>

      <ToastContainer
        position="bottom-center"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
