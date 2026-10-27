# Deployment

1. Validate: `az bicep build --file infra/main.bicep`
2. Provision via `infra/azure.yaml` + `azd up` once domain MVP works offline.
3. Keyless only: User-Assigned Managed Identity — no secrets in Git.
