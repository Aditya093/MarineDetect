# Frontend Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ENV NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
EXPOSE 3000
RUN npm run build
CMD ["npm", "run", "start"]
