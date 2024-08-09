# wristcheck api 部署文档



特定分支(例如main分支)提交代码触发github Actions执行CI/CD

简易流程如下:

- 首先运行测试

- 测试没有问题, 接着build镜像并push到[阿里云容器镜像服务](https://cr.console.aliyun.com/cn-hangzhou/instances)

- 然后SSH连到指定环境的ECS主机, 从阿里云容器镜像服务pull镜像

- 最后启动服务

  

## 1.基础服务准备




| 设施名称    | 数量      | 描述                                                         |
| ----------- | --------- | ------------------------------------------------------------ |
| 阿里云ECS   | 2台       | staging/prod, 目前测试环境选择的是Ubuntu 22.04 64位          |
| Mysql数据库 | 1台       | staging/prod, 目前配置staging环境使用docker容器启动MySQL, 线上数据库需购买 |
| 子域名      | 6个       | mp.wristcheck.com: 后端接口名称, 解析到prod环境的ECS地址<br />mp-staging.wristcheck.com: 后端接口名称, 解析到staging环境的ECS地址<br />portainer.wristcheck.com: ECS上容器管理域名,  解析到prod环境的ECS地址<br />portainer-staging.wristcheck.com:  ECS上容器管理域名, 解析到staging环境的ECS地址 <br />mp-static.wristcheck.com: 静态文件域名, 绑定到prod环境的OSS桶 <br />mp-static-staging.wristcheck.com: 静态文件域名, 绑定staging环境OSS桶 |
| SSL证书     | 无        | 目前使用Caddy来做反向代理, Caddy会自动处理https证书的问题, 如果没有特殊要求, 无需购买证书 |
| OSS         | 2个bucket | 需要开发环境的资源迁移到wristcheck-staging 和 wristcheck-prod<br />在[OSS控制台](https://oss.console.aliyun.com/bucket)分别绑定staging和prod的静态文件域名<br />**注意: stage和prod都需创建[wechat-avatar/](https://oss.console.aliyun.com/bucket/oss-cn-hangzhou/wristcheck/object?path=wechat-avatar%2F) 子目录, 用来存储用户头像** |
| CDN         | 按需求    | 对staging和prod的静态文件域名进行加速: https://cdn.console.aliyun.com/domain/list<br />注意: CDN -> 性能优化 -> 忽略参数 需要保留指定参数x-oss-process, 前端调整尺寸时有用到 |



## 2.环境准备



### 2.1 阿里云容器服务配置



阿里云容器服务分个人和企业, 开发过程中使用个人实例



#### 2.1.1 在阿里云容器服务创建镜像仓库

[here](https://cr.console.aliyun.com/cn-hangzhou/instance/repositories)

例如: wristcheck_api_staging, wristcheck_api_prod



#### 2.1.2 本地打包portainer镜像并上传到阿里云

[最新版本安装](https://docs.portainer.io/v/2.20/start/install/server/docker/linux)

[镜像位置](https://hub.docker.com/r/portainer/portainer-ee/tags?page=&page_size=&ordering=&name=2.20.3) 



最好本地build好上传一份到阿里云, 后续使用阿里云进行
```shell
# 注意: 以下只是参考命令, 请根据实际情况替换变量
docker login --username=willdx1992 registry.cn-hangzhou.aliyuncs.com
docker pull portainer/portainer-ee:2.20.3
docker tag 7150b64ed6a2 registry.cn-hangzhou.aliyuncs.com/willdx1992/portainer:2.20.3
docker push registry.cn-hangzhou.aliyuncs.com/willdx1992/portainer:2.20.3
```



#### 2.1.3 申请portainer许可

整个部署完成后, 访问portainer的域名, 会提示输入license

官方开放3节点免费的许可, 可以申请一下: [申请(3节点免费)license](https://www.portainer.io/take-3)

[3节点授权政策](https://www.portainer.io/3nf-license-agreement)

[具体节点的定义](https://portal.portainer.io/knowledge/what-is-a-node-for-licensing-purposes)



### 2.2 为ECS安装docker环境


[在 Ubuntu 上安装 Docker 引擎参考文档](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)


参考安装步骤如下:


```shell
# 步骤1: 添加阿里云的GPG密钥
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 步骤2: 添加Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 步骤3: 安装必要的软件包
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 步骤4: 安装docker
apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 步骤5: 配置阿里云镜像加速器
# 为了提高拉取镜像的速度，可以配置阿里云提供的镜像加速器 

mkdir -p /etc/docker
vim /etc/docker/daemon.json 
## 添加如下内容, 注意替换镜像加速器地址
## 镜像加速器地址在这里: https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
{
  "registry-mirrors": ["https://gfiuoxu5.mirror.aliyuncs.com"]  
}

# 重启docker
systemctl daemon-reload
systemctl restart docker

# 步骤5: 验证, 运行一个简单的Docker容器来测试安装是否成功
docker --version
docker run hello-world
```



## 2.3 在ECS上生成密钥对



```shell
# 注意: 以下只是参考命令, 请根据实际情况替换变量
ssh-keygen -t ed25519 -C "william@wristcheck.com"  # 一直回车, 会在/root/.ssh目录生成一对秘钥id_ed25519, id_ed25519.pub
```



## 2.4 配置Deploy keys



在项目的Settings -> Deploy keys下添加公钥, 将id_ed25519.pub的内容写入



## 3.为CI/CD配置环境变量



我们使用[Github Actions CI/CD && Environments进行部署](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#deployment-protection-rules)



### 3.1 添加staging和prod环境



**注意: 名称必须是staging和prod, 如下图**

![image-20240809174950540](https://p.ipic.vip/amxhmr.png)



#### 3.1.1 为prod设置**部署保护规则**



用于实现审核后发布功能, 需指定reviewers approve之后才能部署到线上

![image-20240809175042876](https://p.ipic.vip/5qkh06.png)



#### 3.1.2 为不同环境设置环境变量和secrets



这里设置的变量和secrets区分环境, 例如: 同样是DB_URL, staging和prod可以设置不同的内容



#####  Variables



| 名称                 | 描述                                 | 示例                                                         |
| -------------------- | ------------------------------------ | ------------------------------------------------------------ |
| ALLOWED_HOSTS        | 允许访问 Django 应用的域名和 IP 地址 | wristcheck.imdancer.com,imdancer.com,114.55.108.152,dashboard-wristchecklab.pages.dev,127.0.0.1,localhost |
| API_DOMAIN           | API服务地址                          | wristcheck.imdancer.com                                      |
| API_PORT             | 后端API服务启动端口                  | 8888                                                         |
| CORS_ALLOWED_ORIGINS | 跨域                                 | https://dashboard-wristchecklab.pages.dev,https://wristcheck.imdancer.com |
| CSRF_TRUSTED_ORIGINS | 跨站请求伪造                         | https://dashboard-wristchecklab.pages.dev,https://wristcheck.imdancer.com |
| DB_ENGINE            | 服务使用的数据库                     | mysql                                                        |
| DB_HOST              | 数据库地址                           | mysql                                                        |
| DB_NAME              | 数据库名称                           | wristcheck_staging, stage环境使用docker会自动创建            |
| DB_USER              | 数据库用户                           | wristcheck                                                   |
| ECS_HOST             | ECS主机公网IP地址                    | 114.55.108.152                                               |
| ECS_USER             | 远程连接到ECS执行一些命令            | root                                                         |
| ENVIRONMENT          | 环境名称                             | prod/staging                                                 |
| OSS_BUCKET           | bucket的名称                         | wristcheck-prod                                              |
| OSS_ENDPOINT         | 阿里云OSS的ENDPOINT                  | oss-cn-hangzhou.aliyuncs.com                                 |
| PORTAINER_DOMAIN     | docker管理服务地址                   | wristcheck-portainer.imdancer.com                            |
| STATIC_DOMAIN        | 静态文件域名                         | https://wristcheck-static.imdancer.com                       |
| WRISTCHECK_API       | 对接WRISTCHECK主站的api地址          | https://api.wristchecklab.com                                |



##### Secrets



| 名称             | 描述                                                         | 示例                        |
| ---------------- | ------------------------------------------------------------ | --------------------------- |
| DB_PASSWORD      | 数据库DB_USER对应密码                                        | wristcheck                  |
| DB_ROOT_PASSWORD | 数据库root对应密码                                           | wristcheck_root             |
| SSH_PRIVATE_KEY  | 用于ssh的方式连接到ECS, 进行部署代码 的操作, 现在是docker run | ECS的**私钥**id_ed25519内容 |





### 3.2 设置Repository变量和secrets



在staging和prod环境都能使用

![image-20240809180011982](https://p.ipic.vip/nn2sud.png)



##### Variables



| 名称                      | 描述                             | 示例                              |
| ------------------------- | -------------------------------- | --------------------------------- |
| REPO_NAME                 | 项目名称, 在ci_cd.yaml文件中使用 | wristcheck_api                    |
| ALIYUN_CONTAINER_REGISTRY | 阿里云容器服务地址               | registry.cn-hangzhou.aliyuncs.com |



##### Secrets



| 名称                      | 描述                                                         | 示例                                                         |
| ------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| ALIYUN_CONTAINER_USERNAME | 阿里云容器服务账号                                           | https://cr.console.aliyun.com/cn-hangzhou/instance/credentials |
| ALIYUN_CONTAINER_PASSWORD | 阿里云容器服务密码                                           | -                                                            |
| OSS_ACCESS_KEY_ID         | 具有访问阿里云OSS的ACCESS_ID                                 | -                                                            |
| OSS_ACCESS_KEY_SECRET     | 具有访问阿里云OSS的ACCESS_SECRET                             | -                                                            |
| SENTRY_DSN_URL            | 将报错信息发送到sentry方便后续排错, 在sentry官网创建一个project, platform选择Django即可 | https://1b5999f3b527314b18c4ffa17d0dfd0a@o413187.ingest.us.sentry.io/4507656363048960 |
| WECHAT_MINI_APPID         | 微信小程序身份标识APPID                                      | -                                                            |
| WECHAT_MINI_SECRET        | 微信小程序身份标识SECRET                                     | -                                                            |



## 4.最终结果



dev分支push代码触发Github Actions, 直接部署到staging环境的ECS上

main分支push代码触发Github Actions, 需要手动Review, 才能部署到prod环境的ECS上



![image-20240809175941177](https://p.ipic.vip/vjiffg.png)







部署完成后可以在portainer上查看服务的状态, 进行一些后续的管理和维护工作

![image-20240809175839956](https://p.ipic.vip/c6se08.png)