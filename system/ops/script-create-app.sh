#!/bin/bash

aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl
k create ns app-simulate
kubectl label namespaces app-simulate istio-injection=enabled --overwrite=true
k create ns request-simulate
kubectl label namespaces request-simulate istio-injection=enabled --overwrite=true
k create ns predict-controller
kubectl label namespaces predict-controller istio-injection=enabled --overwrite=true

sleep 10

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
