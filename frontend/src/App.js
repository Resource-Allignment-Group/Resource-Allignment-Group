import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/login";
import Home from "./pages/home";

function App() {
  return (<Router>
    <Routes>
      <Route path='/' element={<Navigate to='/login'/>} />

      <Route path="/login" element={<Login />} />
      <Route path="/home" element={<Home />} />
    {/*Will make the home route protected in a later commit*/}
    
    </Routes>
  </Router>
  );
}

export default App;
