# Fetching the latest node image on alpine linux
FROM node:14-alpine

# Set the working directory inside the container
WORKDIR /usr/src/ui

# Copy package.json and package-lock.json (if present)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app
RUN npm run build

# Expose the port that the React app will run on
EXPOSE 3000