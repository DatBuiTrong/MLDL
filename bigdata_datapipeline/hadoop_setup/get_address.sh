#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <your_network_name>"
    exit 1
fi

network_name="$1"

# Run `docker network inspect` and store the JSON output in a variable
network_info=$(docker network inspect "$network_name")

# Use `jq` to extract the container names
container_names=$(echo "$network_info" | jq -r '.[0].Containers | keys[] as $k | .[$k].Name')

# Function to extract the URL for a container name
get_container_url() {
    name="$1"
    port="$2"
    ipv4_address=$(echo "$network_info" | jq -r '.[0].Containers[] | select(.Name == "'$name'").IPv4Address' | cut -d'/' -f1)
    if [ -n "$ipv4_address" ]; then
        echo "$name: http://$ipv4_address:$port"
    fi
}

# Print first 3 important containers
echo $(get_container_url "namenode" 9870)
echo $(get_container_url "historyserver" 8188)
echo $(get_container_url "resourcemanager" 8088)
echo $(get_container_url "postgres-datamart" 5432)

# Create an array to store the container names that contain "datanode"
datanode_containers=()

# Iterate through the container names and filter those containing "datanode"
for container_name in $container_names; do
    if [[ $container_name == *datanode* ]]; then
        datanode_containers+=("$container_name")
    fi
done

# Sort the array in ascending order
sorted_containers=($(printf '%s\n' "${datanode_containers[@]}" | sort))

# Print the sorted container names
for container_name in "${sorted_containers[@]}"; do
    echo $(get_container_url "$container_name" 9864)
done

# Create an array to store the container names that contain "nodemanager"
nodemanager_containers=()

# Iterate through the container names and filter those containing "nodemanager"
for container_name in $container_names; do
    if [[ $container_name == *nodemanager* ]]; then
        nodemanager_containers+=("$container_name")
    fi
done

# Sort the array in ascending order
sorted_containers=($(printf '%s\n' "${nodemanager_containers[@]}" | sort))

# Print the sorted container names
for container_name in "${sorted_containers[@]}"; do
    echo $(get_container_url "$container_name" 8042)
done