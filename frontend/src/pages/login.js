import React, {useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../Authentication"
import "../styles/login.css"

function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleLogin = async (e) => {
  if (e) e.preventDefault();
  try {
    const success = await login(email, password); // call login function in AuthProvider.js

    
    if(success){
      navigate('/home'); 
    } 
    
    else {
      alert('Invalid email or password'); //can make these non alert is decided
    }
    
  } catch (error) {
    console.error('Login error:', error);
    alert('Something went wrong');
  }
};

    const ForgotPassword = async (e) => {
      if (e) e.preventDefault()
        try{
          if (!email){
            alert("Please Enter Email")
          }
          else{
            const res =  await fetch("http://localhost:5000/forgot_password", {
              method: "POST",
              credentials: 'include',
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({
                email: email
              })
            })
            const data = await res.json()
            if (data.result){//may return true even if the email was not sent due to security
              alert("Password recovery email sent to " + email)
            }
            else{
              alert("Something Went Wrong")
            }
          }
          }
        catch (error){
        console.log(error)
        alert("Something Went Wrong")
        }
      }
    

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
              id="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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

          <a href="#" className="sign-up-reference" onClick={() => navigate("/register")}>
            Sign Up
          </a>
          <a href="#" className="forgot-password" onClick={ForgotPassword}>
            Forgot Password
          </a>
        </form>
      </div>
    </div>      
  )
}
export default Login

