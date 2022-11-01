import redis

con = redis.Redis(host='127.0.0.1', port=6379, encoding='utf-8')
con.set('18209620368', 999, ex=10)
value = con.get('18209620368')
print(value)
