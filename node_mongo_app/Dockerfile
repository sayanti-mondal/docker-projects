# Stage 1: Define the base image
FROM node:19-alpine 

# Stage 2: Set environment variables for MongoDB connection
ENV MONGODB_USERNAME=admin
ENV MONGODB_PASSWORD=qwerty

# Stage 3: Create a directory inside the container for the application code
RUN mkdir -p /testapp 

# Stage 4: Copy the application files from the host to the container
# The '.' refers to the current build context (where the Dockerfile is located,
# which is assumed to be the root of the 'testapp' application).
# It copies all contents of the host's current directory into /testapp in the container.
COPY . /testapp 

# Stage 5: Define the command to run the application when the container starts
# This command executes the Node.js server.js file located within the /testapp directory.
CMD ["node", "/testapp/server.js"] 
