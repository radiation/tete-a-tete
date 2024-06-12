import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Profile from './components/Profile';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState('');

  const handleLoginSuccess = (token: string) => {
    setToken(token);
    setIsAuthenticated(true);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={
          !isAuthenticated ?
            <Login onLoginSuccess={handleLoginSuccess} /> :
            <Navigate replace to="/profile" />
        } />
        <Route path="/profile" element={
          isAuthenticated ?
            <Profile token={token} /> :
            <Navigate replace to="/login" />
        } />
        <Route path="*" element={<Navigate replace to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;
