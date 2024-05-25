import requests
from web3 import Web3
import time
import keyboard
from web3.exceptions import TransactionNotFound
from requests.exceptions import HTTPError
from tkinter import Tk, Label, Button, StringVar

# Set your Infura API key
infura_api_key = "c2740059c3de4bf1bac9ca8fa4bb4d70"

# Set your Ethereum node endpoint
sepolia_node_url = "https://sepolia.infura.io/v3/c2740059c3de4bf1bac9ca8fa4bb4d70"
#sepolia_node_url = "http://127.0.0.1:8551"
#sepolia_node_url = "http://52e3a41abba916788d0a83c42fcb023a95c8da42a17bf7477ba918ca5cf7138484d1dc6a5eb80fc985e2291a09639776f88289b7244256f3789557ab9952cdd0@127.0.0.1:8551"
web3 = Web3(Web3.HTTPProvider(sepolia_node_url))

# Set the minimum value for a large transaction (in Ether)
min_large_transaction_value = 10.0

# Function to check the transaction value
def is_large_transaction(transaction_hash):
    try:
        transaction = web3.eth.get_transaction(transaction_hash.hex())
    except TransactionNotFound:
        print(f"Transaction not found: {transaction_hash.hex()}")
        return False

    value_in_ether = web3.from_wei(transaction['value'], 'ether')
    return value_in_ether >= min_large_transaction_value

# Function to check transaction confirmation
def check_confirmation(transaction_hash, confirmations_required):
    receipt = None
    while receipt is None or receipt['blockNumber'] is None or \
          (web3.eth.block_number - receipt['blockNumber']) < confirmations_required:
        try:
            receipt = web3.eth.get_transaction_receipt(transaction_hash.hex())
        except TransactionNotFound:
            print(f"Receipt not found for transaction: {transaction_hash.hex()}")
            return False
        time.sleep(10)  # Adjust the sleep duration based on your needs

    return True

# Function to make sepolia blockchain request with exponential backoff
def make_sepolia_request():
    while True:
        try:
            # Make your sepolia blockchain request here
            latest_block = web3.eth.get_block('latest')
            pending_transactions = []

            for tx_hash in latest_block['transactions']:
                if web3.eth.get_transaction(tx_hash)['blockNumber'] is None:
                    pending_transactions.append(tx_hash.hex())

            
            # Process pending transactions
            for tx_hash in pending_transactions:
                if is_large_transaction(tx_hash):
                    print(f"Large transaction detected: {tx_hash}")

                    # Set the number of confirmations required
                    confirmations_required = 6  # Adjust this based on your requirements

                    # Wait for the specified number of confirmations
                    while not check_confirmation(tx_hash, confirmations_required):
                        time.sleep(10)

                    print(f"Large Transaction Confirmed: {tx_hash}")

        except HTTPError as e:
            if e.response.status_code == 429:
                # If it's a rate limit error, wait for an increasing amount of time
                wait_time = 2 ** len(errors)  # Exponential backoff
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds.")
                time.sleep(wait_time)
                errors.append(e)
            else:
                # If it's a different error, raise it again
                raise

# Function to run Tkinter GUI
def run_gui():
    root = Tk()
    root.title("Sepolia Ethereum Classic Large Transaction Detector")

    global large_transactions_var
    large_transactions_var = StringVar()
    large_transactions_var.set("Large Transactions: None")

    label = Label(root, textvariable=large_transactions_var)
    label.pack()

    def update_gui():
        make_sepolia_request()
        root.after(5000, update_gui)  # Update every 5 seconds

    update_gui()
    root.mainloop()

errors = []
run_gui()