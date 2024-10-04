import "./Indexer.css"
import React, { useState, useEffect } from "react"
import { getBinFile, indexData } from "../services/apiService"

export function Indexer({loading, setLoading}) {

    const [content, setContent] = useState("")
    const [stem, setStem] = useState(false)
    const [permuterm, setPermuterm] = useState(false)
    const [multifield, setMultifield] = useState(false)
    const [positionals, setPositionals] = useState(false)
    const [binFile, setBinFile] = useState("")

    useEffect(() => {
        getBinFile().then((res)=>{
            if(res.found) setBinFile(res.files[0])
        });
    }, []);

    const handleIndexer = async () =>{
        setLoading(true)
        var value = await indexData(stem, permuterm, multifield, positionals);
        getBinFile().then((res)=>{
            if(res.found) setBinFile(res.files[0])
        });
        setContent(value.output)
        setLoading(false)
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
        <div className="divIndexer">
            <div className="indexer-input-section">
                <div className="indexer-inputs">
                    <div className="indexer-input-group">
                        <input type="checkbox" disabled={loading} checked={stem} onClick={()=>setStem(!stem)} />
                        <label className="indexer-input-group-label" onClick={()=>setStem(!stem)}>STEMMING</label>
                    </div>
                    <div className="indexer-input-group">
                        <input type="checkbox" disabled={loading} checked={permuterm} onClick={()=>setPermuterm(!permuterm)} />
                        <label className="indexer-input-group-label" onClick={()=>setPermuterm(!permuterm)}>PERMUTERM</label>
                    </div>
                    <div className="indexer-input-group">
                        <input type="checkbox" disabled={loading} checked={multifield} onClick={()=>setMultifield(!multifield)} />
                        <label className="indexer-input-group-label" onClick={()=>setMultifield(!multifield)}>CAMPO MÚLTIPLE</label>
                    </div>
                    <div className="indexer-input-group">
                        <input type="checkbox" disabled={loading} checked={positionals} onClick={()=>setPositionals(!positionals)} />
                        <label className="indexer-input-group-label" onClick={()=>setPositionals(!positionals)}>LISTAS POSICIONALES</label>
                    </div>
                </div>
                <div style={{display:"flex", flexDirection:"column"}}>
                    <button className="indexer-execute-button" disabled={loading} onClick={handleIndexer}>EJECUTAR</button>
                    {binFile == "" ? 
                        <label className="indexer-binFile-prompt">No se ha indexado</label> 
                        : 
                        <>
                            <label className="indexer-binFile-prompt">Indexado en:</label>
                            <label className="indexer-binFile">{binFile}</label>
                        </>
                    }
                </div>
            </div>

            <div className="indexer-console-output">
                <label>Salida de consola:</label>
                <div className="indexer-console-box">
                {loading ? "Cargando..." : renderTextWithLineBreaks(content)}
                </div>
            </div>
        </div>
    );
}