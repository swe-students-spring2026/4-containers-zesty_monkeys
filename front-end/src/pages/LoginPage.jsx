import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState(null)
    const { login } = useAuth()
    const navigate = useNavigate()

    async function handleSubmit(e) {
        e.preventDefault()

        // TODO: replace mock with real fetch, backend needs to return JSON
        // const res = await fetch('http://localhost:5000/login', {
        //   method: 'POST',
        //   credentials: 'include',
        //   headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        //   body: new URLSearchParams({ username, password })
        // })
        // if (!res.ok) { setError('Invalid username or password.'); return }

        if (username === 'test' && password === 'test') {
        login(username)
        navigate('/')
        } else {
        setError('Invalid username or password.')
        }
    }

    return (
        <div>
        <h1>Login</h1>
        <form onSubmit={handleSubmit}>
            <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
            <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
            {error && <p>{error}</p>}
            <button type="submit">Log In</button>
        </form>
        <p>No account? <Link to="/register">Register</Link></p>
        </div>
    )
}
