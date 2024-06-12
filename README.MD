## bugs :
- anytime we find new items that added to store we should update `AdidasThread.Globals.gotten_items_list` itmes 
- (FIXED) we should save `AdidasThread.Globals.gotten_items_list` anytime we want to finish a job or at scheduled time 
- should move variables from `Settings` class to `Globals` class




## Changes : 
- `AdidasThread.Globals.gotten_items_list` changed to `AdidasThread.Globals.assigned_items_indices`