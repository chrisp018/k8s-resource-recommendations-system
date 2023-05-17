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

var mutex sync.Mutex
func main(){
	taskQueue := make(chan Task, 1000)
	var wg sync.WaitGroup
	appLoadtestReplicasCount, err := getSSMParam("/khanh-thesis/app_loadtest_replicas")
	if err != nil {
		fmt.Println("Error retrieving replicas number param:", err)
		return
	}
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
	numReplicas, err := strconv.Atoi(appLoadtestReplicasCount)
	if err != nil {
		log.Fatal(err)
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
	// requestURL := fmt.Sprintf("http://app-simulate.app-simulate.svc.cluster.local:5000/bytes?%s", queryParams.Encode())
	// requestURL := fmt.Sprintf("http://localhost:5000/bytes?%s", queryParams.Encode())
	requestURL := fmt.Sprintf("http://google.com")
	fmt.Println("DATA INPUT: ")
	fmt.Println("Bytes response each request: ", bytesResponseEachRequest)
	fmt.Println("Number of request per minutes: ", numRequests)
	fmt.Println("START SENDING REQUEST: ")

	currentTime := time.Now()
	nextMinute  := currentTime.Truncate(time.Minute).Add(time.Minute)
	fmt.Println("currentTime: ", currentTime)
	fmt.Println("nextMinute  :", nextMinute)
	duration := nextMinute.Sub(currentTime)
	fmt.Println("duration :", duration)
	nanoseconds := duration.Nanoseconds()
	time.Sleep(time.Duration(nanoseconds) * time.Nanosecond)

	// Create pool for goroutines
	poolSize := 100
	for i := 0; i < poolSize; i++ {
		go worker(taskQueue, i, requestURL, &wg)
	}
	for {
		startTimeRequest := time.Now()
		// Generate tasks and send them to taskQueue
		numRequestsEachReplica := numRequests/numReplicas
		fmt.Println("numRequests each replica: ", numRequestsEachReplica)
		fmt.Println("START:===============================")
		for i := 0; i < numRequestsEachReplica; i ++ {
			task := Task{ID: i}
			taskQueue <- task 
			wg.Add(1)
		}
		currentTime := time.Now()
		nextMinute  := currentTime.Truncate(time.Minute).Add(time.Minute)
		fmt.Println("currentTime: ", currentTime)
		fmt.Println("nextMinute  :", nextMinute )
		duration := nextMinute.Sub(currentTime)
		fmt.Println("duration :", duration)
		nanoseconds := duration.Nanoseconds()
		time.Sleep(time.Duration(nanoseconds) * time.Nanosecond)
		fmt.Println("nanoseconds :", nanoseconds)
		fmt.Println("END:===============================")
		// close(taskQueue)
		wg.Wait()
		endTimeRequest := time.Now()
		loadtestDuration := endTimeRequest.Sub(startTimeRequest)
		loadtestSeconds := loadtestDuration.Seconds()
		appLoadtestResponseDurationAll.Set(loadtestSeconds)
		fmt.Println("loadtestSeconds: ", loadtestSeconds)
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
	mutex.Lock()
	totalRequestsProcessed.Inc()
	mutex.Unlock()
}
