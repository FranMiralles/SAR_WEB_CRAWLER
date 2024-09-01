import React, { useEffect, useState } from "react";
import { crawlData, deleteJSONFile, getJSONFiles } from "../services/apiService"
import "./Crawler.css"

export function Crawler({loading, setLoading}) {

    const [files, setFiles] = useState([]);
    const [content, setContent] = useState("")
    const [batchSize, setBatchSize] = useState(5)
    const [documentLimit, setDocumentLimit] = useState(50)
    const [maxDepth, setMaxDepth] = useState(4)

    useEffect(() => {
        getJSONFiles(setFiles);
    }, []);

    const handleCrawler = async () =>{
        setLoading(true)
        var value = await crawlData(batchSize, documentLimit, maxDepth);
        setLoading(false)
        setContent(value.output)
        getJSONFiles(setFiles);
    }

    const handleBatchSize = (event) => {
        setBatchSize(event.target.value);
    };

    const handleDocumentLimit = (event) => {
        setDocumentLimit(event.target.value);
    };

    const handleMaxDepth = (event) => {
        setMaxDepth(event.target.value);
    };

    const handleDeleteFile = (event) => {
        deleteJSONFile(event.target.value).then(() =>{
            getJSONFiles(setFiles);
        })
    }
    
    return (
        <div className="divCrawler">
            <div className="input-section">
                <div className="inputs">
                <div className="input-group">
                    <label>Documentos por fichero:</label>
                    <input type="number" value={batchSize} onChange={handleBatchSize} disabled={loading} />
                </div>
                <div className="input-group">
                    <label>Límite de documentos:</label>
                    <input type="number" value={documentLimit} onChange={handleDocumentLimit}  disabled={loading} />
                </div>
                <div className="input-group">
                    <label>Profundidad máxima:</label>
                    <input type="number" value={maxDepth} onChange={handleMaxDepth}  disabled={loading} />
                </div>
                </div>
                <button className="execute-button" onClick={handleCrawler}  disabled={loading}>EJECUTAR</button>
            </div>

            <div className="console-output">
                <label>Salida de consola:</label>
                <div className="console-box">
                {loading ? "Cargando..." : content}
                </div>
            </div>

            <div className="files-result">
                <label>Archivos resultado: {files.length}</label>
            </div>
            <div className="file-list">
                {files.map((file, index) => (
                <div key={index} className={index != files.length - 1 ? "file-item" : "file-last-item"}>
                    <img
                    src="https://cdn-icons-png.flaticon.com/128/3735/3735057.png"
                    alt="folder icon"
                    className="file-icon"
                    />
                    <span>{"/json/" + file}</span>
                    <button className="file-bin-icon" value={file} onClick={handleDeleteFile} disabled={loading}></button>
                </div>
                ))}
            </div>
        </div>
    );
}