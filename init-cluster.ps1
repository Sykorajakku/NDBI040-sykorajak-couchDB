# Load environment variables from .env file
$envVars = Get-Content .\.env | ConvertFrom-StringData

$DEPLOYMENT_NAME = $envVars.COMPOSE_PROJECT_NAME
$COORDINATOR_NODE = "0"
$ADDITIONAL_NODES = "1,2"
$ALL_NODES = "$COORDINATOR_NODE,$ADDITIONAL_NODES"

# See https://docs.couchdb.org/en/master/setup/cluster.html

foreach ($NODE_ID in $COORDINATOR_NODE) {
  Invoke-RestMethod -Method POST -ContentType "application/json" -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}${NODE_ID}/_cluster_setup" -Body @{
    action = "enable_cluster"
    bind_address = "0.0.0.0"
    username = "${envVars.COUCHDB_USER}"
    password = "${envVars.COUCHDB_PASSWORD}"
    node_count = "3"
  } | ConvertTo-Json -Depth 5
  Write-Host "You may safely ignore the warning above."
}

foreach ($NODE_ID in $ADDITIONAL_NODES.Split(',')) {
  Invoke-RestMethod -Method POST -ContentType "application/json" -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}0/_cluster_setup" -Body @{
    action = "enable_cluster"
    bind_address = "0.0.0.0"
    username = "${envVars.COUCHDB_USER}"
    password = "${envVars.COUCHDB_PASSWORD}"
    port = 5984
    node_count = "3"
    remote_node = "couchdb-${NODE_ID}.${DEPLOYMENT_NAME}"
    remote_current_user = "${envVars.COUCHDB_USER}"
    remote_current_password = "${envVars.COUCHDB_PASSWORD}"
  } | ConvertTo-Json -Depth 5

  Invoke-RestMethod -Method POST -ContentType "application/json" -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}0/_cluster_setup" -Body @{
    action = "add_node"
    host = "couchdb-${NODE_ID}.${DEPLOYMENT_NAME}"
    port = 5984
    username = "${envVars.COUCHDB_USER}"
    password = "${envVars.COUCHDB_PASSWORD}"
  } | ConvertTo-Json -Depth 5
}

# See https://github.com/apache/couchdb/issues/2858
Invoke-RestMethod -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}0/"

Invoke-RestMethod -Method POST -ContentType "application/json" -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}0/_cluster_setup" -Body @{
  action = "finish_cluster"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}0/_cluster_setup"

Invoke-RestMethod -Uri "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@127.0.0.1:${envVars.PORT_BASE}0/_membership"

Write-Host "Your cluster nodes are available at:"
foreach ($NODE_ID in $ $ALL_NODES.Split(',')) {
  Write-Host "http://${envVars.COUCHDB_USER}:${envVars.COUCHDB_PASSWORD}@localhost:${envVars.PORT_BASE}${NODE_ID}"
}
