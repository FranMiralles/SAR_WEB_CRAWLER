const indexData = async () => {
    const url = 'http://localhost:5000/api/indexer';

    try {
        const response = await axios.get(url, {
            params: {
                dir: 100,
                index: '100_simple.bin',
                permuterm: true,
            }
        });

        return response.data

    } catch (error) {
        return "Error"
    }
};