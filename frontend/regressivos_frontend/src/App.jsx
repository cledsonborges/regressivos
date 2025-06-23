import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import AdminDashboard from './components/AdminDashboard'
import QualityDashboard from './components/QualityDashboard'
import RegressivoDetails from './components/RegressivoDetails'
import LoginPage from './components/LoginPage'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar se há usuário logado no localStorage
    const savedUser = localStorage.getItem('ion_user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
    setLoading(false)
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('ion_user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('ion_user')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route 
            path="/admin" 
            element={
              user.role === 'admin' ? 
                <AdminDashboard user={user} onLogout={handleLogout} /> : 
                <Navigate to="/quality" />
            } 
          />
          <Route 
            path="/quality" 
            element={<QualityDashboard user={user} onLogout={handleLogout} />} 
          />
          <Route 
            path="/regressivo/:id" 
            element={<RegressivoDetails user={user} onLogout={handleLogout} />} 
          />
          <Route 
            path="/" 
            element={
              <Navigate to={user.role === 'admin' ? '/admin' : '/quality'} />
            } 
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App

