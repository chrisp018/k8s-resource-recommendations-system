#!/bin/bash
aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl

cd ../..
cd app-simulate/deploy
k delete -f . 

cd ../..
cd request-simulate/deploy 
k delete -f .

cd ../..
cd app-loadtest/deploy 
k delete -f .

cd ../..
cd system/ops
