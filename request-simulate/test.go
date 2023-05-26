package main 

import (
	"fmt"
	"log"
	// "os"
	"strings"
	"io/ioutil"

	"github.com/go-gota/gota/dataframe"
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
)

const (
	BucketName = "khanh-thesis-validation"
	Key        = "dataset-validation/wc_dataset_processed.csv"
)

var (
	sess *session.Session
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
	s3Client = s3.New(sess)
}

func main(){
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
	fmt.Println(df)
}
