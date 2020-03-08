/*
  NAME: Stewart Dulaney,Pariya Samandi
  EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
  ID: 904-064-791,205-092-357
 */

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <inttypes.h>
#include <math.h>
#include <time.h>
#include "ext2_fs.h"

//offset of 1024 bytes from the start of the device (from TA slide)
#define SUPER_BLOCK_OFFSET 1024
#define SUPER_BLOCK_SIZE 1024
#define INODE_BLOCK_PTR_WIDTH 4
#define GROUP_DESCRIPTOR_TABLE_SIZE 32
#define INODE_S 128

char *file_Name;
int image_Fd, super_Fd, group_Fd, bitmap_Fd, inode_Fd, directory_Fd, indirect_Fd;
int _stat, sBuffer_32;
int Group_Num;
uint64_t buffer_64;
uint32_t buffer_32;
uint16_t buffer_16;
uint8_t buffer_8;
struct super_block_t *super;
struct block_group_t *group;
int **valid_Inode_Directory;
int valid_Inode_Directory_Num = 0;
int *valid_Inodes;
int valid_num_inodes = 0;

struct super_block_t
{
    uint16_t m_num;
    uint32_t num_blocks, num_inodes, block_size, inode_size, blocks_per_group, inodes_per_group, first_non_res_inode, fragment_S, fragments_In_Group, first_data_block;
};

struct block_group_t
{
    uint16_t num_blocks, num_inodes, free_num_blocks, free_num_inodes, directory_Num;
    uint32_t inode_bitmap_block, block_bitmap_block, inode_table_block;
};

// Helper Functions
void parsing_arg(int argc, char **argv)
{
    if (argc == 2)
    {
        file_Name = malloc((strlen(argv[1]) + 1) * sizeof(char));
        file_Name = argv[1];
    }

    else
    {
        fprintf(stderr, "Error in argument number! \n");
        exit(EXIT_FAILURE);
    }
    return;
}

void alloc_mem() //Allocating memory as well as opening the read only image
{
    super = malloc(sizeof(struct super_block_t));
    group = malloc(sizeof(struct block_group_t));
    image_Fd = open(file_Name, O_RDONLY);
    if (image_Fd == -1)
    {
        fprintf(stderr, "Error: the file %s could not be opened.\n", file_Name);
        exit(2);
    }
}

int get_block_offset(int num_blocks)
{
    return SUPER_BLOCK_OFFSET + (super->block_size * (num_blocks - 1));
}

// Superblock summary
void print_superblock()
{
    //Read, Write, and execute permission ==> S_IRUSR | S_IWUSR | S_IXUSR ==> S_IRWXU
    // super_Fd = creat("superFile.csv", S_IRWXU);
    //Reading from Descriptor with Offset
    // pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + 56);
    // super->magicNumber = buffer_16;
    // dprintf(super_Fd, "%x,", super->m_num);

    dprintf(STDOUT_FILENO, "SUPERBLOCK,");

    //Counting # of blocks
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 4);
    super->num_blocks = buffer_32;
    dprintf(STDOUT_FILENO, "%d,", super->num_blocks);

    //Counting inode
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 0);
    super->num_inodes = buffer_32;
    dprintf(STDOUT_FILENO, "%d,", super->num_inodes);

    //Size of block
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 24);
    super->block_size = 1024 << buffer_32;
    dprintf(STDOUT_FILENO, "%d,", super->block_size);

    //Size of inode
    pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + 88);
    super->inode_size = buffer_16;
    dprintf(STDOUT_FILENO, "%d,", super->inode_size);

    // Fragment size
    // pread(image_Fd, &sBuffer_32, 4, SUPER_BLOCK_OFFSET + 28);
    // if (sBuffer_32 > 0)
    // {
    //     super->fragment_S = 1024 << sBuffer_32;
    // }
    // else
    // {
    //     super->fragment_S = 1024 >> -sBuffer_32;
    // }
    // dprintf(super_Fd, "%d,", super->fragment_S);

    // Blocks per group
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 32);
    super->blocks_per_group = buffer_32;
    dprintf(STDOUT_FILENO, "%d,", super->blocks_per_group);

    // inodes per group
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 40);
    super->inodes_per_group = buffer_32;
    dprintf(STDOUT_FILENO, "%d,", super->inodes_per_group);

    // First non-reserved inode
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 84);
    super->first_non_res_inode = buffer_32;
    dprintf(STDOUT_FILENO, "%d\n", super->first_non_res_inode);

    // Fragments per group
    // pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 36);
    // super->fragments_In_Group = buffer_32;
    // dprintf(super_Fd, "%d,", super->fragments_In_Group);

    // First data block
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 20);
    super->first_data_block = buffer_32;

    // Close csv file
    // close(super_Fd);
}

// Free block entries
void print_free_block_entries(int group_num, int block_bitmap_block)
{
    // 1 means “used” and 0 “free/available”
    int num_bytes = ceil((double) group[group_num].num_blocks / 8) * sizeof(char);
    char* buf = malloc(num_bytes);
    unsigned long long curr_block = 1;
    unsigned long long offset = get_block_offset(block_bitmap_block);
    pread(image_Fd, buf, num_bytes, offset);
    int i;
    for (i = 0; i < num_bytes; i++)
    {
        char c = buf[i];
        int j;
        for (j = 0; j < 8; j++)
        {
            int free = !(c & 1);
            if (free)
                dprintf(STDOUT_FILENO, "BFREE,%llu\n", curr_block);
            c = c >> 1;
            curr_block++;
            if (curr_block > group[group_num].num_blocks)
                break;
        }
    }
    free(buf);
}

// I-node summary
void print_inode(int inode_num, int inode_table_block)
{
    struct ext2_inode inode;
    unsigned long long offset = get_block_offset(inode_table_block) + (inode_num - 1) * sizeof(inode);
    pread(image_Fd, &inode, sizeof(inode), offset);
    if (inode.i_mode == 0 || inode.i_links_count == 0)
        return;
    char file_type = '?';
    buffer_16 = inode.i_mode & 0xF000;
    if (buffer_16 == 0x8000)
        file_type = 'f';
    else if (buffer_16 == 0x4000)
        file_type = 'd';
    else if (buffer_16 == 0xA000)
        file_type = 's';
    uint16_t mode = inode.i_mode & 0x0FFF;
    const int time_str_len = 19;

    time_t chg_time = inode.i_ctime;
    struct tm* chg_info = gmtime(&chg_time);
    char chg_time_str[time_str_len];
    strftime(chg_time_str, time_str_len, "%m/%d/%y %H:%M:%S", chg_info);

    time_t mod_time = inode.i_mtime;
    struct tm* mod_info = gmtime(&mod_time);
    char mod_time_str[time_str_len];
    strftime(mod_time_str, time_str_len, "%m/%d/%y %H:%M:%S", mod_info);

    time_t acc_time = inode.i_atime;
    struct tm* acc_info = gmtime(&acc_time);
    char acc_time_str[time_str_len];
    strftime(acc_time_str, time_str_len, "%m/%d/%y %H:%M:%S", acc_info);

    dprintf(STDOUT_FILENO, "INODE,%d,%c,%o,%d,%d,%d,%s,%s,%s,%d,%d", inode_num, file_type, mode, inode.i_uid, inode.i_gid, inode.i_links_count, chg_time_str, mod_time_str, acc_time_str, inode.i_size, inode.i_blocks);

    if (file_type == 's' && inode.i_size <= 60)
    {
        dprintf(STDOUT_FILENO, "\n");
        return;
    }
    else
    {
        dprintf(STDOUT_FILENO, ",");
    }

    if (file_type == 'f' || file_type == 'd' || (file_type == 's' && inode.i_size > 60))
    {
        int i;
        for (i = 0; i < 15; i++)
        {
            if (i == 14)
                dprintf(STDOUT_FILENO, "%d\n", inode.i_block[i]);
            else
                dprintf(STDOUT_FILENO, "%d,", inode.i_block[i]);
        }
    }
}

// Free I-node entries
void print_free_inode_entries(int group_num, int inode_bitmap_block)
{
    // 1 means “used” and 0 “free/available”
    int num_bytes = ceil((double) group[group_num].num_inodes / 8) * sizeof(char);
    char* buf = malloc(num_bytes);
    unsigned long long curr_inode = 1;
    unsigned long long offset = get_block_offset(inode_bitmap_block);
    pread(image_Fd, buf, num_bytes, offset);
    int i;
    for (i = 0; i < num_bytes; i++)
    {
        char c = buf[i];
        int j;
        for (j = 0; j < 8; j++)
        {
            int free = !(c & 1);
            if (free)
                dprintf(STDOUT_FILENO, "IFREE,%llu\n", curr_inode);
            else
                print_inode(curr_inode, group[group_num].inode_table_block);
            c = c >> 1;
            curr_inode++;
            if (curr_inode > group[group_num].num_inodes)
                break;
        }
    }
    free(buf);
}

// Group summary
void print_group()
{
    // Create csv file
    // group_Fd = creat("group.csv", S_IRWXU);

    // Calculate number of groups
    int numGroups = ceil((double)super->num_blocks / super->blocks_per_group);
    int remainder = super->num_blocks % super->blocks_per_group;

    group = malloc(numGroups * sizeof(struct block_group_t));

    int i;
    for (i = 0; i < numGroups; i++)
    {
        dprintf(STDOUT_FILENO, "GROUP,%d,", i);

        // Number of contained blocks
        if (i != numGroups - 1 || remainder == 0)
        {
            group[i].num_blocks = super->blocks_per_group;
            dprintf(STDOUT_FILENO, "%d,", group[i].num_blocks);
        }
        else
        {
            group[i].num_blocks = remainder;
            dprintf(STDOUT_FILENO, "%d,", group[i].num_blocks);
        }

        // Number of inodes
        group[i].num_inodes = super->inodes_per_group;
        dprintf(STDOUT_FILENO, "%d,", group[i].num_inodes);

        // Number of free blocks
        pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 12);
        group[i].free_num_blocks = buffer_16;
        dprintf(STDOUT_FILENO, "%d,", group[i].free_num_blocks);

        // Number of free inodes
        pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 14);
        group[i].free_num_inodes = buffer_16;
        dprintf(STDOUT_FILENO, "%d,", group[i].free_num_inodes);

        // Number of directories
        // pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 16);
        // group[i].directory_Num = buffer_16;
        // dprintf(group_Fd, "%d,", group[i].directory_Num);

        // Free block bitmap block
        pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 0);
        group[i].block_bitmap_block = buffer_32;
        dprintf(STDOUT_FILENO, "%x,", group[i].block_bitmap_block);

        // Free inode bitmap block
        pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 4);
        group[i].inode_bitmap_block = buffer_32;
        dprintf(STDOUT_FILENO, "%x,", group[i].inode_bitmap_block);

        // Inode table start block
        pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 8);
        group[i].inode_table_block = buffer_32;
        dprintf(STDOUT_FILENO, "%x\n", group[i].inode_table_block);

        print_free_block_entries(i, group[i].block_bitmap_block);
        print_free_inode_entries(i, group[i].inode_bitmap_block);
    }

    // Close csv file
    // close(group_Fd);
}

// Directory entries
void print_dir_entries()
{
}

// Indirect block references
void print_indir_block_refs()
{
}

int main(int argc, char **argv)
{
    // Process all arguments
    int c;

    while (1)
    {
        int option_index = 0;
        static struct option long_options[] = {
            {0,
             0,
             0,
             0}};

        c = getopt_long(argc, argv, "",
                        long_options, &option_index);
        if (c == -1)
            break;

        // const char *name = long_options[option_index].name;
        switch (c)
        {
        case 0:
            // Long options
            break;

        case '?':
            fprintf(stderr, "usage: ./laba [IMAGE FILE NAME]\n");
            exit(EXIT_FAILURE);
            break;

        default:
            printf("?? getopt returned character code 0%o ??\n", c);
        }
    }

    parsing_arg(argc, argv);
    alloc_mem();
    print_superblock();
    print_group();

    exit(EXIT_SUCCESS);
}
