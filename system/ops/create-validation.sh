#!/bin/bash

aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl

cd ../..
cd app-loadtest/deploy
k apply -f . 

cd ../..
cd app-simulate/deploy
k apply -f . 

# cd ../..
# cd request-simulate/deploy 
# k apply -f .

cd ../..
cd predict-controller/deploy 
k apply -f .

cd ../..
cd system/ops
