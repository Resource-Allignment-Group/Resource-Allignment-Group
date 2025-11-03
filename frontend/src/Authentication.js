import { useEffect, createContext, useContext, useState } from "react";
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate()
    
    useEffect(() => {
        const checkSession = async () => {
        const res = await fetch("http://localhost:5000/check-session", { //calls the Flask endpoint for checking active sessions
            //sessions are a Flask feature and all session data should stay in the back end
            method: "GET",
            credentials: "include", //needed for CORS and certian permissions
        });
        
        const data = await res.json();
        
        if (data.user) {
            setUser({ username: data.user });
        }
        
        setIsLoading(false);
        };
        
        checkSession();
    }, []);
    
    const login = async (username, password) => {
        const res = await fetch("http://localhost:5000/authenticate", {
            method: "POST",
            headers: { "Content-Type": "application/json" }, //send the username and password to the backend to authenticate
            body: JSON.stringify({ username, password }),
            credentials: "include",
        });
        if (res.ok) {
            const data = await res.json();
            setUser({ username });
            navigate('/home')
            return true;
        }
        
        else{return false}
    };

    const logout = async () => {
        await fetch("http://localhost:5000/logout", {
            method: "POST",
            credentials: "include",
        });
        setUser(null);
    };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
