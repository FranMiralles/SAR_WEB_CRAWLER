import './App.css';
import { MenuInicio } from './features/MenuInicio';
import imagenCartel from "./components/rutacartel.png"
import React, { useState } from 'react';
import {crawlData, indexData, searchData} from "../src/services/apiService"


// npm install axios

function App() {

  const [labelIndexer, setLabelIndexer] = useState("Label indexer")

  const handleCrawler = async () =>{
    var value = await crawlData(5, 50, 4);
    console.log(value.output)
    setLabelIndexer(value.output)
  }

  const handleIndexer = async () =>{
    var value = await indexData(true);
    console.log(value.output)
    setLabelIndexer(value.output)
  }

  const handleSearcher = async () =>{
    var value = await searchData("precisión");
    console.log(value.output)
    setLabelIndexer(value.output)
  }

  

  return (
    <div className="app">
      
      <div className="menu-buttons">
        <button className="menu-button" onClick={handleCrawler}>CRAWLER</button>
        <button className="menu-button" onClick={handleIndexer}>INDEXER</button>
        <button className="menu-button" onClick={handleSearcher}>SEARCHER</button>
      </div>
      <label>{labelIndexer}</label>
    </div>
  );
}

export default App;
