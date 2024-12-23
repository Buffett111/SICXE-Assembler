import sys # Import the sys module for command line arguments
import argparse # Import the argparse module for parsing command line arguments
from Assembler import Assembler


def main():
    asm = Assembler()
    asm.load_tables("tables/opcode.json", "tables/directive.json")
    
    input_path =""; output_path = ""

    parser = argparse.ArgumentParser(description="SIC/XE Assembler made by Buffett")
    
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    #let user choose test directory default is test
    parser.add_argument("-t", "--test", type=str, help="Test directory path", default="test")
    
    parser.add_argument("-o_dir", "--output_dir", type=str, help="Output directory path", default="")
    
    parser.add_argument("input", type=str, help="Input file")
    parser.add_argument("-o", type=str, help="Output file path", default="output.txt")
    
    args = parser.parse_args()
    if args.input == None:
        print("Please provide an input file path.")
        return

    input_path  = args.test            + "/" + args.input
    if args.output_dir == "":
        output_path = args.o
    else:
        output_path = args.output_dir  + "/" + args.o
    
    asm.parser(input_path, output_path)
    

if __name__ == "__main__":
    main()