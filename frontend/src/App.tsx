import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Profile from './components/Profile';
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';
import Navbar from './components/Navbar/Navbar';
import Home from './pages/Home';  // Assuming you have a Home component

const App: React.FC = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [token, setToken] = useState('');

    const handleLoginSuccess = (token: string) => {
        setToken(token);
        setIsAuthenticated(true);
    };

    return (
        <Router>
            <Header />
            {isAuthenticated && <Navbar />}  // Navbar only shown when authenticated
            <Routes>
                <Route path="/" element={<Home />} />
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
            <Footer />
        </Router>
    );
};

export default App;
