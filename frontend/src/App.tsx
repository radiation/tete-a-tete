import React, { useState } from 'react';
import Login from './components/Login';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLoginSuccess = (token: string) => {
    setIsAuthenticated(true);
    // You can also set the user's state or perform a redirect here
  };

  return (
    <div>
      {!isAuthenticated ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <div>Welcome! You are logged in.</div>
      )}
    </div>
  );
};

export default App;
