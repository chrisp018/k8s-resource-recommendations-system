package main

import (
	"fmt"
	"log"
	"strconv"
	"io/ioutil"
	"net/http"
	"net/url"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/ssm"
)

type Task struct {
	ID int 
	Num int
}


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

var (
	sess *session.Session
	ssmClient  *ssm.SSM
)

func init() {
	region := "ap-southeast-1"
	// Initialize the AWS session and SSM client
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(region),
	})
	if err != nil {
		log.Fatal(err)
	}
	ssmClient = ssm.New(sess)
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

func getSSMParam(parameterName string) (string, error){
	// Create an input object for the GetParameter API
	input := &ssm.GetParameterInput{
		Name: aws.String(parameterName),
		WithDecryption: aws.Bool(true),
	}
	result, err := ssmClient.GetParameter(input)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve parameter: %v", err)
	}
	return *result.Parameter.Value, nil
}


func main() {
	taskQueue := make(chan Task, 1000)
	var wg sync.WaitGroup
	appLoadtestRequestParamName, err := getSSMParam("/khanh-thesis/app_loadtest_request")
	if err != nil {
		fmt.Println("Error retrieving request number param:", err)
		return
	}
	appLoadtestBytesParamName, err := getSSMParam("/khanh-thesis/app_loadtest_bytes")
	if err != nil {
		fmt.Println("Error retrieving bytes:", err)
		return
	}
	numBytes, err := strconv.Atoi(appLoadtestBytesParamName)
	if err != nil {
		log.Fatal(err)
	}
	// Start the HTTP server to expose metrics
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Fatal(http.ListenAndServe(":8000", nil))
	}()
	numRequests, err := strconv.Atoi(appLoadtestRequestParamName)
	if err != nil {
		log.Fatal(err)
	}
	bytesResponseEachRequest := strconv.Itoa(numBytes/numRequests)
	queryParams := url.Values{}
	queryParams.Set("num_bytes", bytesResponseEachRequest)
	requestURL := fmt.Sprintf("http://localhost:5000/bytes?%s", queryParams.Encode())
	duration := 20*time.Second
	interval := duration/time.Duration(numRequests)
	fmt.Println("DATA INPUT: ")
	fmt.Println("Bytes response each request: ", bytesResponseEachRequest)
	fmt.Println("Number of request per minutes: ", numRequests)
	fmt.Println("Goroutine interval: ", interval)
	fmt.Println("START SENDING REQUEST: ")
	// Create pool for goroutines
	poolSize := 1000
	for i := 0; i < poolSize; i++ {
		go worker(taskQueue, i, requestURL, &wg)
	}
	for {
		startTime := time.Now()
		// Generate tasks and send them to taskQueue
		for i := 0; i < numRequests; i ++ {
			task := Task{ID: i, Num: i + 1}
			taskQueue <- task 
			wg.Add(1)
		}

		// Close the taskQueue to signal that no more tasks will be added
		// close(taskQueue)
		wg.Wait()
		endTime := time.Now()
		loadtestDuration := endTime.Sub(startTime)
		loadtestSeconds := loadtestDuration.Seconds()
		timeSleep := 0.0
		if loadtestSeconds < 60.0 {
			timeSleep = 10.0 - loadtestSeconds
		}
		appLoadtestResponseDurationAll.Set(loadtestSeconds)
		fmt.Println("loadtestSeconds: ", loadtestSeconds)
		fmt.Println("timeSleep: ",timeSleep)
		time.Sleep(time.Duration(int(timeSleep)) * time.Second)
		fmt.Println("=============================")
	}
}

func worker(taskQueue chan Task, pool int, requestURL string, wg *sync.WaitGroup) {
	for task := range taskQueue {
		processTask(task, pool, requestURL)
		wg.Done()
	}
}

func processTask(task Task, pool int, requestURL string) {
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
	// if loadtestSecondsEachRequest < 0.002 {
	// 	fmt.Println("loadtestSecondsEachRequest ",loadtestSecondsEachRequest)
	// }
	responseDurationEachRequest.Set(loadtestSecondsEachRequest)

	// Increment the requests counter
	totalRequestsProcessed.Inc()
}
