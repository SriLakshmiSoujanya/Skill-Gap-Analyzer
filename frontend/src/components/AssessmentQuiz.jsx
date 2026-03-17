import { useMemo, useState } from 'react'

export default function AssessmentQuiz({ questions, onSubmit, loading, onBack }) {
  const [answers, setAnswers] = useState({})

  const attemptedCount = useMemo(() => Object.keys(answers).length, [answers])

  const handleOptionChange = (questionId, selectedIndex) => {
    setAnswers((previous) => ({
      ...previous,
      [questionId]: selectedIndex,
    }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const payload = Object.entries(answers).map(([questionId, selectedIndex]) => ({
      questionId,
      selectedIndex,
    }))
    onSubmit(payload)
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-indigo-950">Skill Assessment Test</h1>
          <p className="mt-1 text-indigo-900/80">Total marks: 100 | 10 questions | 10 marks each</p>
        </div>
        <button
          type="button"
          onClick={onBack}
          className="rounded-md border border-indigo-200 bg-white px-4 py-2 text-indigo-700 hover:bg-indigo-50"
        >
          Back
        </button>
      </header>

      <form onSubmit={handleSubmit} className="space-y-4">
        {questions.map((question, index) => (
          <section key={question.id} className="rounded-lg border border-indigo-100 bg-white/95 p-5 shadow-md">
            <p className="text-sm text-indigo-500">Q{index + 1} • {question.skill}</p>
            <h3 className="mt-1 font-medium text-indigo-950">{question.question}</h3>
            <div className="mt-3 space-y-2">
              {question.options.map((option, optionIndex) => (
                <label key={`${question.id}-${optionIndex}`} className="flex cursor-pointer items-center gap-2 rounded-md border border-indigo-100 px-3 py-2 hover:bg-indigo-50/70">
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    checked={answers[question.id] === optionIndex}
                    onChange={() => handleOptionChange(question.id, optionIndex)}
                    className="h-4 w-4"
                    required
                  />
                  <span className="text-sm text-slate-800">{option}</span>
                </label>
              ))}
            </div>
          </section>
        ))}

        <div className="sticky bottom-4 flex items-center justify-between rounded-lg border border-indigo-100 bg-white px-4 py-3 shadow-lg">
          <p className="text-sm text-indigo-900/80">Answered {attemptedCount} / {questions.length}</p>
          <button
            type="submit"
            disabled={loading}
            className="rounded-md bg-gradient-to-r from-indigo-600 to-cyan-600 px-4 py-2 text-white shadow-md hover:from-indigo-700 hover:to-cyan-700 disabled:opacity-60"
          >
            {loading ? 'Evaluating...' : 'Submit Test'}
          </button>
        </div>
      </form>
    </div>
  )
}
