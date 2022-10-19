

def snake(num):
    flipflop = False
    count = 1
    for j in range(num): #raw
        for i in range(num): #col
            # if j==2:
            #     print("x")
            if j%2 == 1 and i == 0: #1 3 5
                print(f"\n{(num*(j+1)) - (i+1)} ", end='')
            elif j%2 == 1 and i != 0: #1 3 5
                print(f"{(num*(j+1)) - (i+1)} ", end='')
            elif j%2 == 0 and i == 0: #0 2 4
                print (f"\n{j*num + (i)} ", end='')
            elif j % 2 == 0 and i != 0:  # 0 2 4
                print(f"{j * num + (i)} ", end='')


snake(20)

# snake(3)
#
# 0 1 2
# 5 4 3
# 6 7 8

# snake(4)
#
# 0 1 2 3
# 7 6 5 4
# 8 9 10 11
# 15 14 13 12