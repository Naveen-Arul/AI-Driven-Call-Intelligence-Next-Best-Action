# AI-Driven Call Intelligence Platform - Frontend

React-based frontend for the Call Intelligence Platform.

## Features

- **Dashboard**: Real-time analytics and system health monitoring
- **Process Call**: Upload and analyze call recordings
- **Calls Management**: View, filter, and manage all processed calls
- **Call Details**: Comprehensive view of individual call analysis
- **Knowledge Base**: Upload company policies for context-aware decisions

## Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

## Installation

```bash
cd frontend
npm install
```

## Running the Application

```bash
npm start
```

The application will open at `http://localhost:3000`

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.js
│   │   ├── ProcessCall.js
│   │   ├── CallsList.js
│   │   ├── CallDetail.js
│   │   └── CompanyContext.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── App.css
│   └── index.js
└── package.json
```

## Design Principles

- Clean, professional UI with blue gradient theme
- Easy-to-read typography and spacing
- Responsive design for all screen sizes
- Real-time data updates
- User-friendly form interactions
- Clear visual feedback for all actions

## API Integration

The frontend connects to the backend API at `http://localhost:8000`. All API calls are centralized in `src/services/api.js` for easy maintenance.

## Color Scheme

- Primary: Blue gradient (#1e40af to #3b82f6)
- Success: Green (#10b981)
- Warning: Yellow (#f59e0b)
- Danger: Red (#ef4444)
- Background: Light gray (#f8f9fa)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
