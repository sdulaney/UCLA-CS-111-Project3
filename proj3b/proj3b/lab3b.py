# NAME: Stewart Dulaney,Pariya Samandi
# EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
# ID: 904064791,205092357

#!/usr/bin/env python3


#To Do based on TA discussion:
#Save the .csv in a structure/class
#Create a class or a function that prints out and formats all possible error messages
#Refer to the .csv and that function a lot
#Report on inconsistencies & errors on inodes, blocks, directories



import sys, string, locale

def lists_init():
	#List of map block numbers 
	map_block_num = []
	map_inode_num = []
	with open("group.csv", "r") as file_1:
		for line in file_1:
			group_line = line.rstrip('\n').split(',')
			map_block_num.append(group_line[5])
			map_inode_num.append(group_line[4])

	#List of free blocks & inodes
	free_blocks = []
	free_inodes = []
	with open("bitmap.csv", "r") as file_2:
		for line in file_2:
			bitmap_l = line.rstrip('\n').split(',')
			if(bitmap_l[0] in map_block_num):
				free_blocks.append(int(bitmap_l[1]))
			if(bitmap_l[0] in map_inode_num):
				free_inodes.append(int(bitmap_l[1]))

	#Important info from super block
	block_s = 0
	total_inodes = 0
	inodes_in_group = 0
	total_blocks = 0
	with open("super.csv", "r") as file_3:
		for line in file_3:
			super_line = line.rstrip('\n').split(',')
			total_blocks = int(super_line[2])
			block_s = int(super_line[3])
			total_inodes = int(super_line[1])
			inodes_in_group = int(super_line[6])

	#Return a tuple of lists to be able to index into to get the respective values
	return (free_blocks, free_inodes, map_block_num, map_inode_num, block_s, total_inodes, inodes_in_group, total_blocks)


def block_errors(out_file):
    ...
def duplicate_allocated_blocks(out_file):
    ...

def unallocated_inode(directory_file, out_file):
    ...
def missing_inode(inode_file, out_file):
    ...
def incorrect_link_count(inode_file, out_file):
    ...
def incorrect_directory_entry(directory_file, out_file):
    ...
def open_files():
    ...
def close_files():
    ...
def main():
    ...
    