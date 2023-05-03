from random import Random

def getRanges(list):
    acc = 0
    ranges = []
    for i in list:
        ranges.append((acc, acc + i))
        acc += i

    return ranges
# fair random number generator
class FRand:
    def __init__(self, values, seed=None, incrementor=lambda x: x + 1, reset=lambda x: 0):
        self.seed = seed
        self.lastPicked = [1] * len(values)
        self.values = values
        self.incrementor = incrementor
        self.reset = reset

        if seed is None:
            self.random = Random()
        else:
            self.random = Random(seed)

    
    def next(self):
        # get the sum of the last picked values
        # the chance of picking a value is lastPicked[i]/sum(lastPicked)

        # we emulate this by creating a list of ranges
        # picking a random number between 0 and the sum of the values
        # and then finding the index of the range that the random number falls in

        # get the sum
        s = sum(self.lastPicked)

        ranges = getRanges(self.lastPicked)

        # pick a random number
        r = self.random.randint(0, s - 1)

        # increase all lastPicked values by a certain amount (defaulted to (+1))
        self.lastPicked = list(map(self.incrementor, self.lastPicked))

        # find the index of the range that the random number falls in
        for i, range in enumerate(ranges):
            if r >= range[0] and r < range[1]:
                self.lastPicked[i] = self.reset(self.lastPicked[i])
                return self.values[i]            
            

        # if we get here, something went wrong
        print("Error: random number not found in range")
        print("Random number: " + str(r))
        print("Ranges: " + str(ranges))
        print("sum: " + str(s))

        

if __name__ == "__main__":
    # test
    n = 5
    frand = FRand(list(range(n)), 1)
    frequencies = [0] * 5
    for i in range(1000):
        x = frand.next()
        print(x)
        frequencies[x] += 1

    print(frequencies)    
