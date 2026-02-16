import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ProcessCall from './components/ProcessCall';
import CallsList from './components/CallsList';
import CallDetail from './components/CallDetail';
import CompanyContext from './components/CompanyContext';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        {/* Navigation */}
        <nav className="navbar">
          <div className="navbar-content">
            <div className="navbar-brand">
              🎯 Call Intelligence Platform
            </div>
            <ul className="navbar-nav">
              <li>
                <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  📊 Dashboard
                </NavLink>
              </li>
              <li>
                <NavLink to="/process" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  🎙️ Process Call
                </NavLink>
              </li>
              <li>
                <NavLink to="/calls" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  📋 Calls
                </NavLink>
              </li>
              <li>
                <NavLink to="/knowledge" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  🧠 Knowledge Base
                </NavLink>
              </li>
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/process" element={<ProcessCall />} />
            <Route path="/calls" element={<CallsList />} />
            <Route path="/calls/:callId" element={<CallDetail />} />
            <Route path="/knowledge" element={<CompanyContext />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
