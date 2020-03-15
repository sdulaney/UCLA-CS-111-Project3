# NAME: Stewart Dulaney,Pariya Samandi
# EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
# ID: 904064791,205092357

#!/usr/bin/env python3

import sys, string, locale, csv

class Ext2SuperBlock:
	def __init__(self, blocks_count, inodes_count, block_size, inode_size, blocks_per_group, inodes_per_group, first_nonres_inode):
		self.blocks_count = blocks_count				# total number of blocks (decimal)
		self.inodes_count = inodes_count				# total number of i-nodes (decimal)
		self.block_size = block_size					# block size (in bytes, decimal)
		self.inode_size = inode_size					# i-node size (in bytes, decimal)
		self.blocks_per_group = blocks_per_group		# blocks per group (decimal)
		self.inodes_per_group = inodes_per_group		# i-nodes per group (decimal)
		self.first_nonres_inode = first_nonres_inode	# first non-reserved i-node (decimal)
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Ext2Group:
	def __init__(self, group_num, block_count, inode_count, free_block_count, free_inode_count, block_bitmap, inode_bitmap, inode_table):
		self.group_num = group_num						# group number (decimal, starting from zero)
		self.block_count = block_count					# total number of blocks in this group (decimal)
		self.inode_count = inode_count					# total number of i-nodes in this group (decimal)
		self.free_block_count = free_block_count		# number of free blocks (decimal)
		self.free_inode_count = free_inode_count		# number of free i-nodes (decimal)
		self.block_bitmap = block_bitmap				# block number of free block bitmap for this group (decimal)
		self.inode_bitmap = inode_bitmap				# block number of free i-node bitmap for this group (decimal)
		self.inode_table = inode_table					# block number of first block of i-nodes in this group (decimal)
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Ext2Block:
	def __init__(self, block_num, level_of_indir, inode_num, offset):
		self.block_num = block_num
		self.level_of_indir = level_of_indir
		self.inode_num = inode_num
		self.offset = offset
		self.refs = []
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Ext2Inode:
	def __init__(self, inode_num, file_type, mode, owner, group, link_count, ctime, mtime, atime, file_size, num_512_blocks):
		self.inode_num = inode_num
		self.file_type = file_type
		self.mode = mode
		self.owner = owner
		self.group = group
		self.link_count = link_count
		self.ctime = ctime
		self.mtime = mtime
		self.atime = atime
		self.file_size = file_size
		self.num_512_blocks = num_512_blocks
		self.block_ptrs = []
		# TODO	

# TODO
# class Ext2Directory:
# 	def __init__(self):

class Ext2IndirBlockRef:
	def __init__(self, inode_num, level_of_indir, offset, indir_block_num, refd_block_num):
		self.inode_num = inode_num
		self.level_of_indir = level_of_indir
		self.offset = offset
		self.indir_block_num = indir_block_num
		self.refd_block_num = refd_block_num

class Ext2Image:
	def __init__(self, filename):
		self.rows = []
		# self.superblock = None
		self.group = None
		self.blocks_on_freelist = set()
		self.blocks_allocated = {}
		self.inodes_on_freelist = set()
		self.inodes_alloc = dict()
		self.indir_block_refs = []
		self.read_csv(filename)
		self.parse_csv()
	def read_csv(self, filename):
		with open(filename, "r") as csvfile:
			csvreader = csv.reader(csvfile)
			for row in csvreader:
				if any(x.strip() for x in row):						# handle empty lines
					self.rows.append([x.strip(' ') for x in row]) 	# handle leading/trailing whitespace in cells
	def parse_csv(self):
		for row in self.rows:
			if row[0] == "SUPERBLOCK":
				self.superblock = Ext2SuperBlock(int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]))
			if row[0] == "GROUP":
				self.group = Ext2Group(int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]), int(row[8]))
			if row[0] == "BFREE":
				self.blocks_on_freelist.add(int(row[1]))
			if row[0] == "IFREE":
				self.inodes_on_freelist.add(int(row[1]))
			if row[0] == "INODE":
				self.inodes_alloc[int(row[1])] = Ext2Inode(int(row[1]), row[2], int(row[3]), int(row[4]), int(row[5]), int(row[6]), row[7], row[8], row[9], int(row[10]), int(row[11]))
				for i in range(12,27):
					self.inodes_alloc[int(row[1])].block_ptrs.append(int(row[i]))
				# TODO
			# if row[0] == "DIRENT":
				# TODO
			if row[0] == "INDIRECT":
				self.indir_block_refs.append(Ext2IndirBlockRef(int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5])))
	# Precondition: self.superblock.block_size >= 1024
	def get_first_data_block_num(self):
		# Block containing the superblock structure
		if self.superblock.block_size == 1024:				# always 1 for file systems with a block size of 1KB		
			return 1							
		return 0											# always 0 for file systems with a block size larger than 1KBs
	def get_max_block_num(self):
		return self.superblock.blocks_count - 1
	def get_first_legal_block_number(self):
		# first data block + 1 (group descriptor) +  1 (data block bitmap) + 1 (inode bitmap) + size(inode table) + 1 (next block after)
		return int(self.get_first_data_block_num() + 1 + 1 + 1 + self.superblock.inodes_count * (self.superblock.inode_size / self.superblock.block_size) + 1)
	def get_logic_offset_first_indir_block(self):
		return 12
	def get_logic_offset_first_doub_indir_block(self):
		pointers_per_indir_block = self.superblock.block_size / 4
		return int(12 + pointers_per_indir_block)
	def get_logic_offset_first_trip_indir_block(self):
		pointers_per_indir_block = self.superblock.block_size / 4
		return int(12 + pointers_per_indir_block + (pointers_per_indir_block * pointers_per_indir_block))

class Ext2ErrorMsgHandler:
	def __init__(self):
		pass
	# Block Consistency Errors
	def block_invalid_error(self, block_num, inode_num, offset, level_of_indir):
		indir_str = ""							# assume level_of_indir = 0 means no indirection
		if level_of_indir == 1:
			indir_str = "INDIRECT "
		elif level_of_indir == 2:
			indir_str = "DOUBLE INDIRECT "
		elif level_of_indir == 3:
			indir_str = "TRIPLE INDIRECT "
		sys.stdout.write(f"INVALID {indir_str}BLOCK {block_num} IN INODE {inode_num} AT OFFSET {offset}\n")
	def block_reserved_error(self, block_num, inode_num, offset, level_of_indir):
		indir_str = ""							# assume level_of_indir = 0 means no indirection
		if level_of_indir == 1:
			indir_str = "INDIRECT "
		elif level_of_indir == 2:
			indir_str = "DOUBLE INDIRECT "
		elif level_of_indir == 3:
			indir_str = "TRIPLE INDIRECT "
		sys.stdout.write(f"RESERVED {indir_str}BLOCK {block_num} IN INODE {inode_num} AT OFFSET {offset}\n")
	def block_unref_and_used_error(self, block_num):
		sys.stdout.write(f"UNREFERENCED BLOCK {block_num}\n")
	def block_alloc_and_free_error(self, block_num):
		sys.stdout.write(f"ALLOCATED BLOCK {block_num} ON FREELIST\n")
	def block_duplicate_error(self, block_num, inode_num, offset, level_of_indir):
		indir_str = ""							# assume level_of_indir = 0 means no indirection
		if level_of_indir == 1:
			indir_str = "INDIRECT "
		elif level_of_indir == 2:
			indir_str = "DOUBLE INDIRECT "
		elif level_of_indir == 3:
			indir_str = "TRIPLE INDIRECT "
		sys.stdout.write(f"DUPLICATE {indir_str}BLOCK {block_num} IN INODE {inode_num} AT OFFSET {offset}\n")
	# Inode Allocation Errors
	def inode_alloc_on_freelist_error(self, inode_num):
		sys.stdout.write(f"ALLOCATED INODE {inode_num} ON FREELIST\n")
	def inode_unalloc_not_on_freelist_error(self, inode_num):
		sys.stdout.write(f"UNALLOCATED INODE {inode_num} NOT ON FREELIST\n")
	# Directory Consistency Errors
	def dir_incorrect_link_count_error(self, inode_num, ref_count, link_count):
		sys.stdout.write(f"INODE {inode_num} HAS {ref_count} LINKS BUT LINKCOUNT IS {link_count}\n")
	def dir_unalloc_inode_error(self, dir_num, name, inode_num):
		sys.stdout.write(f"DIRECTORY INODE {dir_num} NAME '{name}' UNALLOCATED INODE {inode_num}\n")
	def dir_invalid_inode_error(self, dir_num, name, inode_num):
		sys.stdout.write(f"DIRECTORY INODE {dir_num} NAME '{name}' INVALID INODE {inode_num}\n")
	def dir_invalid_parent_link_error(self, dir_num, inode_num, correct_inode_num):
		sys.stdout.write(f"DIRECTORY INODE {dir_num} NAME '..' LINK TO INODE {inode_num} SHOULD BE {correct_inode_num}\n")
	def dir_invalid_self_link_error(self, dir_num, inode_num, correct_inode_num):
		sys.stdout.write(f"DIRECTORY INODE {dir_num} NAME '.' LINK TO INODE {inode_num} SHOULD BE {correct_inode_num}\n")

class Ext2Checker:
	def __init__(self, filename):
		self.img = Ext2Image(filename)
		self.msg_handler = Ext2ErrorMsgHandler()
	# Block Consistency Audits
	def find_block_errors(self):
		first_legal_block_num = self.img.get_first_legal_block_number()
		max_block_num = self.img.get_max_block_num()
		# Check INODE lines from CSV
		for inode in self.img.inodes_alloc.values():
			if (inode.file_type == 'f') or (inode.file_type == 'd') or (file_type == 's' and inode.file_size > 60):
				# Direct block pointers
				for i in range(0,12):
					# Block group 0 starts with block 1 on 1KB block systems, so max block number is superblock.blocks_count
					if inode.block_ptrs[i] < 0 or inode.block_ptrs[i] > max_block_num:		
						self.msg_handler.block_invalid_error(inode.block_ptrs[i], inode.inode_num, i, 0)
					if inode.block_ptrs[i] > 0 and inode.block_ptrs[i] < first_legal_block_num:		
						self.msg_handler.block_reserved_error(inode.block_ptrs[i], inode.inode_num, i, 0)
					if inode.block_ptrs[i] > 0:
						if inode.block_ptrs[i] not in self.img.blocks_allocated.keys():
							self.img.blocks_allocated[inode.block_ptrs[i]] = Ext2Block(inode.block_ptrs[i], 0, inode.inode_num, i)
						self.img.blocks_allocated[inode.block_ptrs[i]].refs.append(Ext2Block(inode.block_ptrs[i], 0, inode.inode_num, i))
				# Single indirection block pointers
				if inode.block_ptrs[12] < 0 or inode.block_ptrs[12] > max_block_num:		
						self.msg_handler.block_invalid_error(inode.block_ptrs[12], inode.inode_num, self.img.get_logic_offset_first_indir_block(), 1)
				if inode.block_ptrs[12] > 0 and inode.block_ptrs[12] < first_legal_block_num:		
						self.msg_handler.block_reserved_error(inode.block_ptrs[12], inode.inode_num, self.img.get_logic_offset_first_indir_block(), 1)
				if inode.block_ptrs[12] > 0:
					if inode.block_ptrs[12] not in self.img.blocks_allocated.keys():
						self.img.blocks_allocated[inode.block_ptrs[12]] = Ext2Block(inode.block_ptrs[12], 1, inode.inode_num, self.img.get_logic_offset_first_indir_block())
					self.img.blocks_allocated[inode.block_ptrs[12]].refs.append(Ext2Block(inode.block_ptrs[12], 1, inode.inode_num, self.img.get_logic_offset_first_indir_block()))
				# Double indirection block pointers
				if inode.block_ptrs[13] < 0 or inode.block_ptrs[13] > max_block_num:		
						self.msg_handler.block_invalid_error(inode.block_ptrs[13], inode.inode_num, self.img.get_logic_offset_first_doub_indir_block(), 2)
				if inode.block_ptrs[13] > 0 and inode.block_ptrs[13] < first_legal_block_num:		
						self.msg_handler.block_reserved_error(inode.block_ptrs[13], inode.inode_num, self.img.get_logic_offset_first_doub_indir_block(), 2)
				if inode.block_ptrs[13] > 0:
					if inode.block_ptrs[13] not in self.img.blocks_allocated.keys():
						self.img.blocks_allocated[inode.block_ptrs[13]] = Ext2Block(inode.block_ptrs[13], 2, inode.inode_num, self.img.get_logic_offset_first_doub_indir_block())
					self.img.blocks_allocated[inode.block_ptrs[13]].refs.append(Ext2Block(inode.block_ptrs[13], 2, inode.inode_num, self.img.get_logic_offset_first_doub_indir_block()))
				# Triple indirection block pointers
				if inode.block_ptrs[14] < 0 or inode.block_ptrs[14] > max_block_num:		
						self.msg_handler.block_invalid_error(inode.block_ptrs[14], inode.inode_num, self.img.get_logic_offset_first_trip_indir_block(), 3)
				if inode.block_ptrs[14] > 0 and inode.block_ptrs[14] < first_legal_block_num:		
						self.msg_handler.block_reserved_error(inode.block_ptrs[14], inode.inode_num, self.img.get_logic_offset_first_trip_indir_block(), 3)	
				if inode.block_ptrs[14] > 0:
					if inode.block_ptrs[14] not in self.img.blocks_allocated.keys():
						self.img.blocks_allocated[inode.block_ptrs[14]] = Ext2Block(inode.block_ptrs[14], 3, inode.inode_num, self.img.get_logic_offset_first_trip_indir_block())	
					self.img.blocks_allocated[inode.block_ptrs[14]].refs.append(Ext2Block(inode.block_ptrs[14], 3, inode.inode_num, self.img.get_logic_offset_first_trip_indir_block()))
		# Check INDIRECT lines from CSV
		for indir_block_ref in self.img.indir_block_refs:
			# Block number of the indirect block being scanned
			# TODO: do we need to check if already saw block num in INODE lines?
			# if indir_block_ref.indir_block_num < 0 or indir_block_ref.indir_block_num > max_block_num:
			# 	self.msg_handler.block_invalid_error(indir_block_ref.indir_block_num, indir_block_ref.inode_num, indir_block_ref.offset, indir_block_ref.level_of_indir)
			# if indir_block_ref.indir_block_num > 0 and indir_block_ref.indir_block_num < first_legal_block_num:
			# 	self.msg_handler.block_reserved_error(indir_block_ref.indir_block_num, indir_block_ref.inode_num, indir_block_ref.offset, indir_block_ref.level_of_indir)
			# if indir_block_ref.indir_block_num > 0:
			# 	if indir_block_ref.indir_block_num not in self.img.blocks_allocated.keys():
			# 		self.img.blocks_allocated[indir_block_ref.indir_block_num] = Ext2Block(indir_block_ref.indir_block_num, indir_block_ref.level_of_indir, indir_block_ref.inode_num, indir_block_ref.offset)
			# 	self.img.blocks_allocated[indir_block_ref.indir_block_num].refs.append(Ext2Block(indir_block_ref.indir_block_num, indir_block_ref.level_of_indir, indir_block_ref.inode_num, indir_block_ref.offset))
			# Block number of the referenced block
			if indir_block_ref.refd_block_num < 0 or indir_block_ref.refd_block_num > max_block_num:		
				self.msg_handler.block_invalid_error(indir_block_ref.refd_block_num, indir_block_ref.inode_num, indir_block_ref.offset, indir_block_ref.level_of_indir - 1)
			if indir_block_ref.refd_block_num > 0 and indir_block_ref.refd_block_num < first_legal_block_num:		
				self.msg_handler.block_reserved_error(indir_block_ref.refd_block_num, indir_block_ref.inode_num, indir_block_ref.offset, indir_block_ref.level_of_indir - 1)
			if indir_block_ref.refd_block_num > 0:
				if indir_block_ref.refd_block_num not in self.img.blocks_allocated.keys():
					self.img.blocks_allocated[indir_block_ref.refd_block_num] = Ext2Block(indir_block_ref.refd_block_num, indir_block_ref.level_of_indir - 1, indir_block_ref.inode_num, indir_block_ref.offset)
				self.img.blocks_allocated[indir_block_ref.refd_block_num].refs.append(Ext2Block(indir_block_ref.refd_block_num, indir_block_ref.level_of_indir - 1, indir_block_ref.inode_num, indir_block_ref.offset))
		for i in range(first_legal_block_num, max_block_num + 1):
			if i not in self.img.blocks_allocated.keys() and i not in self.img.blocks_on_freelist:
				self.msg_handler.block_unref_and_used_error(i)
			if i in self.img.blocks_allocated.keys() and i in self.img.blocks_on_freelist:
				self.msg_handler.block_alloc_and_free_error(i)
			if i in self.img.blocks_allocated.keys():
				num_refs = len(self.img.blocks_allocated[i].refs)
				if num_refs > 1:
					for j in range(0, num_refs):
						# print(self.img.blocks_allocated[i].refs[j])
						self.msg_handler.block_duplicate_error(self.img.blocks_allocated[i].refs[j].block_num, self.img.blocks_allocated[i].refs[j].inode_num, self.img.blocks_allocated[i].refs[j].offset, self.img.blocks_allocated[i].refs[j].level_of_indir)
	# I-node Allocation Audits
	def find_inode_errors(self):
		# TODO
		for key in self.img.inodes_alloc:
			if key in self.img.inodes_on_freelist:
				self.msg_handler.inode_alloc_on_freelist_error(key)
		for inode_num in range(11, self.img.superblock.inodes_count + 1):
			if inode_num not in self.img.inodes_alloc and inode_num not in self.img.inodes_on_freelist:
				self.msg_handler.inode_unalloc_not_on_freelist_error(inode_num)
	# Directory Consistency Audits
	def find_dir_errors(self):
		# TODO
		pass
	def find_all_errors(self):
		self.find_block_errors()
		self.find_inode_errors()
		self.find_dir_errors()

def main():
	if (len(sys.argv) != 2):
		sys.stderr.write("Error: invalid number of arguments.\nusage: ./lab3b [CSV FILE NAME]\n")
		sys.exit(1)
	try:
		with open(sys.argv[1], 'r') as file:
			check = csv.reader(file, delimiter=',')
	except:
		sys.stderr.write("Error: unable to open required file.\n")
		sys.exit(1)
	checker = Ext2Checker(sys.argv[1])
	checker.find_all_errors()
    
if __name__ == "__main__":
    main()
