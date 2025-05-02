### Kubernetes ###

configure:
	aws configure

connect:
	aws eks update-kubeconfig --name aws-account-name --region us-east-1

add-registry-secret:
	kubectl create secret docker-registry regcred \
	--docker-server=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com \
	--docker-username=AWS \
	--docker-password=$(shell aws ecr get-login-password) \
	--namespace=default

verify:
	kubectl cluster-info

apply:
	kubectl apply -f $(APP).yaml

### Docker ###

docker-build:
	docker build --platform linux/amd64 --provenance false -t $(APP) -f $(APP).Dockerfile .
	
docker-push:
	aws ecr describe-repositories --repository-names $(APP) || aws ecr create-repository --repository-name $(APP)
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com
	docker tag $(APP) ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(APP):latest
	docker push ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(APP):latest