import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Host from './Host';
import Play from './Play';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Host />} />
        <Route path="/play" element={<Play />} />
      </Routes>
    </Router>
  );
}

export default App;
