import '../styles/home.css';
import { useNavigate } from 'react-router-dom';

function Home(){
    const navigate = useNavigate()

    return(
        <div className="home-container">
            <div className="sidebar">
                <p>Filters</p>
            </div>

            <div className="main">
                <nav className="navbar">
                    <div className='nav-links'>
                        <ul className="nav-links">
                            <li><a href="">Add Equipment</a></li> {/*Add link */}
                            <li><a href="">Notifications</a></li> {/*Add link */}
                            <li><a href="">Reports</a></li>  {/*Add link */}
                        </ul>
                    </div>
                     
                    <div className="nav-right">
                    <div className='notification'>
                        <p>&#x1F514;</p>
                    </div>
                    <div className="profile" onClick={() => navigate("/profile")}>
                        <p>&#x1F464;</p>
                    </div>
                    </div>
                </nav>

                <div className="search-bar">
                    <p>Search Bar</p>
                </div>

                <div className="content">
                   <p>Equipment</p>
                </div>
            </div>
        </div>
  );
}

export default Home