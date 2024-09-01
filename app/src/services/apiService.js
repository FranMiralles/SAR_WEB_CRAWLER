import axios from 'axios';

export const crawlData = async (batchSize, documentLimit, maxDepthLevel) => {
    const url = 'http://localhost:5000/api/crawler';

    let params = {
        OUT_BASE_FILENAME: './CrawlerIndexerSearcher/json/crawl.json',
        INITIAL_URL: 'https://es.wikipedia.org/wiki/oric_1',
        BATCH_SIZE: batchSize,
        DOCUMENT_LIMIT: documentLimit,
        MAX_DEPTH_LEVEL: maxDepthLevel,
    };

    try {
        const response = await axios.get(url, { params });
        if(response.data.error=="") response.data.output = "Proceso de crawling completado"
        return response.data;

    } catch (error) {
        return "Error"
    }
};

export const indexData = async (stem, permuterm, multifield, positional) => {
    const url = 'http://localhost:5000/api/indexer';

    let params = {
        dir: './CrawlerIndexerSearcher/json',
        index: './CrawlerIndexerSearcher/indexedData.bin',
    };

    if (stem) params.stem = true;
    if (permuterm) params.permuterm = true;
    if (multifield) params.multifield = true;
    if (positional) params.positional = true;

    try {
        const response = await axios.get(url, { params });
        return response.data;

    } catch (error) {
        return "Error"
    }
};

export const searchData = async (query) => {
    const url = 'http://localhost:5000/api/searcher';

    let params = {
        index: './CrawlerIndexerSearcher/indexedData.bin',
        query: query,
    };

    try {
        const response = await axios.get(url, { params });
        return response.data;

    } catch (error) {
        return "Error"
    }
};

export const getJSONFiles = async (setFiles) => {
    const url = 'http://localhost:5000/api/files';

    try {
        const response = await axios.get(url, {  });
        setFiles(response.data.sort())

    } catch (error) {
        setFiles("ERROR")
    }
}

export const deleteJSONFile = async (file_name) => {
    const url = 'http://localhost:5000/api/crawler/delete_file';

    try {
        const response = await axios.post(url, { file_name:file_name });
        return response.data

    } catch (error) {
        return ["Error"]
    }
}

export const getBinFile = async () => {
    const url = 'http://localhost:5000/api/indexer/check_bin_file';

    try {
        const response = await axios.get(url, {  });
        return response.data

    } catch (error) {
        return ["Error"]
    }
}