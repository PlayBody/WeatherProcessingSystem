import mongoose from "mongoose";

// Define a Mongoose schema and model
const stormReportSchema = new mongoose.Schema({
  time: String,
  f_scale: String,
  speed: String,
  size: String,
  location: String,
  county: String,
  state: String,
  lat: Number,
  lon: Number,
  comments: String,
  // You can add more fields if necessary
});

const StormReport = mongoose.model("StormReport", stormReportSchema);

export default StormReport;
