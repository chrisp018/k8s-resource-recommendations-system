package main 

import (
	"fmt"
	"log"
	// "os"
	"strings"
	"sync"
	"time"
	"io/ioutil"
	"net/http"
	"net/url"
	"strconv"

	"github.com/go-gota/gota/dataframe"
	// "github.com/go-gota/gota/series"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/ssm"
	"github.com/aws/aws-sdk-go/service/s3"
)

const (
	BucketName = "khanh-thesis-validation"
	Key        = "dataset-validation/wc_dataset_processed.csv"
)

type Task struct {
	ID int
	RequestURL string
}

var (
	totalRequestsProcessed = prometheus.NewCounter(prometheus.CounterOpts{
			Name: "simulate_requests_total",
			Help: "Total number of simulate requests made by the app",
    })

	successRequestsCount = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "simulate_requests_successful_total",
		Help: "Total number of app load test requests successful made by the app",
	})

	errorRequestsCount = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "simulate_requests_failed_total",
		Help: "Total number of app load test requests failed made by the app",
	})

	responseSize = prometheus.NewHistogram(prometheus.HistogramOpts{
            Name: "simulate_response_size_bytes",
            Help: "Size of HTTP simulate responses",
            Buckets: []float64{100, 200, 300, 400, 500, 1000, 2000},
    })

	responseDurationEachRequest = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "simulate_response_duration_each_request",
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
	s3Client *s3.S3
)

func init() {
	region := "ap-southeast-1"
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(region),
	})
	if err != nil {
		log.Fatal(err)
	}
	ssmClient = ssm.New(sess)
	s3Client = s3.New(sess)
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

func putSSMParam(parameterName string, currentTriggerTime string) (error){
	input := &ssm.PutParameterInput{
		Name:      aws.String(parameterName),
		Value:     aws.String(currentTriggerTime),
		Type:      aws.String("String"),
		Overwrite: aws.Bool(true),
	}
	_, err := ssmClient.PutParameter(input)
	if err != nil {
		return fmt.Errorf("failed to put parameter: %v", err)
	}
	return nil
}

func main(){
	pastTriggerTime, _ := getSSMParam("/khanh-thesis/past_trigger_time")
	replicasCount, _ := getSSMParam("/khanh-thesis/request_simulate_replicas")
	numReplicas, _ := strconv.Atoi(replicasCount)
	pastTriggerTimeParse, err := time.Parse("2006-01-02 15:04:00", pastTriggerTime)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("pastTriggerTime: ", pastTriggerTimeParse)
	fmt.Println("numReplicas: ", numReplicas)
	// temp data
	taskQueue := make(chan Task, 1000)
	var wg sync.WaitGroup
	// file, _ := os.Open("wc_dataset_processed.csv")
	// defer file.Close()

	// Prepare the input parameters for the S3 getObject operation
	input := &s3.GetObjectInput{
		Bucket: aws.String(BucketName),
		Key:    aws.String(Key),
	}
	// Perform the S3 getObject operation
	result, err := s3Client.GetObject(input)
	if err != nil {
		log.Fatal("Failed to get S3 object:", err)
	}
	// Read the object body into a byte array
	body, err := ioutil.ReadAll(result.Body)
	if err != nil {
		log.Fatal("Failed to read object body:", err)
	}
	csvString := string(body)
	reader := strings.NewReader(csvString)

	df := dataframe.ReadCSV(reader)
	queryParams := url.Values{}
	eventTime := df.Col("event_time")
	eventCount := df.Col("event_count")
	sumBytes := df.Col("sum_bytes")

	// Start the HTTP server to expose metrics
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Fatal(http.ListenAndServe(":8000", nil))
	}()
	// Calib time
	currentTime := time.Now()
	nextMinute  := currentTime.Truncate(time.Minute).Add(time.Minute)
	fmt.Println("currentTime: ", currentTime)
	fmt.Println("nextMinute  :", nextMinute)
	duration := nextMinute.Sub(currentTime)
	fmt.Println("duration :", duration)
	nanoseconds := duration.Nanoseconds()
	time.Sleep(time.Duration(nanoseconds) * time.Nanosecond)
	// SSM Trigger time
	triggerTime := time.Now()
	currentTriggerTime := triggerTime.Format("2006-01-02 15:04:00")
	fmt.Println("currentTriggerTime (ssm): ", currentTriggerTime)
	putSSMParam("/khanh-thesis/current_trigger_time", currentTriggerTime)
	poolSize := 1000
	for i := 0; i < poolSize; i++ {
		go worker(taskQueue, i, &wg)
	}
	for i := 0; i < df.Nrow(); i++ {
		eventTime, _ := time.Parse("2006-01-02 15:04:05", eventTime.Elem(i).String())
		if !eventTime.Before(pastTriggerTimeParse) {
			startTimeRequest := time.Now()
			fmt.Println("START:===============================")
			fmt.Println("DATA INPUT: ")
			numRequests, _ := strconv.Atoi(eventCount.Elem(i).String())
			numBytes, _ := strconv.Atoi(sumBytes.Elem(i).String())
			numRequestsEachReplica := numRequests/numReplicas
			bytesResponseEachRequest := strconv.Itoa(numBytes/numRequests)
			fmt.Println("Number of request per minutes: ", numRequests)
			fmt.Println("Bytes response all requests: ", numBytes)
			fmt.Println("Bytes response each request: ", bytesResponseEachRequest)
			fmt.Println("START SENDING REQUEST: ")
			queryParams.Set("num_bytes", bytesResponseEachRequest)
			requestURL := fmt.Sprintf("http://app-simulate.app-simulate.svc.cluster.local:5000/bytes?%s", queryParams.Encode())
			time.Sleep(10000 * time.Millisecond)
			for i := 0; i < numRequestsEachReplica; i ++ {
				task := Task{ID: i, RequestURL: requestURL}
				taskQueue <- task
				wg.Add(1)
			}
			currentTime := time.Now()
			nextMinute  := currentTime.Truncate(time.Minute).Add(time.Minute)
			duration := nextMinute.Sub(currentTime)
			nanoseconds := duration.Nanoseconds()
			fmt.Println("Need to sleep :", duration)
			time.Sleep(time.Duration(nanoseconds) * time.Nanosecond)
			fmt.Println("END:===============================")
			wg.Wait()
			endTimeRequest := time.Now()
			loadtestDuration := endTimeRequest.Sub(startTimeRequest)
			loadtestSeconds := loadtestDuration.Seconds()
			appLoadtestResponseDurationAll.Set(loadtestSeconds)
			fmt.Println("loadtestSeconds: ", loadtestSeconds)
		}
	}
}

func worker(taskQueue chan Task, pool int, wg *sync.WaitGroup) {
	for task := range taskQueue {
		processTask(task, pool)
		wg.Done()
	}
}

func processTask(task Task, pool int) {
	startTimeEachRequest := time.Now()
	rs, err := http.Get(task.RequestURL)
	if err != nil {
		errorRequestsCount.Inc()
	} else {
		defer rs.Body.Close()
		// Read the response body to get the bytes
		responseBody, _ := ioutil.ReadAll(rs.Body)
		numBytes := len(responseBody)
		// fmt.Println("numBytes ", numBytes)
		responseSize.Observe(float64(numBytes))
		successRequestsCount.Inc()
	}
	endTimeEachRequest := time.Now()
	loadtestDurationEachRequest := endTimeEachRequest.Sub(startTimeEachRequest)
	loadtestSecondsEachRequest := loadtestDurationEachRequest.Seconds()
	// fmt.Println("load test in seconds each request: ", loadtestSecondsEachRequest)
	responseDurationEachRequest.Set(loadtestSecondsEachRequest)
	totalRequestsProcessed.Inc()
}
