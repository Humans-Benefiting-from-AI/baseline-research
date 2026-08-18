import { useState, useMemo } from 'react'
import registryData from './data/registry.json'
import './App.css'

interface Project {
  id: number
  name: string
  category: string
  maturity: string
  link: string
  description: string
  core_feature: string
  differentiator: string
  variation_ideas: string[]
}

const projects: Project[] = registryData as Project[]

function App() {
  const [filter, setFilter] = useState('All')
  const [search, setSearch] = useState('')

  const categories = useMemo(() => {
    const cats = new Set(projects.map(p => p.category))
    return ['All', ...Array.from(cats)].sort()
  }, [])

  const filteredProjects = useMemo(() => {
    return projects.filter(p => {
      const matchCat = filter === 'All' || p.category === filter
      const matchSearch = p.name.toLowerCase().includes(search.toLowerCase()) || 
                          p.description.toLowerCase().includes(search.toLowerCase()) ||
                          p.core_feature.toLowerCase().includes(search.toLowerCase())
      return matchCat && matchSearch
    })
  }, [filter, search])

  return (
    <div className="container">
      <header className="header">
        <div className="branding">
          <h1>Baseline Research</h1>
          <p className="subtitle">The independent registry and audit of 110 Jewish AI tools.</p>
        </div>
        <div className="controls">
          <input 
            type="text" 
            placeholder="Search tools, features, descriptions..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
        </div>
      </header>

      <main>
        <div className="metrics">
          Showing <strong>{filteredProjects.length}</strong> of <strong>{projects.length}</strong> tools
        </div>
        <div className="grid">
          {filteredProjects.map((p) => (
            <article key={p.id} className="card">
              <div className="card-header">
                <h2>
                  {p.link && p.link !== 'NaN' ? (
                    <a href={p.link} target="_blank" rel="noreferrer">{p.name}</a>
                  ) : (
                    p.name
                  )}
                </h2>
                <div className="badges">
                  <span className="badge category">{p.category}</span>
                  <span className="badge maturity">{p.maturity}</span>
                </div>
              </div>
              <div className="card-body">
                <p className="description">{p.description}</p>
                
                <div className="analysis-section">
                  <h3>Core Feature</h3>
                  <p>{p.core_feature}</p>
                </div>
                
                <div className="analysis-section highlight">
                  <h3>Differentiator</h3>
                  <p>{p.differentiator}</p>
                </div>
                
                <div className="analysis-section">
                  <h3>Variation Ideas</h3>
                  <ul className="variation-list">
                    {p.variation_ideas.map((idea, index) => (
                      <li key={index}>{idea}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>
          ))}
        </div>
      </main>
    </div>
  )
}

export default App
