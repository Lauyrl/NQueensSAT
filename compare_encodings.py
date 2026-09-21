from main import main

for N in [50, 100, 150, 200]:
    print("############################################################################")
    print("N: ", N)
    print()
    for encoding in ["commander", "binary"]: #, "sequential"
        print("Encoding: ", encoding)
        main(N, encoding, False)
        print()
        print()
