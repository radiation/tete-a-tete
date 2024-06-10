# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json from the frontend directory into the working directory
COPY ./frontend/package.json ./
COPY ./frontend/package-lock.json ./

# Install any needed packages specified in package.json
RUN npm install

# Copy the rest of your frontend application source code from the frontend directory
COPY ./frontend/ .

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Command to run your app
CMD ["npm", "start"]
