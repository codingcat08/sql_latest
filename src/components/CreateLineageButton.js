import React from 'react';
import axios from 'axios';

function CreateLineageButton({ onCreateLineage, setStatus }) {
    const handleCreateLineage = () => {
        setStatus('Processing...');
        axios.get('/execute_logic')
            .then(response => {
                onCreateLineage(response.data);
                setStatus('Graph loaded successfully');
            })
            .catch(error => {
                console.error('Error:', error);
                setStatus('Failed to load graph');
            });
    };

    return (
        <div>
            <button onClick={handleCreateLineage}>Create Lineage</button>
        </div>
    );
}

export default CreateLineageButton;
