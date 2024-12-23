import json

class Assembler:
    
    def __init__(self):
        self.symbol_table = {}
        self.literals = {}
        self.program_blocks = {}
        self.control_sections = []
        self.instructions = []
        self.errors = []
        self.__instructions = []
        self.__sections = []

    def parser(self, input_path: str, output_path: str) -> None:
        self.clear()
        self.load_tables("tables/opcode.json", "tables/directive.json")
        self.pass_one(input_path)
        self.pass_two()
        self.write_file(output_path)
        print("Assemble Done")

    def clear(self) -> None:
        self.symbol_table.clear()
        self.literals.clear()
        self.program_blocks.clear()
        self.control_sections.clear()
        self.instructions.clear()
        self.errors.clear()
        self.__instructions.clear()
        self.__sections.clear()

    def write_output(self, object_code, output_path):
        with open(output_path, "w") as f:
            f.writelines("\n".join(object_code))
    

    def load_tables(self, opcode_path, directive_path):
        # 加載操作碼表與指令集
        with open(opcode_path, "r") as f:
            self.opcode_table = json.load(f)
        with open(directive_path, "r") as f:
            self.directive_table = json.load(f)


    def is_valid_label(self, label):
        # 判斷是否為有效的 SIC/XE 使用者自定義標籤
        if label in self.opcode_table or label in self.directive_table:
            return False
        if not label[0].isalpha():
            return False
        if not label.isalnum():
            return False
        if len(label) > 10:
            return False
        return True

        '''判斷是否為有效的 SIC/XE 使用者自定義標籤
        規則:
        - 不能是操作碼或指令
        - 必須以字母開頭
        - 不能包含特殊字符（僅允許字母和數字）
        - 長度限制（通常 1-6 個字元）'''

    def pass_one(self, input_file):         # 第一遍：生成符號表、處理標籤與區塊、計算指令地址
        location_counter = 0
        current_block = "DEFAULT"
        with open(input_file, "r") as f:
            for line in f:
                #find , in line and remove any blank space after it until reach any non-blank character
                if "," in line:

                    for i in range(len(line)):
                        if line[i] == ",":
                            j = i + 1
                            while j < len(line) and line[j] == " ":
                                j += 1
                            line = line[:i] + "," + line[j:]
                            break
                tokens = line.strip().replace("\t", " ").split()
                
                instruction = Instruction(-1, 0, "", "", "")
                    

                if len(tokens) == 0 or tokens[0].startswith("."): # 跳過空行和註解
                    continue

                tokens +=[""] * (3 - len(tokens))

                # 判斷是否為標籤

                label = tokens[0] if self.is_valid_label(tokens[0]) else None
                opcode = tokens[1] if label else tokens[0]
                
                if len(tokens) > 2:
                    operand = tokens[2] if label else tokens[1]
                else:
                    operand = ""
            
                # 更新符號表
                if label:

                    self.instructions.append(f"{location_counter:04X} {line.strip()}")  # 保存指令

                    if label in self.symbol_table:

                        self.errors.append(f"重複定義的標籤: {label}")
                    else:

                        self.symbol_table[label] = location_counter


                # 判斷指令或指令集
                # 判斷是否為format 4指令
                format_type = 0
                # 印出opcode和command
                # print(tokens)
                # print("opcode:", opcode)

                if "+" in opcode:
                    opcode = opcode[1:]
                    format_type = 4
                
                if opcode in self.opcode_table:
                    if not label : self.instructions.append(f"{location_counter:04X} {line.strip()}")  # 保存指令

                    if format_type!=4 : format_type = self.opcode_table[opcode]["format"]
                    #print(f"location_counter:{location_counter:04X}" , end=" ")
                    location_counter += self.opcode_table[opcode]["format"]

                    if format_type == 4:
                        location_counter += 1

                elif opcode in self.directive_table: 
                    self.instructions.append(f"{location_counter:04X} {line.strip()}")  # 保存指令                   
                    """
                    [
                        "START",
                        "END",
                        "WORD",
                        "EXTDEF",
                        "EXTREF",
                        "ORG",
                        "LTORG",
                        "EQU",
                        "USE"

                    ]"""

                    if opcode == "START":
                        location_counter = int(operand, 16)

                    elif opcode == "END":
                        pass
                    elif opcode == "BYTE":
                        if operand.startswith("C'") and operand.endswith("'"):
                            location_counter += len(operand) - 3
                        elif operand.startswith("X'") and operand.endswith("'"):
                            location_counter += (len(operand) - 3) // 2
                    elif opcode == "WORD":
                        location_counter += 3
                    elif opcode == "RESW":
                        location_counter += 3 * int(operand)
                    elif opcode == "RESB":
                        location_counter += int(operand)
                    elif opcode == "BASE":
                        pass  # BASE 指令在 pass 2 中處理
                    elif opcode == "CSECT":
                        self.control_sections.append(current_block)
                        current_block = operand
                        location_counter = 0
                    elif opcode == "EXTDEF" or opcode == "EXTREF":
                        pass  # EXTDEF 和 EXTREF 在 pass 2 中處理
                    elif opcode == "ORG":
                        location_counter = int(operand, 16)
                    elif opcode == "LTORG":
                        pass  # LTORG 在 pass 2 中處理
                    elif opcode == "EQU":
                        if operand.isdigit():
                            self.symbol_table[label] = int(operand)
                        else:
                            self.symbol_table[label] = self.symbol_table.get(operand, 0)
                    elif opcode == "USE":
                        self.program_blocks[current_block] = location_counter
                        current_block = operand
                        location_counter = self.program_blocks.get(current_block, 0)
                    else:
                        self.errors.append(f"未知的指令: {opcode}")

                else:
                    self.errors.append(f"無效的指令: {opcode}")

                if label: instruction.symbol = label
                else: instruction.symbol = ""

                instruction.mnemonic = opcode

                #print(f"operand: {operand}")
                instruction.operand = operand
                instruction.format = format_type
                
                if instruction.format != 4 and instruction.mnemonic in self.opcode_table:
                    instruction.format = self.opcode_table[instruction.mnemonic]["format"]

                elif instruction.format != 4:
                    instruction.format = 0

                #print(instruction)
                self.__instructions.append(instruction)
                #print(f"add{instruction} to __instructions")
        
        self.__sections.append(Section())
        for instruction in self.__instructions:
            if instruction.mnemonic == "END":
                self.__sections[0].instructions.append(instruction)
                break

            if instruction.mnemonic == "CSECT":
                self.__sections.append(Section())
            self.__sections[-1].instructions.append(instruction)

        for section in self.__sections[1:]: #format index, format, symbol, mnemonic, operand
            section.instructions.append(Instruction(-1, 0, "", "END", "")) # Add END instruction to the end of each section

        #print all instructions for each section
        # for section in self.__sections:
        #     print("SECTION:")
        #     for instruction in section.instructions:
        #         print(instruction)
        #     print("-"*50,end="\n\n")
        #Pass 1 Debug Output

        #輸出符號表
        print("符號表:")
        for symbol, address in self.symbol_table.items():
            #以16進位輸出
            print(f"{symbol} => {address:04X}")
        # 輸出指令集
        print("指令集:")
        for instruction in self.instructions:
            print(instruction)
        # 輸出錯誤訊息
        print("錯誤訊息:")
        for error in self.errors:
            print(error)
        # 輸出區塊資訊
        print("區塊資訊:")
        for block, address in self.program_blocks.items():
            print(f"{block} => {address}")
        print("End of Pass 1")

    def pass_two(self) -> None:
        # Bonus Version, each sections can be assembled independently
        for section in enumerate(self.__sections):
            index, sectionasm = section
            print("SECTION number ", index, ":")
            sectionasm.assemble()
            print(section)


    def write_file(self, path: str) -> None:
        for index, section in enumerate(self.__sections): # Write each section to object code file
            with open(path + "_" + str(index + 1) + ".obj", "w") as f:
                section.write(f)

    #old version for single section assembly,probably not needed in bonus version
    # def assemble(self, input_file, output_file): 
    #     self.pass_one(input_file)
    #     self.pass_two()
    #     self.write_file(output_path)
    #     with open(output_file, "w") as f:
    #         f.writelines("\n".join(object_code))

class Instruction:
    def __init__(self, index: int, format: int, symbol: str, mnemonic: str, operand: str) -> None:

        self.index = index
        self.format = format
        self.symbol = symbol
        self.mnemonic = mnemonic
        self.operand = operand
        self.location = None
        self.object_code = ""

    def __str__(self) -> str:
        location = hex(self.location) if self.location != None else self.location
        return f"({self.index}, {self.format}, {self.symbol}, {self.mnemonic}, {self.operand}, {location}, {self.object_code})"


class Modification_record: #format: M START ADDRESS LENGTH SIGN SYMBOL

    def __init__(self, location: int, length: int, sign: str = "", symbol: str = "") -> None:
        self.location = location
        self.length = length
        self.sign = sign
        self.symbol = symbol

    def __str__(self) -> str:
        return f"({self.location}, {self.length}, {self.sign}, {self.symbol})"
    
    

class Section:

    def __init__(self) -> None:

        self.opcode_table = json.load(open("tables/opcode.json", "r"))
        self.directive_table = json.load(open("tables/directive.json", "r"))
        self.__extdef_table = {}
        self.__extref_table = {} 
        self.__symbol_table = {} #SYMTAB
        self.__literal_table = [] #LITTAB
        self.instructions = []
        self.__modified_record = []
    
    def get_register_number(self, reg):
        registers = {
            "A": 0, "X": 1, "L": 2, "B": 3, "S": 4, "T": 5, "F": 6,
            "PC": 8, "SW": 9
        }
        return registers.get(reg.upper(), 0)

    def __debug_print__(self) -> str:
        # symbol already printed in pass1
        # print instruction
        print("Instructions:")
        for insruction in self.instructions:
            print("\t", insruction)
        print("\n")
        # print each modified record
        print("M record:")
        for record in self.__modified_record:
            print("\t", record)
        print("}\n")

        return ""

    def assemble(self) -> None: #Section can be assembled independently of each other

        self.generate_literal_table()
        self.handling_block()
        self.set_symbol()
        self.set_location()
        self.sorting_index()
        self.generate_object_code()
        #self.__debug_print__()
    

    def generate_literal_table(self) -> None:

        literal_table = []
        literal_count = 1
        literal_set = {}


        def add_literal(instruction, literal_count):
            literal_table.append(
                {
                    "name": "LITTAB" + str(literal_count),
                    "data": instruction.operand[1:],
                }
            )
            literal_set[instruction.operand] = "LITTAB" + str(literal_count)
            instruction.operand = "LITTAB" + str(literal_count)
            return literal_count + 1


        def insert_literals(index):
            for lit in literal_table[::-1]:
                literal_instruction = Instruction(
                    -1, 0, lit["name"], "BYTE", lit["data"]
                )
                self.instructions.insert(index, literal_instruction)
                # print LITTAB for debug
                # print(literal_instruction)
            return []

        def process_instruction(instruction, literal_set, literal_count):
            if instruction.operand and instruction.operand != "":
                if instruction.mnemonic == "*":
                    print("found *:", instruction)
                    instruction.mnemonic = "BYTE"

                if instruction.operand[0] == "=":
                    if instruction.operand in literal_set:
                        instruction.operand = literal_set[instruction.operand]
                    else:
                        literal_count = add_literal(instruction, literal_count)
            return literal_count

        def handle_literals(instruction, index):
            if instruction.mnemonic in ["LTORG", "END"]:
                return insert_literals(index)
            return None

        for index, instruction in enumerate(self.instructions):
            literal_count = process_instruction(instruction, literal_set, literal_count)
            result = handle_literals(instruction, index)
            if result is not None:
                literal_table = result
                

        # print("literal_table:", literal_table)
        # print("literal_set:", literal_set)
        # print("Instructions:")
        # for instruction in self.instructions:
        #     print(instruction)
        # print("\n")

    def handling_block(self) -> None:
        blocks = {}
        cur_block = None
        end_instruction = None

        def add_instruction_to_block(block_name, instruction):
            if block_name not in blocks:
                blocks[block_name] = []
            blocks[block_name].append(instruction)

        for index, instruction in enumerate(self.instructions):
            if instruction.mnemonic == "START" or instruction.mnemonic == "CSECT":
                cur_block = instruction.symbol
                add_instruction_to_block(cur_block, instruction)
            elif instruction.mnemonic == "END":
                end_instruction = instruction
                continue
            elif instruction.mnemonic == "USE":
                cur_block = instruction.operand if instruction.operand !="" else list(blocks.keys())[0]
                add_instruction_to_block(cur_block, instruction)
            else:
                add_instruction_to_block(cur_block, instruction)
            instruction.index = index

        #debug print all blocks
        for block in blocks:
            print(f"Block: {block}")
            for instruction in blocks[block]:
                print(instruction)
            print("\n\n")    
        
        self.instructions = [instr for block in blocks.values() for instr in block]

        if end_instruction:
            end_instruction.index = max(self.instructions, key=lambda x: x.index).index + 1
            self.instructions.append(end_instruction)
        else:
            print("Error: END instruction not found")

        #self.__debug_print__()
        
        
    def set_symbol(self) -> None:

        self.__initialize_symbols()
        end = False
        while not end:
            end = True
            for symbol in self.__symbol_table:
                if self.__symbol_table[symbol] == None:
                    end = False
                    break

            if end: break #if all symbols are resolved, break the loop
            self.__process_symbols()
        
        self.__resolve_forward_references()
        # print("End of setting_symbol, Symbol Table:")
        # for symbol in self.__symbol_table:
        #     print(f"{symbol} => {self.__symbol_table[symbol]}")
        # print("\n")

    #don't call these 3 functions directly, they are called by set_symbol
    def __initialize_symbols(self) -> None:
        for instruction in self.instructions:

            if instruction.symbol != "":
                self.__symbol_table[instruction.symbol] = None

            if instruction.mnemonic == "EXTDEF":
                for symbol in instruction.operand.split(","):
                    self.__extdef_table[symbol] = None

            if instruction.mnemonic == "EXTREF":
                for symbol in instruction.operand.split(","):
                    self.__extref_table[symbol] = 0


    def __process_symbols(self) -> None:

        LOCCTR = 0
        #print("Processing symbols...")
        for instruction in self.instructions:
            #print("processing instruction:", instruction)
            if instruction.symbol != "":
                self.__symbol_table[instruction.symbol] = LOCCTR
                if instruction.symbol in self.__extdef_table:
                    self.__extdef_table[instruction.symbol] = LOCCTR
                #print(f"symbol: {instruction.symbol}, LOCCTR: {LOCCTR}")

            if instruction.mnemonic == "START":
                LOCCTR = int(instruction.operand, 16)
                self.__symbol_table[instruction.symbol] = LOCCTR
            elif instruction.mnemonic == "CSECT":
                LOCCTR = 0
                self.__symbol_table[instruction.symbol] = 0
                #print(f"symbol: {instruction.symbol}, LOCCTR: {LOCCTR}")
            elif instruction.mnemonic == "RESW":
                self.__symbol_table[instruction.symbol] = LOCCTR
                try:
                    LOCCTR += 3 * int(self.calculate(instruction.operand, LOCCTR, instruction.mnemonic))
                except:
                    continue
            elif instruction.mnemonic == "RESB":
                self.__symbol_table[instruction.symbol] = LOCCTR
                try:
                    LOCCTR += int(self.calculate(instruction.operand, LOCCTR, instruction.mnemonic))
                except:
                    print("calculate error:"+ self.calculate(instruction.operand, LOCCTR, instruction.mnemonic))
                    continue
            elif instruction.mnemonic == "BYTE":
                self.__symbol_table[instruction.symbol] = LOCCTR
                if instruction.operand[0] == "C" or instruction.operand[0] == "X":
                    LOCCTR += len(instruction.operand) - 3 if instruction.operand[0] == "C" else (len(instruction.operand) - 3) // 2
                else:
                    print("Syntax Error: Invalid BYTE operand"+instruction.operand+" at "+instruction.location)
                    print("Expected: C'EOF' or X'05'")
                    raise Exception("Syntax Error: Invalid BYTE operand")
            elif instruction.mnemonic == "WORD":
                result = self.calculate(instruction.operand, LOCCTR, instruction.mnemonic)
                if result != None:
                    if self.__symbol_table[instruction.symbol] == None:
                        self.__symbol_table[instruction.symbol] = result
                    else:
                        self.__symbol_table[instruction.symbol+"_addr"] = self.__symbol_table[instruction.symbol] 
                        self.__symbol_table[instruction.symbol] = result
                LOCCTR += 3
            elif instruction.mnemonic == "EQU":
                result = self.calculate(instruction.operand, LOCCTR, instruction.mnemonic)
                # print(f"instruction: {instruction}")
                # print(f"result: {result}")
                if result != None:
                    if self.__symbol_table[instruction.symbol] == None:
                        self.__symbol_table[instruction.symbol] = result
                    else:
                        self.__symbol_table[instruction.symbol+"_addr"] = self.__symbol_table[instruction.symbol] 
                        self.__symbol_table[instruction.symbol] = result
            elif instruction.mnemonic == "ORG":
                try:
                    LOCCTR = int(self.calculate(instruction.operand, LOCCTR, instruction.mnemonic))
                except:
                    raise Exception("ORG does't support forward reference")
                    
            elif instruction.mnemonic == "BASE":
                result = self.calculate(instruction.operand, LOCCTR, instruction.mnemonic)
                if result != None:
                    self.__symbol_table[instruction.symbol] = result
            elif instruction.mnemonic == "RSUB":
                instruction.operand = "#0"
                LOCCTR += 3
            else:
                LOCCTR += int(instruction.format)
            
            # print("End of processing symbols")
            # for symbol in self.__symbol_table:
            #     #print symbol in hex
            #     try:
            #         print(f"{symbol} => {self.__symbol_table[symbol]:04X}")
            #     except:
            #         print(f"Error:{symbol} => {self.__symbol_table[symbol]}")
            # print("\n")
            

    def __resolve_forward_references(self) -> None:
        for exd_symbol in self.__extdef_table:
            if exd_symbol in self.__symbol_table:
                self.__extdef_table[exd_symbol] = self.__symbol_table[exd_symbol]
            else:
                print(f"Error: exd_symbol '{exd_symbol}' not found in __symbol_table")
    

    def set_location(self) -> None:
        locctr = 0  # Initialize the location counter

        mnemonic_handlers = {
            "START": self._handle_start,
            "CSECT": self._handle_csect,
            "RESW": self._handle_resw,
            "RESB": self._handle_resb,
            "BYTE": self._handle_byte,
            "WORD": self._handle_word,
            "ORG": self._handle_org,
        }

        for instruction in self.instructions:
            instruction.location = locctr  # Default assignment

            handler = mnemonic_handlers.get(instruction.mnemonic)
            if handler:
                locctr = handler(instruction, locctr)
            else:
                locctr += int(instruction.format)

        self._resolve_extdef_locations()

    def _handle_start(self, instruction, locctr: int) -> int:
        locctr = int(instruction.operand, 16)
        instruction.location = locctr
        return locctr

    def _handle_csect(self, instruction, locctr: int) -> int:
        instruction.location = 0
        return 0

    def _handle_resw(self, instruction, locctr: int) -> int:
        result = self.calculate(instruction.operand, locctr, instruction.mnemonic)
        return locctr + 3 * int(result)

    def _handle_resb(self, instruction, locctr: int) -> int:
        result = self.calculate(instruction.operand, locctr, instruction.mnemonic)
        return locctr + int(result)

    def _handle_byte(self, instruction, locctr: int) -> int:
        if instruction.operand[0] in {"C", "X"}:
            length = len(instruction.operand) - 3  # Account for enclosing C'' or X''
            locctr += length if instruction.operand[0] == "C" else length // 2
        else:
            raise Exception("Syntax Error: Invalid BYTE operand")
        return locctr

    def _handle_word(self, instruction, locctr: int) -> int:
        return locctr + 3

    def _handle_org(self, instruction, locctr: int) -> int:
        result = self.calculate(instruction.operand, locctr, instruction.mnemonic)
        return int(result)

    def _resolve_extdef_locations(self) -> None:
        for symbol in self.__extdef_table:
            if not symbol:
                print("Warning: Empty symbol encountered in __extdef_table")
                continue

            if symbol in self.__symbol_table:
                self.__extdef_table[symbol] = self.__symbol_table[symbol]
            else:
                print(f"Error: Symbol '{symbol}' not found in __symbol_table")


    def sorting_index(self) -> None: # just a function for readability
        self.instructions.sort(key=lambda x: x.index)
    
    def generate_object_code(self) -> None:
        base = 0
 
        def format_3_obj_code(code): #convert binary code to hexadecimal to fit format in the textbook
            object_code = f"{int(code, 2):>06X}" 
            return object_code

        def handle_base_relative(TA, base, opcode, n, i, x, e):
            b, p = 1, 0
            disp = TA - base
            return f"{opcode:>06b}{n}{i}{x}{b}{p}{e}{disp:>012b}"

        def handle_pc_relative(TA, instruction, opcode, n, i, x, e):
            b, p = 0, 1
            disp = TA - (instruction.location + instruction.format)
            if disp < 0:
                # 2's complement of 12 bits signed integer
                disp = (1 << 12) + disp
            return f"{opcode:>06b}{n}{i}{x}{b}{p}{e}{disp:>012b}"

        def handle_immediate_addressing(instruction, opcode, n, i, x, e):
            if instruction.operand[1:].isdigit(): #Ta=disp
                b, p = 0, 0
                disp = int(instruction.operand[1:])  #let disp=TA
                return f"{opcode:>06b}{n}{i}{x}{b}{p}{e}{disp:>012b}"
            else:
                TA = int(self.calculate(instruction.operand[1:], instruction.location, instruction.mnemonic))
                if -2048 <= TA - (instruction.location + instruction.format) <= 2048 - 1:
                    return handle_pc_relative(TA, instruction, opcode, n, i, x, e)
                elif 0 <= TA - base <= 4096 - 1:
                    return handle_base_relative(TA, base, opcode, n, i, x, e)
                else:
                    raise Exception("Error: Need format 4")

        for instruction in self.instructions:
            
            if instruction.mnemonic == "WORD":
                instruction.object_code = f"{int(self.calculate(instruction.operand, instruction.location, instruction.mnemonic)):06X}"
            elif instruction.mnemonic == "BASE":
                base = self.calculate(instruction.operand, instruction.location, instruction.mnemonic)
            elif instruction.mnemonic == "RSUB":
                instruction.object_code = "4F0000"
            elif instruction.mnemonic == "BYTE":
                if instruction.operand[0] == "X":
                    instruction.object_code = instruction.operand[2:-1]
                elif instruction.operand[0] == "C":
                    for char in instruction.operand[2:-1]:
                        instruction.object_code += f"{ord(char):02X}"
            elif instruction.mnemonic in self.opcode_table: #normal instruction
                opcode = int(self.opcode_table[instruction.mnemonic]["obj"], 16) >> 2
                n, i, x, b, p, e = 0, 0, 0, 0, 0, 0
                if instruction.format == 1:
                    instruction.object_code = f"{self.opcode_table[instruction.mnemonic]['obj']}"
                elif instruction.format == 2:
                    register1 = self.get_register_number(instruction.operand.split(",")[0])
                    register2 = self.get_register_number(instruction.operand.split(",")[1] if len(instruction.operand.split(",")) > 1 else "A")
                    instruction.object_code = f"{self.opcode_table[instruction.mnemonic]['obj']}{register1}{register2}"
                elif instruction.format == 3:
                    if "," in instruction.operand:
                        x = 1
                        instruction.operand = instruction.operand[:-2]
                    if instruction.operand[0] == "#":
                        n, i = 0, 1
                        instruction.object_code =format_3_obj_code( handle_immediate_addressing(instruction, opcode, n, i, x, e) )
                    elif instruction.operand[0] == "@":
                        n, i = 1, 0
                        TA = int(self.calculate(instruction.operand[1:], instruction.location, instruction.mnemonic))
                        if -2048 <= TA - (instruction.location + instruction.format) <= 2048 - 1:
                            instruction.object_code =format_3_obj_code( handle_pc_relative(TA, instruction, opcode, n, i, x, e) )
                        elif 0 <= TA - base <= 4096 - 1:
                            instruction.object_code =format_3_obj_code( handle_base_relative(TA, base, opcode, n, i, x, e) )
                        else:
                            raise Exception("Error: Need format 4")
                    else:  # simple addressing
                        n, i = 1, 1
                        TA = int(self.calculate(instruction.operand, instruction.location, instruction.mnemonic))
                        
                        if -2048 <= TA - (instruction.location + instruction.format) <= 2048 - 1:
                            instruction.object_code =format_3_obj_code( handle_pc_relative(TA, instruction, opcode, n, i, x, e) )
                        elif 0 <= TA - base <= 4096 - 1:
                            instruction.object_code =format_3_obj_code( handle_base_relative(TA, base, opcode, n, i, x, e) )
                        else:
                            raise Exception("Error: Need format 4")
                elif instruction.format == 4:
                    opcode = int(self.opcode_table[instruction.mnemonic]["obj"], 16) >> 2
                    n, i, x, b, p, e = 0, 0, 0, 0, 0, 1
                    if "," in instruction.operand:
                        x = 1
                        instruction.operand = instruction.operand[:-2]
                    if instruction.operand[0] == "#":
                        n, i = 0, 1
                        disp = int(self.calculate(instruction.operand[1:], instruction.location, instruction.mnemonic))
                        code = f"{opcode:>06b}{n}{i}{x}{b}{p}{e}{disp:>020b}"
                        instruction.object_code = f"{int(code, 2):>08X}"
                    else:
                        n, i = 1, 1
                        disp = int(self.calculate(instruction.operand, instruction.location, instruction.mnemonic))
                        code = f"{opcode:>06b}{n}{i}{x}{b}{p}{e}{disp:>020b}"
                        instruction.object_code = f"{int(code, 2):>08X}"
                        
                        #check if modification record is needed
                        if not any(record.location == instruction.location + 1 and record.symbol == instruction.operand for record in self.__modified_record):
                            self.__modified_record.append(Modification_record(instruction.location + 1, 5))

          
    def write(self, file) -> None:
        def write_header():
            file.write(f"H{self.instructions[0].symbol.ljust(6)}{self.instructions[0].location:06X}{self.instructions[-1].location - self.instructions[0].location:06X}\n")

        def write_extdef():
            if self.__extdef_table:
                file.write("D")
                for i, (symbol, address) in enumerate(self.__extdef_table.items()):
                    file.write(f"{symbol.ljust(6)}{int(address):06X}")
                    if (i + 1) % 5 == 0:
                        file.write("\nD")
                file.write("\n")

        def write_extref():
            if self.__extref_table:
                file.write("R")
                for i, symbol in enumerate(self.__extref_table):
                    file.write(symbol.ljust(6))
                    if (i + 1) % 5 == 0:
                        file.write("\nR")
                file.write("\n")

        def write_text_records():
            cur_start = ""
            cur_text = ""
            for instruction in self.instructions:
                if instruction.mnemonic in ["RESW", "RESB", "USE"]:
                    if cur_text != "":
                        file.write(f"T{cur_start:06X}{len(cur_text) // 2:02X}{cur_text}\n")
                        cur_text = ""
                    continue
                
                if cur_text == "":
                    cur_start = instruction.location
                if len(cur_text) + len(instruction.object_code) > 60:
                    file.write(f"T{cur_start:06X}{len(cur_text) // 2:02X}{cur_text}\n")
                    cur_text = ""
                    cur_start = instruction.location
                cur_text += instruction.object_code

            if cur_text:
                file.write(f"T{cur_start:06X}{len(cur_text) // 2:02X}{cur_text}\n")

        def write_modification_records():
            # Sort modification records by location and sign
            self.__modified_record.sort(key=lambda x: (x.location, x.sign == "-"))

            for record in self.__modified_record:
                file.write(f"M{record.location:06X}{record.length:02X}{record.sign}{record.symbol}\n")

        def write_end_record():
            file.write(f"E{self.instructions[0].location:06X}\n\n" if self.instructions[0].mnemonic == "START" else "E\n\n")

        write_header()
        write_extdef()
        write_extref()
        write_text_records()
        write_modification_records()
        write_end_record()

    def calculate(self, operand: str, locctr: int, mnemonic: str) -> str:
        """
        Calculate the resolved value of an operand based on symbol and external reference tables.

        Args:
            operand (str): The operand to resolve.
            locctr (int): The current memory location.
            mnemonic (str): The mnemonic (e.g., WORD, BYTE) for the operand.

        Returns:
            str: The calculated value of the operand, or None if evaluation fails.
        """
        if operand == "*":
            return str(locctr)

        operand = self._replace_symbols(operand, locctr)
        operand = self._process_external_references(operand, locctr, mnemonic)

        return self._evaluate_operand(operand)

    def _replace_symbols(self, operand: str, locctr: int) -> str:
        for symbol in self.__symbol_table:
            if symbol in operand:
                replacement = self.__symbol_table.get(f"{symbol}_addr") or self.__symbol_table[symbol]
                if replacement == None:
                    # raise exception here
                    print(f" Symbol '{symbol}' not solved in __symbol_table")
                    return operand
                    #raise Exception(f"Error: Symbol '{symbol}' not found in __symbol_table")
                else:
                    operand = operand.replace(symbol, str(replacement))
        return operand

    def _process_external_references(self, operand: str, locctr: int, mnemonic: str) -> str:
        for symbol in self.__extref_table:
            if symbol in operand and self.__extref_table[symbol] is not None:
                index = operand.find(symbol)
                operand = operand.replace(symbol, str(self.__extref_table[symbol]))

                sign = self._determine_sign(operand, index)
                if not self._is_record_already_modified(locctr, symbol):
                    record_length = 6 if mnemonic == "WORD" else 5
                    self.__modified_record.append(Modification_record(locctr + 1, record_length, sign, symbol))
        return operand

    def _determine_sign(self, operand: str, index: int) -> str:
        if index >= 1:
            return "+" if operand[index - 1] == "+" else "-"
        return "+"

    def _is_record_already_modified(self, locctr: int, symbol: str) -> bool:
        for record in self.__modified_record:
            if record.location == locctr + 1 and record.symbol == symbol:
                return True
        return False

    def _evaluate_operand(self, operand: str) -> str:
        try:
            return eval(operand)
        except Exception:
            return None
