const express = require('express');
const kafka = require('kafka-node');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// MongoDB Configuration
mongoose.connect('mongodb://localhost:27017/weather', { useNewUrlParser: true, useUnifiedTopology: true });
const db = mongoose.connection;
db.on('error', console.error.bind(console, 'MongoDB connection error:'));

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

const StormReport = mongoose.model('StormReport', stormReportSchema);

// Kafka Configuration
const kafkaClient = new kafka.KafkaClient({ kafkaHost: 'localhost:9092' });
const consumer = new kafka.Consumer(
  kafkaClient,
  [{ topic: 'transformed-weather-data', partition: 0 }],
  { autoCommit: true }
);

// Consume messages from Kafka
consumer.on('message', async (message) => {
  try {
    const report = JSON.parse(message.value);

    // Create a new storm report document
    const stormReport = new StormReport({
      time: report.Time || '',
      f_scale: report.F_Scale || '',
      speed: report.Speed || '',
      size: report.Size || '',
      location: report.Location || '',
      county: report.County || '',
      state: report.State || '',
      lat: parseFloat(report.Lat) || 0,
      lon: parseFloat(report.Lon) || 0,
      comments: report.Comments || '',
    });

    await stormReport.save();
    console.log('Data saved to MongoDB:', stormReport);
  } catch (err) {
    console.error('Error processing message:', err);
  }
});

// API Endpoint to query storm data
app.get('/api/reports', async (req, res) => {
  try {
    const { date, location } = req.query;
    const query = {};
    if (date) query.time = new RegExp(date, 'i');
    if (location) query.location = new RegExp(location, 'i');

    const reports = await StormReport.find(query);
    res.json(reports);
  } catch (err) {
    res.status(500).send('Error querying reports');
  }
});

// Start the Express server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
