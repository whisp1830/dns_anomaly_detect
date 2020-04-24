import sys

if __name__ == "__main__":
    SIZE_HINT = 10000000

    fileNumber = 0
    with open(sys.argv[1], "rt") as f:
        while True:
            buf = f.readlines(SIZE_HINT)
            if not buf:
                # we've read the entire file in, so we're done.
                break
            outFile = open("output_file/part%d.txt" % fileNumber, "wt")
            outFile.writelines(buf)
            outFile.close()
            fileNumber += 1 