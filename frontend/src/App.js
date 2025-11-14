import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/login";
import Home from "./pages/home";
import Profile from './pages/profile';
import { AuthProvider } from './Authentication';
import ProtectedRoute from './ProtectedRoute';
import Register from './pages/register';
function App() {
  return (
  <Router>
    <AuthProvider>
    <Routes>
      <Route path='/' element={<Navigate to='/login'/>} />
      <Route path="/register" element={<Register/>} />
      <Route path="/profile" element={<ProtectedRoute><Profile/></ProtectedRoute>} />
      <Route path="/login" element={<Login />} />
      <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
    {/*Will make the home route protected in a later commit*/}

    </Routes>
      </AuthProvider>
  </Router>
  
  );
}

export default App;
