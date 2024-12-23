# SIC/XE Assembler (System Software Final Project)

This project is an implementation of an assembler for the SIC/XE machine architecture. The assembler translates assembly language programs into machine code that can be executed by the SIC/XE machine.

## Features

- Supports SIC/XE instruction set
- Handles both format 3 and format 4 instructions
- Supports literals, expressions, and symbols
- SUpports program_block, control section
- Generates object code and listing files

## Requirements
- Language: Python >= 3.11.7
- Program was write and tested under Windows11 Env

## Installation

## Steps

1. **Clone the Repository**:
    Clone the project repository to your local machine using the following command:
    ```sh
    git clone https://github.com/yourusername/SICXE-Assembler.git
    ```

2. **Navigate to the Project Directory**:
    After cloning, navigate to the project folder:
    ```sh
    cd SICXE-Assembler
    ```

3. **Run the Assembler**:
    Execute the assembler by specifying the input file and output options:
    ```sh
    python main.py basic.asm -o basic
    ```

---

## Usage Instructions

### Command Options
Below are the options you can use with `main.py`:

- **`input`** (required):
  - Specifies the input file name (e.g., `basic.asm`).
  - This file must be located in the default input directory (`/test`).

- **`-o`** (optional):
  - Specifies the name of the output file.
  - If not provided, the default output file name is `output.txt`.
  - Example:
    ```sh
    python main.py basic.asm -o basic_output
    ```

- **`-t` or `--test`** (optional):
  - Specifies a custom directory for input files. The default is `/test`.
  - Example:
    ```sh
    python main.py -t custom_test_dir example.asm -o output
    ```

- **`-o_dir` or `--output_dir`** (optional):
  - Specifies a custom directory for output files. By default, the output file is generated in the same directory as `assembler.py`.
  - Example:
    ```sh
    python main.py basic.asm -o basic_output -o_dir output_files
    ```

- **`-v` or `--version`**:
  - Displays the current version of the assembler.
  - Example:
    ```sh
    python main.py -v
    ```

---

### main.exe usage

If you want to use main.exe instead of main.py
make sure you put main.exe under SIC/XE-Assembler directory
and there are opcode.json and directive.json under tables directory(you can use yours if you want)
rest of the usage is exactly the same of main.py

---

## Default Behavior
1. **Input Directory**:
   - If no `-t` is specified, the assembler will look for the input file in the `/test` directory.

2. **Output Directory**:
   - If no `-o_dir` is specified, the output file will be created in the same directory as `assembler.py`.

3. **Output File**:
   - The default output file name is `output.txt` unless overridden using the `-o` option.

---

### Example Workflow
1. Place your input file (e.g., `basic.asm`) in the `/test` directory.
2. Run the assembler:
    ```sh
    python main.py basic.asm -o basic_output
    ```
3. Find the generated output file (`basic_output.txt`) in the current directory.

Some testing file are already in the test directory,most of them are from textbook,rest of them are written by me

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
