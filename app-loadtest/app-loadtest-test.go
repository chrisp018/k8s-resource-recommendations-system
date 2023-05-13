package main 
import (
	"fmt"
	"sync"
	// "time"
)


func main() {
	for {
		// Start sending requests in goroutines
		var wg sync.WaitGroup
		numRequests := 10
		wg.Add(numRequests)
	
		for i := 0; i < numRequests; i++ {
			go sendRequest(&wg, i)
			// time.Sleep(time.Second)
		}
		wg.Wait()
	}
}


func sendRequest(wg *sync.WaitGroup, counter int) {
	defer wg.Done()
	fmt.Println("counter: ", counter)
}
