import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import EnqueteurApp from './components/EnqueteurApp.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <EnqueteurApp />
  </StrictMode>,
)