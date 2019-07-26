import hashlib
import time
import boto3

dynamodb = boto3.resource('dynamodb')
frontier = dynamodb.Table('crawler_frontier')
history = dynamodb.Table('item_history')

def save(catalog):
    with history.batch_writer() as batch:
        for key, item in catalog.items():
            hash = hashlib.sha256(('banggood' + item['id']).encode('utf-8')).hexdigest()
            print(hash)
            batch.put_item(Item={'item_hash': hash, 'date': str(item['date']), 'price':str(item['price']), 'url':item['uri']})
