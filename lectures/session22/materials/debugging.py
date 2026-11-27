temperatures = [25, 30, 37, 45, 60]  # temperature in C
yields = [41, 58, 87, 72, 35]  # yield in %

best_yield = 0
best_temp = 0

for i in range(len(temperatures)):
    if yields[i] > best_yield:
        best_yield = yields[i]
    best_temp = temperatures[i]

print("Best temperature:", best_temp, "C")
print("Yield at that temperature:", best_yield, "%")
