#!/bin/bash

aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl
k create ns external-dns
k create ns istio-istio
k create ns istio-ingress
k create ns kiali-operator
k create ns appsimulate
k create ns request-simulate

cd external-dns
helm install -f values.yaml external-dns . -n external-dns 
cd ..

cd istio
helm install -f values.yaml istio-system . -n istio-system 
cd ..

cd istio-ingress 
helm install -f values.yaml istio-ingress . -n istio-ingress 
cd ..

cd metrics-server 
helm install -f values.yaml metrics-server . -n metrics-server 
cd ..

# cd kiali
# helm install -f values.yaml kiali-operator --set cr.create=true . -n kiali-operator
# cd ..

cd istio_monitor
k apply -f . 
cd ..

cd ../..
cd appsimulate/deploy
k apply -f . 

cd ../..
cd request_simulate/deploy 
k apply -f .

cd ../..
cd system/ops
