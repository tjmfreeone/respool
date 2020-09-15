## 简介
respool是一个基于Flask, redis开发的，提供多种抽样策略的对象池

## 特性
- 提供API，使用者可以通过http方式调用
- 易于扩展，目前本人已经实现了Random、Priority两种类型的pool，使用者可以根据自己的需要在poolhub下编写自己的pool类
- 基于redis

## 部署环境
python>=3.6、redis-py>=3.5.3、redis>=4.0.9

## 原理架构
![respool](https://github.com/taojinmin/MDimages/blob/master/respool-images/respool.jpg?raw=true)
