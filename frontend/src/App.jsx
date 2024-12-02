import React from 'react';
import Tabs from './components/tabs';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              EOS System
            </h1>
            <span className="text-sm text-gray-500">
              Version 1.0
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4">
        <Tabs />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4">
          <div className="flex justify-between items-center text-sm text-gray-500">
            <div>
              © {new Date().getFullYear()} EOS System
            </div>
            <div>
              Développé avec ❤️ pour EOS France
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;