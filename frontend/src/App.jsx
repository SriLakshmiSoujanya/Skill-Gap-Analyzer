import { useEffect, useMemo, useState } from 'react'
import AssessmentQuiz from './components/AssessmentQuiz'
import AuthPage from './components/AuthPage'
import RecommendationResults from './components/RecommendationResults'
import StudentInputForm from './components/StudentInputForm'
import TrendsPanel from './components/TrendsPanel'
import {
  fetchAssessmentQuestions,
  fetchRecommendation,
  fetchRoleTrends,
  fetchSkillTrends,
  getPowerBIExportUrl,
  loginUser,
  registerUser,
  setAuthToken,
  submitAssessment,
} from './services/api'

function SiteFooter() {
  return (
    <div className="end fixed bottom-0 left-0 right-0 z-40 border-t border-indigo-100 bg-white/90 px-4 py-2 text-center text-xs text-slate-700 backdrop-blur">
      <p>
        Email: Sowjanyathatavarthi2601@gmail.com | Copyright © 2026 Skill Gap Analyzer | All Rights Reserved.
        <br />
        Website developed by: Sowjanya T | Sowjanya K | Lavanya K | Valli
      </p>
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [recommendation, setRecommendation] = useState(null)
  const [currentPage, setCurrentPage] = useState('input')
  const [studentProfile, setStudentProfile] = useState(null)
  const [assessmentQuestions, setAssessmentQuestions] = useState([])
  const [assessmentResult, setAssessmentResult] = useState(null)
  const [roleTrends, setRoleTrends] = useState([])
  const [skillTrends, setSkillTrends] = useState([])

  const exportLinks = useMemo(
    () => ({
      role_demand: getPowerBIExportUrl('role_demand'),
      skill_demand_by_year: getPowerBIExportUrl('skill_demand_by_year'),
      latest_role_skills: getPowerBIExportUrl('latest_role_skills'),
    }),
    [user],
  )

  useEffect(() => {
    setAuthToken('')
    setUser(null)
  }, [])

  useEffect(() => {
    if (!user) {
      setRoleTrends([])
      setSkillTrends([])
      return
    }

    const loadTrends = async () => {
      try {
        const [rolesRes, skillsRes] = await Promise.all([fetchRoleTrends(), fetchSkillTrends()])
        setRoleTrends(rolesRes.items || [])
        setSkillTrends(skillsRes.items || [])
      } catch {
        setError('Failed to load trends data. Make sure backend is running.')
      }
    }

    loadTrends()
  }, [user])

  const handleRegister = async (payload) => {
    setLoading(true)
    setError('')
    try {
      const response = await registerUser(payload)
      setAuthToken(response.token)
      setUser(response.user)
    } catch (requestError) {
      setError(requestError.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (payload) => {
    setLoading(true)
    setError('')
    try {
      const response = await loginUser(payload)
      setAuthToken(response.token)
      setUser(response.user)
    } catch (requestError) {
      setError(requestError.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async (payload) => {
    setLoading(true)
    setError('')

    try {
      const questionRes = await fetchAssessmentQuestions(payload)
      setStudentProfile(payload)
      setAssessmentQuestions(questionRes.questions || [])
      setCurrentPage('assessment')
    } catch (requestError) {
      setError(requestError.message || 'Failed to start skill assessment.')
    } finally {
      setLoading(false)
    }
  }

  const handleAssessmentSubmit = async (answers) => {
    if (!studentProfile) {
      setError('Student profile is missing. Please start again.')
      setCurrentPage('input')
      return
    }

    setLoading(true)
    setError('')

    try {
      const assessment = await submitAssessment({
        desiredRole: studentProfile.desiredRole,
        skills: studentProfile.skills,
        answers,
      })
      setAssessmentResult(assessment)

      const recommendationResult = await fetchRecommendation({
        desiredRole: studentProfile.desiredRole,
        skills: studentProfile.skills,
        testScore: assessment.score,
        proficiency: assessment.proficiency,
      })

      setRecommendation(recommendationResult)
      setCurrentPage('results')
    } catch (requestError) {
      setError(requestError.message || 'Failed to submit assessment.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoBack = () => {
    setError('')
    setAssessmentResult(null)
    setAssessmentQuestions([])
    setCurrentPage('input')
  }

  const handleLogout = () => {
    setAuthToken('')
    setUser(null)
    setError('')
    setRecommendation(null)
    setStudentProfile(null)
    setAssessmentResult(null)
    setAssessmentQuestions([])
    setCurrentPage('input')
  }

  if (!user) {
    return (
      <>
        <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-cyan-50 to-violet-50 p-6 lg:p-10">
          <AuthPage onLogin={handleLogin} onRegister={handleRegister} loading={loading} error={error} />
        </main>
        <SiteFooter />
      </>
    )
  }

  return (
    <>
      <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-cyan-50 to-violet-50 p-6 pb-24 lg:p-10 lg:pb-24">
        {currentPage === 'input' ? (
          <div className="mx-auto flex min-h-[80vh] max-w-3xl items-center justify-center">
            <div className="w-full max-w-xl rounded-xl border border-indigo-100 bg-white/95 p-8 shadow-xl">
              <div className="mb-6 flex items-center justify-between gap-3">
                <h1 className="text-3xl font-bold text-indigo-950">Skill Gap Analyzer</h1>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-md border border-indigo-200 bg-white px-3 py-1 text-sm text-indigo-700 hover:bg-indigo-50"
                >
                  Logout
                </button>
              </div>
              {error ? <div className="mb-4 rounded-md border border-rose-200 bg-rose-50 px-4 py-2 text-rose-700">{error}</div> : null}
              <StudentInputForm onSubmit={handleAnalyze} loading={loading} minimal />
            </div>
          </div>
        ) : currentPage === 'assessment' ? (
          <div className="mx-auto max-w-6xl space-y-6">
            {error ? <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-2 text-rose-700">{error}</div> : null}
            <AssessmentQuiz
              questions={assessmentQuestions}
              onSubmit={handleAssessmentSubmit}
              loading={loading}
              onBack={handleGoBack}
            />
          </div>
        ) : (
          <div className="mx-auto max-w-6xl space-y-6">
            <header className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h1 className="text-3xl font-bold text-indigo-950">Analysis Result</h1>
                <p className="mt-1 text-indigo-900/80">Personalized skill-gap and role recommendations based on your input.</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleGoBack}
                  className="rounded-md border border-indigo-200 bg-white px-4 py-2 text-indigo-700 hover:bg-indigo-50"
                >
                  New Analysis
                </button>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-md border border-indigo-200 bg-white px-4 py-2 text-indigo-700 hover:bg-indigo-50"
                >
                  Logout
                </button>
              </div>
            </header>

            {error ? <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-2 text-rose-700">{error}</div> : null}

            <RecommendationResults
              data={
                recommendation
                  ? {
                      ...recommendation,
                      ...(assessmentResult || {}),
                      reportUserName: user?.fullName || '-',
                      reportUserEmail: user?.email || '-',
                    }
                  : null
              }
            />
            <TrendsPanel roleTrends={roleTrends} skillTrends={skillTrends} exportLinks={exportLinks} />
          </div>
        )}
      </main>
      <SiteFooter />
    </>
  )
}
