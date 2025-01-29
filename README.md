SQL Lineage Dashboard
Project Overview
This project aims to create an interactive SQL Lineage Dashboard that allows users to upload SQL queries, generate detailed column descriptions, visualize the lineage graph, and understand the relationships between columns in the dataset.

Table of Contents
Project Structure

Setup and Installation

Usage

Backend Description

Frontend Description

Graph Visualization

Project Structure
sql-lineage-dashboard/
│
├── backend/
│   ├── app.py
│   ├── script.py
│
├── frontend/
│   ├── src/
│       ├── components/
│           ├── CreateLineageButton.js
│           ├── FileUpload.js
│           ├── GraphDisplay.js
│       ├── App.js
│
├── README.md
├── package.json
├── .gitignore
└── ...
Setup and Installation
Backend
Navigate to sql-lineage-dashboard/ directory:

sh
Install required Python packages:

sh
pip install flask sqlparse sqllineage pandas openai
Run the Flask server:

sh
python app.py

Frontend
Navigate to the sql-lineage-dashboard/ directory:

sh
Install required Node.jspackages:

sh
npm install
Start the React application:

sh
npm start

Usage//

Upload SQL Queries:

Use the FileUpload component to upload SQL query files.

Create Lineage:

Click the "Create Lineage" button to generate the lineage graph.


Visualize Graph:

The GraphDisplay component will render the lineage graph based on the uploaded SQL queries.

Functionality:

Parsing SQL context, detecting transformations, generating descriptions, and exporting reports using pandas.

Frontend Description
Components
FileUpload.js

Allows users to upload SQL query files.

Located in frontend/src/components/.

CreateLineageButton.js

Handles the creation of SQL lineage by sending requests to the backend.

Displays status messages to indicate processing and successful graph creation.

Located in frontend/src/components/.

GraphDisplay.js

Renders the SQL lineage graph using vis-network/standalone.

Displays nodes and edges representing the relationships between columns.

Located in frontend/src/components/.

App.js

Main application component coordinating interactions between other components.

Located in frontend/src/.

Graph Visualization
The graph visualization displays the relationships and dependencies between columns in the dataset. Below is an example of the graph generated by the application:


Description:

The nodes represent individual columns.

The edges indicate relationships or dependencies between the columns.

Different colors and labels help distinguish various columns and their sources.
