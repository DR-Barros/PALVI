import { useEffect, useState } from 'react'
import ExecutivoBrief from './components/ExecutivoBrief'
import RevenueHealth from './components/RevenueHealth'
import Funnel from './components/Funnel'
import CustomerSupport from './components/CustomerSupport'

const API_URL = import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== '' ? import.meta.env.VITE_API_URL : 'http://localhost:8000'
const SECTION_OPTIONS = [
  { value: 'revenue', label: 'Revenue Health' },
  { value: 'funnel', label: 'Funnel' },
  { value: 'support', label: 'Customer Support' },
]

export default function App() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('A')
  const [days, setDays] = useState([])
  const [selectedDay, setSelectedDay] = useState(null)
  const [activeSection, setActiveSection] = useState('revenue')
  const [loadingDatasets, setLoadingDatasets] = useState(true)
  const [loadingDays, setLoadingDays] = useState(false)

  // Cargar lista de datasets al montar
  useEffect(() => {
    async function loadDatasets() {
      try {
        const response = await fetch(`${API_URL}/api/datasets`)
        if (!response.ok) throw new Error('Error al cargar datasets')
        const data = await response.json()
        setDatasets(data)
        setSelectedDataset(data[0] || 'A')
      } catch (error) {
        console.error('Error cargando datasets:', error)
        setDatasets(['A', 'B', 'C', 'D'])
        setSelectedDataset('A')
      } finally {
        setLoadingDatasets(false)
      }
    }

    loadDatasets()
  }, [])

  // Cargar días cuando cambia el dataset
  useEffect(() => {
    async function loadDays() {
      if (!selectedDataset) return

      setLoadingDays(true)
      try {
        const response = await fetch(`${API_URL}/api/data/${selectedDataset}?days=365`)
        if (!response.ok) throw new Error('Error al cargar días')
        const data = await response.json()

        // Obtener el array de días y excluir los primeros 30
        const allDays = data.latest_days || []
        const filteredDays = allDays.slice(30)

        setDays(filteredDays)

        if (filteredDays.length > 0) {
          setSelectedDay(filteredDays[filteredDays.length - 1].date)
        }
      } catch (error) {
        console.error('Error cargando días:', error)
        setDays([])
        setSelectedDay(null)
      } finally {
        setLoadingDays(false)
      }
    }

    loadDays()
  }, [selectedDataset])

  return (
    <main className="dashboard-shell">
      {/* Barra de controles superior */}
      <div className="dashboard-controls">
        <div className="control-group">
          <label htmlFor="dataset-select">Dataset:</label>
          <select
            id="dataset-select"
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            disabled={loadingDatasets}
          >
            {datasets.map((ds) => (
              <option key={ds} value={ds}>
                {ds}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="day-select">Día:</label>
          <select
            id="day-select"
            value={selectedDay || ''}
            onChange={(e) => setSelectedDay(e.target.value)}
            disabled={loadingDays || days.length === 0}
          >
            <option value="">
              {loadingDays ? 'Cargando días...' : days.length === 0 ? 'Sin días disponibles' : 'Seleccionar día'}
            </option>
            {days.map((day) => (
              <option key={day.date} value={day.date}>
                {day.date}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="dashboard-section-stack">
        <ExecutivoBrief dataset={selectedDataset} day={selectedDay} />

        <div className="dashboard-controls section-controls">
          <div className="section-toggle-group" role="tablist" aria-label="Sección del dashboard">
            {SECTION_OPTIONS.map((section) => {
              const isActive = activeSection === section.value

              return (
                <button
                  key={section.value}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  className={`section-toggle-button${isActive ? ' active' : ''}`}
                  onClick={() => setActiveSection(section.value)}
                >
                  {section.label}
                </button>
              )
            })}
          </div>
        </div>

        {activeSection === 'revenue' && (
          <RevenueHealth dataset={selectedDataset} day={selectedDay} />
        )}

        {activeSection === 'funnel' && (
          <Funnel dataset={selectedDataset} day={selectedDay} />
        )}

        {activeSection === 'support' && (
          <CustomerSupport dataset={selectedDataset} day={selectedDay} />
        )}
      </div>
    </main>
  )
}
