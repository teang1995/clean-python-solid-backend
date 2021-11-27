import jwt

data_to_encode = {"some": "payload"}
encryption_secret = 'secrete'
algorithm = 'HS256'
encoded = jwt.encode(data_to_encode, encryption_secret, algorithm)
print(encoded)
decoded = jwt.decode(encoded, encryption_secret, algorithms=[algorithm])
print(decoded)

'''
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb21lIjoicGF5bG9hZCJ9.j4hydZvraNFUqUHpXw0hYBN9qTRzbm9-yS9h5skNht0
{'some': 'payload'}

'''