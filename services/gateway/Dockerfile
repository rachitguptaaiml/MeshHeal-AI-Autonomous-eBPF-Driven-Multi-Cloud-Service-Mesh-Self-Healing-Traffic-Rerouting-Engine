FROM node:20-alpine
WORKDIR /app
COPY gateway/package.json ./
RUN npm install
COPY gateway/ .
COPY shared/ ../shared/
EXPOSE 4000
CMD ["node", "index.js"]