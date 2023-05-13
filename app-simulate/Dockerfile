# Use the official Golang base image
FROM golang:1.16-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the Go module files
COPY go.mod ./

# Download and cache Go dependencies
RUN go mod download

# Copy the rest of the application source code
COPY app-simulate.go app-simulate.go

# Build the Go application
RUN go build -o main

# Expose the port that the application listens on
EXPOSE 8080

# Set the entry point for the container
CMD ["./main"]
