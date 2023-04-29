#!/bin/bash
aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl
k create ns external-dns
k create ns istio-system
k create ns metrics-server
k create ns istio-ingress
k create ns prometheus-adapter

cd external-dns
helm install -f values.yaml external-dns . -n external-dns 
cd ..

cd istio
helm install -f values.yaml istio-system . -n istio-system 
cd ..

sleep 10
cd istio-ingress 
helm install -f values.yaml istio-ingress . -n istio-ingress 
cd ..

cd metrics-server 
helm install -f values.yaml metrics-server . -n metrics-server 
cd ..

sleep 10
cd istio-monitor
k apply -f . 
cd ..

cd prometheus-adapter
helm install -f values.yaml prometheus-adapter . -n prometheus-adapter
cd ..

cd ../..
cd system/ops
