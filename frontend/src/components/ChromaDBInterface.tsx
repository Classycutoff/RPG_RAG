'use client';

import { useState } from 'react';
import Image from 'next/image';

type Result = {
  text: string;
  metadata: {
    source: string;
    page: number;
  };
  image: string;
  distance: number;
};


export default function ChromaDBInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | null>(null); // New state for file name
  const [textVisibility, setTextVisibility] = useState<Record<number, boolean>>({});

  const handleSearch = async () => {
    const response = await fetch('http://127.0.0.1:5000/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    setResults(data);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setFile(selectedFile || null);
    setFileName(selectedFile ? selectedFile.name : null); // Set the file name
  };


  const handleAddFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/add-file', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    console.log(data);
    setFile(null);
    setFileName(null);
  };

  const toggleTextVisibility = (index: number) => {
    setTextVisibility((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">ChromaDB Interface</h1>
      
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
        <button onClick={handleAddFile} className="bg-green-500 text-white p-2 rounded">
          Add File
        </button>
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
