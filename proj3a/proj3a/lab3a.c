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
struct super_t *super;
struct group_t *group;
int **valid_Inode_Directory;
int valid_Inode_Directory_Num = 0;
int *valid_Inodes;
int valid_Inode_Num = 0;

struct super_t
{
    uint16_t m_num;
    uint32_t inode_Num, block_Num, block_S, fragment_S, blocks_In_Group, inodes_In_Group, fragments_In_Group, first_Data_Block;
};

struct group_t
{
    uint16_t contain_Block_Num, free_Block_Num, free_Inode_Num, directory_Num;
    uint32_t inode_Bitmap_Block, block_Bitmap_Block, inode_Table_Block;
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
    super = malloc(sizeof(struct super_t));
    group = malloc(sizeof(struct group_t));
    image_Fd = open(file_Name, O_RDONLY);
    if (image_Fd == -1)
    {
        fprintf(stderr, "Error: the file %s could not be opened.\n", file_Name);
        exit(2);
    }
}

int get_block_offset(int block_num)
{
    return SUPER_BLOCK_OFFSET + (super->block_S * (block_num - 1));
}

// Superblock summary
void parsing_SuperB()
{
    //Read, Write, and execute permission ==> S_IRUSR | S_IWUSR | S_IXUSR ==> S_IRWXU
    super_Fd = creat("superFile.csv", S_IRWXU);
    //Reading from Descriptor with Offset
    pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + 56);
    // super->magicNumber = buffer_16;
    dprintf(super_Fd, "%x,", super->m_num);

    //Counting inode
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 0);
    super->inode_Num = buffer_32;
    dprintf(super_Fd, "%d,", super->inode_Num);

    //Counting # of blocks
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 4);
    super->block_Num = buffer_32;
    dprintf(super_Fd, "%d,", super->block_Num);

    //Size of block
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 24);
    super->block_S = 1024 << buffer_32;
    dprintf(super_Fd, "%d,", super->block_S);

    // Fragment size
    pread(image_Fd, &sBuffer_32, 4, SUPER_BLOCK_OFFSET + 28);
    if (sBuffer_32 > 0)
    {
        super->fragment_S = 1024 << sBuffer_32;
    }
    else
    {
        super->fragment_S = 1024 >> -sBuffer_32;
    }
    dprintf(super_Fd, "%d,", super->fragment_S);

    // Blocks per group
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 32);
    super->blocks_In_Group = buffer_32;
    dprintf(super_Fd, "%d,", super->blocks_In_Group);

    // inodes per group
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 40);
    super->inodes_In_Group = buffer_32;
    dprintf(super_Fd, "%d,", super->inodes_In_Group);

    // Fragments per group
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 36);
    super->fragments_In_Group = buffer_32;
    dprintf(super_Fd, "%d,", super->fragments_In_Group);

    // First data block
    pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + 20);
    super->first_Data_Block = buffer_32;
    dprintf(super_Fd, "%d\n", super->first_Data_Block);

    // Close csv file
    close(super_Fd);
}

// Group summary
void parsing_GroupB()
{
    // Create csv file
    group_Fd = creat("group.csv", S_IRWXU);

    // Calculate number of groups
    int numGroups = ceil((double)super->block_Num / super->blocks_In_Group);
    double remainder = numGroups - ((double)super->block_Num / super->blocks_In_Group);

    group = malloc(numGroups * sizeof(struct group_t));

    int i;
    for (i = 0; i < numGroups; i++)
    {

        // Number of contained blocks
        if (i != numGroups - 1 || remainder == 0)
        {
            group[i].contain_Block_Num = super->blocks_In_Group;
            dprintf(group_Fd, "%d,", group[i].contain_Block_Num);
        }
        else
        {
            group[i].contain_Block_Num = super->blocks_In_Group * remainder;
            dprintf(group_Fd, "%d,", group[i].contain_Block_Num);
        }

        // Number of free blocks
        pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 12);
        group[i].free_Block_Num = buffer_16;
        dprintf(group_Fd, "%d,", group[i].free_Block_Num);

        // Number of free inodes
        pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 14);
        group[i].free_Inode_Num = buffer_16;
        dprintf(group_Fd, "%d,", group[i].free_Inode_Num);

        // Number of directories
        pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 16);
        group[i].directory_Num = buffer_16;
        dprintf(group_Fd, "%d,", group[i].directory_Num);

        // Free inode bitmap block
        pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 4);
        group[i].inode_Bitmap_Block = buffer_32;
        dprintf(group_Fd, "%x,", group[i].inode_Bitmap_Block);

        // Free block bitmap block
        pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 0);
        group[i].block_Bitmap_Block = buffer_32;
        dprintf(group_Fd, "%x,", group[i].block_Bitmap_Block);

        // Inode table start block
        pread(image_Fd, &buffer_32, 4, SUPER_BLOCK_OFFSET + SUPER_BLOCK_SIZE + (i * GROUP_DESCRIPTOR_TABLE_SIZE) + 8);
        group[i].inode_Table_Block = buffer_32;
        dprintf(group_Fd, "%x\n", group[i].inode_Table_Block);
    }

    // Close csv file
    close(group_Fd);
}

// Free block entries, Free I-node entries
void parsing_bitM()
{
}

// I-node summary
void parsing_inode()
{
}

// Directory entries
void parsing_dir()
{
}

// Indirect block references
void parsing_inDir()
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
    parsing_SuperB();

    exit(EXIT_SUCCESS);
}
