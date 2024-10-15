import random
import hashlib
import time
import datetime


class Block:
    def __init__(self, index, previous_hash, transactions, timestamp, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.timestamp = datetime.datetime.now()
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined with hash: {self.hash}")


class BlockchainPoWPoS:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.stakeholders = {}  # PoS: stakeholders holding coins
        self.ejected_miners = set()  # Track ejected malicious miners
        self.backup_chain = []  # Backup to restore the chain in case of malicious activity

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block", time.time())

    def get_last_block(self):
        return self.chain[-1]

    def add_stakeholder(self, miner_id, stake):
        """ Add a stakeholder with a given stake (amount of cryptocurrency) """
        if miner_id not in self.ejected_miners:  # Only allow if not ejected
            self.stakeholders[miner_id] = stake
        else:
            print(f"{miner_id} is ejected and cannot rejoin the network.")

    def select_validator(self):
        """ Select validator based on stake """
        total_stake = sum(self.stakeholders.values())
        validator_weights = {
            miner: stake / total_stake for miner, stake in self.stakeholders.items()}

        # Select validator based on weighted random choice
        validator = random.choices(list(validator_weights.keys()), list(
            validator_weights.values()), k=1)[0]
        return validator

    def add_block(self, transactions):
        """ Add block using PoW + PoS hybrid """
        validator = self.select_validator()

        # Backup current chain state before adding new block
        self.backup_chain = self.chain.copy()

        new_block = Block(
            len(self.chain), self.get_last_block().hash, transactions, time.time())
        print(f"Mining initiated by validator: {validator}")
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

        # Check for malicious behavior after adding block
        self.check_for_malicious_activity(validator)
        return validator

    def is_chain_valid(self):
        """ Check if the blockchain is valid """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def detect_malicious_activity(self):
        """ Detect if any miner has tampered with a block """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return True  # Tampering detected
        return False

    def eject_malicious_miner(self, miner_ids):
        """ Eject the malicious miner(s) by removing their stake """
        for miner_id in miner_ids:
            print(f"\n--- Ejecting malicious miner: {miner_id} ---")
            if miner_id in self.stakeholders:
                del self.stakeholders[miner_id]  # Remove their stake
                self.ejected_miners.add(miner_id)  # Add to ejected list
                print(f"Miner {miner_id} has been ejected from the network.")

    def restore_blockchain(self):
        """ Restore the blockchain to its original valid state """
        print("\n--- Restoring blockchain to original valid state ---")
        self.chain = self.backup_chain  # Restore from backup
        print("Blockchain successfully restored.")

    def simulate_51_attack(self, malicious_miners):
        """ Simulate the malicious miners attempting to rewrite the blockchain """
        print(f"\n--- Simulating 51% Attack by {malicious_miners} ---")

        # Malicious miners attempt to tamper with the last block
        last_block = self.get_last_block()
        fake_block = Block(
            last_block.index, last_block.previous_hash, "Fake Transactions", time.time())

        print(
            f"Malicious miners {malicious_miners} trying to rewrite block {last_block.index}")
        fake_block.mine_block(self.difficulty)

        # If attack succeeds, replace the last block
        if fake_block.hash[:self.difficulty] == '0' * self.difficulty:
            self.chain[-1] = fake_block  # Replace last block with fake block
            print(f"Malicious block replaced: {fake_block.hash}")

            # Check for tampering after replacing block
            self.check_for_malicious_activity(', '.join(malicious_miners))
        else:
            print(f"Malicious attempt failed to meet the difficulty criteria.")

    def check_for_malicious_activity(self, validator):
        """ Check if the validator (or any miner) has tampered with the blockchain """
        if self.detect_malicious_activity():
            print(f"Malicious activity detected from {validator}.")
            self.restore_blockchain()  # Restore the blockchain to its valid state
        else:
            print(
                f"No malicious activity detected after block mined by {validator}.")


# print blockchain
def print_blockchain(hybrid_blockchain):
    print("\n-------- Blockchain --------")
    for block in hybrid_blockchain.chain:
        print(f"Block {block.index} {block.hash}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Transactions: {block.transactions}")
        print(f"Previous Hash: {block.previous_hash}")
        print(f"Nonce: {block.nonce}\n")


# --- Simulation ---
# Create the PoW + PoS Blockchain
hybrid_blockchain = BlockchainPoWPoS()

# Add 10 stakeholders (miners) with different stakes
for i in range(1, 11):
    hybrid_blockchain.add_stakeholder(f"Miner_{i}", random.randint(10, 100))

# Print initial stakeholders
print("\nInitial Stakeholders:")
for miner, stake in hybrid_blockchain.stakeholders.items():
    print(f"{miner}: {stake} coins")

# Simulate the creation of blocks
for i in range(3):
    print(f"\n--- Mining Block {i+1} ---")
    validator = hybrid_blockchain.add_block(
        f"Transaction Data for Block {i+1}")
    print(f"Block {i+1} was validated by {validator}")

# Check blockchain validity before attack
print("\nBlockchain valid before attack:", hybrid_blockchain.is_chain_valid())

# Select a random subset of miners and pool their stakes
subset_size = random.randint(4, 6)  # Randomly select 3 to 6 miners
malicious_miners = random.sample(
    list(hybrid_blockchain.stakeholders.keys()), subset_size)
pooled_stake = sum([hybrid_blockchain.stakeholders[miner]
                   for miner in malicious_miners])

# Check if pooled stake is majority (>50% of total stake)
total_stake = sum(hybrid_blockchain.stakeholders.values())
print(f"\nSelected malicious miners: {malicious_miners}")
print(f"Pooled stake: {pooled_stake} coins (Total stake: {total_stake} coins)")

if pooled_stake > total_stake / 2:
    print(f"\n--- Pooled stake is a majority ---")
    hybrid_blockchain.simulate_51_attack(malicious_miners)
    # Eject malicious miners if attack occurred and print status
    if pooled_stake > total_stake / 2:
        hybrid_blockchain.eject_malicious_miner(malicious_miners)
        print("\nBlockchain valid after ejecting malicious miners:",
            hybrid_blockchain.is_chain_valid())

    # Restore the blockchain if necessary
    if pooled_stake > total_stake / 2:
        hybrid_blockchain.restore_blockchain()

    # Re-mine the block after restoration
    print("\n--- Re-mining Block after restoration ---")
    validator = hybrid_blockchain.add_block(
        "New Transaction Data after Restoration")
    print(f"New Block was validated by {validator}")
else:
    print("\n--- Pooled stake is not a majority, no attack simulated ---")


# Call the function to print the final blockchain
print_blockchain(hybrid_blockchain)
