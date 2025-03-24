import socket
import threading
import random
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

PORT = 8080
registered_bidders = {}  # BidderID → PublicKey
bids = {}  # BidderID → Current Bid Amount
proxy_bids = {}  # BidderID → Max Bid Amount


# ====================== Digital Signature Utilities =========================
def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key


def sign_bid(private_key, message):
    key = RSA.import_key(private_key)
    hashed_msg = SHA256.new(message.encode())
    signature = pkcs1_15.new(key).sign(hashed_msg)
    return signature.hex()


def verify_bid(public_key, message, signature):
    key = RSA.import_key(public_key)
    hashed_msg = SHA256.new(message.encode())
    try:
        pkcs1_15.new(key).verify(hashed_msg, bytes.fromhex(signature))
        return True
    except (ValueError, TypeError):
        return False


# ====================== Send Message to Client =========================
def send_to_client(client_socket, message):
    client_socket.sendall(message.encode())
    client_socket.close()


# ====================== Register Bidder =========================
def register_bidder(bidder_num, public_key_str):
    bidder_id = str(random.randint(100, 999))
    registered_bidders[bidder_id] = public_key_str
    print(f"✅ Registration Successful for Bidder {bidder_num} with ID: {bidder_id}")
    return bidder_id


# ====================== Receive and Process Bids =========================
def receive_bid(bidder_id, bid_amount_str, signature):
    if bidder_id not in registered_bidders:
        return False, "❌ Invalid Bidder ID!"

    # Verify digital signature
    message = f"{bidder_id}:{bid_amount_str}"
    public_key = registered_bidders[bidder_id]
    if not verify_bid(public_key, message, signature):
        return False, "❌ Invalid Bid Signature!"

    bid_amount = int(bid_amount_str)

    # Check proxy bidding
    if bidder_id in proxy_bids and proxy_bids[bidder_id] >= bid_amount:
        bids[bidder_id] = bid_amount
        print(f"✅ Proxy Bid Updated from Bidder ID: {bidder_id} for {bid_amount}")
    else:
        bids[bidder_id] = bid_amount
        print(f"✅ Bid Received from Bidder ID: {bidder_id} with Amount: {bid_amount}")

    return True, "BID_SUCCESS"


# ====================== Proxy Bidding =========================
def set_proxy_bid(bidder_id, max_bid):
    proxy_bids[bidder_id] = max_bid
    print(f"🤖 Proxy Bid Set for Bidder ID: {bidder_id} with Max Bid: {max_bid}")
    return "PROXY_SUCCESS"


# ====================== Find Winner =========================
def find_winner():
    highest_bid = 0
    winner_id = ""

    for bidder_id, bid_amount in bids.items():
        if bid_amount > highest_bid:
            highest_bid = bid_amount
            winner_id = bidder_id

    return winner_id, highest_bid


# ====================== Announce Winner =========================
def announce_winner():
    winner_id, highest_bid = find_winner()
    if winner_id:
        print(
            f"🏆 Highest bid from Bidder ID: {winner_id} with highest bid: {highest_bid}"
        )
        print("✅ Winner Verified! Secure Auction Completed.")
        return f"BID_WINNER {winner_id} with Amount {highest_bid}"
    else:
        return "❌ No Valid Bids Received!"


# ====================== Handle Client Requests =========================
def handle_client(client_socket):
    request = client_socket.recv(4096).decode()

    try:
        data = json.loads(request)
        action = data.get("action")

        if action == "REGISTER":
            public_key_str = data["public_key"]
            bidder_num = data["bidder_num"]
            bidder_id = register_bidder(bidder_num, public_key_str)
            send_to_client(client_socket, f"REG_SUCCESS {bidder_id}")

        elif action == "BID":
            bidder_id = data["bidder_id"]
            bid_amount_str = data["bid_amount"]
            signature = data["signature"]
            success, message = receive_bid(bidder_id, bid_amount_str, signature)
            send_to_client(client_socket, message)

        elif action == "PROXY_BID":
            bidder_id = data["bidder_id"]
            max_bid = int(data["max_bid"])
            message = set_proxy_bid(bidder_id, max_bid)
            send_to_client(client_socket, message)

        elif action == "WINNER":
            message = announce_winner()
            send_to_client(client_socket, message)

        else:
            send_to_client(client_socket, "INVALID_ACTION")

    except Exception as e:
        send_to_client(client_socket, f"ERROR: {str(e)}")


# ====================== Main Server =========================
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
    print(f"🚀 Server listening on port {PORT}...")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
