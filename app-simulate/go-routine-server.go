package main

import (
	"fmt"
	"net/http"
	"sync"
	"time"
)

func main() {
	// Create a counter variable to keep track of concurrent requests
	var counter int
	var wg sync.WaitGroup

	// Create a handler function
	handler := func(w http.ResponseWriter, r *http.Request) {
		// Increment the counter when a request is received
		counter++
		fmt.Println("Handling request", counter)

		// Decrement the counter when the request is handled
		defer func() {
			counter--
			fmt.Println("Finished handling request", counter)
		}()

		// Your request handling logic goes here
		// ...

		// Simulate some work
		time.Sleep(time.Second)

		// Send a response
		w.Write([]byte("Hello, World!"))
	}

	// Start the server
	http.HandleFunc("/", handler)
	fmt.Println("Server started at http://localhost:8080")
	wg.Add(1)
	go func() {
		defer wg.Done()
		if err := http.ListenAndServe(":8080", nil); err != nil {
			fmt.Println("Server error:", err)
		}
	}()

	// Wait for the server to finish
	wg.Wait()
}
