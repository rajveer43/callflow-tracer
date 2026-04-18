def leaf():
    return 1

def mid():
    return leaf() + 1

def root():
    return mid() + 1

if __name__ == "__main__":
    print(root())
