import assert from 'assert';
import supertest from 'supertest';
import sinon from 'sinon';
import mongoose from 'mongoose';
import { KafkaClient, Consumer } from 'kafka-node';
import app from '../server.js'; // Adjust the path as necessary
import StormReport from '../models/StormReport.js'; // Adjust the path as necessary

describe('Weather Processing System', () => {
  before(async () => {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://localhost:27017/weather_test', {
        useNewUrlParser: true, // Deprecated but should not cause issues
        useUnifiedTopology: true, // Deprecated but should not cause issues
      });
    }
  });

  after(async () => {
    await mongoose.connection.close();
  });

  describe('GET /api/reports', () => {
    beforeEach(async () => {
      await StormReport.deleteMany({}); // Ensure a clean slate
      await StormReport.create({
        time: '524',
        f_scale: 'UNK',
        location: 'Rockaway Beach',
        county: 'Tillamook',
        state: 'OR',
        lat: 45.61,
        lon: -123.94,
        comments: 'Test comment',
      });
    });

    afterEach(async () => {
      await StormReport.deleteMany({});
    });

    it('should return storm reports', async () => {
      const res = await supertest(app)
        .get('/api/reports')
        .expect(200);

      assert.strictEqual(Array.isArray(res.body), true);
      assert.strictEqual(res.body.length, 1);
      assert.strictEqual(res.body[0].location, 'Rockaway Beach');
    });

    it('should filter reports by location', async () => {
      const res = await supertest(app)
        .get('/api/reports?location=Rockaway Beach')
        .expect(200);

      assert.strictEqual(Array.isArray(res.body), true);
      assert.strictEqual(res.body.length, 1);
    });
  });

  describe('Kafka Consumer', () => {
    let kafkaConsumer;
    let mockKafkaClient;

    beforeEach(() => {
      mockKafkaClient = sinon.createStubInstance(KafkaClient);
      kafkaConsumer = sinon.createStubInstance(Consumer);
    });

    afterEach(() => {
      sinon.restore();
    });

    it('should process messages and save them to MongoDB', async () => {
      const message = {
        value: JSON.stringify({
          Time: '524',
          F_Scale: 'UNK',
          Location: 'Rockaway Beach',
          County: 'Tillamook',
          State: 'OR',
          Lat: '45.61',
          Lon: '-123.94',
          Comments: 'Test Kafka message',
        }),
      };

      // Simulate Kafka message processing
      kafkaConsumer.emit('message', message);

      // Allow some time for the async operation
      await new Promise((resolve) => setTimeout(resolve, 100));

      const reports = await StormReport.find({ location: 'Rockaway Beach' });
      assert.strictEqual(reports.length, 1);
      assert.strictEqual(reports[0].comments, 'Test Kafka message');
    });
  });
});
