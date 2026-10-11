FROM node:20-alpine
WORKDIR /app
COPY auth/package.json ./
RUN npm install
COPY auth/ .
COPY shared/ ../shared/
EXPOSE 4000
CMD ["node", "index.js"]