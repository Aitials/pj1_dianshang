# 前端用多阶段构建：第一阶段用 Node 把 Vue 编译成静态文件，第二阶段只用 Nginx 托管。
# 最终镜像里不含 Node、不含源码、不含 node_modules，体积远小于单阶段方案。
FROM node:20-alpine AS build

WORKDIR /app

# 先只拷依赖清单：只要 package.json / package-lock.json 没变，npm ci 这层就能命中缓存
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# ---------- 运行阶段 ----------
FROM nginx:1.27-alpine

# 覆盖默认站点配置：Vue Router 的 history 回退 + /api 反向代理
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 只把编译产物 dist 搬过来
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]