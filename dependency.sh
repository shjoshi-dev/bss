# Generate the raw dependencies.
sfood ./bst > /tmp/raw.deps

# Filter and cluster.
cd ./bst ; ls -1d * > /tmp/clusters
cat /tmp/raw.deps | grep -v test_widget | sfood-cluster -f /tmp/clusters > /tmp/filt.deps

# Generate the graph.
cat /tmp/raw.deps | sfood-graph -p | dot -Tps | pstopdf -i -o /tmp/myproject.pdf