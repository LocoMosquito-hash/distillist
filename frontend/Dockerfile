# Development image: runs the Vite dev server with hot reload.
# (A multi-stage production build served by nginx will come later.)
FROM node:22-slim

WORKDIR /usr/src/app

# install dependencies first so Docker can cache this layer
COPY package*.json ./
RUN npm install

# add app
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
