import express from "express";
import StormReport from "../models/StormReport.js";
import logger from "../services/logger.js";

const router = express.Router();

// API Endpoint to query storm data
router.get("/", async (req, res) => {
  try {
    const { date, location } = req.query;
    const query = {};
    if (date) query.time = new RegExp(date, "i");
    if (location) query.location = new RegExp(location, "i");

    const reports = await StormReport.find(query);
    logger.info(`Fetched ${reports.length} reports`);
    res.json(reports);
  } catch (err) {
    logger.error(`Error querying reports: ${err}`);
    res.status(500).send("Error querying reports");
  }
});

export default router;
