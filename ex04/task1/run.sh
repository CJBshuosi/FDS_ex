#!/bin/bash

# Build the project
echo "Building project..."
./gradlew clean build

# Get the classpath
CLASSPATH="build/classes/main"

# Add all dependencies from gradle cache
for jar in ~/.gradle/caches/modules-2/files-2.1/*/*/*/*/*.jar; do
    CLASSPATH="$CLASSPATH:$jar"
done

# Run the main class
echo ""
echo "Running XaBankingAppTest..."
echo "=========================================="
java -cp "$CLASSPATH" ch.unibas.dmi.dbis.fds._2pc.XaBankingAppTest
echo "=========================================="

