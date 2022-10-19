"""
Read 3 numbers from the user
and print their total sum
"""

print ("Type in 3 numbers:")
x = input()
y = input()
z = input()

total = float(x) + float(y) + float(z)

print (f"Sum of the numbers is:  {total}")
######################################################################################################

# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")



import re
#S="We test coders. Give us a try?im a  hero! you"
S="Forget  CVs..Save time . x x"
def solution(S):
    max=0
    sentences=re.split('\.|\?|\!',S)
    # write your code in Python 3.6
    print (f"sentences")
    for i in sentences:
        words =re.split(' ',i)
        num_of_words=0
        for j in words:
            if not j:
                pass
            else:
                num_of_words +=1
        if num_of_words > max:
            max = num_of_words
        print (f"{words}")
        print (f"{num_of_words}")
    print (f"max is:  {str(max)}")
        
    pass

solution(S)