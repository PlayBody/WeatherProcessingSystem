import mongoose from "mongoose";

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
});

const StormReport = mongoose.model("StormReport", stormReportSchema);

export default StormReport;
