## 简介
respool是一个基于Flask, redis开发的，提供多种抽样策略，而且易于扩展的资源池

## 特性
- 提供API，使用者可以方便调用
- 易于扩展，目前本人已经实现了RandomPool、PriorityPool、ProxyPool3种类型的pool，使用者可以根据自己的需要在poolhub下编写自己的pool类, 
- 基于redis, 响应速度极快
- 提供config.ini, 可以快速调整配置

## 部署环境
python>=3.6、redis-py>=3.5.3、redis>=4.0.9、flask>=1.1.2

## 原理架构
![respool](https://github.com/taojinmin/MDimages/blob/master/respool-images/respool_V2.jpg?raw=true)

## 已实现的pool
  
  
### 1. RandomPool
每次调用返回一个随机的对象，如果开启了冷却池功能，这个对象将被收进冷却池等待指定的时间后再回到资源池内  
调用路由是“ https://ip:port/random ”
  
  
### 2. PriorityPool
每次调用也返回一个随机的对象，同时还有一个权重值score, 对象的score值越小，代表被抽取到的概率越小，可以通过请求“ https://ip:port/dec_weight?res=target_res ”来降低权重  
调用路由是“ https://ip:port/priority ”
  
### 3. ProxyPool
代理池，实现了自动抓取免费代理的功能，我们可以随机抽取这些代理来为自己的工作服务
  
### 4. API列表
| 路由 | 返回结果 | 返回示例 | 
| :-----: | :-----: | :----: |
| https://ip:port/random | 返回一个随机池抽取的资源 | { "res":"1a" }| 
| https://ip:port/priority | 返回一个权重池抽取的资源 | { "res":"1a","score":20.0 } |
| https://ip:port/proxy | 返回一个代理池抽取的代理 | { "ip":"123.149.XXX.XX", "port":"9999", "score":20.0} |
| https://ip:port/dec_weight?res={res} | 降低权重池里某资源的权重 | { "msg":"success" } | 
| https://ip:port/dec_proxy_weight?res={res} | 降低代理池中某代理的权重 | { "msg":"success" } |
| https://ip:port/pool_size?type={pool_type} | 获取某个池的资源数量 | { "pool_size":2 } |
