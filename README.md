# 🎯 Secure Online Bidding System

A secure online bidding system that uses **RSA cryptography** for bidder authentication and digital signatures, ensuring the integrity and security of bids. The system implements a **proxy bidding mechanism** to automate bid increments and declares the winner at the end of the bidding process.

---

## 🚀 **Features**

### 🔐 Bidder Registration with RSA Public Key
- Each bidder generates a unique **2048-bit RSA key pair**.
- Public key is sent to the server for registration.
- Bidder receives a unique **bidder ID** upon successful registration.

### ✍️ Digital Signature for Bid Security
- Bids are digitally signed using the bidder's **private key**.
- Signature is generated using **SHA-256 hashing** and `pkcs1_15` signing.
- Prevents bid tampering and ensures data integrity.

### 🎲 Proxy Bidding Mechanism
- Automatically places bids based on a **random increment (100-500 units)**.
- Ensures the bid does not exceed the bidder’s maximum bid limit.
- Enables competitive bidding without manual intervention.

### 📡 Secure Client-Server Communication
- Bid requests and responses are transmitted using **TCP sockets**.
- Bid data is encoded in **JSON format** for efficient communication.

### 💰 Bid Placement & Verification
- Validates the authenticity of each bid using RSA signature verification.
- Only bids higher than the current highest bid are considered.

### 🏆 Winner Declaration
- Declares the winner by verifying the highest valid bid.
- Ensures transparency and fairness in determining the winning bidder.

### 🎮 Simulated Multi-Bidder Environment
- Supports multiple bidders with unique keys and randomized bid order.
- Enables **scalability** to handle numerous bidders simultaneously.

### 📧 Error Handling and Notifications
- Provides feedback on:
    - Registration success/failure.
    - Bid placement success/failure.
    - Winner announcement.

---

## 📚 **Technical Stack**

- **Language:** Python 3
- **Cryptography Library:** PyCryptodome (`RSA`, `SHA256`, `pkcs1_15`)
- **Socket Programming:** Python `socket` module
- **JSON for Data Exchange:** `json` module

---

