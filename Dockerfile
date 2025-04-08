# Use the official Node.js image as the base
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on (commonly 3000 or 8080)
EXPOSE 8080

# Define the command to run your app (like in the Procfile)
CMD ["node", "server.js"]
