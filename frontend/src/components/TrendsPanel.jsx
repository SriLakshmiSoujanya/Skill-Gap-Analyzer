export default function TrendsPanel({ roleTrends, skillTrends, exportLinks }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section className="rounded-lg border border-indigo-100 bg-white/95 p-6 shadow-lg">
        <h3 className="mb-3 text-lg font-semibold text-indigo-950">Trending Roles (Latest Year)</h3>
        <ul className="space-y-2">
          {roleTrends.map((item, index) => (
            <li key={item.role} className="flex justify-between border-b border-indigo-50 pb-1 text-sm">
              <span className="capitalize">{item.role}</span>
              <span className="font-semibold text-indigo-700">#{index + 1}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-lg border border-indigo-100 bg-white/95 p-6 shadow-lg">
        <h3 className="mb-3 text-lg font-semibold text-indigo-950">Trending Skills (Across Years)</h3>
        <ul className="space-y-2">
          {skillTrends.map((item, index) => (
            <li key={item.skill} className="flex justify-between border-b border-indigo-50 pb-1 text-sm">
              <span>{item.skill}</span>
              <span className="font-semibold text-indigo-700">#{index + 1}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="lg:col-span-2 rounded-lg border border-indigo-100 bg-white/95 p-6 shadow-lg">
        <h3 className="mb-2 text-lg font-semibold text-indigo-950">Power BI Data Exports</h3>
        <p className="mb-3 text-sm text-indigo-900/80">Use these CSV endpoints in Power BI Get Data from Web.</p>
        <div className="flex flex-wrap gap-3 text-sm">
          {Object.entries(exportLinks).map(([name, url]) => (
            <a
              key={name}
              href={url}
              target="_blank"
              rel="noreferrer"
              className="rounded-md border border-indigo-200 bg-indigo-50/40 px-3 py-1 text-indigo-700 hover:bg-indigo-100"
            >
              {name}
            </a>
          ))}
        </div>
      </section>
    </div>
  )
}
