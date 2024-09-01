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
      setContent(value.output)
      setLoading(false)
    }else{
      setContent("Inserta una consulta")
    }
  }

  const renderTextWithLineBreaks = (text) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        <br />
      </React.Fragment>
    ));
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
          {loading ? "Cargando..." :renderTextWithLineBreaks(content)}
        </label>
      </div>
    </div>
  );
}