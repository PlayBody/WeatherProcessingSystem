import express from "express";
import { KafkaClient, Consumer } from "kafka-node";
import mongoose from "mongoose";
import bodyParser from "body-parser";
import config from "config";
import StormReport from "./models/StormReport.js"; // Ensure the file extension is included

const app = express();
app.use(bodyParser.json());

// MongoDB Configuration
mongoose.connect(
  config.get("mongoUrl") || "mongodb://localhost:27017/weather",
  {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  }
);
const db = mongoose.connection;
db.on("error", console.error.bind(console, "MongoDB connection error:"));

const kafkaConfig = config.get("kafka") || {
  host: "localhost:9092",
  transformedTopic: "transformed-weather-data",
};

// Kafka Configuration
const kafkaClient = new KafkaClient({
  kafkaHost: kafkaConfig.host || "localhost:9092",
});
const consumer = new Consumer(
  kafkaClient,
  [{ topic: kafkaConfig.transformedTopic, partition: 0 }],
  { autoCommit: true }
);

// Consume messages from Kafka
consumer.on("message", async (message) => {
  try {
    const report = JSON.parse(message.value);

    // Create a new storm report document
    const stormReport = new StormReport({
      time: report.Time || "",
      f_scale: report.F_Scale || "",
      speed: report.Speed || "",
      size: report.Size || "",
      location: report.Location || "",
      county: report.County || "",
      state: report.State || "",
      lat: parseFloat(report.Lat) || 0,
      lon: parseFloat(report.Lon) || 0,
      comments: report.Comments || "",
    });

    await stormReport.save();
    console.log("Data saved to MongoDB:", stormReport);
  } catch (err) {
    console.error("Error processing message:", err);
  }
});

// API Endpoint to query storm data
app.get("/api/reports", async (req, res) => {
  try {
    const { date, location } = req.query;
    const query = {};
    if (date) query.time = new RegExp(date, "i");
    if (location) query.location = new RegExp(location, "i");

    const reports = await StormReport.find(query);
    res.json(reports);
  } catch (err) {
    res.status(500).send("Error querying reports");
  }
});

// Start the Express server
const PORT = config.get("port") || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

export default app;
