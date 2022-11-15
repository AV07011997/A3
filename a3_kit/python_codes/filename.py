# Python3 code to demonstrate
# Get String after substring occurrence
# using partition()

# initializing string
test_string = "D:\\12345_HDFC_03.pdf"

# initializing split word
spl_word = '_'

# printing original string
print("The original string : " + str(test_string))

# printing split string
print("The split string : " + str(spl_word))

# using partition()
# Get String after substring occurrence
res = test_string.partition(spl_word)[2]

# print result
print("String after the substring occurrence : " + res)

