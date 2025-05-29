// src/components/layout/NavBar.tsx

import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import './NavBar.css'

export default function NavBar() {
  const clearAuth = useAuth(s => s.clear)
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate('/login', { replace: true })
  }

  return (
    <nav className="navbar">
      <div className="navbar-links">
        <NavLink
          to="/chat"
          className={({ isActive }) =>
            isActive ? 'nav-link active' : 'nav-link'
          }
        >
          Chat
        </NavLink>
      </div>
      <button className="logout-button" onClick={handleLogout}>
        Logout
      </button>
    </nav>
  )
}
