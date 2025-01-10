#!/bin/bash

# Set the number of iterations and delay in seconds
iterations=10
delay=1

# Function to get the count from MySQL
get_count() {
  docker exec -i mysql bash -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD -sN -e "use demo; SELECT COUNT(*) FROM ORDERS;"'
}

# Variables for calculating average
total_diff=0

# Loop to get counts and calculate differences
for ((i=0; i<iterations; i++)); do
  prev_count=$(get_count)
  start_time=$(date +%s)  # start time here
  sleep $delay
  current_count=$(get_count)
  end_time=$(date +%s)    # end time here

  count_diff=$((current_count - prev_count))
  elapsed_time=$((end_time - start_time))
  new_records_per_second=$((count_diff / elapsed_time))
  echo "Records/s attempt $((i+1)): $new_records_per_second"
  total_diff=$((total_diff + new_records_per_second))
done

# Calculate and print the average
average_diff=$((total_diff / iterations))
echo "Average Records/s: $average_diff"
