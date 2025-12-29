import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import "../styles/register.css";

function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fname, setFirstName] = useState('')
  const [lname, setLastName] = useState('')
  const [phone_number, setPhoneNumber] = useState('')
  // const [adminEmail, setAdminEmail] = useState('')
  const navigate = useNavigate() 
  
  const handleRegister = async (e) => {
  if (e) e.preventDefault();
    try{
      const res = await fetch("http://localhost:5000/register", { //logis in the user and starts their session
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          "email": email, 
          "password": password,
          "fname": fname,
          "lname": lname,
          "phone_number": phone_number
        }),
        credentials: "include", 
      });
      const data = await res.json();
      
      if(data.message === "success") {
        alert("Account Request has been sent to Admin\nAwaiting Approval")
        navigate("/login")
      }
      else{
        alert("Rugh Rough Raggy, something is wrong")
      }
    }
    catch (error) {
    console.error('Login error:', error);
    alert('Something went wrong');
  }
  }

  return (
    <div className="container">
      <div className="image-side">
        <img
          src="/static/mafes-webstie-photos-35.jpg" //Need to find an image that we want to use and adds it path here in the 'static folder'
          alt="Forrest #2"
          className="background-image"
        />
      </div>

      <div className="register-side">
        <h2 className="title">Register</h2>

        <form className="form">
          <label>First Name</label>
          <input
          type="text"
          onChange={(e) => setFirstName(e.target.value)} 
          />

          <label>Last Name</label>
          <input 
          type="text"
          onChange={(e) => setLastName(e.target.value)} 
          />

          <label>Email</label>
          <input
          type="email" 
          onChange={(e) => setEmail(e.target.value)} 
          />

          <label>Password</label>
          <input 
          type="password"
          onChange={(e) => setPassword(e.target.value)} 
          />

          <label>Phone Number</label>
          <input
          type="tel" 
          onChange={(e) => setPhoneNumber(e.target.value)} 
          />

          <button type="submit" onClick={handleRegister}>Sign Up</button>
        </form>
      </div>
    </div>
  );
}

export default Register;
