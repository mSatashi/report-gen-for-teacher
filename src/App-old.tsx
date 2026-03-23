import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import heroImg from './assets/hero.png'
import './App.css'

import './assets/plugins/custom/fullcalendar/fullcalendar.bundle.css'
import './assets/plugins/custom/datatables/datatables.bundle.css'
import './assets/plugins/global/plugins.bundle.css'
import './assets/css/style.bundle.css'
import MainLayout from './layout/MainLayout'
import Dashboard from './pages/dashboard/Dashboard'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

function App() {
  const [count, setCount] = useState(0)

  return (
    // 
    //   <Routes>
    //     <Route path="/" element={<Dashboard />} />
    //   </Routes>
    // </MainLayout>
      <BrowserRouter>
    <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
    </MainLayout>
      </BrowserRouter>
  )
}

export default App
