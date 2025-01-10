#!/bin/bash

# Set your Kafka broker list, topic
broker_list="kafka-0:9092,kafka-1:9092,kafka-2:9092"
kafka_topic="mysql-debezium-alo123.demo.ORDERS"
kafka_container_name="kafka-0"

# Set the number of iterations and delay in seconds
iterations=10
delay=1

# Function to get the current offset for a specific topic inside the Kafka-0 container
get_offset() {
  docker exec -i "$kafka_container_name" kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list "$broker_list" --topic "$kafka_topic" | awk -F ":" '{print $3}'
}

total_records_per_second=0

# Loop to get counts and calculate differences
for ((i=0; i<iterations; i++)); do
  prev_count=$(get_offset)
  start_time=$(date +%s)  # start time here
  sleep $delay
  current_count=$(get_offset)
  end_time=$(date +%s)    # end time here

  count_diff=$((current_count - prev_count))
  elapsed_time=$((end_time - start_time))
  new_offsets_per_second=$((count_diff / elapsed_time))
  echo "new_offsets/s attempt $((i+1)): $new_offsets_per_second"
  total_records_per_second=$((total_records_per_second + new_offsets_per_second))
  # prev_count=$current_count
done

# Calculate and print the average
average_records_per_second=$((total_records_per_second / iterations))
echo "Average new_offsets/s: $average_records_per_second"
