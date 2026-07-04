def calculate_average(numbers):
    if not numbers:
        return 0
    total = sum(numbers)
    return total / len(numbers)

if __name__ == '__main__':
    print(calculate_average([]))
