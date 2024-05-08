'use client'

import * as React from 'react';


export default function Home() {
  const [searchResults, setSearchResults] = React.useState('');
  const [focus, setFocus] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('')
  const [companyFilter, setCompanyFilter] = React.useState('')
  const [uploading, setUploading] = React.useState(false);
  const [companyOptions, setOptions] = React.useState([]);

  React.useEffect(() => {
    (async () => {
      const res = await fetch("http://localhost:3333/companies");
      const json = await res.json()
      setOptions(json['companies'])
    })();
  }, []);  
    
  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    setUploading(true)

    const file = event.target.files![0];
    const formData = new FormData();

    formData.append('file', file);

    try {
      await fetch('http://localhost:3333/upload', {
        method: 'POST',
        body: formData
      }).then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('File upload failed');
        }
      })
        .then(data => {
          console.log('Server response:', data);
        })
        .catch(error => {
          console.error('Error uploading file:', error);
        });
      // Update state or display the enhanced image
    } catch (error) {
      console.error('Error enhancing image:', error);
    }
    setUploading(false)
  };

  const handleSearchBarChange = (e: React.FormEvent<HTMLInputElement>) => {
    e.preventDefault(); // prevent the default action
    setSearchTerm(e.currentTarget.value); // set name to e.target.value (event)
  }

  function search() {
    fetch(
      'http://localhost:3333/search',
      {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_term: searchTerm, company_filter: companyFilter })
      }).then(res => res.json().then(jsonData => setSearchResults(jsonData)))
  }

  const searchBar = (
    <div className="flex flex-row space-x-4" >
      <div className="relative mr-3">
        {!focus && (<div className="absolute top-3 left-3 items-center" >
          <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"></path></svg>
        </div>)}
        <input
          type="text"
          className="block p-2 pl-10 w-70 text-gray-900 bg-gray-50 rounded border border-gray-300 focus:pl-3"
          placeholder="Search Here..."
          onFocus={() => setFocus(true)}
          onChange={handleSearchBarChange}
          onBlur={() => setFocus(false)}
        />
      </div>
      <div className="block p-2 text-gray-900 bg-gray-50 rounded border border-gray-300 focus:pl-3">
      <select value={companyFilter} onChange={(e) => setCompanyFilter(e.currentTarget.value)} className="py-2 text-sm text-gray-900">
        {companyOptions.map((company) => (
          <option key={company} value={company} className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">
            {company}
          </option>
        ))}
      </select>
      </div>
      <button
        className="bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded"
        onClick={search}
      >
        Search
      </button>
    </div>
  )

  return (
    <div className="flex flex-col space-y-4">
      <h1 className="text-xl">Hebbia Search</h1>
      <>{searchBar}</>
      <>{searchResults.length == 0 ? (<></>) : (<div className="text-xs" ><pre>{JSON.stringify(searchResults, null, 2)}</pre></div>)}</>
      <div>
        {uploading ? (<p>Uploading...</p>) : <input type="file" accept="html" onChange={handleImageUpload} />}
      </div>
    </div>
  )
}
