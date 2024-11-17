# Comprehensive Weather Data Processing System
## Objective
> Develop a comprehensive weather data processing system that handles real-time storm data.

> The system will consist of three main services: a Data Collection Service that fetches storm reports from NOAA, a Golang service for ETL operations, and a NodeJS (or Golang) service that exposes the processed data through an API.
## Requirements
### 1. Data Collection Service:
• Service Bootstrapping:

    • Set up initial configurations, logging, and establish a Kafka producer.
• Data Ingestion:

    • Implement a scheduled task or webhook that accesses the NOAA Climatology Reports page: NOAA Storm Reports. This should fetch new data ideally every 24 hours or more frequently if required.
    • Parse the CSV content to extract storm report data, which could include parameters like location, time, and type of storm.

• Data Publishing:

    • Format the raw data appropriately and publish it to the Kafka topic named raw-weather-reports.

• Error Handling:

    • Handle potential issues such as connectivity failures, data parsing errors, and publishing failures.

• Testing:

    • Write tests to ensure the reliability and accuracy of the data collection and publishing processes.

### 2. Golang Service:

• Service Bootstrapping:

    • Configure and initialize service dependencies, logging, and Kafka connections.
• Kafka Consumer:

    • Consume incoming weather data from the raw-weatherreports topic.
• Data Processing:
    • Perform ETL operations to standardize and enrich the storm data.

• Data Publishing:

    • Serialize and publish the processed data to a new Kafka topic named transformed-weather-data.
• Error Handling:

    • Develop robust error handling mechanisms for the ETL process.
• Testing:

    • Create unit tests to validate the transformations and data handling.
### 3. NodeJS Service:
• Service Bootstrapping:

    • Initialize all components including Kafka consumers, database connections, and API routes.
• Kafka Consumer:

    • Listen to the transformed-weather-data topic for processed data.
• Data Handling:

    • Store the transformed data in a structured format in a database.
• API Endpoint:

    • Develop an API that allows users to query the storm data by date and location.

• Logging and Monitoring:

    • Implement logging for API requests and data processing tasks, along with metrics for monitoring system performance.
### 4. Documentation:
• Provide comprehensive documentation including:

    • System architecture diagrams.
    • Setup and operational instructions.
    • Detailed descriptions of each component's functionality and interactions.
### 5. Code Quality:
• Ensure all code is clean, modular, and adheres to industry best practices.
### 6. Bonus Points:
• Dockerize each service for easy setup and deployment.

• Optimize CSV reader for large file sizes.

• Use Docker Compose or some other tool to manage local development environments including Kafka and databases.

• Build a simple front-end application to visualize the reports.

### Evaluation Criteria
• System Architecture and Bootstrapping: Effectiveness and efficiency of the initial setup and overall system design.

• Functionality: Full system operation with accurate and timely data processing.

• Code Quality: Adherence to best coding practices and standards.

• Innovative Problem Solving: Creativity and effectiveness in addressing challenges of real-time data processing and availability.