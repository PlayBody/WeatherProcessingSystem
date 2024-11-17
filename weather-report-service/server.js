import express from "express";
import mongoose from "mongoose";
import bodyParser from "body-parser";
import config from "config";
import logger from "./services/logger.js";
import "./services/kafkaConsumer.js"; // Initialize Kafka consumer
import reportsRouter from "./routes/reports.js";
import { registerMetrics, metricsMiddleware } from "./metrics.js";

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
db.on("error", (error) => logger.error(`MongoDB connection error: ${error}`));

// Middleware for logging and metrics
app.use((req, res, next) => {
  logger.info(`Incoming request: ${req.method} ${req.url}`);
  next();
});
app.use(metricsMiddleware);

// Serve static files
app.use(express.static("public"));

// Use routes
app.use("/api/reports", reportsRouter);

// Metrics endpoint
app.get("/metrics", async (req, res) => {
  res.set("Content-Type", registerMetrics.contentType);
  res.end(await registerMetrics.metrics());
});

// Start the server
const PORT = config.get("port") || 3000;
app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`);
});
