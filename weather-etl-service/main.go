package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"

	"github.com/IBM/sarama"
	"golang.org/x/text/cases"
	"golang.org/x/text/language"
	"gopkg.in/yaml.v2"
)

var config Config

type KafkaConfig struct {
	Broker           string `yaml:"broker"`
	RawTopic         string `yaml:"rawTopic"`
	TransformedTopic string `yaml:"transformedTopic"`
	ConsumerGroup    string `yaml:"consumerGroup"`
}

type Config struct {
	Kafka KafkaConfig `yaml:"kafka"`
}

type StormReport struct {
	Time     string  `json:"Time"`
	FScale   string  `json:"F_Scale,omitempty"`
	Speed    string  `json:"Speed,omitempty"`
	Size     string  `json:"Size,omitempty"`
	Location string  `json:"Location"`
	County   string  `json:"County"`
	State    string  `json:"State"`
	Lat      float64 `json:"Lat"`
	Lon      float64 `json:"Lon"`
	Comments string  `json:"Comments"`
}

func main() {
	// Set up logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Read the YAML file
	data, err := os.ReadFile("config.yaml")
	if err != nil {
		log.Fatalf("error: %v", err)
	}

	// Unmarshal the YAML data into the struct
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		log.Fatalf("error: %v", err)
	}

	// Create a new Sarama consumer group
	saramaConfig := sarama.NewConfig()
	saramaConfig.Consumer.Return.Errors = true
	saramaConfig.Version = sarama.V2_5_0_0
	saramaConfig.Consumer.Offsets.Initial = sarama.OffsetOldest

	consumerGroup, err := sarama.NewConsumerGroup([]string{config.Kafka.Broker}, config.Kafka.ConsumerGroup, saramaConfig)
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
			if err := consumerGroup.Consume(context.Background(), []string{config.Kafka.RawTopic}, &Consumer{}); err != nil {
				log.Fatalf("Error consuming messages: %v", err)
			}
		}
	}()

	<-sigchan
	log.Println("Terminating: via signal")
}

type Consumer struct{}

func (Consumer) Setup(_ sarama.ConsumerGroupSession) error {
	return nil
}

func (Consumer) Cleanup(_ sarama.ConsumerGroupSession) error {
	return nil
}

func (c Consumer) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	for message := range claim.Messages() {
		msg := strings.ReplaceAll(string(message.Value), "\"", "`")
		msg = strings.ReplaceAll(msg, "'", "\"")
		msg = strings.ReplaceAll(msg, "`", "'")
		log.Printf("Message received: %s", msg)
		var report map[string]string
		if err := json.Unmarshal([]byte(msg), &report); err != nil {
			log.Printf("Error unmarshalling message: %v", err)
			continue
		}

		// Perform ETL operations
		transformedReport := transform(report)

		producer, err := sarama.NewSyncProducer([]string{config.Kafka.Broker}, nil)
		if err != nil {
			log.Printf("Error new sync producer: %v", err)
			continue
		}

		// Publish the transformed data
		if err := publishTransformedData(producer, transformedReport); err != nil {
			log.Printf("Error publishing transformed data: %v", err)
		}

		session.MarkMessage(message, "")
	}
	return nil
}

func transform(report map[string]string) StormReport {
	lat := parseFloat(report["Lat"])
	lon := parseFloat(report["Lon"])

	return StormReport{
		Time:     report["Time"],
		FScale:   report["F_Scale"],
		Speed:    report["Speed"],
		Size:     report["Size"],
		Location: cases.Title(language.English).String(strings.ToLower(report["Location"])),
		County:   cases.Title(language.English).String(strings.ToLower(report["County"])),
		State:    strings.ToUpper(report["State"]),
		Lat:      lat,
		Lon:      lon,
		Comments: report["Comments"],
	}
}

func parseFloat(value string) float64 {
	parsedValue, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Printf("Error parsing float: %v", err)
		return 0.0
	}
	return parsedValue
}

func publishTransformedData(producer sarama.SyncProducer, report StormReport) error {
	defer producer.Close()
	data, err := json.Marshal(report)
	if err != nil {
		return err
	}

	msg := &sarama.ProducerMessage{
		Topic: config.Kafka.TransformedTopic,
		Value: sarama.ByteEncoder(data),
	}

	_, _, err = producer.SendMessage(msg)
	if err != nil {
		return err
	}

	log.Printf("Transformed data published: %v", report)
	return nil
}
