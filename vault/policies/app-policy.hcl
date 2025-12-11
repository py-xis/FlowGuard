# Policy for spam-classifier application
path "secret/data/spam-classifier/*" {
  capabilities = ["read", "list"]
}

path "secret/data/dockerhub/*" {
  capabilities = ["read", "list"]
}

path "database/creds/mlflow" {
  capabilities = ["read"]
}
