# Print average of list, ignoring Nones
def avg(l):
    sum = 0
    count = 0
    for num in l:
        if num is None:
            continue
        sum += num
        count += 1
    return sum/count
