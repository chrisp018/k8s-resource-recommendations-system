# Use the official Golang base image
FROM golang:1.20-alpine

# Set the working directory inside the container
WORKDIR /app

COPY healthy healthy

# Copy the Go module files
COPY go.mod go.sum ./

COPY wc_dataset_processed.csv wc_dataset_processed.csv

# Download and cache Go dependencies
RUN go mod download

# Copy the rest of the application source code
COPY request-simulate.go request-simulate.go

# Build the Go application
RUN go build -o main

# Expose the port that the application listens on
EXPOSE 8000

# Set the entry point for the container
CMD ["./main"]
