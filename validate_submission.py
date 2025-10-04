import ast
import inspect
import pytest
from glob import glob
import re

allwed_nodes = (
    ast.FunctionDef,
    ast.ClassDef,
    ast.Import,
    ast.ImportFrom
)


def is_main_block(node):
    """
    Check if the given AST node is an if __name__ == "__main__": block.
    """
    if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
        if (
            isinstance(node.test.left, ast.Name) and
            node.test.left.id == "__name__" and
            len(node.test.ops) == 1 and
            isinstance(node.test.ops[0], ast.Eq) and
            len(node.test.comparators) == 1 and
            isinstance(node.test.comparators[0], ast.Constant) and
            node.test.comparators[0].value == "__main__"
        ):
            return True
    return False


def test_filename():
    pass

def get_filename():
    """
    Get the filenames of the student's tasks:
    task1_<7-digit-ID>.py, task2_<7-digit-ID>.py, task3_<7-digit-ID>.py
    """
    pattern = re.compile(r"^(task[1-3])_(\d{7})\.py$")

    # Scan all candidate files in a single pass
    task_files = {
        match.group(1): f
        for f in glob("task*_*.py")
        if (match := pattern.match(f))
    }

    # Required tasks
    required_tasks = ["task1", "task2", "task3"]

    # Check all required tasks exist
    missing = [t for t in required_tasks if t not in task_files]
    if missing:
        raise AssertionError(
            f"Missing files for tasks: {', '.join(missing)}. "
            "Files should be named taskX_<7-digit-StudentID without prefix 's'>.py"
        )

    # Check all IDs are the same
    student_ids = {pattern.match(task_files[t]).group(2) for t in required_tasks}
    if len(student_ids) != 1:
        raise AssertionError(
            f"Student IDs do not match across files: {', '.join(task_files[t] for t in required_tasks)}"
        )

    print("Found files:")
    for t in required_tasks:
        print(f"{t}: {task_files[t]}")

    # Return ordered list of filenames
    return [task_files[t] for t in required_tasks]

def test_code_outside_functions():
    """
    This function checks that there is no code outside of functions or classes.
    """
    filenames = get_filename()
    
    for filename in filenames:
        with open(filename, "r") as f:
            student_module = f.read()

        tree = ast.parse(student_module)

        for node in tree.body:
            if not isinstance(
                node,
                allwed_nodes
            ):
                # Check if this is the if __name__ == "__main__": block
                if is_main_block(node):
                    continue

                raise AssertionError(
                    f"Code found outside of functions or classes in {filename} at line number: "
                    f"{node.lineno}"
                )


def test_function_signatures():
    """
    This function checks that the function signatures match the expected ones.
    """
    filenames = get_filename()
    
    # Define expected signatures for each task
    expected_signatures_by_task = {
        "task1": {
            "mock_datastream": [],
            "reservoir_sampling": ["k", "datastream"],
        },
        "task2": {
            "create_hash_functions": [
                "num_hash_functions",
                "size_bit_array",
            ],
            "add_to_bloom_filter": [
                "bloom_filter",
                "hash_functions",
                "bank_account"
            ],
            "check_bloom_filter": [
                "bloom_filter",
                "hash_functions",
                "bank_account"
            ],
        },
        "task3": {
            "FlajoletMartin.__init__": ["self", "num_hashes=10"],
            "FlajoletMartin.hash_function": [
                "self",
                "item",
                "seed"
            ],
            "FlajoletMartin.count_trailing_zeros": ["self", "x"],
            "FlajoletMartin.add": ["self", "item"],
            "FlajoletMartin.estimate_number": ["self"]
        }
    }

    for filename in filenames:
        # Extract task number from filename (e.g., "task1_<studentnumber>.py" -> "task1")
        task_name = filename.split('_')[0]

        if task_name not in expected_signatures_by_task:
            continue
            
        student = __import__(filename.strip(".py"))
        expected_signatures = expected_signatures_by_task[task_name]

        for func_name, expected_params in expected_signatures.items():
            if '.' in func_name:
                class_name, method_name = func_name.split('.')
                func = getattr(student, class_name).__dict__[method_name]
            else:
                func = getattr(student, func_name)

            sig = inspect.signature(func)
            params = [str(param) for param in sig.parameters.values()]

            assert params == expected_params, (
                f"Function '{func_name}' in {filename} has incorrect signature. "
                f"Expected: {expected_params}, Found: {params}"
            )

if __name__ == "__main__":
    pytest.main([__file__])
