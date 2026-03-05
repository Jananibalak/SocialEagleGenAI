"""
y=[1,2,'a','b']
print(y)

z=(5,6,7)

b={"num":5}

k={10,5,z}


print(z)

print(type(y))
print(type(z))
print(type(b))
print(type(k))
"""

"""
mark=int(input("enter mark"))
if mark >= 90:
    print("nighty")
elif mark >= 80:
    print("eighty")
else:
    print("FAIL")
"""
"""
for i in [1,5,6] :
    print(i)


for i in {1,5,6} :
    print(i)

for i in range(100,105) :
    print(i)
"""
"""
list1 = ['a','b','c']
list2 = [1,2]
dict = {}
len1=0
length=len(list1)
for j in range(0,length) :
    len1=j
    dict[j]=list1[j]
len1=len1+1
for k in list2 :
    dict[len1]=k
    len1=len1+1
print(dict)
"""

list = ["d","a","b","c"]
list.sort()
print(list)
list.reverse()
print(list)
list.remove("c")
print(list)
print(list.__sizeof__())
