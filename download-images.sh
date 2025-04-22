#!/bin/bash

# Create assets directory if it doesn't exist
mkdir -p assets

# Download placeholder images
curl -o assets/hero-japan.jpg "https://source.unsplash.com/1600x900/?japan,tokyo"
curl -o assets/tokyo.jpg "https://source.unsplash.com/600x400/?tokyo,city"
curl -o assets/paris.jpg "https://source.unsplash.com/600x400/?paris,eiffel"
curl -o assets/new-york.jpg "https://source.unsplash.com/600x400/?newyork,city"
curl -o assets/japan-flight.jpg "https://source.unsplash.com/600x400/?airplane,japan"
curl -o assets/tokyo-hotel.jpg "https://source.unsplash.com/600x400/?hotel,tokyo"

# Make the script executable
chmod +x download-images.sh 