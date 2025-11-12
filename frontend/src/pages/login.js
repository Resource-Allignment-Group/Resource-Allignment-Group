import React, {useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../Authentication"

function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleLogin = async (e) => {
  if (e) e.preventDefault();
  try {
    const success = await login(username, password); // call login function in AuthProvider.js
    if(success){
      navigate('/home'); 
    } 
    
    else {
      alert('Invalid username or password'); //can make these non alert is decided
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