# Set up a fake data set with legal bank account numbers and a fake data set with illegal bank account numbers.
from hashlib import sha256
import numpy as np
import functools


def create_hash_functions(num_hash_functions, size_bit_array):
    """Create a list of runnable hash functions.
    It is important to use lambda functions to create the hash functions.

    Args:
        num_hash_functions (Int): The number of hash functions to create.
        size_bit_array (Int): The size of the bit array.

    Returns:
        list[lambda]: A list containing the hash functions.
    """
    hash_functions = []
    for i in range(num_hash_functions):
        hash_functions.append(
            (lambda index=i: (
                lambda x: int(sha256(f"hash_function_index_{index}_bank_account_{x}".encode()).hexdigest(),
                              16) % size_bit_array))())
    return hash_functions


def add_to_bloom_filter(bloom_filter, hash_functions, bank_account):
    """This function should set the bits in the bloom filter to 1 for each 
    hash function for the given bank account.

    Args:
        bloom_filter (list[int]): The bit array to set the bits in.
        hash_functions (list[lambda]): The hash functions to use.
        bank_account (str): The bank account to add to the bloom filter.

    Returns:
        list[int]: The updated bloom filter.
    """
    for custom_hash in hash_functions:
        bloom_filter[custom_hash(bank_account)] = 1
    return bloom_filter


def check_bloom_filter(bloom_filter, hash_functions, bank_account):
    """This function should check if the bank account is in the bloom filter.

    Args:
        bloom_filter (list[int]): The bit array to check.
        hash_functions (list[lambda]): The hash functions to use.
        bank_account (str): The bank account to check.

    Returns:
        bool: True if the bank account is in the bloom filter, False otherwise.
    """

    for custom_hash in hash_functions:
        if bloom_filter[custom_hash(bank_account)] != 1:
            return False
    return True


# if __name__ == '__main__':
#     hash_functions = create_hash_functions(3, 10)
#     print([f("abc") for f in hash_functions])

# if __name__ == "__main__":
#     # This section can be used to debug your submission
#
#     nr_bank_accounts = 100_000
#     # nr_bank_accounts = 10
#
#     # Create a list of legal bank account numbers
#     real_bank_accounts = ["real" + str(i) for i in range(nr_bank_accounts)]
#
#     # Set up the Bloom filter as an array 8 times as big as the number of bank accounts
#     bloom_filter = [0] * 8 * nr_bank_accounts
#     # Experiment with 2 hash functions (try raising it to 30)
#     # hash_functions = create_hash_functions(2, 8*nr_bank_accounts)
#     hash_functions = create_hash_functions(2, 8 * nr_bank_accounts)
#     # Enter all valid account numbers
#     for account in real_bank_accounts:
#         add_to_bloom_filter(bloom_filter, hash_functions, account)
#
#     # print(bloom_filter)
#
#     # Calculate the false positive rate
#     fake_bank_accounts = ["fake" + str(i) for i in range(nr_bank_accounts)]
#     false_positives = 0
#     for fake_account in fake_bank_accounts:
#         if check_bloom_filter(bloom_filter, hash_functions, fake_account):
#             false_positives += 1
#     print(f"False positive rate: {false_positives / nr_bank_accounts}")
#
#     print("Fraction of bits set: ", np.sum(bloom_filter) / (nr_bank_accounts * 8))
#
#     print("Is real12345 a valid account number?", check_bloom_filter(bloom_filter, hash_functions, "real12345"))
#     print("Is real123456 a valid account number?", check_bloom_filter(bloom_filter, hash_functions, "real123456"))
#     print("Is 12345 a valid account number?", check_bloom_filter(bloom_filter, hash_functions, "12345"))

def expected_fpr(k: int, n: int, N: int) -> float:
    return float((1.0 - np.exp(-k * n / N)) ** k)


if __name__ == "__main__":

    nr_bank_accounts = 100_000
    N = 8 * nr_bank_accounts

    k_opt_float = (N / nr_bank_accounts) * np.log(2.0)
    k_opt = max(1, int(round(k_opt_float)))

    print("[INPUTS]")
    print(f"  n (real bank accounts): {nr_bank_accounts}")
    print(f"  N (bloom filter size): {N}")
    print(f"  k_opt (float): {k_opt_float:.3f} -> rounded: {k_opt}\n")

    real_bank_accounts = [f"real{i}" for i in range(nr_bank_accounts)]
    fake_bank_accounts = [f"fake{i}" for i in range(nr_bank_accounts)]

    print("[RUN] Start k=2..30")
    print(f"  Sample size(n): {nr_bank_accounts}, Bloom Filter Size: {N}\n")

    best_k = None
    best_fpr = 1.0

    # for k in range(2, 31):
    for k in range(2, 8):
        bloom = [0] * N
        custom_hash_functions = create_hash_functions(k, N)

        for real_bank_account in real_bank_accounts:
            add_to_bloom_filter(bloom, custom_hash_functions, real_bank_account)

        false_positives = 0
        for fake_bank_account in fake_bank_accounts:
            if check_bloom_filter(bloom, custom_hash_functions, fake_bank_account):
                false_positives += 1
        fpr_meas = false_positives / len(fake_bank_accounts)
        fpr_exp = expected_fpr(k, nr_bank_accounts, N)
        frac_bits_set = float(np.sum(bloom)) / N
        is_tpr_ok = all(check_bloom_filter(bloom, custom_hash_functions, acc) for acc in real_bank_accounts)

        print(
            f"[RUN] k={k:2d} | bits_set={frac_bits_set:.3f} | "
            f"FPR_meas={fpr_meas:.6f} vs FPR_exp={fpr_exp:.6f} | "
            f"TPR==1? {is_tpr_ok}"
        )

        if fpr_meas < best_fpr:
            best_fpr = fpr_meas
            best_k = k
            print(f"         ↳ New best: k={best_k} with FPR_meas={best_fpr:.6f}")

    print("\n[RUN] Done.")
    print(f"  Theoretical k_opt (rounded): {k_opt}")
    print(f"  Best empirical k in [2..30]: {best_k} (FPR_meas ≈ {best_fpr:.6f})")

    k_final = best_k
    print("\n[FINAL] Build with empirical k_opt on full dataset")
    print(f"  Using k={k_final}, N={N}, n={nr_bank_accounts}")

    bloom_filter = [0] * N
    hash_functions = create_hash_functions(k_final, N)

    step = max(1, nr_bank_accounts // 10)
    for account_index, real_account in enumerate(real_bank_accounts, 1):
        add_to_bloom_filter(bloom_filter, hash_functions, real_account)
        if account_index % step == 0 or account_index == nr_bank_accounts:
            print(f"  Inserted {account_index}/{nr_bank_accounts} ({account_index / nr_bank_accounts:.0%})")

    false_positives = 0
    for fake_account in fake_bank_accounts:
        if check_bloom_filter(bloom_filter, hash_functions, fake_account):
            false_positives += 1
    fpr_meas_final = false_positives / nr_bank_accounts
    fpr_exp_full = expected_fpr(k_final, nr_bank_accounts, N)

    frac_bits_set_full = float(np.sum(bloom_filter)) / N
    tpr_ok_final = all(
        check_bloom_filter(bloom_filter, hash_functions, acc)
        for acc in real_bank_accounts[:min(10_000, nr_bank_accounts)]
    )

    print("\n[FINAL] Results")
    print(f"  k used: {k_final}")
    print(f"  FPR_meas={fpr_meas_final:.6f} vs FPR_exp={fpr_exp_full:.6f} ")
    print(f"  Fraction of bits set: {frac_bits_set_full:.6f}")
    print(f"  TPR==1? {tpr_ok_final}\n")

    print("[QUERIES]")
    print("  Is real12345 a valid account number?",
          check_bloom_filter(bloom_filter, hash_functions, "real12345"))
    print("  Is real123456 a valid account number?",
          check_bloom_filter(bloom_filter, hash_functions, "real123456"))
    print("  Is 12345 a valid account number?",
          check_bloom_filter(bloom_filter, hash_functions, "12345"))
