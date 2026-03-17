import { useState } from 'react'

export default function AuthPage({ onLogin, onRegister, loading, error }) {
  const [mode, setMode] = useState('login')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (mode === 'register') {
      await onRegister({ fullName, email, password })
      return
    }

    await onLogin({ email, password })
  }

  return (
    <div className="mx-auto flex min-h-screen items-center justify-center rounded-2xl bg-gradient-to-br from-[#ffffff] via-[#f8fbff] to-[#eef6ff] p-4">
      <div className="w-full max-w-xl rounded-2xl border border-indigo-200/30 bg-white/90 p-8 shadow-2xl backdrop-blur">
        <div className="mb-6 text-center">
          <h1 className="text-4xl font-bold text-indigo-950">Skill Gap Analyzer</h1>
        </div>

        <p className="mb-4 text-sm text-indigo-900/80">
          {mode === 'login' ? 'Login to continue your assessment and reports.' : 'Register to create your secure account.'}
        </p>

        {error ? <div className="mb-4 rounded-md border border-rose-200 bg-rose-50 px-4 py-2 text-sm text-rose-700">{error}</div> : null}

        <form className="space-y-4" onSubmit={handleSubmit}>
          {mode === 'register' ? (
            <div>
              <label className="mb-1 block text-sm font-medium text-indigo-900">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="w-full rounded-md border border-indigo-200 bg-white px-3 py-2 focus:border-indigo-500 focus:outline-none"
                placeholder="Enter your full name"
                required
              />
            </div>
          ) : null}

          <div>
            <label className="mb-1 block text-sm font-medium text-indigo-900">Email</label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded-md border border-indigo-200 bg-white px-3 py-2 focus:border-indigo-500 focus:outline-none"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-indigo-900">Password</label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-md border border-indigo-200 bg-white px-3 py-2 focus:border-indigo-500 focus:outline-none"
              placeholder="Minimum 6 characters"
              minLength={6}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-gradient-to-r from-indigo-600 to-cyan-600 px-4 py-2 text-white shadow-md hover:from-indigo-700 hover:to-cyan-700 disabled:opacity-60"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-indigo-900/80">
          {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
          <button
            type="button"
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
            className="font-medium text-indigo-700 underline"
          >
            {mode === 'login' ? 'Register' : 'Login'}
          </button>
        </div>
      </div>
    </div>
  )
}
