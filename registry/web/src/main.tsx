import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import Whitepaper from './Whitepaper.tsx'
import './index.css'

// Extremely simple router for the static site
const path = window.location.pathname;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {path === '/whitepaper' ? <Whitepaper /> : <App />}
  </React.StrictMode>,
)
