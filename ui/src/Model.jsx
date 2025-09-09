import './Model.css'
import React from 'react';
import { useState, useEffect } from 'react'
import { Menu, Settings, Search, ChevronDown, ChevronLeft, ChevronRight, Plus, ExternalLink, HelpCircle } from 'lucide-react';

function Model() {
    // const defaultModels = [
    //     { name: 'ab', lastModified: '09/03/2025, 10:48:17 ...' },
    //     { name: 'abc', lastModified: '09/03/2025, 10:48:22 ...' },
    //     { name: 'abcd', lastModified: '09/03/2025, 10:48:30 ...' },
    //     { name: 'c', lastModified: '09/03/2025, 10:48:36 ...' },
    //     { name: 'd', lastModified: '09/03/2025, 10:48:05 ...' },
    //     { name: 'dd', lastModified: '09/03/2025, 10:48:11 ...' },
    //     { name: 'ddd', lastModified: '09/01/2025, 09:56:15 ...' },
    //     { name: 'dddd', lastModified: '09/01/2025, 09:56:22 ...' },
    //     { name: 'eeee', lastModified: '09/01/2025, 09:56:28 ...' },
    //     { name: 'fgee', lastModified: '09/03/2025, 10:47:13 ...' }
    // ];

    const [models, setModels] = useState([]);

    // Method to get list of models from model service
    async function fetchModels() {
        try {
            const response = await fetch('/orchestrator/model/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            // Assuming the response is an array of models
            console.log(data)
            setModels(data);
        } catch (error) {
            console.error('Failed to fetch models:', error);
        }
    }

    // Init function to call fetchModels
    useEffect(() => {
        fetchModels();
    }, []);

    return (
        <main className="flex-1 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Registered Models</h2>
                        {/* <p className="text-gray-600">
                            Share and manage machine learning models.
                            <a href="#" className="text-blue-600 hover:text-blue-800 ml-1 inline-flex items-center">
                                Learn more
                                <ExternalLink className="w-3 h-3 ml-1" />
                            </a>
                        </p> */}
                    </div>
                    <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium">
                        Create Model
                    </button>
                </div>

                {/* Search */}
                <div className="mb-6">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Filter registered models by name or tags"
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                        <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
                        <HelpCircle className="absolute right-3 top-2.5 w-5 h-5 text-gray-400" />
                    </div>
                </div>

                {/* Table */}
                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Name
                                    <ChevronDown className="inline w-3 h-3 ml-1" />
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Latest version
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Aliased versions
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Created by
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Last modified
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Tags
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {models.map((model, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <a href="#" className="text-blue-600 hover:text-blue-800">{model.name}</a>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">—</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">—</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">—</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">{model.lastModified}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">—</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between mt-6">
                    <div className="flex items-center space-x-3">
                        {/* <span className="text-gray-700">New model registry UI</span>
                        <div className="relative inline-block w-10 mr-2 align-middle select-none">
                            <input type="checkbox" name="toggle" id="toggle" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer" defaultChecked />
                            <label htmlFor="toggle" className="toggle-label block overflow-hidden h-6 rounded-full bg-blue-600 cursor-pointer"></label>
                        </div> */}
                    </div>
                    <div className="flex items-center space-x-4">
                        <button className="flex items-center space-x-1 text-gray-500 hover:text-gray-700">
                            <ChevronLeft className="w-4 h-4" />
                            <span>Previous</span>
                        </button>
                        <button className="flex items-center space-x-1 text-blue-600 hover:text-blue-800">
                            <span>Next</span>
                            <ChevronRight className="w-4 h-4" />
                        </button>
                        <div className="flex items-center space-x-2">
                            <select className="border border-gray-300 rounded px-3 py-1 text-sm">
                                <option>10 / page</option>
                                <option>25 / page</option>
                                <option>50 / page</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

export default Model
