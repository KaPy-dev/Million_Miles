FROM node:20-alpine

WORKDIR /app


COPY package.json package-lock.json* ./
RUN npm ci

COPY src ./src
COPY public ./public
COPY next.config.ts .
COPY tsconfig.json .


RUN npm run build


CMD ["npm", "run", "start"]
