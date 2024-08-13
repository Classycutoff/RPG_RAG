'use client';

import { useState } from 'react';
import Image from 'next/image';

import { Result } from '../types';


export default function ChromaDBInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null); // New state for file name
  const [textVisibility, setTextVisibility] = useState<Record<number, boolean>>({});

  const handleSearch = async () => {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      console.error('Error fetching data from the proxy API:', response.statusText);
      return;
    }
    
    const data = await response.json();
    console.log(data['message']);
    console.log(data)
    setResults(data['filtered_results']);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setFile(selectedFile || null);
    setFileName(selectedFile ? selectedFile.name : null); // Set the file name
  };


  const handleAddFile = async () => {
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/add-file', {
          method: 'POST',
          body: formData,
      });

      const data = await response.json();
      console.log(data);
      setFile(null);
      setFileName(null);
    } catch (error) {
        console.error('Error uploading file:', error);
    } finally {
        setIsLoading(false); // Set loading to false when the process is done
    }
  };

  const toggleTextVisibility = (index: number) => {
    setTextVisibility((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">PDF Rag Interface</h1>
      
      <div className="mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query"
          className="border p-2 mr-2"
        />
        <button onClick={handleSearch} className="bg-blue-500 text-white p-2 rounded">
          Search
        </button>
        {fileName && (
          <p className="mt-2 text-sm text-gray-600">Selected file: {fileName}</p>
        )}
      </div>

      <div className="mb-4">
    <input type="file" onChange={handleFileUpload} className="mr-2" />
    <button 
        onClick={handleAddFile} 
        className="bg-green-500 text-white p-2 rounded"
        disabled={isLoading} // Optionally disable the button during loading
    >
        Add File
    </button>
    {isLoading && (
        <div className="ml-2 inline-block">
            {/* Simple spinner, you can replace this with any spinner component or custom styling */}
            <svg 
                className="animate-spin h-5 w-5 text-gray-500" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24"
            >
                <circle 
                    className="opacity-25" 
                    cx="12" 
                    cy="12" 
                    r="10" 
                    stroke="currentColor" 
                    strokeWidth="4"
                ></circle>
                <path 
                    className="opacity-75" 
                    fill="currentColor" 
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                ></path>
            </svg>
            <p>Adding files might take a while...</p>
        </div>
    )}
</div>

      <div>
        <h2 className="text-xl font-semibold mb-2">Results:</h2>
        {results.map((result, index) => (
          <div key={index} className="mb-4 p-4 border rounded">
            <p className="text-sm text-gray-600">
              Source: {result.metadata.source}, Page: {result.metadata.page}, Distance: {result.distance}
            </p>

            <button
              onClick={() => toggleTextVisibility(index)}
              className="flex items-center space-x-2 mb-2"
            >
              <span>{textVisibility[index] ? '▼' : '▲'}</span>
              <span>{textVisibility[index] ? 'Hide Text' : 'Show Text'}</span>
            </button>

            {textVisibility[index] && <p>{result.text}</p>}
            {result.image && (
              <Image 
                src={`${result.image}`} 
                alt="PDF Page" 
                className="mt-2 img-class" 
                width={200} 
                height={200}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
