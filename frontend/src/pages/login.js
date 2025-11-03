import React, {useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../Authentication"

function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleLogin = async (e) => {
        if (e) e.preventDefault(); // 
            try {
                const response = await fetch('http://127.0.0.1:5000/authenticate', { //calls the Flask backend endpoint
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                    credentials: "include"
            });

            const data = await response.json();

            if (data.message) {
                const user = { user: username };
                login(user); // Update auth state
                console.log(user);

                navigate('/home'); //send them to the home page
            } else {
                alert(data.message || 'Login failed');
            }
            } catch (error) {
            console.error('Login error:', error);
            alert('Something went wrong');
            }
    };

    return(        
    <div className="login-container">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <button type="submit">Login</button>
          </form>
        </div>
          )
}

export default Login