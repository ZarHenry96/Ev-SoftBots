import matplotlib.pyplot as plt
import pandas as pd
import sys

if len(sys.argv) == 1:
    print("Missing parameters! Usage: python experimentName,label ...")
    exit(1)

figure = plt.figure()
name = ""

for i in range(1, len(sys.argv)):
    input = sys.argv[i].split(",")
    exp_data = pd.read_csv(input[0]+"/bestSoFar/bestOfGen.txt", sep="\t\t", engine='python')
    plt.plot(exp_data["fitness"], label=input[1])
    name += ("-"+input[0])

plt.legend()

plt.xlabel("Generation")
plt.ylabel("Best fitness")

plt.show()

figure.savefig("comparison"+name+".pdf")