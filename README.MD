## bugs :
- anytime we find new items that added to store we should update `AdidasThread.Globals.gotten_items_list` items 
- (IMPORTANT) should find another way to check which items downloaded
- *****(IMPORTANT)(SOLUTION) at retrieve_preferences thread I should traverse items project_id until we reach first item that we have inside model_product_objects
    - first I should check , I need to get new reminder or not  ??????
- (IMPORTANT) create a mechanism  that while threads that  getting items gets an error, they could revert their procedure or we should surveillance gotten data after a scheduled time BUG-#10 
- (IMPORTANT) when check_preferences found uot new items has beed added to the store it should create a flag for main.py to prevent it to create new get_items thread and after all get_items thread finished it can update the data eg items_info and ...
## Changes : 
- `AdidasThread.Globals.gotten_items_list` changed to `AdidasThread.Globals.assigned_items_indices`

## Fixed
- (FIXED) we should store `AdidasThread.Globals.gotten_items_list` anytime we want to finish a job or at scheduled time 
- (FIXED)should move variables from `Settings` class to `Globals` class
