// import '../styles/home.css';
// import { useNavigate } from 'react-router-dom';
// import EquipmentPopup from '../Popup';
// import { useState } from 'react';

// function Home(){
//     const navigate = useNavigate()
//     const [activatePopup, setActivatePopup] = useState(false)

//     function AddEquipment(equipmentInformation){
//         console.log("Added equipment", equipmentInformation)
//     }
//     return(
//         <div className="home-container">
//             <div className="sidebar">
//                 <p>Filters</p>
//             </div>

//             <div className="main">
//                 <nav className="navbar">
//                     <div className='nav-links'>
//                         <ul className="nav-links">
//                             <li><a href="#" onClick={() => setActivatePopup(true)}>Add Equipment</a></li> {/*Add link */}
//                             <li><a href="">Notifications</a></li> {/*Add link */}
//                             <li><a href="">Reports</a></li>  {/*Add link */}
//                         </ul>
//                     </div>

//                     <div className="nav-right">
//                     <div className='notification'>
//                         <p>&#x1F514;</p>
//                     </div>
//                     <div className="profile" onClick={() => navigate("/profile")}>
//                         <p>&#x1F464;</p>
//                     </div>
//                     </div>
//                 </nav>

//                 <div className="search-bar">
//                     <p>Search Bar</p>
//                 </div>

//                 <div className="content">
//                    <p>Equipment</p>
//                 </div>
//             </div>

//         {activatePopup && (
//         <EquipmentPopup
//           onClose={() => setActivatePopup(false)}
//           onSubmit={AddEquipment}
//         />
//       )}
//         </div>
//   );
// }

// export default Home
