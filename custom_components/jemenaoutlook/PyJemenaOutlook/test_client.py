import asyncio
import csv
import time
from .jemena_client import JemenaOutlookClient
import logging
def read_secret(file_path):
    result_dict = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) == 2:
                key, value = row
                result_dict[key] = value
    return result_dict

async def test():
    logging.basicConfig(level=logging.DEBUG)
    # Example usage
    file_path = 'PyJemenaOutlook/secret.csv'
    secret = read_secret(file_path)

    client = JemenaOutlookClient(secret['username'], secret['password'])
    
    start_time = time.time()
    await client.fetch_data()
    end_time = time.time()

    print(client.get_data())
    print(client.get_raw_data())
    print(f"Time taken: {end_time - start_time} seconds")

asyncio.run(test())