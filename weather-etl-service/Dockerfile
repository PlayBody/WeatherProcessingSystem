# Use the official Golang image to create a build environment
FROM golang:1.18 as builder

# Set the working directory inside the container
WORKDIR /app

# Copy the Go module files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy the source code into the container
COPY . .

# Build the Go app
RUN go build -o weather-etl-service main.go

# Use a smaller base image for the final container
FROM gcr.io/distroless/base-debian10

# Copy the built binary from the builder image
COPY --from=builder /app/weather-etl-service /weather-etl-service

# Command to run the executable
CMD ["/weather-etl-service"]
