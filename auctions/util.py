from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def checkHighest(listing):
    bids = listing.bids.all()
    try:
        highestBid = float(listing.highestBid)
    except TypeError:
        return
        
    for bid in bids:
        if bid.amount > highestBid:
            highestBid = bid.amount
            listing.highestBid = highestBid
            listing.save()
    
    return
        
def checkLeadBidder(userBids, listing):
    for bid in userBids:
        if listing.highestBid == bid.amount:
            return True
    return False

