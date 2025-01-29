import React, { useState } from 'react';
import axios from 'axios';

function FileUpload({ onUpload }) {
    const [file, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = () => {
        if (!file) {
            alert("Please select an SQL file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("sql_file", file);

        axios.post('/store_queries', formData)
            .then(response => {
                alert(response.data.message);
                onUpload();
            })
            .catch(error => console.error('Error:', error));
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} accept=".sql" />
            <button onClick={handleUpload}>Upload SQL File</button>
        </div>
    );
}

export default FileUpload;
