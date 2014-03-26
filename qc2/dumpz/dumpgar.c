/* dumpgara:

   in Hexdump:

      mogeljkheid van een wig met 15 unitsop de 15e rij
      wordt op 18 eenheden gegoten

   program read code-files the last record first

   keeps track of the position of the wedges D10 & D11,

   when the wedges are in position, the correction code will be ignored
   but for variable spaces, the code will be inserted, if needed

   versie 18 december 2004

   interactie met interface:



   using the keyboard: bit 0 will be set, when only one or zero bits are set.

   25 november:

   casting cases:

       depending on a 5 -wedge  536 = garamond

       wishes:
	  row of characters behind each other


   hexdump : #include < c:\qc2\dump_y\dumpin11.c >
       was dumpin01
   control : #include < c:\qc2\dump_y\intfdump.c >
   cases2                             dumpin01c
   ontcijfer
   ontcijfer2
   wig :
 */

#include <stdio.h>

#include <io.h>
#include <string.h>
#include <conio.h>
#include <dos.h>
#include <stdlib.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <process.h>
#include <bios.h>
#include <graph.h>
#include <ctype.h>
#include <fcntl.h>
#include <time.h>
#include <sys\types.h>
#include <sys\stat.h>
#include <malloc.h>
#include <errno.h>

#define    poort1   0x278
#define    poort2   0x378
#define    poort3   0x3BC
#define    FALSE    0
#define    TRUE     1
#define    MAX      60

typedef struct monocode {
    unsigned char mcode[5];
    /*
	byte 0: O N M L   K J I H
	byte 1: G F S E   D g C B   g = '0075'
	byte 2: A 1 2 3   4 5 6 7
	byte 3: 8 9 a b   c d e k   k = '0005'
	byte 4: seperator byte
	      0xf0 = in file
	      0xff = eof-teken
     */
} ;

int  width_row15;
int  w18_u1;
int  w18_u2;

int ad_05, ad_75;

void choose_wedge();
void adjust (int set, int row, int width );

unsigned char bitc[8] = {
	0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 };

int  regelnr;

int  rnr, cnr;

int        poort;
char       pnr;

/* #define BCSP 1 */

int statx1;
int statx2;

/* void spaces() */

int try_x;

char line_buffer[MAX+2];
int glc, gli, gllim=MAX;

int getlineAO();
int getline10();
int get_line();

void exit1();

#include <c:\qc2\dump_y\getline.c>

int    get__line(int row, int col);
double get__float(int row, int col);
int    get__dikte(int row, int col);
int    get__int(int row, int col);
int    get__row(int row, int col);
int    get__col(int row, int col);
void thin_spaces();

/* #include <c:\qc2\dump\incxdump.c> */

void intro();
char menu();
char sgnl;
void composition();
void punching();
void test();
void aline_caster();
void spaces();
void cases2();       /* in:      */

void apart();
void apart2();
void apart3();
int  case_j;

void cases();
void test_caster();
void control38();
void print_at( unsigned int r, unsigned int c, char x[] );


#include <c:\qc2\dump_y\incxdump.c>
  /* get_line (); */

#include <c:\qc2\dump_y\inc0dump.c>
     /* test_caster() */
     /* l[  */

int test_O15();
int pstart75;
int pstart05;
int pi75;
int pi05;

unsigned char cancellor[4];

#include <c:\qc2\dump_y\intfdump.c>


  /* noodstop
     test_row()
     int test_NK()
     int test_NJ()
     int test2_NK()
     int test2_NJ()
     int test_GS()
     int test_N()
     int test_k()
     int test_g()

     gotoXY(inr row, int column)

  */




#include <c:\qc2\dump_y\menu.c>
/*
#include <c:\qc2\dump_y\adjust.c>
 */
#include <c:\qc2\dump_y\dumpin11.c>


/* SEEK.C illustrates low-level file I/O functions including:
 *      filelength      lseek           tell
 */


void error( char *errmsg );
void error( char *errmsg )
{
    perror( errmsg );
    exit( 1 );
}

/* RECORDS2.C illustrates reading and writing of file records with the

128 � 80 200  144 � 90 220  160 � a0 240  176 �    192 �    208 �    224 �   240 �
129 � 81 201  145 � 91 221  161 � a1 241  177 �    193 �    209 �    225 �   241 �
130 � 82 202  146 � 92 222  162 � a2 242  178 �    194 �    210 �    226 �   242 �
131 � 83 203  147 � 93 223  163 � a3 243  179 �    195 �    211 �    227 �   243 �
132 � 84 204  148 � 94 224  164 � a4 244  180 �    196 �    212 �    228 �   244 �
133 � 85 205  149 � 95 225  165 � a5 245  181 �    197 �    213 �    229 �   245 �
134 � 86 206  150 � 96 226  166 � a6 246  182 �    198 �    214 �    230 �   246 �
135 � 87 207  151 � 97 227  167 � a7 247  183 �    199 �    215 �    231 �   247 �
136 � 88 210  152 � 98 230  168 � a8 250  184 �    200 �    216 �    232 �   248 �
137 � 89 211  153 � 99 231  169 � a9 251  185 �    201 �    217 �    233 �   249 �
138 � 8a 212  154 � 9a 232  170 � aa 252  186 �    202 �    218 �    234 �   250 �
139 � 8b 213  155 � 9b 233  171 � ab 253  187 �    203 �    219 �    235 �   251 �
140 � 8c 214  156 � 9c 234  172 � ac 254  188 �    204 �    220 �    236 �   252 �
141 � 8d 215  157 � 9d 235  173 � ad 255  189 �    205 �    221 �    237 �   253 �
142 � 8e 216  158 � 9e 236  174 � ae 256  190 �    206 �    222 �    238 �   254 �
143 � 8f 217  159 � 9f 237  175 � af 257  191 �    207 �    223 �    239 �   255


128 �      144 �      160 �    176 �    192 �    208 �    224 �   240 �
129 �      145 �      161 �    177 �    193 �    209 �    225 �   241 �
130 �      146 �      162 �    178 �    194 �    210 �    226 �   242 �
131 �      147 �      163 �    179 �    195 �    211 �    227 �   243 �
132 �      148 �      164 �    180 �    196 �    212 �    228 �   244 �
133 �      149 �      165 �    181 �    197 �    213 �    229 �   245 �
134 �      150 �      166 �    182 �    198 �    214 �    230 �   246 �
135 �      151 �      167 �    183 �    199 �    215 �    231 �   247 �
136 �      152 �      168 �    184 �    200 �    216 �    232 �   248 �
137 �      153 �      169 �    185 �    201 �    217 �    233 �   249 �
138 �      154 �      170 �    186 �    202 �    218 �    234 �   250 �
139 �      155 �      171 �    187 �    203 �    219 �    235 �   251 �
140 �      156 �      172 �    188 �    204 �    220 �    236 �   252 �
141 �      157 �      173 �    189 �    205 �    221 �    237 �   253 �
142 �      158 �      174 �    190 �    206 �    222 �    238 �   254 �
143 �      159 �      175 �    191 �    207 �    223 �    239 �   255

*/

#include <c:\qc2\dump_y\get__rtn.c>

main()
{
    int stoppen;
    int c, c1, newrec, ctest;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t *recpos;
    int a=0, b=0;
    double flo;

    intro();
    /* standaard instelling wig */

    menu();

    if (getchar()=='#')exit(1);



    interf_aan = 0;
    caster = ' ';

    do {
       c = '\0';
       cls();
       printf("Test interface <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  interf_aan = 0;
	  caster = ' ';
	  startinterface();
	  test();
       }
    }
       while ( c != 'n');


    do {
       c = '\0';
       cls();
       printf("aline the caster <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }


       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  if (caster != 'c' ) {
	       caster = ' ';
	       interf_aan = 0;
	  }
	  if ( ! interf_aan ) {
	       startinterface();
	  }
	  aline_caster();
       }
    }
       while ( c != 'n');

    do {
       c = '\0';
       cls();
       printf("aline the diecase  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getch(); }

       /*
       get_line();
       c = line_buffer[0];
	*/

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  do {
	     if (caster != 'c' ) {
		interf_aan = 0;
		caster = ' ';
	     }
	     if ( ! interf_aan ) {
		startinterface();
	     }
	  }
	     while (caster != 'c' );
	  apart2();
       }
    }
       while ( c != 'n');
    do {
       c = '\0';
       cls();
       printf("test low quad  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }
       /*
       get_line();
       c = line_buffer[0];
	*/
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  do {
	     if (caster != 'c' ) {
		interf_aan = 0;
		caster = ' ';
	     }
	     if ( ! interf_aan ) {
		startinterface();
	     }
	  }
	     while (caster != 'c' );
	  apart3();
       }
    }
       while ( c != 'n');

    /*
	 test();   test interface  c:\qc2\dump_y\inc0dump.c
	 aline_caster();
	 apart2(); aline diecase
	 apart3(); printf("test low quad  <y/n> ? ");
     */



    do {
       c = '\0';
       cls();
       printf("casting separate character  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  do {
	     if (caster != 'c' ) {
		interf_aan = 0;
		caster = ' ';
	     }
	     if ( ! interf_aan ) {
		startinterface();
	     }
	  }
	     while (caster != 'c' );
	  apart();
       }
    }
       while ( c != 'n');


    do {
       c = '\0';
       cls();
       printf("casting spaces <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  if (caster != 'c' ) {
	      interf_aan = 0;
	      caster = ' ';
	  }
	  if ( ! interf_aan ) {
	      startinterface();
	  }
	  spaces();
       }
    }
       while ( c != 'n');

    /*
	 apart in: incxdump
	 read_row in:

	 test();   printf("test interface ");
	 aline_caster();
	 apart2(); aline diecase
	 apart3(); printf("test low quad  <y/n> ? ");
	 apart();  printf("casting separate character  <y/n> ? ");
	 spaces(); printf("casting spaces <y/n> ? ");
	 cases();  printf("cast cases  <y/n> ? ");
	 hexdump(); printf("casting files ");

     */


    do {
       c = '\0';
       cls();
       printf("cast cases  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  if (caster != 'c' ) {
	       caster = ' ';
	       interf_aan = 0;
	  }
	  if ( ! interf_aan ) {
	       startinterface();
	  }
	  cases();
       }
    }
       while ( c != 'n');



    do {
       interf_aan = 0;
       caster = ' ';

       if ( ! interf_aan ) {
	    startinterface();
       }
       stoppen = 0;

       hexdump();

       printf("File succesfully transferred \n\n");
       printf("Another file ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }
       /*
       get_line();
	*/

       switch ( c ) {
	  case 'Y' : line_buffer[0]='y'; break;
	  case 'J' : line_buffer[0]='y'; break;
	  case 'N' : line_buffer[0]='n'; break;
       }
       if (getchar()=='#') exit(1);
       stoppen = (line_buffer[0] != 'y');
    }
       while ( ! stoppen );




    exit(1);


    if (getchar()=='#') exit(1);



    records1();

}


