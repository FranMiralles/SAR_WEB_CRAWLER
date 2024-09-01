import "./Searcher.css"

export function Searcher() {

    
    
  
  return (
    <div className="divSearcher">
      <div className="search-bar">
        <div className="search-container">
          <input className="search-input" placeholder="Busca algo..." />
          <div className="search-icon-container">
            <div className="search-vr"></div>
            <button className="search-button"></button>
          </div>
        </div>
      </div>
      <hr className="search-hr" />
      <div className="content-box">
        <label>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent
          aliquam, quam ut consequat tempor, nisl urna malesuada ex, sed tempus
          ligula lectus non neque. Integer bibendum nisl ut ligula scelerisque,
          ut suscipit libero gravida.
        </label>
      </div>
    </div>
  );
}