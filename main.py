from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    AssetCreateParams,
    AssetOptInParams,
    AssetTransferParams,
    PayParams,
)

# Client to connect to localnet
algorand = AlgorandClient.default_local_net()

# Import dispenser from KMD 
dispenser = algorand.account.dispenser()
print("Dispenser Address: ", dispenser.address)

# Create a wallet for the creator of the token
creator = algorand.account.random()
print("Creator Address: ",creator.address)

# Get account info about creator
print(algorand.account.get_information(creator.address))

# Fund creator address with algo
algorand.send.payment(
    PayParams(
        sender=dispenser.address,
        receiver=creator.address,
        amount=10_000_000
    )
)

# Check out the creator account changes after funding
print(algorand.account.get_information(creator.address))

# Create Algorand Standard Asset
sent_txn = algorand.send.asset_create(
    AssetCreateParams(
        sender=creator.address,
        total= 1000,
        asset_name="nameofasset",
        unit_name="NOA",
        manager=creator.address,
        clawback=creator.address,
        freeze=creator.address
    )
)

# Extracting the confirmation and asset index of the asset creation transaction to get asset ID
asset_id= sent_txn["confirmation"]["asset-index"]
print("Asset ID: ", asset_id)

# Create receiver account
receiver_acct = algorand.account.random()
print("Receiver Account: ", receiver_acct.address)

# showcase error whithout opt-in

'''
asset_transfer = algorand.send.asset_transfer(
    AssetTransferParams(
        sender=creator.address,
        receiver=receiver_acct.address,
        asset_id=asset_id,
        amount=10
    )
) 
'''

#----------------------------------------------------------
# Opt-in segment without atomic transfer

# 1 Fund receiver account
# algorand.send.payment(
#     PayParams(
#         sender=dispenser.address,
#         receiver=receiver_acct.address,
#         amount=10_000_000
#     )
# )


# 2 Optin to the asset 
# algorand.send.asset_opt_in(
#     AssetOptInParams(
#         sender=receiver_acct.address,
#         asset_id=asset_id
#     )
# )

# 3 Transfer the asset (Code above)
# ---------------------------------------------------------


# Fund receiver account
algorand.send.payment(
    PayParams(
        sender=dispenser.address,
        receiver=receiver_acct.address,
        amount=10_000_000
    )
)

print(algorand.account.get_information(receiver_acct.address))

# Atomic transfer segment - optin txn / payment txn / asset transfer txn

# Create a new transaction group
group_tx = algorand.new_group()

# Add an asset opt-in transaction to the group
group_tx.add_asset_opt_in(
    AssetOptInParams(
        sender=receiver_acct.address,  # The receiver's account opting in to the asset
        asset_id=asset_id               # The ID of the asset to opt in to
    )
)

# Add a payment transaction to the group
group_tx.add_payment(
    PayParams(
        sender=receiver_acct.address,   # The sender of the payment (receiver account)
        receiver=creator.address,       # The receiver of the payment (creator account)
        amount=1_000_000                # The amount to be paid (in microAlgos) = 1 algo
    ))

# Add an asset transfer transaction to the group
group_tx.add_asset_transfer(
    AssetTransferParams(
        sender=creator.address,         
        receiver=receiver_acct.address, 
        asset_id=asset_id,              
        amount=10                       
    )
)

# Execute the transaction group
group_tx.execute()

# Print the entire information from the Receiver Account
print(algorand.account.get_information(receiver_acct.address))

# Print the amount of the asset the receiver account holds after the transactions
print("Receiver Account Asset Balance:",algorand.account.get_information(receiver_acct.address)['assets'][0]['amount'])

# Print the remaining balance of the creator account after the transactions
print("Creator Account Balance:", algorand.account.get_information(creator.address)['amount'])
