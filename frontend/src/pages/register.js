import "../styles/register.css"

function Register(){
    return(        
      <div className="container">
        <div className="image-side">
          <img
            src="/static/mafes-webstie-photos-35.jpg"//Need to find an image that we want to use and adds it path here in the 'static folder'
            alt="Forrest #2"
            className="background-image"
          />
        </div>


        <div className="register-side">
          <h2 className="title">Register</h2>

          <form className="form">
            <label>Email *</label>
            <input type="email" />

            <label>Password *</label>
            <input type="password" />

            <label>Admin ID *</label>
            <input type="text" />

            <button type="submit">Login</button>
          </form>
        </div>
      </div>
  )
}

export default Register
