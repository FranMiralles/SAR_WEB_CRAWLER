import './App.css';
import React, { useState, useEffect } from 'react';
import { indexData } from "../src/services/apiService"
import { Searcher } from './pages/Searcher';
import { Crawler } from './pages/Crawler';
import { Indexer } from './pages/Indexer';


// npm install axios

function App() {

  const [text, setText] = useState("Contenido")
  const [activeTab, setActiveTab] = useState("Crawler");
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    document.body.style.cursor = loading ? 'wait' : 'default';
    return () => {
      document.body.style.cursor = 'default';
    };
  }, [loading])

  const renderTextWithLineBreaks = (text) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        <br />
      </React.Fragment>
    ));
  };
  

  

  const renderContent = () => {
    switch (activeTab) {
      case "Crawler":
        return <Crawler loading={loading} setLoading={setLoading} />;
      case "Indexer":
        return <Indexer loading={loading} setLoading={setLoading} />;
      case "Searcher":
        return <Searcher loading={loading} setLoading={setLoading} />;
      default:
        return <></>;
    }
  };

  return (
    <div className="App">
      <div className="tabs">
        <button
          className={activeTab === "Crawler" ? "active" : ""}
          onClick={() => setActiveTab("Crawler")}
          disabled={loading}
        >
          CRAWLER
        </button>
        <button
          className={activeTab === "Indexer" ? "active" : ""}
          onClick={() => setActiveTab("Indexer")}
          disabled={loading}
        >
          INDEXER
        </button>
        <button
          className={activeTab === "Searcher" ? "active" : ""}
          onClick={() => setActiveTab("Searcher")}
          disabled={loading}
        >
          SEARCHER
        </button>
      </div>
      <div className="content">{renderContent()}</div>
    </div>
  );
}

export default App;
