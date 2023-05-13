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
	// Start the HTTP server to expose metrics
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Fatal(http.ListenAndServe(":8000", nil))
	}()
	numRequests, err := strconv.Atoi(appLoadtestRequestParamName)
	if err != nil {
		log.Fatal(err)
	}
	queryParams := url.Values{}
	queryParams.Set("num_bytes", appLoadtestBytesParamName)
	// requestURL := fmt.Sprintf("http://app-simulate.app-simulate.svc.cluster.local:5000/bytes?%s", queryParams.Encode())
	requestURL := fmt.Sprintf("http://localhost:5000/bytes?%s", queryParams.Encode())
	duration := 60*time.Second
	interval := duration/time.Duration(numRequests)

	for {
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
	fmt.Println("loadtestSecondsEachRequest ",loadtestSecondsEachRequest)
	responseDurationEachRequest.Set(loadtestSecondsEachRequest)

	// Increment the requests counter
	totalRequestsProcessed.Inc()
}
