import { useEffect, createContext, useContext, useState } from "react";
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch("http://localhost:5000/check-session", { //checks to see if user is loged in with Flask sessions
          method: "GET",
          credentials: "include", 
        });

        const data = await res.json();
        setUser(data.user ? { username: data.user } : null);
      } 
      
      catch (err) {
        console.error("Session check failed", err);
        setUser(null);
      } 
      
      finally {
        setIsLoading(false);
      }

    };
    checkSession();
  }, []);

  const login = async (username, password) => {
    try {
      const res = await fetch("http://localhost:5000/authenticate", { //logis in the user and starts their session
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include", 
      });
      
      const data = await res.json();
      if (data.message === "success") {
        setUser({ username });
        return true;
      }

      return false;
    } 
    catch (err) {
      console.error("Login failed", err);
      return false;
    }
  };

  const logout = async () => {
    try {
      await fetch("http://localhost:5000/logout", { //Logs the user out, will need tro impliment into pack end
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout failed", err);
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext)