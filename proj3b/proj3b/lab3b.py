# NAME: Stewart Dulaney,Pariya Samandi
# EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
# ID: 904064791,205092357

#!/usr/bin/env python3

#To Do based on TA discussion:
#Save the .csv in a structure/class
#Create a class or a function that prints out and formats all possible error messages
#Refer to the .csv and that function a lot
#Report on inconsistencies & errors on inodes, blocks, directories

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

# TODO
class Ext2Block:
	def __init__(self):
		return self.first_nonres_inode + (128*self.inodes_count-1)/self.block_size+1

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
	def __init__(self, inode_num, level_of_indir, logical_block_offset, indir_block_num, refd_block_num):
		self.inode_num = inode_num
		self.level_of_indir = level_of_indir
		self.logical_block_offset = logical_block_offset
		self.indir_block_num = indir_block_num
		self.refd_block_num = refd_block_num

class Ext2Image:
	def __init__(self, filename):
		self.rows = []
		# self.superblock = None
		self.group = None
		self.blocks_on_freelist = set()
		self.inodes_on_freelist = set()
		self.inodes_alloc = dict()
		self.indir_block_refs = []
		self.read_csv(filename)
		self.parse_csv()
	def read_csv(self, filename):
		with open(filename, "r") as csvfile:
			csvreader = csv.reader(csvfile)
			for row in csvreader:
				if any(x.strip() for x in row):			# handle empty lines
					self.rows.append([x.strip(' ') for x in row]) # handle leading/trailing whitespace in cells
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

class Ext2ErrorMsgHandler:
	def __init__(self):
		pass
	# Block Consistency Errors
	def block_invalid_error(self, block_num, inode_num, offset, level_of_indir):
		indir_str = ""							# assume level_of_indir = 0 means no indirection
		indir_offset = 0
		if level_of_indir == 1:
			indir_str = "INDIRECT "
		elif level_of_indir == 2:
			indir_str = "DOUBLE INDIRECT "
			indir_offset = 255
		elif level_of_indir == 3:
			indir_str = "TRIPLE INDIRECT "
			indir_offset = 65535 + 255
		sys.stdout.write(f"INVALID {indir_str}BLOCK {block_num} IN INODE {inode_num} AT OFFSET {offset + indir_offset}\n")
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
		# TODO: handle different file types
		for inode in self.img.inodes_alloc.values():
			if (inode.file_type == 'f') or (inode.file_type == 'd') or (file_type == 's' and inode.file_size > 60):
				for i in range(0,12):
					if inode.block_ptrs[i] < 0 or inode.block_ptrs[i] > self.img.superblock.blocks_count:		# block group 0 starts with block 1 on 1KB block systems
						self.msg_handler.block_invalid_error(inode.block_ptrs[i], inode.inode_num, i, 0)
				if inode.block_ptrs[12] < 0 or inode.block_ptrs[12] > self.img.superblock.blocks_count:		# block group 0 starts with block 1 on 1KB block systems
						self.msg_handler.block_invalid_error(inode.block_ptrs[12], inode.inode_num, 12, 1)
				if inode.block_ptrs[13] < 0 or inode.block_ptrs[13] > self.img.superblock.blocks_count:		# block group 0 starts with block 1 on 1KB block systems
						self.msg_handler.block_invalid_error(inode.block_ptrs[13], inode.inode_num, 13, 2)
				if inode.block_ptrs[14] < 0 or inode.block_ptrs[14] > self.img.superblock.blocks_count:		# block group 0 starts with block 1 on 1KB block systems
						self.msg_handler.block_invalid_error(inode.block_ptrs[14], inode.inode_num, 14, 3)
				
		# TODO
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
	# TODO: add error checking for no arguments, too many arguments, invalid arguments or unable to open required files: https://piazza.com/class/k4x6oonkcge2mj
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
