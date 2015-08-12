def getOLBullet(olType, num):
	olType = olType%2
	if(olType == 0):
		return str(num) + '. '
	elif(olType == 1):
		num = num % 52
		if(num < 26):
			return chr(num + ord('a'))  + '. '
		return chr(num + ord('A') - 26) + '. '

print getOLBullet(0, 1)
print getOLBullet(1, 17)