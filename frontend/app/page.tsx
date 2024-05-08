'use client'

import * as React from 'react';

export default function Home() {
  const [active, setUsers] = React.useState('');
  const [populated, setPopulated] = React.useState(false);

  // React.useEffect(() => getUsers(), [])

  function getUsers() {
    fetch('http://localhost:3333/test', {
      method: 'GET', headers: {
        'Content-Type': 'application/json',
      }
    }).then(res => res.json().then(jsonData => setUsers(jsonData)))
  }

  function populateUsers() {
    fetch('http://localhost:3333/populate', {
      method: 'POST', headers: {
        'Content-Type': 'application/json',
      }
    }).then(res => setPopulated(true))
  }

  const getButton = (
    <button
      className="bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded"
      onClick={getUsers}
    >
      Fetch
    </button>
  )

  const seedButton = (
    <button
      className="bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded"
      onClick={populateUsers}
    >
       <>{populated ? "Data is populated! You want more?" : "Populate some data!"}</>
    </button>
  )
  return (
    <div className="flex flex-col space-y-4">
      <h1 className="text-xl">Gabe&lsquos Awesome Server Admin Page</h1>
      <>{seedButton}</>
      <>{active.length == 0 ? (getButton) : (<div className="text-xs" ><pre>{JSON.stringify(active, null, 2)}</pre></div>)}</>
    </div>
  )
}
