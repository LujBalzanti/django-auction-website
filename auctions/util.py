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
    
    if highestBid != listing.highestBid:
        listing.highestBid = highestBid
        listing.save()
    
    return
        