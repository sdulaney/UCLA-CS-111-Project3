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
#define SUPER_BLOCK_S 1024
#define INODE_BLOCK_PTR_WIDTH 4
#define GROUP_TABLE_SIZE 32
#define INODE_S 128

char *file_Name;
int image_Fd, super_Fd, group_Fd, bitmap_Fd, inode_Fd, directory_Fd, indirect_Fd;
int stat, sBuffer_32;
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
    uint32_t inode_Num, block_Num, block_S, fragment_S, blocks_In_Group, inodes_In_Group, fragments_In_Group, first_Data_Block
};

struct group_t
{
    uint16_t contain_Block_Num, free_Block_Num, free_Inode_Num, directory_Num;
    uint32_t inode_Bitmap_Block, block_Bitmap_Block, inode_Table_Block;
};

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
    image_Fd = open(fileName, O_RDONLY);
}

void parsing_SuperB()
{
    //Read, Write, and execute permission ==> S_IRUSR | S_IWUSR | S_IXUSR ==> S_IRWXU
    super_Fd = creat("superFile.csv", S_IRWXU);
    //Reading from Descriptor with Offset
    pread(image_Fd, &buffer_16, 2, SUPER_BLOCK_OFFSET + 56);
    super->magicNumber = buf16;
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

void parsing_GroupB()
{
}

void parsing_bitM()
{
}

void parsing_inode()
{
}

void parsing_dir()
{
}

void parsing_inDir()
{
}

int main()
{
}

// int num_threads = 0;
// int num_iterations = 0;
// int num_lists = 0;
// int opt_yield = 0;
// int opt_sync = 0;
// char *arg_sync = NULL;
// SortedListElement_t *element_arr = NULL;
// char **key_arr = NULL;
// SortedList_t *list_arr = NULL;
// pthread_mutex_t *lock_arr = NULL;
// int *spin_lock_arr = NULL;

// int main(int argc, char **argv)
// {

//     // Process all arguments
//     int c;
//     int opt_threads = 0;
//     int opt_iterations = 0;
//     int opt_lists = 0;
//     char *arg_threads = NULL;
//     char *arg_iterations = NULL;
//     char *arg_yield = NULL;
//     char *arg_lists = NULL;
//     char default_val = '1';

//     while (1)
//     {
//         int option_index = 0;
//         static struct option long_options[] = {
//             {"threads",
//              optional_argument,
//              0,
//              0},
//             {"iterations",
//              optional_argument,
//              0,
//              0},
//             {"yield",
//              required_argument,
//              0,
//              0},
//             {"sync",
//              required_argument,
//              0,
//              0},
//             {"lists",
//              required_argument,
//              0,
//              0},
//             {0,
//              0,
//              0,
//              0}};

//         c = getopt_long(argc, argv, "t::i::y:s:l:",
//                         long_options, &option_index);
//         if (c == -1)
//             break;

//         const char *name = long_options[option_index].name;
//         switch (c)
//         {
//         case 0:
//             if (strcmp(name, "threads") == 0)
//             {
//                 opt_threads = 1;
//                 if (optarg)
//                     arg_threads = optarg;
//                 else
//                     arg_threads = &default_val;
//             }
//             else if (strcmp(name, "iterations") == 0)
//             {
//                 opt_iterations = 1;
//                 if (optarg)
//                     arg_iterations = optarg;
//                 else
//                     arg_iterations = &default_val;
//             }
//             else if (strcmp(name, "sync") == 0)
//             {
//                 opt_sync = 1;
//                 if (optarg)
//                     arg_sync = optarg;
//             }
//             else if (strcmp(name, "yield") == 0)
//             {
//                 if (optarg)
//                 {
//                     arg_yield = optarg;
//                     int len = strlen(arg_yield);
//                     for (int i = 0; i < len; i++)
//                     {
//                         if (optarg[i] == 'i')
//                             opt_yield |= INSERT_YIELD;
//                         else if (optarg[i] == 'd')
//                             opt_yield |= DELETE_YIELD;
//                         else if (optarg[i] == 'l')
//                             opt_yield |= LOOKUP_YIELD;
//                     }
//                 }
//             }
//             else if (strcmp(name, "lists") == 0)
//             {
//                 opt_lists = 1;
//                 if (optarg)
//                     arg_lists = optarg;
//             }
//             break;

//         case '?':
//             fprintf(stderr, "usage: ./lab2_list [OPTION]...\nvalid options: --threads=# (default 1), --iterations=# (default 1), --yield=[idl], --sync=[ms], --lists=# (default 1)\n");
//             exit(1);
//             break;

//         default:
//             printf("?? getopt returned character code 0%o ??\n", c);
//         }
//     }

//     exit(0);
// }
