# Medichain: A Blockchain Counterfeit Medicine Detector

> The goal? To simulate how blockchain can be used to detect counterfeit medicine in a supply chain. No Ethereum, no fancy frameworks — just pure logic, code, and a drive to solve something real.

## The Problem

Fake medicine kills people.

And a lot of the time, no one even realizes when something in the supply chain has been tampered with.

So I asked myself:
**Can I build something that makes it obvious — even impossible — to mess with medicine data without being caught?**

This project is my answer to that.

## What I’m Building

This is a custom blockchain built in Python from scratch.

* Each block holds real-looking medicine batch info (like ID, manufacturer, expiry, etc.).
* Each block is cryptographically linked to the one before it using a SHA-256 hash.
* If **anything** is tampered with, the chain breaks and the system throws a flag.

I’m also adding a simple HTML/CSS interface later to view/submit medicine data.

## Tech Stack

* **Core Logic:** Python 3
* **Hashing:** SHA-256 (via `hashlib`)
* **Frontend (Planned):** HTML/CSS
* **API (Maybe):** Flask

## Project Roadmap

* [x] Start the repo and commit my "why"
* [ ] Build the `Block` and `Blockchain` classes from scratch
* [ ] Add hashing + tamper detection logic
* [ ] Store & simulate medicine batch data
* [ ] Optional UI: make a simple web viewer for blocks
* [ ] Final walkthrough + README polish

## How to Run (Developer Guide)

This project is in active development. To run the backend logic:

1.  Clone the repository:
    ```bash
    git clone [https://github.com/rajeev-bhardwajsharma/blockchain_counterfeit_detector.git](https://github.com/rajeev-bhardwajsharma/blockchain_counterfeit_detector.git)
    cd blockchain_counterfeit_detector/medledger_backend
    ```

2.  (Recommended) Create a virtual environment:
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  Run the main script (once available):
    ```bash
    python blockchain.py
    ```

## A Note from the Developer

Hi, I’m Rajeev Sharma  a CS student who tends to overthink, sometimes freeze, but still shows up anyway.

If you scroll through this later:
You’ll see raw logic, not just libraries. You'll see comments, breakdowns, decisions — everything I understood. You'll see a few intentional mistakes and corrections too — because I’m here to learn, not just impress.

This project is part of a larger journey where I’m learning how to push past fear, build cool stuff, and actually finish things that matter.

If you're reading this, thanks for being a part of that.
