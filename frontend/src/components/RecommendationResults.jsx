import { downloadAnalysisPdf } from '../utils/pdfReport'

function Tag({ children, tone = 'default' }) {
  const toneStyles = {
    default: 'bg-indigo-100 text-indigo-700',
    danger: 'bg-rose-100 text-rose-700',
    success: 'bg-cyan-100 text-cyan-700',
  }

  return <span className={`inline-flex rounded-full px-3 py-1 text-sm ${toneStyles[tone]}`}>{children}</span>
}

export default function RecommendationResults({ data }) {
  if (!data) {
    return (
      <div className="rounded-lg bg-white p-6 shadow-sm border border-slate-200">
        <p className="text-slate-500">Submit your role and skills to get personalized recommendations.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 rounded-lg border border-indigo-100 bg-white/95 p-6 shadow-xl">
      {data.testScore !== null && data.testScore !== undefined ? (
        <div className="rounded-md border border-indigo-100 bg-gradient-to-r from-indigo-50 to-cyan-50 p-4">
          <div className="mb-3 flex justify-end">
            <button
              type="button"
              onClick={() => downloadAnalysisPdf(data)}
              className="rounded-md bg-gradient-to-r from-indigo-600 to-cyan-600 px-3 py-2 text-sm text-white shadow-md hover:from-indigo-700 hover:to-cyan-700"
            >
              Download PDF Report
            </button>
          </div>

          <h4 className="font-semibold text-indigo-950">Assessment Result</h4>
          <p className="mt-1 text-sm text-indigo-900/80">Score: {data.testScore}/100</p>
          <p className="text-sm text-indigo-900/80">Proficiency: {data.proficiency}</p>
          {data.careerBand ? (
            <div className="mt-2 space-y-1 text-sm text-indigo-900/80">
              <p>Recommended company type: {data.careerBand.companyTypes?.join(', ')}</p>
              <p>Recommended salary band: {data.careerBand.salaryBandLPA}</p>
              <p>Job level fit: {data.careerBand.jobLevel}</p>
            </div>
          ) : null}
        </div>
      ) : null}

      <div>
        <h3 className="text-lg font-semibold text-indigo-950">Role Fit: {data.desiredRole}</h3>
        <p className="text-sm text-indigo-900/80">Current match score: {data.roleMatchScore}%</p>
      </div>

      <div>
        <h4 className="mb-2 font-medium text-indigo-900">Skills You Should Learn</h4>
        <div className="flex flex-wrap gap-2">
          {data.missingSkills.length ? data.missingSkills.map((skill) => <Tag key={skill} tone="danger">{skill}</Tag>) : <Tag tone="success">No gap for selected role</Tag>}
        </div>
      </div>

      <div>
        <h4 className="mb-2 font-medium text-indigo-900">Highly Recommended (Trending + Missing)</h4>
        <div className="flex flex-wrap gap-2">
          {data.recommendedSkills.length ? data.recommendedSkills.map((skill) => <Tag key={skill} tone="success">{skill}</Tag>) : <Tag>Build broader project portfolio</Tag>}
        </div>
      </div>

      <div>
        <h4 className="mb-2 font-medium text-indigo-900">Suggested Career Roles</h4>
        <div className="space-y-2">
          {data.suggestedRoles.map((role) => (
            <div key={role.role} className="flex items-center justify-between rounded-md border border-indigo-100 bg-indigo-50/40 p-3">
              <div>
                <p className="font-medium text-indigo-950">{role.role}</p>
                <p className="text-xs text-indigo-700/80">Market demand: {role.market_demand}</p>
              </div>
              <Tag>{role.match_percentage}% match</Tag>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
