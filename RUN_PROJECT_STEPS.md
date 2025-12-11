# 🚀 MLOps Project Execution Manual
## Email/SMS Spam Classifier - Complete CI/CD & MLOps Pipeline

**Course:** CSE 816 - Software Production Engineering  
**Domain:** MLOps  
**Team Size:** 2 Students

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Part 1: Local Development & Testing](#part-1-local-development--testing)
4. [Part 2: Docker Build & Push](#part-2-docker-build--push)
5. [Part 3: Kubernetes Infrastructure Setup](#part-3-kubernetes-infrastructure-setup)
6. [Part 4: ELK Stack Deployment](#part-4-elk-stack-deployment)
7. [Part 5: MLflow Setup](#part-5-mlflow-setup)
8. [Part 6: Jenkins CI/CD Setup](#part-6-jenkins-cicd-setup)
9. [Part 7: Application Deployment](#part-7-application-deployment)
10. [Part 8: Verify Complete Pipeline](#part-8-verify-complete-pipeline)
11. [Part 9: Demo Execution](#part-9-demo-execution)
12. [Troubleshooting](#troubleshooting)
13. [Port Reference](#port-reference)

---

## PREREQUISITES

### Required Software
- ✅ **Git** - Version control
- ✅ **Docker** & **Docker Compose** - Containerization
- ✅ **Kubernetes** (Minikube or Kind) - Orchestration
- ✅ **kubectl** - Kubernetes CLI
- ✅ **Jenkins** - CI/CD server
- ✅ **Ansible** - Configuration management
- ✅ **Python 3.11+** - Application runtime
- ✅ **Helm** (optional) - For Vault installation

### Verify Installationsa
```bash
git --version
docker --version
docker-compose --version
kubectl version --client
minikube version  # or: kind version
jenkins --version
ansible --version
python3 --version
```

---

## INITIAL SETUP

### 1. Clone Repository (if not already done)
```bash
cd /Users/pranav_kulkarni/Desktop/SPE/Projects/Final_Project
```

### 2. Set Environment Variables
```bash
# Docker Hub credentials (REPLACE WITH YOUR VALUES)
export DOCKERHUB_USERNAME="your_dockerhub_username"
export DOCKERHUB_PASSWORD="your_dockerhub_password"

# Update deployment.yaml
sed -i '' "s/YOUR_DOCKERHUB_USERNAME/${DOCKERHUB_USERNAME}/g" kubernetes/deployment.yaml
sed -i '' "s/YOUR_DOCKERHUB_USERNAME/${DOCKERHUB_USERNAME}/g" kubernetes/mlflow-deployment.yaml
sed -i '' "s/YOUR_DOCKERHUB_USERNAME/${DOCKERHUB_USERNAME}/g" jenkins/Jenkinsfile
```

### 3. Start Kubernetes Cluster
```bash
# Using Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable metrics server (required for HPA)
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

---

## PART 1: LOCAL DEVELOPMENT & TESTING

### Step 1.1: Setup Python Environment
```bash
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh
```

### Step 1.2: Run Tests
```bash
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh
```

Expected output: All tests should pass with >80% coverage

### Step 1.3: Test Application Locally (Optional)
```bash
source venv/bin/activate
streamlit run src/app.py
```

Access at: http://localhost:8501  
Press Ctrl+C to stop

---

## PART 2: DOCKER BUILD & PUSH

### Step 2.1: Build Docker Images
```bash
# Build spam classifier image
docker build -f docker/Dockerfile -t ${DOCKERHUB_USERNAME}/spam-classifier:latest .

# Build MLflow server image
docker build -f docker/Dockerfile.mlflow -t ${DOCKERHUB_USERNAME}/mlflow-server:latest .

# Verify images
docker images | grep spam-classifier
docker images | grep mlflow-server
```

### Step 2.2: Test Docker Image Locally
```bash
# Run container
docker run -d -p 8501:8501 --name spam-test ${DOCKERHUB_USERNAME}/spam-classifier:latest

# Check logs
docker logs spam-test

# Test health endpoint
sleep 20
curl http://localhost:8501/_stcore/health

# Stop and remove
docker stop spam-test
docker rm spam-test
```

### Step 2.3: Push to Docker Hub
```bash
# Login to Docker Hub
echo $DOCKERHUB_PASSWORD | docker login -u $DOCKERHUB_USERNAME --password-stdin

# Push images
docker push ${DOCKERHUB_USERNAME}/spam-classifier:latest
docker push ${DOCKERHUB_USERNAME}/mlflow-server:latest

# Verify on Docker Hub
echo "Verify at: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/spam-classifier"
```

---

## PART 3: KUBERNETES INFRASTRUCTURE SETUP

### Step 3.1: Create Namespace and ConfigMaps
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml

# Verify
kubectl get namespaces
kubectl get configmap -n spam-classifier
```

### Step 3.2: Deploy MLflow Server
```bash
kubectl apply -f kubernetes/mlflow-deployment.yaml

# Wait for MLflow to be ready
kubectl wait --for=condition=ready pod -l app=mlflow -n spam-classifier --timeout=300s

# Verify
kubectl get pods -n spam-classifier
kubectl get svc -n spam-classifier
```

### Step 3.3: Access MLflow UI (Port Forward)
```bash
# Port forward to access MLflow
kubectl port-forward -n spam-classifier svc/mlflow-service 5000:5000 &

# Access MLflow UI at: http://localhost:5000
```

---

## PART 4: ELK STACK DEPLOYMENT

### Step 4.1: Deploy Elasticsearch
```bash
kubectl apply -f kubernetes/elk/elasticsearch.yaml

# Wait for Elasticsearch (this may take 2-3 minutes)
kubectl wait --for=condition=ready pod -l app=elasticsearch -n spam-classifier --timeout=600s

# Verify
kubectl get pods -n spam-classifier | grep elasticsearch
```

### Step 4.2: Deploy Logstash
```bash
kubectl apply -f kubernetes/elk/logstash.yaml

# Wait for Logstash
kubectl wait --for=condition=ready pod -l app=logstash -n spam-classifier --timeout=300s
```

### Step 4.3: Deploy Kibana
```bash
kubectl apply -f kubernetes/elk/kibana.yaml

# Wait for Kibana
kubectl wait --for=condition=ready pod -l app=kibana -n spam-classifier --timeout=300s

# Get Kibana LoadBalancer IP
kubectl get svc kibana -n spam-classifier
```

### Step 4.4: Deploy Filebeat
```bash
kubectl apply -f kubernetes/elk/filebeat-daemonset.yaml

# Verify Filebeat is running on all nodes
kubectl get daemonset -n spam-classifier
kubectl get pods -n spam-classifier | grep filebeat
```

### Step 4.5: Access Kibana Dashboard
```bash
# If LoadBalancer is pending, use port-forward
kubectl port-forward -n spam-classifier svc/kibana 5601:5601 &

# Open in browser: http://localhost:5601
```

---

## PART 5: MLFLOW SETUP

### Step 5.1: Train Initial Model
```bash
# Activate Python environment
source venv/bin/activate

# Create local directories for MLflow artifacts
mkdir -p mlruns artifacts models

# Set MLflow tracking URI (for experiment tracking)
export MLFLOW_TRACKING_URI=http://localhost:5000

# Unset artifact root to use local storage
unset MLFLOW_ARTIFACT_ROOT

# Train model
python -m src.train --algorithm naive_bayes --max-features 3000

# Check MLflow UI to see the experiment run
# Note: Metrics/parameters will be on MLflow server, artifacts saved locally
```

### Step 5.2: Verify Model Artifacts
```bash
ls -lh models/
# Should see: model.pkl and vectorizer.pkl

# Check in MLflow UI:
# 1. Go to http://localhost:5000
# 2. Click on "spam-classifier-training" experiment
# 3. View logged metrics, parameters, and artifacts
```

---

## PART 6: JENKINS CI/CD SETUP

### Step 6.1: Install and Start Jenkins
```bash
# If Jenkins is not installed, install via Homebrew (macOS)
brew install jenkins-lts

# Start Jenkins
brew services start jenkins-lts

# Get initial admin password
cat ~/.jenkins/secrets/initialAdminPassword
```

### Step 6.2: Configure Jenkins
1. Open Jenkins: http://localhost:8080
2. Enter initial admin password
3. Install suggested plugins
4. Create admin user
5. Save and continue

### Step 6.3: Install Required Plugins
Go to: Manage Jenkins → Manage Plugins → Available

Install:
- ✅ Docker Pipeline
- ✅ Kubernetes CLI
- ✅ Git Plugin
- ✅ GitHub Hook Trigger
- ✅ HTML Publisher (for coverage reports)
- ✅ JUnit Plugin
- ✅ Ansible Plugin

### Step 6.4: Configure Credentials
Go to: Manage Jenkins → Manage Credentials → Global → Add Credentials

**Add Docker Hub Credentials:**
- Kind: Username with password
- ID: `dockerhub-credentials`
- Username: Your Docker Hub username
- Password: Your Docker Hub password

### Step 6.5: Create Jenkins Pipeline Job
1. New Item → Pipeline
2. Name: `spam-classifier-pipeline`
3. Check: "GitHub hook trigger for GITScm polling"
4. Pipeline:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your Git repository URL
   - Script Path: `jenkins/Jenkinsfile`
5. Save

### Step 6.6: Create Training Pipeline Job
1. New Item → Pipeline
2. Name: `spam-classifier-train`
3. Pipeline:
   - Definition: Pipeline script from SCM
   - Script Path: `jenkins/Jenkinsfile.train`
4. Save

### Step 6.7: Configure GitHub Webhook
1. Go to GitHub repository → Settings → Webhooks
2. Add webhook:
   - Payload URL: `http://YOUR_JENKINS_URL:8080/github-webhook/`
   - Content type: application/json
   - Events: Just the push event
3. Save

---

## PART 7: APPLICATION DEPLOYMENT

### Step 7.1: Deploy Using Ansible
```bash
cd ansible

# Deploy infrastructure
ansible-playbook -i inventory/hosts.ini playbooks/setup-infrastructure.yml

# Deploy application
ansible-playbook -i inventory/hosts.ini playbooks/deploy-app.yml

cd ..
```

### Step 7.2: Manually Apply Kubernetes Manifests (Alternative)
```bash
# Apply deployment
kubectl apply -f kubernetes/deployment.yaml

# Apply service
kubectl apply -f kubernetes/service.yaml

# Apply HPA
kubectl apply -f kubernetes/hpa.yaml
```

### Step 7.3: Wait for Deployment
```bash
# Watch deployment rollout
kubectl rollout status deployment/spam-classifier -n spam-classifier --timeout=5m

# Verify pods are running
kubectl get pods -n spam-classifier -l app=spam-classifier

# Check HPA
kubectl get hpa -n spam-classifier
```

### Step 7.4: Access Application
```bash
# Get service details
kubectl get svc spam-classifier-service -n spam-classifier

# If LoadBalancer is pending, use port-forward
kubectl port-forward -n spam-classifier svc/spam-classifier-service 8080:80 &

# Open in browser: http://localhost:8080
```

---

## PART 8: VERIFY COMPLETE PIPELINE

### Step 8.1: Verify All Components
```bash
# Check all pods
kubectl get pods -n spam-classifier

# Expected pods:
# - spam-classifier-xxx (2+ replicas)
# - mlflow-xxx
# - elasticsearch-0
# - logstash-xxx
# - kibana-xxx
# - filebeat-xxx (on each node)

# Check all services
kubectl get svc -n spam-classifier

# Check HPA
kubectl get hpa -n spam-classifier
```

### Step 8.2: Test End-to-End Flow
```bash
# Make a prediction
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won $1000. Click here to claim now!"}'

# Check logs in Kibana
# 1. Go to http://localhost:5601
# 2. Management → Stack Management → Index Patterns
# 3. Create index pattern: spam-classifier-logs-*
# 4. Go to Discover and view logs
```

### Step 8.3: Verify Prometheus Metrics (if using Flask API)
```bash
# Port forward Prometheus
kubectl port-forward -n spam-classifier svc/prometheus 9090:9090 &

# Access Prometheus: http://localhost:9090
# Query: spam_classifier_requests_total
```

---

## PART 9: DEMO EXECUTION


### 9.1: Faculty Demo Flow (15-20 minutes)

#### **Step 1: Show Architecture (2 min)**
```bash
# Show project structure
tree -L 2 -I 'venv|__pycache__|email-sms-spam-classifier'

# Explain architecture diagram from project_architecture_plan.md
```

#### **Step 2: Code Walkthrough (3 min)**
Show key files:
- `jenkins/Jenkinsfile` - CI/CD pipeline
- `kubernetes/deployment.yaml` - Rolling update config
- `kubernetes/hpa.yaml` - Auto-scaling config
- `ansible/roles/app-deployment/tasks/main.yml` - Ansible role

#### **Step 3: Trigger CI/CD Pipeline (5 min)**
```bash
# Make a visible code change
echo "# Updated $(date)" >> src/app.py

# Commit and push
git add src/app.py
git commit -m "Demo: Trigger CI/CD pipeline"
git push origin main

# Show Jenkins automatically triggered
# Open Jenkins: http://localhost:8080
# Watch pipeline execute all stages
```

#### **Step 4: Show MLflow (2 min)**
```bash
# Open MLflow UI: http://localhost:5000
# Show:
# - Experiment runs
# - Logged parameters and metrics
# - Model artifacts
# - Model registry
```

#### **Step 5: Show Kubernetes & HPA (3 min)**
```bash
# Show running pods
kubectl get pods -n spam-classifier -w

# Show HPA status
kubectl get hpa -n spam-classifier

# Load test to trigger scaling
for i in {1..100}; do
  curl -s http://localhost:8080/_stcore/health &
done

# Watch HPA scale up
kubectl get hpa -n spam-classifier -w
```

#### **Step 6: Show Application (2 min)**
```bash
# Open application: http://localhost:8080

# Test spam prediction:
# Input: "URGENT! You won $1000. Click here NOW!"
# Show prediction result
```

#### **Step 7: Show ELK Stack (3 min)**
```bash
# Open Kibana: http://localhost:5601

# Show:
# 1. Discover tab - Real-time logs
# 2. Filter by "prediction" field
# 3. Show spam vs not_spam distribution
# 4. Show prediction confidence
# 5. Show pod-level logs
```

#### **Step 8: Show Zero-Downtime Update (2 min)**
```bash
# Trigger another deployment
echo "# Updated $(date)" >> README.md
git add README.md
git commit -m "Demo: Zero-downtime deployment"
git push origin main

# Watch rolling update
kubectl get pods -n spam-classifier -w

# Show application remains accessible during update
while true; do curl -s http://localhost:8080/_stcore/health && echo " - $(date)"; sleep 2; done
```

#### **Step 9: Show Vault (Optional - 1 min)**
```bash
# Show Vault configuration
cat vault/policies/app-policy.hcl

# Show Vault annotations in deployment
grep -A 2 "vault.hashicorp.com" kubernetes/deployment.yaml
```

---

### 9.2: Marks Demonstration Checklist

**Working Project (20/20):**
- ✅ Git push triggers Jenkins automatically
- ✅ Jenkins runs tests, builds Docker image, pushes to Docker Hub
- ✅ Kubernetes deployment updates automatically
- ✅ Application shows new version immediately
- ✅ Kibana dashboard shows real-time logs

**Advanced Features (3/3):**
- ✅ Vault policy configured (show file)
- ✅ Ansible roles demonstrated (show directory structure)
- ✅ HPA scales from 2 to 10 pods (demonstrate with load)

**Innovation (2/2):**
- ✅ MLflow tracks all experiments (show UI)
- ✅ Prediction logging with confidence scores (show in Kibana)

**Domain-Specific MLOps (5/5):**
- ✅ MLflow experiment tracking (show runs)
- ✅ Model versioning and registry (show versions)
- ✅ Separate training pipeline (show Jenkinsfile.train)
- ✅ Model metadata in logs (show in Kibana)
- ✅ Complete ML lifecycle (show diagram)

---

## TROUBLESHOOTING

### Issue 1: Pods Not Starting
```bash
# Check pod status
kubectl get pods -n spam-classifier

# Describe pod for errors
kubectl describe pod <POD_NAME> -n spam-classifier

# Check logs
kubectl logs <POD_NAME> -n spam-classifier
```

### Issue 2: Cannot Pull Docker Image
```bash
# Verify image exists on Docker Hub
docker pull ${DOCKERHUB_USERNAME}/spam-classifier:latest

# Check imagePullPolicy in deployment.yaml should be: Always
```

### Issue 3: HPA Not Scaling
```bash
# Check if metrics-server is running
kubectl get pods -n kube-system | grep metrics-server

# Enable metrics-server in Minikube
minikube addons enable metrics-server

# Check HPA status
kubectl describe hpa spam-classifier-hpa -n spam-classifier
```

### Issue 4: Kibana Not Showing Logs
```bash
# Check Elasticsearch is running
kubectl get pods -n spam-classifier | grep elasticsearch

# Check Filebeat is collecting logs
kubectl logs -n spam-classifier <FILEBEAT_POD_NAME>

# Verify index exists
curl http://localhost:9200/_cat/indices
```

### Issue 5: Jenkins Pipeline Fails
```bash
# Check Jenkins console output for errors
# Common fixes:
# - Verify Docker Hub credentials in Jenkins
# - Ensure kubectl is configured in Jenkins environment
# - Check Ansible is installed on Jenkins server
```

---

## PORT REFERENCE

| Service                         | Port | Access URL            | Purpose            |
| ------------------------------- | ---- | --------------------- | ------------------ |
| **Spam Classifier (Streamlit)** | 8501 | http://localhost:8080 | Main application   |
| **MLflow**                      | 5000 | http://localhost:5000 | MLflow tracking UI |
| **Jenkins**                     | 8080 | http://localhost:8080 | CI/CD server       |
| **Kibana**                      | 5601 | http://localhost:5601 | Log visualization  |
| **Elasticsearch**               | 9200 | http://localhost:9200 | Log storage        |
| **Logstash**                    | 5044 | N/A                   | Log processing     |
| **Prometheus**                  | 9090 | http://localhost:9090 | Metrics monitoring |
| **Vault**                       | 8200 | http://localhost:8200 | Secrets management |

---

## KUBERNETES COMMANDS QUICK REFERENCE

```bash
# View all resources
kubectl get all -n spam-classifier

# View logs
kubectl logs -f <POD_NAME> -n spam-classifier

# View HPA metrics
kubectl top pods -n spam-classifier

# Restart deployment
kubectl rollout restart deployment/spam-classifier -n spam-classifier

# Scale manually
kubectl scale deployment spam-classifier --replicas=5 -n spam-classifier

# Delete all resources
kubectl delete namespace spam-classifier

# Port forward services
kubectl port-forward -n spam-classifier svc/spam-classifier-service 8080:80
kubectl port-forward -n spam-classifier svc/mlflow-service 5000:5000
kubectl port-forward -n spam-classifier svc/kibana 5601:5601
```

---

## SUCCESS CRITERIA VERIFICATION

Before presenting, verify all these work:

- [ ] **Git push** triggers Jenkins automatically
- [ ] **Jenkins** runs all stages successfully
- [ ] **Docker image** is built and pushed to Docker Hub
- [ ] **Kubernetes** deployment updates with new image
- [ ] **Application** is accessible and functional
- [ ] **MLflow** shows experiment runs
- [ ] **Kibana** shows application logs
- [ ] **HPA** can scale up and down
- [ ] **Zero-downtime** deployment works
- [ ] **All 30 marks** criteria are demonstrable

---

## FINAL NOTES

1. **Practice the demo** at least 2-3 times before presentation
2. **Have backup** screenshots/videos in case live demo fails
3. **Explain design choices** when asked
4. **Know your code** - be ready to explain any file
5. **Time management** - allocate time for Q&A
6. **2-student teamwork** - clearly explain who did what

---

## 🎉 PROJECT COMPLETION

Once all steps are verified working, your project is complete and ready for demonstration!

**Expected Grade: 30/30** ✅

Good luck with your presentation! 🚀
