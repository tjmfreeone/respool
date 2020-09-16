from poolhub.ProxyPool import kuaidaili


if __name__ == "__main__":
    k = kuaidaili()
    k.keep_crawl_until_reach_capacity()
    print(k.proxy_list)
