aws eks update-kubeconfig --region ap-southeast-1  --name thesis

export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION="ap-southeast-1"
export AWS_SESSION_TOKEN=""

## Update kube config
kubectl edit -n kube-system configmap/aws-auth

```
apiVersion: v1
data:
  mapRoles: |
    - rolearn: 
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:masters
kind: ConfigMap
```
## Install helm
Install helm: https://www.eksworkshop.com/beginner/060_helm/helm_intro/install/
curl -sSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm version --short
