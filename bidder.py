import socket
import json
import random
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

PORT = 8080
SERVER_HOST = "127.0.0.1"


# ====================== Generate RSA Keys =========================
def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return private_key, public_key


# ====================== Sign Bid =========================
def sign_bid(private_key, message):
    key = RSA.import_key(private_key)
    hashed_msg = SHA256.new(message.encode())
    signature = pkcs1_15.new(key).sign(hashed_msg)
    return signature.hex()


# ====================== Send Request to Server =========================
def send_request(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, PORT))
    request = json.dumps(data)
    client_socket.sendall(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response


# ====================== Register Bidders =========================
def register_bidders(num_bidders):
    bidder_keys = {}

    for i in range(1, num_bidders + 1):
        private_key, public_key = generate_keys()

        # Send registration request
        data = {"action": "REGISTER", "bidder_num": str(i), "public_key": public_key}
        response = send_request(data)

        if "REG_SUCCESS" in response:
            bidder_id = response.split(" ")[1]
            bidder_keys[bidder_id] = private_key
            print(f"✅ Registration Successful for Bidder {i} with ID: {bidder_id}")
        else:
            print(f"❌ Registration Failed for Bidder {i}")

    return bidder_keys


# ====================== Proxy Bidding Mechanism =========================
def proxy_bid(current_highest, max_bid):
    """Returns the next bid amount based on proxy bidding rules."""
    increment = random.randint(100, 500)  # Random increment between 100 and 500
    next_bid = current_highest + increment

    if next_bid > max_bid:
        return max_bid
    return next_bid


# ====================== Place Bids =========================
def place_bids(bidder_keys, max_bids):
    current_highest = 100  # Initial minimum bid to start

    # Shuffle bidder order to make bidding fair
    shuffled_bidders = list(bidder_keys.keys())
    random.shuffle(shuffled_bidders)

    for bidder_id in shuffled_bidders:
        max_bid = max_bids[bidder_id]
        bid_amount = proxy_bid(current_highest, max_bid)

        # Only place bid if it's higher than the current highest
        if bid_amount > current_highest:
            current_highest = bid_amount  # Update highest bid

            private_key = bidder_keys[bidder_id]
            message = f"{bidder_id}:{bid_amount}"
            signature = sign_bid(private_key, message)

            # Send bid
            data = {
                "action": "BID",
                "bidder_id": bidder_id,
                "bid_amount": str(bid_amount),
                "signature": signature,
            }
            response = send_request(data)

            if "BID_SUCCESS" in response:
                print(
                    f"✅ Bid Placed Successfully by Bidder {bidder_id} with Amount: {bid_amount}"
                )
            else:
                print(f"❌ Bid Failed for Bidder {bidder_id}")


# ====================== Request Winner =========================
def request_winner():
    data = {"action": "WINNER"}
    response = send_request(data)
    print(response)


# ====================== Main =========================
if __name__ == "__main__":
    num_bidders = int(input("Enter the number of bidders: "))

    # Register Bidders
    bidder_keys = register_bidders(num_bidders)

    if not bidder_keys:
        print("❌ No Bidders Registered. Exiting...")
        exit()

    # Simulate Random Maximum Bidding for Each Registered Bidder
    max_bids = {}
    for i, bidder_id in enumerate(bidder_keys.keys()):
        max_bids[bidder_id] = random.randint(500, 10000)  # Random max bid

    # Place bids with randomized order and adjusted logic
    place_bids(bidder_keys, max_bids)

    # Request Winner
    request_winner()
