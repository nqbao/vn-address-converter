#!/bin/bash

# Loop from 2 to 35 and run the table extractor for each number
for i in {2..35}; do
    echo "Running table extractor for table $i..."
    python pipelines/llm_table_extractor.py $i
    
    # Optional: Add a small delay between runs to avoid overwhelming the system
    sleep 1
done

echo "All table extractions completed!"
