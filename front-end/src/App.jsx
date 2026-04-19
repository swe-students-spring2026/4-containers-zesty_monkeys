import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import RecordPage from './pages/RecordPage'
import ResultsPage from './pages/ResultsPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RecordPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/dashboard" element={<DashboardPage />}/>
        <Route path="/login" element={<LoginPage />}/>
      </Routes>
    </Router>
  )
}

export default App