import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Home from './components/Home';
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
              <svg className="brand-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14l9-5-9-5-9 5 9 5z"/>
                <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
                <path d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222"/>
              </svg>
              Call Intelligence Platform
            </div>
            <ul className="navbar-nav">
              <li>
                <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <svg className="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                  </svg>
                  Home
                </NavLink>
              </li>
              <li>
                <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <svg className="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                    <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                  </svg>
                  Dashboard
                </NavLink>
              </li>
              <li>
                <NavLink to="/process" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <svg className="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                  </svg>
                  Process Call
                </NavLink>
              </li>
              <li>
                <NavLink to="/calls" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <svg className="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                    <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                  </svg>
                  Calls
                </NavLink>
              </li>
              <li>
                <NavLink to="/knowledge" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <svg className="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                  </svg>
                  Knowledge Base
                </NavLink>
              </li>
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
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
