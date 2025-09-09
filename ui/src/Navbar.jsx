import './Navbar.css'
import { Menu, Settings, Search, ChevronDown, ChevronLeft, ChevronRight, Plus, ExternalLink, HelpCircle } from 'lucide-react';
import Model from './Model.jsx'

function Navbar() {

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Menu className="w-5 h-5 text-gray-600" />
            <div className="flex items-center space-x-2">
              <span className="text-blue-600 font-semibold text-lg">Triton Mesh</span>
              <span className="text-gray-400 text-sm">0.0.1</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Settings className="w-5 h-5 text-gray-600" />
            <a href="#" className="text-gray-600 hover:text-gray-800">GitHub</a>
            <a href="#" className="text-gray-600 hover:text-gray-800">Docs</a>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-48 bg-white border-r border-gray-200 min-h-screen">
          <div className="p-4">
            {/* <button className="flex items-center space-x-2 text-gray-700 hover:bg-gray-100 w-full px-3 py-2 rounded">
              <Plus className="w-4 h-4" />
              <span>New</span>
            </button> */}
          </div>
          <nav className="px-4 space-y-1">
            <a href="#" className="flex items-center space-x-2 text-gray-700 hover:bg-gray-100 px-3 py-2 rounded">
              <span>🖥️</span>
              <span>Servers</span>
            </a>
            <a href="#" className="flex items-center space-x-2 text-blue-600 bg-blue-50 px-3 py-2 rounded">
              <span>📦</span>
              <span>Models</span>
            </a>
          </nav>
        </aside>

        {/* Main Content */}
        <Model />
        
      </div>
    </div>
  );
};

export default Navbar
