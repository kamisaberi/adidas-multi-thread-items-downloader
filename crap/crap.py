

def print_progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + ('░' * (100 - int(percent)))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")





