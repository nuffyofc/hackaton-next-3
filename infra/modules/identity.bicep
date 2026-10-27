param environmentName string
param location string = resourceGroup().location

var identityName = 'id-app-${environmentName}'

resource appIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

output identityId string = appIdentity.id
output principalId string = appIdentity.properties.principalId
output clientId string = appIdentity.properties.clientId
