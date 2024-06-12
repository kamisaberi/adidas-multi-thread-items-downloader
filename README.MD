## bugs :
- anytime we find new items that added to store we should update `AdidasThread.Globals.gotten_items_list` itmes 
- (IMPORTANT) should find another way to check which items downloaded 


## Changes : 
- `AdidasThread.Globals.gotten_items_list` changed to `AdidasThread.Globals.assigned_items_indices`

## Fixed
- (FIXED) we should store `AdidasThread.Globals.gotten_items_list` anytime we want to finish a job or at scheduled time 
- (FIXED)should move variables from `Settings` class to `Globals` class
