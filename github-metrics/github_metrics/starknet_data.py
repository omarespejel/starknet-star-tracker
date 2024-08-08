from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import MAINNET

client = GatewayClient(MAINNET)

latest_block = client.get_block("latest")
latest_block_num = latest_block.block_number
print(f"Latest block number: {latest_block_num}")

new_class_hashes = set()

for block_num in range(latest_block_num, 0, -1):
    block = client.get_block(block_num)

    for tx in block.transactions:
        if hasattr(tx, "declare"):
            new_class_hashes.add(tx.declare.class_hash)

total_new_classes = len(new_class_hashes)
print(f"Total number of new class hashes deployed: {total_new_classes}")
