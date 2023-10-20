# JS Data Generator for MongoDB

![Project Image](project-image-url-if-available)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Description

The **JS Data Generator for MongoDB** is a simple tool that allows you to generate data and store it in a MongoDB database using JavaScript. This project provides an easy way to import data from a CSV file into your MongoDB database, making it useful for data migration and data seeding tasks.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-username/JS-Data-Generator-MongoDB.git

Step 2: Install Dependencies

Navigate to the project folder:

  cd JS-Data-Generator-MongoDB
  
Install the required dependencies using npm:
  
  npm install

Step 3: Configure the Application

Open the script.js file in a text editor or code editor and update the MongoDB server configuration. Replace the placeholders with your MongoDB server details:

  const host = "mongodb://your-host:your-port"; // Replace with your MongoDB host and port
  const dbName = "your-database"; // Replace with your database name
  const collectionName = "your-collection"; // Replace with your collection name
  
Step 4: Run the Application

Once you've configured the application, you can run it using the following command:

  node script.js

The application will connect to your MongoDB server and prompt you to enter the database name, collection name, and the path to the CSV file containing data to import.
Follow the prompts and the application will import the data from the CSV file into your specified MongoDB collection.
That's it! You have successfully cloned the repository, configured the application, and executed it to import data into MongoDB.
