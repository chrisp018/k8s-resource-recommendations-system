package main 
import (
	// "fmt"
	"log"
	"io/ioutil"
	"net/http"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)


var (
	totalRequestsProcessed = prometheus.NewCounter(prometheus.CounterOpts{
			Name: "app_loadtest_requests_total",
			Help: "Total number of app load test requests made by the app",
    })

	successRequestsCount = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "app_loadtest_requests_successful_total",
		Help: "Total number of app load test requests successful made by the app",
	})

	errorRequestsCount = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "app_loadtest_requests_failed_total",
		Help: "Total number of app load test requests failed made by the app",
	})

	responseSize = prometheus.NewHistogram(prometheus.HistogramOpts{
            Name: "app_loadtest_response_size_bytes",
            Help: "Size of HTTP app load test responses",
            Buckets: []float64{100, 200, 300, 400, 500, 1000, 2000},
    })

	responseDurationEachRequest = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "app_loadtest_response_duration_each_request",
		Help: "Duration of HTTP app load test response each request",
	})

	appLoadtestResponseDurationAll = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "app_loadtest_response_duration_all",
		Help: "Duration of HTTP app load test response all requests received",
	})
)

func init() {
	// Add go runtime metrics and process collectors.
	prometheus.MustRegister(
		totalRequestsProcessed,
		successRequestsCount,
		errorRequestsCount,
		responseSize,
		responseDurationEachRequest,
		appLoadtestResponseDurationAll,
	)
}


func main() {
	// Start the HTTP server to expose metrics
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Fatal(http.ListenAndServe(":8080", nil))
	}()

	numRequests := 1000
	requestURL := "http://google.com"
	duration := 60*time.Second
	interval := duration/time.Duration(numRequests)

	startTime := time.Now()
	// Start sending requests in goroutines
	var wg sync.WaitGroup
	wg.Add(numRequests)

	for i := 0; i < numRequests; i++ {
		go sendRequest(&wg, requestURL)
		time.Sleep(interval)
	}
	endTime := time.Now()
	loadtestDuration := endTime.Sub(startTime)
	loadtestSeconds := loadtestDuration.Seconds()
	appLoadtestResponseDurationAll.Set(loadtestSeconds)
	wg.Wait()
}


func sendRequest(wg *sync.WaitGroup, requestURL string) {
	defer wg.Done()
	startTimeEachRequest := time.Now()
	rs, err := http.Get(requestURL)
	if err != nil {
		errorRequestsCount.Inc()
	} else {
		defer rs.Body.Close()
		// Read the response body to get the bytes
		responseBody, err := ioutil.ReadAll(rs.Body)
		if err != nil {
			errorRequestsCount.Inc()
		}
		numBytes := len(responseBody)
		responseSize.Observe(float64(numBytes))
		successRequestsCount.Inc()
	}
	endTimeEachRequest := time.Now()
	loadtestDurationEachRequest := endTimeEachRequest.Sub(startTimeEachRequest)
	loadtestSecondsEachRequest := loadtestDurationEachRequest.Seconds()
	responseDurationEachRequest.Set(loadtestSecondsEachRequest)

	// Increment the requests counter
	totalRequestsProcessed.Inc()
}
