import './App.css';
import { MenuInicio } from './features/MenuInicio';
import imagenCartel from "./components/rutacartel.png"
import React, { useState } from 'react';
import {crawlData, indexData, searchData} from "../src/services/apiService"
import { Searcher } from './pages/Searcher';


// npm install axios

function App() {

  const [text, setText] = useState("Contenido")

  const handleCrawler = async () =>{
    var value = await crawlData(5, 50, 4);
    console.log(value.error)
    console.log(value.output)
    setText(value.output)
  }

  const handleIndexer = async () =>{
    var value = await indexData(true);
    console.log(value.error)
    console.log(value.output)
    setText(value.output)
  }

  const handleSearcher = async () =>{
    console.log("BUSCANDO")
    var value = await searchData("Europa es");
    console.log(value.error)
    console.log(value.output)
    setText(value.output)
  }

  const renderTextWithLineBreaks = (text) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        <br />
      </React.Fragment>
    ));
  };
  

  const [activeTab, setActiveTab] = useState("Crawler");

  const renderContent = () => {
    switch (activeTab) {
      case "Crawler":
        return <label>CRAWLER CONTENT</label>;
      case "Indexer":
        return <label>INDEXER CONTENT</label>;
      case "Searcher":
        return <label>SEARCHER CONTENT</label>;
      default:
        return <label>CRAWLER CONTENT</label>;
    }
  };

  return (
    <div className="App">
      <div className="tabs">
        <button
          className={activeTab === "Crawler" ? "active" : ""}
          onClick={() => setActiveTab("Crawler")}
        >
          Crawler
        </button>
        <button
          className={activeTab === "Indexer" ? "active" : ""}
          onClick={() => setActiveTab("Indexer")}
        >
          Indexer
        </button>
        <button
          className={activeTab === "Searcher" ? "active" : ""}
          onClick={() => setActiveTab("Searcher")}
        >
          Searcher
        </button>
      </div>
      <div className="content">{renderContent()}</div>
    </div>
  );
}

export default App;
