#python
# use '\a' to specify leaving the character out of the password
charlib = ['abc', 'DEF', 'ghi', '&*%', 'VDAFE', 'Kk', 'VAE', 'q', 'e', '123', '\aeE3', '!1lLIi']
print (charlib)
outfile = 'g:/wordlist.txt'

def makeWord(chars, its):
	word = list()
	for i in xrange(0, len(its), 1):
		temp = chars[i]
		j = its[i]
		ltr = temp[j]
		if ltr != '\a':
			word.append(ltr)
	
	#print word
	return ''.join(word)

def incIts(chars, its):
	for i in xrange(len(chars)-1, -1, -1):
		if its[i] == len(chars[i]) - 1:
			# reached max for that character, reset to 0 and increment the next character from the end
			if i == 0:
				break
			else:
				its[i] = 0
		else:
			its[i] = its[i] + 1
			break
	
	return its

iterators = []
maxcount = 1
for i in range(len(charlib)):
	iterators.append(0) 
	maxcount = maxcount * len(charlib[i])

print iterators
print maxcount

# iterators = [2, 1, 1, 1, 4, 2, 4, 1, 1, 2, 4, 4, 2]
words = list()
words.append(makeWord(charlib, iterators))
#print words

for i in xrange(1, maxcount, 1):
	incIts(charlib, iterators)
	words.append(makeWord(charlib, iterators))

#print words		

f = open(outfile, 'w')
for word in words:
	f.write(word + '\n')

f.close()

