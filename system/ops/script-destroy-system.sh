#!/bin/bash
aws eks update-kubeconfig --name app --region ap-southeast-1
alias k=kubectl

cd external-dns
helm uninstall external-dns  -n external-dns 
cd ..

cd istio
helm uninstall istio-system  -n istio-system 
cd ..

cd istio-ingress 
helm uninstall istio-ingress  -n istio-ingress 
cd ..

cd metrics-server 
helm uninstall metrics-server  -n metrics-server 
cd ..

cd istio-monitor
k delete -f . 
cd ..

cd prometheus-adapter
helm uninstall prometheus-adapter -n prometheus-adapter
cd ..

cd ../..
cd system/ops


k delete ns external-dns
k delete ns istio-system
k delete ns metrics-server
k delete ns istio-ingress
k delete ns prometheus-adapter
