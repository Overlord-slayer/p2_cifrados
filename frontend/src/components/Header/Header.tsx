import { useAuth } from "@store/useAuth";
import { Link, useNavigate } from "react-router-dom";
import styles from "./Header.module.css";

export function Header() {
  const { accessToken, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className={styles.header}>
      <div className={styles.left}></div>
      <nav className={styles.nav}>
        {!accessToken && (
          <>
            <Link to="/signup" className={styles.link}>
              Signup
            </Link>
            <Link to="/login" className={styles.link}>
              Login
            </Link>
          </>
        )}
        {accessToken && (
          <>
            <Link to="/chat" className={styles.link}>
              P2P Chat
            </Link>
            <Link to="/group-chat" className={styles.link}>
              Group Chat
            </Link>
            <button onClick={handleLogout} className={styles.logoutButton}>
              Logout
            </button>
          </>
        )}
      </nav>
    </header>
  );
}
