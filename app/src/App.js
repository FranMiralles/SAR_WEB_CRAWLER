import './App.css';
import { MenuInicio } from './features/MenuInicio';
import imagenCartel from "./components/rutacartel.png"
import React, { useState } from 'react';
import axios from 'axios';

// npm install axios

function App() {

  const [labelIndexer, setLabelIndexer] = useState("Label indexer")
  const handleIndexer = async () =>{
    var value = await fetchData();
    console.log(value.output)
    setLabelIndexer(value.output)
  }

  

  return (
    <div className="app">
      
      <div className="menu-buttons">
        <button className="menu-button" onClick={handleIndexer}>INDEXER</button>
        <button className="menu-button">Opción 2</button>
        <button className="menu-button">Opción 3</button>
      </div>
      <label>{labelIndexer}</label>
    </div>
  );
}

export default App;
