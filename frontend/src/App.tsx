import React, { Suspense } from 'react';

const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Profile = React.lazy(() => import('./pages/Profile'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Dashboard />
      <Settings />
      <Profile />
    </Suspense>
  );
}

export default App;