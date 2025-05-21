// src/components/layout/NavBar.tsx

import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'  

export default function NavBar() {
  const clearAuth = useAuth(s => s.clear)
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate('/login', { replace: true })
  }

  return (
    <nav className="w-full bg-white shadow px-6 py-3 flex justify-between items-center">
      <div className="flex gap-4">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            isActive
              ? 'text-blue-600 font-semibold'
              : 'text-gray-600 hover:text-blue-600'
          }
        >
          Dashboard
        </NavLink>
      </div>
      <button
        onClick={handleLogout}
        className="px-4 py-1 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Logout
      </button>
    </nav>
  )
}
