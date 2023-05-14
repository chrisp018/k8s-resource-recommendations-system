package main 

import (
	"fmt"
	// "log"
	"net/http"
	"strconv"
	"sync"
	// "math/rand"
)


// func consumeCPUMemory(n int) {
// 	result := make([][]float64, 0)

// 	for i := 0; i < n; i++ {
// 		// Consume CPU by computing the sum of a large random array
// 		arr := make([]float64, 10000)
// 		for j := 0; j < len(arr); j++ {
// 			arr[j] = rand.Float64()
// 		}
// 		sum := 0.0
// 		for _, num := range arr {
// 			sum += num
// 		}

// 		// Consume memory by appending the array to the result list
// 		result = append(result, arr)
// 	}
// }


func byteHandler(w http.ResponseWriter, r *http.Request){
	if r.URL.Path != "/bytes" {
		http.Error(w, "404 not found", http.StatusNotFound)
		return
	}

	if r.Method != "GET" {
		http.Error(w, "Method is not supported", http.StatusNotFound)
		return
	}

	bytesParam := r.URL.Query().Get("num_bytes")
	// Convert the parameter to an integer
	numBytes, err := strconv.Atoi(bytesParam)
	if err != nil {
		http.Error(w, "Invalid 'bytes' parameter", http.StatusBadRequest)
		return
	}
	// consumeCPUMemory(1)
	// Create a byte slice of the specified length
	data := make([]byte, numBytes)
	// Write the byte slice as the response
	w.Write(data)
}


func healthzReadyHandler(w http.ResponseWriter, r *http.Request){
	if r.URL.Path != "/healthz/ready" {
		http.Error(w, "404 not found", http.StatusNotFound)
		return
	}

	if r.Method != "GET" {
		http.Error(w, "Method is not supported", http.StatusNotFound)
		return
	}
	fmt.Fprintf(w, "ok")
}

func healthzLiveHandler(w http.ResponseWriter, r *http.Request){
	if r.URL.Path != "/healthz/live" {
		http.Error(w, "404 not found", http.StatusNotFound)
		return
	}

	if r.Method != "GET" {
		http.Error(w, "Method is not supported", http.StatusNotFound)
		return
	}
	fmt.Fprintf(w, "ok")
}
var wg sync.WaitGroup

func main(){
	// Create new http server and register the handler
	http.HandleFunc("/bytes", byteHandler)
	http.HandleFunc("/healthz/ready", healthzReadyHandler)
	http.HandleFunc("/healthz/live", healthzLiveHandler)

	fmt.Printf("Starting server at port 5000\n")
	wg.Add(1)
	go func() {
		defer wg.Done()
		if err := http.ListenAndServe(":5000", nil); err != nil {
			fmt.Println("Server error:", err)
		}
	}()
	wg.Wait()
}
