#!/bin/bash

aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl
k create ns app-simulate
k create ns request-simulate
k create ns predict-controller

cd ../..
cd app-simulate/deploy
k apply -f . 

cd ../..
cd request-simulate/deploy 
k apply -f .

cd ../..
cd predict-controller/deploy 
k apply -f .

cd ../..
cd system/ops
