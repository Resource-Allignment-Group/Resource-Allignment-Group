import { Navigate } from "react-router-dom";
import { useAuth } from "./Authentication";

const ProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth()
  if (isLoading) return <div><p>Loading...</p></div>
  return user ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;