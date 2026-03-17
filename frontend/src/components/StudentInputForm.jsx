import { useState } from 'react'

function normalizeSkills(input) {
  return input
    .split(/[\n,;|]+/)
    .map((skill) => skill.trim())
    .filter(Boolean)
}

export default function StudentInputForm({ onSubmit, loading, minimal = false }) {
  const [desiredRole, setDesiredRole] = useState('')
  const [skillsInput, setSkillsInput] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit({
      desiredRole,
      skills: normalizeSkills(skillsInput),
    })
  }

  const formClass = minimal ? 'space-y-4' : 'space-y-4 rounded-lg bg-white p-6 shadow-sm border border-slate-200'

  return (
    <form onSubmit={handleSubmit} className={formClass}>
      <div>
        <label className="block text-sm font-medium text-indigo-900 mb-1">Desired Role</label>
        <input
          type="text"
          value={desiredRole}
          onChange={(event) => setDesiredRole(event.target.value)}
          className="w-full rounded-md border border-indigo-200 bg-white px-3 py-2 text-slate-900 focus:border-indigo-500 focus:outline-none"
          placeholder="e.g., Data Analyst"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-indigo-900 mb-1">Skills the Student Has</label>
        <textarea
          rows={4}
          value={skillsInput}
          onChange={(event) => setSkillsInput(event.target.value)}
          className="w-full rounded-md border border-indigo-200 bg-white px-3 py-2 text-slate-900 focus:border-indigo-500 focus:outline-none"
          placeholder="e.g., Python, SQL, Power BI"
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-gradient-to-r from-indigo-600 to-cyan-600 px-4 py-2 text-white shadow-md hover:from-indigo-700 hover:to-cyan-700 disabled:opacity-60"
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </form>
  )
}
