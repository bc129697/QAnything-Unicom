#!/bin/bash
# 自动配置Nginx静态资源服务器的脚本

# 配置参数（按需修改）
IMAGE_DIR="/workspace/QAnything/QANY_DB/file_images"
NGINX_CONF="/etc/nginx/sites-available/default"
SERVER_NAME="localhost"  # 改为你的域名或IP
PORT=${IMAGE_NGINX_PORT:-1080}
export IMAGE_NGINX_PORT=$PORT


# 1. 更新系统并安装Nginx
# echo "正在安装Nginx..."
# if command -v apt &> /dev/null; then
#     apt update
#     apt install -y nginx

#     # 离线安装nginx
#     # wget https://nginx.org/download/nginx-1.22.1.tar.gz
#     # cd third_party
#     # tar -zxvf nginx-1.22.1.tar.gz
#     # cd nginx-1.22.1
#     # ./configure --without-http_rewrite_module --without-http_gzip_module
#     # make
#     # make install
# elif command -v yum &> /dev/null; then
#     yum install -y nginx
# else
#     echo "不支持的包管理器，退出安装"
#     exit 1
# fi


if [ ! -f "$NGINX_CONF" ]; then
    NGINX_CONF="/etc/nginx/conf.d/images.conf"
    if [ ! -f "$NGINX_CONF" ]; then
        touch "$FILE_PATH"
    fi
    echo "文件 $FILE_PATH 已创建。"
else
    echo "文件 $FILE_PATH 已存在。"
fi



# 2. 创建图片目录并设置权限
if [ ! -d "$IMAGE_DIR" ]; then
    echo "创建图片目录：$IMAGE_DIR"
    mkdir -p $IMAGE_DIR
fi
chmod -R 755 $IMAGE_DIR
chown -R www-data:www-data $IMAGE_DIR  # CentOS使用nginx:nginx

# 3. 生成Nginx配置文件
echo "生成Nginx配置文件..."
tee $NGINX_CONF > /dev/null <<EOF
server {
    listen $PORT;
    server_name $SERVER_NAME;

    location /images/ {
        alias $IMAGE_DIR/;
        autoindex on;
        expires 30d;
        
        # 防盗链配置（可选）
        # valid_referers none blocked \$host;
        # if (\$invalid_referer) {
        #     return 403;
        # }
    }
}
EOF

# 4. 配置SELinux/AppArmor（如需要）
# 以下为可选配置，根据系统环境取消注释
# if command -v setenforce &> /dev/null; then
#     echo "配置SELinux策略..."
#     chcon -Rt httpd_sys_content_t $IMAGE_DIR
#     setsebool -P httpd_can_network_connect 1
# fi

# 5. 重启Nginx服务
echo "重启Nginx服务..."
nginx -t
ARCH=$(uname -m)
if [[ "$ARCH" == "arm"* || "$ARCH" == "aarch64" ]]; then
    echo "当前系统是ARM架构"
    nginx
    /usr/sbin/nginx -s reload
else
    echo "当前系统不是ARM架构"
    systemctl restart nginx || service nginx restart
fi



# 6. 开放防火墙端口（如需要）
# if command -v ufw &> /dev/null; then
#     echo "开放$PORT端口..."
#     ufw allow $PORT/tcp
# elif command -v firewall-cmd &> /dev/null; then
#     firewall-cmd --permanent --add-port=$PORT/tcp
#     firewall-cmd --reload
# fi

# 7. 验证配置
echo "验证Nginx状态..."
if pgrep nginx > /dev/null; then
    echo "Nginx运行正常（PID: $(pgrep nginx)）"
else
    echo "Nginx未运行，请检查日志：tail -f /var/log/nginx/error.log"
    exit 1
fi


# 输出访问信息
echo -e "\n图像代理配置完成！"
echo "访问地址：http://${GATEWAY_IP:-0.0.0.0}:$PORT/images/"
echo "请将图片文件放入目录：$IMAGE_DIR"

