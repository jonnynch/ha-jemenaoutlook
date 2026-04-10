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
    logging.basicConfig(level=logging.INFO)
    # Example usage
    file_path = 'PyJemenaOutlook/secret.csv'
    secret = read_secret(file_path)

    client = JemenaOutlookClient(secret['username'], secret['password'], secret['gmid'])
    response = await client.login()
    if not response.success:
        print("Login failed: ", response.error_code, response.error_message)
        print("Details: ", response.error_details)
        if response.tfa:
            await client.send_tfa()
            code = input("Enter your otp token: ")
            response = await client.submit_tfa(code)
            if response.success:
                client.gmid = response.gmid
                print("gmid: ", client.gmid)
            else:
                print("Login failed: ", response.error_code, response.error_message)
                print("Details: ", response.error_details)
    if response.success:
        start_time = time.time()
        await client.fetch_data(2)
        end_time = time.time()
    
        #print(client.get_data())
        #print(client.get_raw_data())
        print(f"Time taken: {end_time - start_time} seconds")

asyncio.run(test())