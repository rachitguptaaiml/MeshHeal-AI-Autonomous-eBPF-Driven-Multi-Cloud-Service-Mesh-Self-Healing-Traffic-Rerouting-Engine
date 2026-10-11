FROM node:20-alpine
WORKDIR /app
COPY payments/package.json ./
RUN npm install
COPY payments/ .
COPY shared/ ../shared/
EXPOSE 4000
CMD ["node", "index.js"]