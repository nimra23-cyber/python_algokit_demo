
from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    AssetCreateParams,
    AssetOptInParams,
    AssetTransferParams,
    PayParams,

)

# Client to connect to localnet
algorand = AlgorandClient.default_local_net()

# import dispenser from KMD
dispenser = algorand.account.dispenser()
print(dispenser.address)

#Create a wallet for the creator of the token
creator = algorand.account.random()
print(creator.address)

#Get account info about creator
print(algorand.account.get_information(creator.address))

#Send Algos
algorand.send.payment(
    PayParams(
        sender=dispenser.address,
        receiver=creator.address,
        amount=10_000_000
    )
)
print(algorand.account.get_information(creator.address))

#Create asset

sent_txn = algorand.send.asset_create(
    AssetCreateParams(
        sender=creator.address,
        total= 1000,
        asset_name="PAK-COIN",
        unit_name="PKC"
        
    )
)

asset_id= sent_txn["confirmation"]["asset-index"]
print(asset_id)

#Create receiver account
receiver_acct = algorand.account.random()
print(receiver_acct.address)


#error whithout opt-in

""" asset_transfer = algorand.send.asset_transfer(
    AssetTransferParams(
        sender=creator.address,
        receiver=receiver_acct.address,
        asset_id=asset_id,
        amount=10
    )
) """


#Opt-in

#1 fund receiver account

algorand.send.payment(
    PayParams(
        sender=dispenser.address,
        receiver=receiver_acct.address,
        amount=10_000_000
    )
)


#2 Optin to the asset 

# algorand.send.asset_opt_in(
#     AssetOptInParams(
#         sender=receiver_acct.address,
#         asset_id=asset_id
#     )
# )


print(algorand.account.get_information(receiver_acct.address))

#Atomic transfer

group_tx = algorand.new_group()

group_tx.add_asset_opt_in(
    AssetOptInParams(
        sender=receiver_acct.address,
        asset_id=asset_id
    )
)

group_tx.add_payment(
    PayParams(
        sender=receiver_acct.address,
        receiver=creator.address,
        amount= 1_000_000
    ))

group_tx.add_asset_transfer(
    AssetTransferParams(
        sender=creator.address,
        receiver=receiver_acct.address,
        asset_id=asset_id,
        amount=10
    )
)

group_tx.execute()

print(algorand.account.get_information(receiver_acct.address)['assets'][0]['amount'])
print(algorand.account.get_information(creator.address)['amount'])


