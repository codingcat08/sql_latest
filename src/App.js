import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import CreateLineageButton from './components/CreateLineageButton';
import GraphDisplay from './components/GraphDisplay';
import DownloadExcelButton from './components/DownloadExcelButton';

function App() {
    const [graphData, setGraphData] = useState({});
    const [status, setStatus] = useState('');

    const handleUpload = () => {
        setGraphData({});
        setStatus('');
    };

    const handleCreateLineage = (data) => {
        setGraphData(data);
        setStatus('Graph loaded successfully');
    };

    return (
        <div className="App">
            <h1>SQL Lineage Dashboard</h1>
            <FileUpload onUpload={handleUpload} />
            <CreateLineageButton onCreateLineage={handleCreateLineage} setStatus={setStatus} />
            <p>{status}</p>
            <GraphDisplay data={graphData} />
            <DownloadExcelButton />
        </div>
    );
}

export default App;
