import React from 'react';
import axios from 'axios';

function DownloadExcelButton() {
    const handleDownload = () => {
        axios({
            url: '/export_report', // Endpoint to download the Excel file
            method: 'GET',
            responseType: 'blob', // Important
        }).then((response) => {
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'column_descriptions.xlsx'); // File name
            document.body.appendChild(link);
            link.click();
        }).catch((error) => {
            console.error('Error downloading file:', error);
        });
    };

    return (
        <button onClick={handleDownload}>Download Excel</button>
    );
}

export default DownloadExcelButton;
