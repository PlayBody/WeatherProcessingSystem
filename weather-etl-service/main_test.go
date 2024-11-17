package main

import (
	"encoding/json"
	"testing"

	"github.com/IBM/sarama"
	"github.com/stretchr/testify/assert"
)

// TestTransform tests the transform function
func TestTransform(t *testing.T) {
	input := map[string]string{
		"Time":     "524",
		"F_Scale":  "UNK",
		"Location": "rockaway beach",
		"County":   "tillamook",
		"State":    "or",
		"Lat":      "45.61",
		"Lon":      "-123.94",
		"Comments": "Test comment",
	}

	expected := StormReport{
		Time:     "524",
		FScale:   "UNK",
		Location: "Rockaway Beach",
		County:   "Tillamook",
		State:    "OR",
		Lat:      45.61,
		Lon:      -123.94,
		Comments: "Test comment",
	}

	result := transform(input)

	assert.Equal(t, expected, result)
}

// TestParseFloat tests the parseFloat function
func TestParseFloat(t *testing.T) {
	assert.Equal(t, 45.61, parseFloat("45.61"))
	assert.Equal(t, 0.0, parseFloat("invalid"))
}

// MockProducer is a mock implementation of sarama.SyncProducer
type MockProducer struct {
	Messages []*sarama.ProducerMessage
}

func (mp *MockProducer) SendMessage(msg *sarama.ProducerMessage) (partition int32, offset int64, err error) {
	mp.Messages = append(mp.Messages, msg)
	return 0, 0, nil
}

func (mp *MockProducer) SendMessages(msgs []*sarama.ProducerMessage) error {
	mp.Messages = append(mp.Messages, msgs...)
	return nil
}

func (mp *MockProducer) Close() error {
	return nil
}

// Implement missing methods for the sarama.SyncProducer interface

func (mp *MockProducer) AbortTxn() error {
	return nil
}

func (mp *MockProducer) BeginTxn() error {
	return nil
}

func (mp *MockProducer) IsTransactional() bool {
	return false
}

func (mp *MockProducer) TxnStatus() sarama.ProducerTxnStatusFlag {
	return 0
}

func (mp *MockProducer) AddOffsetsToTxn(offsets map[string][]*sarama.PartitionOffsetMetadata, groupId string) error {
	return nil
}

func (mp *MockProducer) AddMessageToTxn(msg *sarama.ConsumerMessage, groupId string, metadata *string) error {
	return nil
}

func (mp *MockProducer) CommitTxn() error {
	return nil
}

func (mp *MockProducer) InitTransactions() error {
	return nil
}

// TestPublishTransformedData tests the publishTransformedData function
func TestPublishTransformedData(t *testing.T) {
	mockProducer := &MockProducer{}
	config.Kafka.Broker = "mockBroker"
	report := StormReport{
		Time:     "524",
		FScale:   "UNK",
		Location: "Rockaway Beach",
		County:   "Tillamook",
		State:    "OR",
		Lat:      45.61,
		Lon:      -123.94,
		Comments: "Test comment",
	}

	err := publishTransformedData(mockProducer, report)
	assert.NoError(t, err)
	assert.Equal(t, 1, len(mockProducer.Messages))

	var actual StormReport
	err = json.Unmarshal(mockProducer.Messages[0].Value.(sarama.ByteEncoder), &actual)
	assert.NoError(t, err)
	assert.Equal(t, report, actual)
}
