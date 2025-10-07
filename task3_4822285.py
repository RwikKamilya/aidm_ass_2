import hashlib
import statistics


class FlajoletMartin:
    def __init__(self, num_hashes=10):
        self.max_trailing_zeros = [0] * num_hashes

    def hash_function(self, item, seed):
        """Hash the given item using SHA-256 and return an integer."""
        item_seeded = f"{seed}-{item}"
        hash_object = hashlib.sha256(item_seeded.encode())
        hash_value = int(hash_object.hexdigest(), 16)
        return hash_value

    def count_trailing_zeros(self, x):
        """Count the number of trailing zeros in the binary representation of a number."""
        binary_representation = bin(x)[2:]
        try:
            trailing_zeros_count = binary_representation[::-1].index('1')
        except ValueError:
            trailing_zeros_count = 0
        return trailing_zeros_count

    def add(self, item):
        """Add a new item to the estimator and update the maximum trailing zeros."""
        for i in range(len(self.max_trailing_zeros)):
            hash_value = self.hash_function(item, i)
            trailing_zeros_count = self.count_trailing_zeros(hash_value)
            if trailing_zeros_count > self.max_trailing_zeros[i]:
                self.max_trailing_zeros[i] = trailing_zeros_count


    def estimate_number(self):
        """Estimate the number of distinct elements by taking the median from multiple hashes."""
        median_trailing_zeros = statistics.median(self.max_trailing_zeros)
        estimated_number = 2 ** median_trailing_zeros / 0.75351
        return estimated_number, median_trailing_zeros


if __name__ == "__main__":
    fm = FlajoletMartin(num_hashes=20)
    unique_elements = [f"element-{i}" for i in range(100000)]

    for element_id, element in enumerate(unique_elements, start=1):
        if element_id % 1000 == 0:
            print(f"Finished processing {element_id}/{len(unique_elements)} elements")
        fm.add(element)

    estimate, median_R = fm.estimate_number()
    print(f"Median R: {median_R}")
    print(f"Estimated Cardinality: {estimate}")
