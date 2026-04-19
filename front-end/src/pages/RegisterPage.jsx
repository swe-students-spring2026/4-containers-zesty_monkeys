import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    if (password !== confirm) { setError('Passwords do not match.'); return }

    // TODO: replace mock with real fetch, backend needs to return JSON
    // const res = await fetch('http://localhost:5000/register', {
    //   method: 'POST',
    //   credentials: 'include',
    //   headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    //   body: new URLSearchParams({ username, password, confirm_password: confirm })
    // })
    // if (!res.ok) { setError('Registration failed.'); return }

    navigate('/login')
  }

  return (
    <div>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <input placeholder="Confirm Password" type="password" value={confirm} onChange={e => setConfirm(e.target.value)} />
        {error && <p>{error}</p>}
        <button type="submit">Register</button>
      </form>
      <p>Already have an account? <Link to="/login">Log in</Link></p>
    </div>
  )
}
