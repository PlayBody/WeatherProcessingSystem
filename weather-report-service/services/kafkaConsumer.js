import { KafkaClient, Consumer } from "kafka-node";
import config from "config";
import StormReport from "../models/StormReport.js";
import logger from "./logger.js";

const kafkaConfig = config.get("kafka") || {
  host: "localhost:9092",
  transformedTopic: "transformed-weather-data",
};

const kafkaClient = new KafkaClient({ kafkaHost: kafkaConfig.host });

const consumer = new Consumer(
  kafkaClient,
  [{ topic: kafkaConfig.transformedTopic, partition: 0 }],
  { autoCommit: true }
);

consumer.on("message", async (message) => {
  try {
    const report = JSON.parse(message.value);

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
    logger.info("Data saved to MongoDB:", stormReport);
  } catch (err) {
    logger.error("Error processing message:", err);
  }
});
