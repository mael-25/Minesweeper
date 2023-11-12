def loop(lst,d=0):
    if d < len(lst)-1:
        r = loop(lst,d+1)
        l = [[i]+t for i in range(lst[d]) for t in r]
        return l
    else:
        return [[x] for x in range(lst[d])]
    

print(loop([3,3,4]))
