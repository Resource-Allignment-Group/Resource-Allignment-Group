import { Navigate } from "react-router-dom";
import { useAuth } from "./Authentication";

const AdminRoute = ({ children }) => {
  const { user, role, isLoading } = useAuth(); 

  if (isLoading) return <div><p>Loading...</p></div>;
  console.log(user, role)
  return user && role === "a" ? children : <Navigate to="/home" />;
};

export default AdminRoute;
