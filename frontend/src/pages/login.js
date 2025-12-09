import React, {useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../Authentication"
import "../styles/login.css"

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
      <div className="container">
      <div className="image-side">
        <img
          src="/static/mafes-webstie-photos-66.jpg" //Need to find an image that we want to use and adds it path here in the 'static folder'
          alt="Ship Yard"
          className="background-image"
        />
      </div>

      <div className="login-side">
        <h2 className="title">Login</h2>

        <form className="form">
          <label>Email *</label>
          <input
              type="text"
              id="username"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

          <label>Password *</label>
          <input
              type="password"
              id="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

          <button type="submit" onClick={handleLogin}>Sign In</button>

          <a href="#" className="forgot-password" onClick={() => navigate("/register")}>
            Sign Up
          </a>
        </form>
      </div>
    </div>      
  )
}

export default Login

