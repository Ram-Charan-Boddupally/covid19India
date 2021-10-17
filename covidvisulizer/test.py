# This program prints Hello, world!
size = 1
data = "50"
array = list(map(int,list(data.split())))
peak = len(array)-1
for element in range(1,size):
    if array[element] > array[element-1]:
        if element+1 == size:
            peak = element
            break
        elif element < size:
            if array[element] > array[element+1]:
                    peak = element
                    break

print(peak)