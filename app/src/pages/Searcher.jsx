import "./Searcher.css"
import React, { useState } from "react";
import { searchData } from "../services/apiService"

export function Searcher({loading, setLoading}) {

  const [query, setQuery] = useState("")
  const [content, setContent] = useState("")

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSearcher = async () =>{
    if(query != ""){
      setLoading(true)
      var value = await searchData(query);
      console.log(value)
      console.log(value.output)
      console.log(value.error)
      setContent(value.output)
      setLoading(false)
    }else{
      setContent("Inserta una consulta")
    }
  }

  const renderTextWithLinks = (text) => {
    return text.split('\n').map((line, index) => {
      const urlMatch = line.match(/(.*?):\s*(https?:\/\/\S+)/);
      if (urlMatch) {
        const label = urlMatch[1].trim();
        const url = urlMatch[2].trim();

        return (
          <React.Fragment>
            <div className="div-content-result">
              <label>{label}:</label>
              <a href={url} target="_blank" rel="noopener noreferrer"> {url} </a>
            </div>
          </React.Fragment>
        );
      }
    });
  };
  

  return (
    <div className="divSearcher">
      <div className="search-bar">
        <div className="search-container">
          <input className="search-input" placeholder="Realiza una consulta..." value={query} onChange={handleQueryChange} />
          <div className="search-icon-container">
            <div className="search-vr"></div>
            <button className="help-button" disabled={loading}></button>
            <button className="search-button" onClick={handleSearcher} disabled={loading}></button>
          </div>
        </div>
      </div>
      <hr className="search-hr" />
      <div className="content-box">
        <label>
          {loading ? "Cargando..." :renderTextWithLinks(content)}
        </label>
      </div>
    </div>
  );
}