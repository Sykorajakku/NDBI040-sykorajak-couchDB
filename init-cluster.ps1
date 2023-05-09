# Load environment variables from .env file
$envFileContent = Get-Content .env
$envVars = @{}

foreach ($line in $envFileContent) {
  if (-not [string]::IsNullOrWhiteSpace($line)) {
      $keyValuePair = $line -split '=', 2
      $key = $keyValuePair[0].Trim()
      $value = $keyValuePair[1].Trim()
      $envVars[$key] = $value
  }
}

$DEPLOYMENT_NAME = $envVars.COMPOSE_PROJECT_NAME

$COORDINATOR_NODE = "0"
$ADDITIONAL_NODES = "1,2"
$ALL_NODES = "$COORDINATOR_NODE,$ADDITIONAL_NODES"
$COUCHDB_USER = $envVars.COUCHDB_USER
$COUCHDB_PASSWORD = $envVars.COUCHDB_PASSWORD

curl.exe -X POST -H "Content-Type: application/json" http://couchdb.admin:couchdb.admin@127.0.0.1:10010/_cluster_setup -d '{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\":\"couchdb.admin\", \"password\":\"couchdb.admin\", \"node_count\":\"3\"}'
Write-Host "You may safely ignore the warning above."

curl.exe -X POST -H "Content-Type: application/json" "http://$($envVars.COUCHDB_USER):$($envVars.COUCHDB_PASSWORD)@127.0.0.1:$($envVars.PORT_BASE)0/_cluster_setup" -d '{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": \"couchdb.admin\", \"password\":\"couchdb.admin\", \"port\": 5984, \"node_count\": \"3\", \"remote_node\": \"couchdb-1.aspw-dev\", \"remote_current_user\": \"couchdb.admin\", \"remote_current_password\": \"couchdb.admin\" }'
curl.exe -X POST -H "Content-Type: application/json" "http://$($envVars.COUCHDB_USER):$($envVars.COUCHDB_PASSWORD)@127.0.0.1:$($envVars.PORT_BASE)0/_cluster_setup" -d '{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": \"couchdb.admin\", \"password\":\"couchdb.admin\", \"port\": 5984, \"node_count\": \"3\", \"remote_node\": \"couchdb-2.aspw-dev\", \"remote_current_user\": \"couchdb.admin\", \"remote_current_password\": \"couchdb.admin\" }'
curl.exe -X POST -H "Content-Type: application/json" "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@127.0.0.1:$($envVars.PORT_BASE)0/_cluster_setup" -d '{\"action\": \"add_node\", \"host\":\"couchdb-1.aspw-dev\", \"port\": 5984, \"username\":\"couchdb.admin\", \"password\":\"couchdb.admin\"}'
curl.exe -X POST -H "Content-Type: application/json" "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@127.0.0.1:$($envVars.PORT_BASE)0/_cluster_setup" -d '{\"action\": \"add_node\", \"host\":\"couchdb-2.aspw-dev\", \"port\": 5984, \"username\":\"couchdb.admin\", \"password\":\"couchdb.admin\"}'

curl.exe "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@127.0.0.1:$($envVars.PORT_BASE)0/"
curl.exe -X POST -H "Content-Type: application/json" "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@127.0.0.1:$($envVars.PORT_BASE)0/_cluster_setup" -d '{\"action\": \"finish_cluster\"}'
curl.exe "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@127.0.0.1:$($envVars.PORT_BASE)0/_cluster_setup"
curl.exe "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@127.0.0.1:$($envVars.PORT_BASE)0/_membership"

Write-Host "Your cluster nodes are available at:"
foreach ($NODE_ID in $ALL_NODES.Split(',')) {
  Write-Host "http://$($envVars.COUCHDB_USER):$($envVars.COUCHDB_PASSWORD)@localhost:$($envVars.PORT_BASE)${NODE_ID}"
}