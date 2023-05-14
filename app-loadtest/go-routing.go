package main 
import (
	"fmt"
	"time"
	// "sync"
)

func main(){
	dataChan := make(chan int, 1)

	go cc1(dataChan)
	a := <- dataChan
	fmt.Println(a)
	b := <- dataChan
	fmt.Println(b)
	time.Sleep(20*time.Second)
}

func cc1(c chan int){
	c <- 1
	c <- 2
	time.Sleep(10*time.Second)
	fmt.Println("ok")
}