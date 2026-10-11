FROM node:20-alpine
WORKDIR /app
COPY orders/package.json ./
RUN npm install
COPY orders/ .
COPY shared/ ../shared/
EXPOSE 4000
CMD ["node", "index.js"]