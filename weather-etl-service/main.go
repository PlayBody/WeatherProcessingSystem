package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/IBM/sarama"
)

const (
	kafkaBroker      = "localhost:9092"
	rawTopic         = "raw-weather-reports"
	transformedTopic = "transformed-weather-data"
)

type StormReport struct {
	Time     string `json:"Time"`
	Location string `json:"Location"`
	Type     string `json:"Type"`
	// Add more fields as needed
}

func main() {
	// Set up logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Create a new Sarama consumer group
	config := sarama.NewConfig()
	config.Consumer.Return.Errors = true
	config.Version = sarama.V2_5_0_0

	consumerGroup, err := sarama.NewConsumerGroup([]string{kafkaBroker}, "weather-etl-group", config)
	if err != nil {
		log.Fatalf("Error creating consumer group: %v", err)
	}
	defer consumerGroup.Close()

	// Set up a channel to handle OS signals
	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, os.Interrupt, syscall.SIGTERM)

	// Consume messages in a separate goroutine
	go func() {
		for {
			if err := consumerGroup.Consume(context.Background(), []string{rawTopic}, &consumer{}); err != nil {
				log.Fatalf("Error consuming messages: %v", err)
			}
		}
	}()

	<-sigchan
	log.Println("Terminating: via signal")
}

type consumer struct{}

func (consumer) Setup(_ sarama.ConsumerGroupSession) error   { return nil }
func (consumer) Cleanup(_ sarama.ConsumerGroupSession) error { return nil }
func (c consumer) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	for message := range claim.Messages() {
		var report StormReport
		if err := json.Unmarshal(message.Value, &report); err != nil {
			log.Printf("Error unmarshalling message: %v", err)
			continue
		}

		// Perform ETL operations
		transformedReport := transform(report)

		// Publish the transformed data
		if err := publishTransformedData(transformedReport); err != nil {
			log.Printf("Error publishing transformed data: %v", err)
		}

		session.MarkMessage(message, "")
	}
	return nil
}

func transform(report StormReport) StormReport {
	// Example ETL operation: Convert time to a different format, standardize location, etc.
	report.Time = strings.ToUpper(report.Time) // Example transformation
	report.Location = strings.Title(strings.ToLower(report.Location))
	return report
}

func publishTransformedData(report StormReport) error {
	producer, err := sarama.NewSyncProducer([]string{kafkaBroker}, nil)
	if err != nil {
		return err
	}
	defer producer.Close()

	data, err := json.Marshal(report)
	if err != nil {
		return err
	}

	msg := &sarama.ProducerMessage{
		Topic: transformedTopic,
		Value: sarama.ByteEncoder(data),
	}

	// Send the message to the transformed topic
	_, _, err = producer.SendMessage(msg)
	if err != nil {
		return err
	}

	log.Printf("Transformed data published: %v", report)
	return nil
}
