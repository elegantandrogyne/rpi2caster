/* c:\qc2\last02\monowtr6.c

      was: caslon\monocas6.c

		 caslon 12 punt
*/



int glc, gli;
int gllimit;



unsigned char kolcode[KOLAANTAL][4] = {
     0x42,    0,  0,   0,
     0x50,    0,  0,   0,
	0,    0,  0x80,0,
	0,    1,  0,   0,
	0,    2,  0,   0,
	0,    8,  0,   0,
	0, 0x10,  0,   0,
	0, 0x40,  0,   0,
	0, 0x80,  0,   0,
	1,    0,  0,   0,
	2,    0,  0,   0,
	4,    0,  0,   0,
	8,    0,  0,   0,
     0x10,    0,  0,   0,
     0x20,    0,  0,   0,
     0x40,    0,  0,   0,
	0,    0,  0,   0
};

unsigned char rijcode[RIJAANTAL][4] = {
      0, 0, 0x40, 0,
       0, 0, 0x20, 0,
       0, 0, 0x10, 0,
       0, 0, 0x08, 0,
       0, 0, 0x04, 0,
       0, 0,  0x2, 0,
       0, 0,  0x1, 0,
       0, 0,    0, 0x80,
       0, 0,    0, 0x40,
      0, 0,    0, 0x20,
      0, 0,    0, 0x10,
       0, 0,    0,  0x8,
      0, 0,    0,  0x4,
      0, 0,    0,  0x2,
       0, 0,    0,    0,
      0, 0,    0,    0
};


regel text[8] = {
"^F0^01Beknopte geschiedenis van de vitrage^00Uitvergroting van de br^01ffi^00ffl^01uidssluier filtert\015\12",
"^F0^01De_Twentse_Bank_naast_het_monument_voor_de_gevallenen.\015\012",
"en_boucl^82,_marquisette_in_slingerdraadbinding.\015\012",
"Te_onderscheiden:_polyester,_trevira,_brod^82\015\012" };


struct rec02 stcochin = {
   "Bembo 270 series               ",
   5,6,7,8,9,9,10,10,11,11,13,14,15,16,18,0, /* 334 wedge == 0 ? => 17*15 */
   12,16,18,20,22, 26, 28, 36, 48,  0,
   27,33,34,34,38, 44, 46, 58, 78,  0
};


struct matrijs far matrix[272]  = {
/*    NI            NL               A              B           C
      D             E                F              G           H
      I             J                K              L           M
      N             O   */

"~", 0,9 , 0, 8,


/* 1 */
"",0,9, 0, 0,  "",0,9, 0, 1, "",0,9, 0, 2, "",0,9, 0, 3, "",0,9, 0, 4,
"",0,9, 0, 5,  "" ,0,9, 0, 6, "`",0,9, 0, 7, " ",0,9, 0, 8,"\'",0,9, 0, 9,

",",0,9, 0,10,  "",0,9, 0,11,  ".",0,9, 0,12, "",0,9, 0,13, "",0,9, 0,14,
"",0,9, 0,15,  "",0,9, 0,16,

/* 2 */
"",0,9, 1, 0, "",0,9, 1, 1, "",0, 9,1,2, "",0,9, 1, 3, "\213",0,9, 1, 4,
"\214",0,9, 1, 5, "\241",0,9, 1, 6, "\215",0, 9,1, 7, " ",0,9, 1, 8, "i",0,9, 1, 9,
"f",0,9, 1,10, "",0,9, 1,11, "j",0,9, 1,12, "``",0,9, 1,13, "l",0,9, 1,14,
"",0,9, 1,15, "",0,9, 1,16,

/* 3 */
"",0,9, 2, 0, "",0,9, 2, 1, "",0,9, 2, 2, "",0,9, 2, 3, "[",0,9, 2, 4,
"]",0,9, 2, 5, "(",0,9, 2, 6, ")",0,9, 2, 7, "t",0,9, 2, 8, ":",0,9, 2, 9,
";",0,9, 2,10, "",0,9, 2,11, "/",0,9, 2,12, "!",0,9, 2,13, "",0,9, 2,14,
"",0,9, 2,15, "",0,9, 2,16,
/* 4 */

"",0,9, 3, 0, "",0,9, 3, 1, "",0,9, 3, 2, "",0,9, 3, 3, "",0,9, 3, 4,
"",0,9, 3, 5, "",0,9, 3, 6, "",0,9, 3, 7, "I",0,9, 3, 8, "",0,9, 3, 9,
"",0,9, 3,10, "",0,9, 3,11, "",0,9, 3,12, "",0,9, 3,13, "",0,9, 3,14,
"",0,9, 3,15, "",0,9, 3,16,
/* 5 */

"",0,9, 4, 0, "",0,9, 4, 1, "",0,9, 4, 2, "",0,9, 4, 3, "",0,9, 4, 4,
",,",0,9, 4, 5, "\212",0,9, 4, 6, "\202",0,9, 4, 7, " ",0,9, 4, 8, "\210",0,9, 4, 9,
"\211",0,9, 4,10, "",0,9, 4,11, "",0,9, 4,12, "",0,9, 4,13, "",0,9, 4,14,
"",0,9, 4,15, "7/8",0,9, 4,16,

/* 6  */
"",0,9, 5, 0, "",0,9, 5, 1, "",0,9, 5, 2, "",0,9, 5, 3, "",0,9, 5, 4,

"\257",0,9, 5, 5, "+",0,9, 5, 6, "*",0,9, 5, 7, "\256",0,9, 5, 8, "\207",0,9, 5, 9,
"-",0,9, 5,10, "",0,9, 5,11, "",0,9, 5,12, "",0,9, 5,13, "3/8",0,9, 5,14,
"",0,9, 5,15, "",0,9, 5,16,

/* 7 */
"", 0,9, 6, 0, "",0,9, 6, 1, "", 0,9, 6, 2, "", 0,9, 6, 3, "", 0,9, 6, 4,
"", 0,9, 6, 5, "z",0,9, 6, 6, "c", 0,9, 6, 7, "e", 0,9, 6, 8, "r", 0,9, 6, 9,
"s", 0,9, 6,10, "",0,9, 6,11, "", 0,9, 6,12, "", 0,9, 6,13, "", 0,9, 6,14,
"", 0,9, 6,15, "5/8",0,9, 6,16,

/* 8  */
"", 0,9, 7, 0, "",0,9, 7, 1, "",0,9, 7, 2, "\240",0,9, 7, 3, "\205",0,9, 7, 4,
"\203", 0,9, 7, 5, "\204",0,9, 7, 6, "v",0,9, 7, 7, "a",0,9, 7, 8, "o",0,9, 7, 9,
"\224", 0,9, 7,10, "",0,9, 7,11, "\225",0,9, 7,12, "\242",0,9, 7,13, "\223",0,9, 7,14,
"", 0,9, 7,15, "",0,9, 7,16,

/* 9  */
"",0,9, 8, 0, "",0,9, 8, 1, "", 0,9, 8, 2, "1",0,9, 8, 3, "2",0,9, 8, 4,
"3",0,9, 8, 5, "4",0,9, 8, 6, "5", 0,9, 8, 7, "6",0,9, 8, 8, "7",0,9, 8, 9,
"8",0,9, 8,10, "",0,9, 8,11, "0", 0,9, 8,12, "y",0,9, 8,13, "9",0,9, 8,14,
"b",0,9, 8,15, "",0,9, 8,16,

/* 10 */
"\244",0,9, 9, 0, "\243",0,9, 9, 1, "\225",0,9, 9, 2, "\223",0,9, 9, 3, "p",0,9, 9, 4,
"q",0,9, 9, 5, "h",0,9, 9, 6, "u",0,9, 9, 7, "n",0,9, 9, 8, "d",0,9, 9, 9,
"g",0,9, 9,10, "",0,9, 9,11, "k",0,9, 9,12, "x",0,9, 9,13, "\201",0,9, 9,14,
"J",0,9, 9,15, "?",0,9, 9,16,

/* 11       */
"",0,9,10, 0, "",0,9,10, 1, "",0,9,10, 2, "",0,9,10, 3, "",0,9,10, 4,
"&",0,9,10, 5, "",0,9,10, 6, "",0,9,10, 7, "\341",0,9,10, 8, "F",0,9,10, 9,
"L",0,9,10,10, "",0,9,10,11, "Z",0,9,10,12, "S",0,9,10,13, "\365",0,9,10,14,
"",0,9,10,15, "",0,9,10,16,

/* 12 A" */
"",0,9,11, 0, "",0,9,11, 1, "\220",0,9,11, 2, "\322",0,9,11, 3, "\324",0,9,11, 4,
"",0,9,11, 5, "\200",0,9,11, 6, "C",0,9,11, 7, "E",0,9,11, 8, "V",0,9,11, 9,
"P",0,9,11,10, "",0,9,11,11, "Y",0,9,11,12, "\222",0,9,11,13, "",0,9,11,14,
"",0,9,11,15, "",0,9,11,16,

/* 13 */
"",0,9,12, 0, "",0,9,12, 1, "",0,9,12, 2, "",0,9,12, 3, "\221",0,9,12, 4,
"X",0,9,12, 5, "K",0,9,12, 6, "B",0,9,12, 7, "A",0,9,12, 8, "R",0,9,12, 9,
"D",0,9,12,10, "",0,9,12,11, "\216",0,9,12,12, "T",0,9,12,13, "",0,9,12,14,
"",0,9,12,15, "",0,9,12,16,

/* 14 */
"",0,9,13, 0, "",0,9,13, 1, "",0,9,13, 2, "",0,9,13, 3, "",0,9,13, 4,
"oe!",0,9,13, 5, "H",0,9,13, 6, "U",0,9,13, 7, "O",0,9,13, 8, "N",0,9,13, 9,
"G",0,9,13,10, "",0,9,13,11, "Q",0,9,13,12, "w",0,9,13,13, "",0,9,13,14,
"",0,9,13,15, "",0,9,13,16,
/* 15 */
"",0,9,14, 0, "",0,9,14, 1, "",0,9,14, 2, "+",0,9,14, 3, "",0,9,14, 4,
"OE!",0,9,14, 5, "M",0,9,14, 6, "=",0,9,14, 7, "1/4",0,9,14, 8, "W",0,9,14, 9,
"3/4",0,9,14,10, "",0,9,14,11, "1/3",0,9,14,12, "1/2",0,9,14,13, "%",0,9,14,14,
"---",0,9,14,15, "",0,9,14,16,
/* 16 */
  "",0,9,15, 3, "",0,9,15, 4,
"",0,5,0, 2,

"", 0, 9, 1, 6,  "",0, 7, 1, 6,

"", 0, 9, 0, 8, /* vaste spatie */
"", 0,9, 7, 16, "", 0, 9, 7, 16, "", 0,9,7,16,

"",0,9,0,5, "",0,9,0,5, /* ' = 39 = 0x27 = \047 = asc */

"",0,9, 0,3, "",0,9,0, 3,

"",0,9,15, 2,
/* "", 0,10, 7,12, */

 "", 0,9, 15,15, "",0,9,15,16


} ;





/* the routines fabs, labs etc.

    from the library can not be trusted to work

 */

float fabsoluut( float d )
{
   return ( d < 0. ? -d : d );
}

int  iabsoluut( int ii )
{
   return ( ii < 0  ? -ii : ii );
}

long int labsoluut( long int li )
{
   return ( li < 0 ? -li : li);
}

double dabsoluut (double db )
{
   return ( db < 0. ? - db : db );
}

void cls( void)
{
   _clearscreen( _GCLEARSCREEN );
}

void ontsnap(int r, int k, char b[])
{
    print_at( r, k, b);
    if ( '#'==getchar() ) exit(1);
}

void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

void ce()    /* escape-routine exit if '#' is entered */
{
   if ('#'==getchar())exit(1);
}


int get_line()
{

   gllimit = MAX_REGELS;
   gli=0;
   while ( --gllimit > 0 && (glc=getchar()) != EOF && glc != '\n')
       line_buffer [gli++]=glc;
   if (glc == '\n')
       line_buffer[gli++] = glc;
   line_buffer[gli] = '\0';
   return ( gli );
}


/*
   testing NK: function:
	unit-adding off: turn on pump
	unit-adding on : change position wedge 0005"

   testing NJ: function:
	unit-adding off: change position wedge 0075"
	unit-adding on : line-kill
 */
int NK_test ( unsigned char  c[] )
{                    /*   N               K */
    return ( ( testbits(c,1) + testbits(c,4) ) == 2 ? 1 : 0 );
}

int NJ_test ( unsigned char  c[] )
{                    /*   N               J */
    return ( ( testbits(c,1) + testbits(c,5) ) == 2 ? 1 : 0 );
}

/*
    S-needle active ?
      activate adjustment wedges during casting space or character
*/
int S_test  (unsigned char  c[] )
{                  /*    S */
    return ( testbits(c,10) );
}


int GS2_test(unsigned char  c[])
{                 /*    G               S              2  */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,18) ) == 3 ? 1 : 0 );
}

int GS1_test(unsigned char  c[])
{                 /*    G                S              1 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,17) ) == 3 ? 1 : 0 );
}

int GS5_test(unsigned char  c[])
{                 /*    G                S              5 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,21) ) == 3 ? 1 : 0 );
}

/*  testbits:

       returns 1 when a specified bit is set in c[]

       input: *c = 4 byte = 32 bits char string
	      nr = char   0 - 31

*/

int testbits( unsigned char  c[], unsigned char  nr)
{
    return ( ( ( 0x80 >> (nr % 8) ) & c[nr/8] ) >= 1 ? 1 : 0 );
}

/*
      returns the (first) row-value set in s[]
 */



int row_i;

int row_test (unsigned char  c[])
{
   row_i = 16;

   while ( ( testbits(c, ++ row_i ) == 0 ) && (row_i < 31) );

   return ( row_i - RIJAANTAL);
}



/*
   set the desired bit of the row in the code
       input: row
 */
void setrow( unsigned char  c[],unsigned char  nr)
{
   if ( nr < 8 )
     c[2] |= tb[nr-1];
   else
     c[3] |= tb[nr-1];
}

void stcol ( unsigned char c[], unsigned char nr )
{
   switch (nr ) {
       case 2 : c[2] |= 0x80; break; /* A */
       case 5 :
	  if (central.syst == SHIFT )
	      c[1] |= 0x50; /* EF */
	  else
	      c[1] |= 0x08; /* D  */
	  break;
       default :
	  if ( nr > 2 && nr < 9 )
	      c[1] |= tk[nr];
	  else
	      c[0] |= tk[nr];
	  break;
   }
}



/*
  shows the code on screen
 */
int showi;

void showbits( unsigned char  c[])
{

    if (c[0] != -1) {
       for (showi=0;showi<=31;showi++) {
	   (testbits(c,showi) == 1) ? printf("%1c",tc[showi]) : printf(".");
	   if ( ( (showi-7) % 8) == 0)
	      printf(" ");
       }
    }
    for (showi=0;showi<4;showi++){
       printf(" %2x",c[showi]);
    }
    printf("\n");
}   /* showbits i */





/*

struct fspace {
    unsigned char pos;       / * row '_' space          * /
    float         wsp;       / * width in point         * /
    float         wunits;    / * width in units         * /
    unsigned char u1;        / * u1 position 0075 wedge * /
    unsigned char u2;        / * u2 position 0005 wedge * /
    unsigned char code[12];  / * code fixed space       * /
} datafix ;

    datafix stores all data about the fixed spaces, the text uses

	wsp = width in pointsizes
	width
	pos = row of the variable space i
	code = GS(row),
	NK g u1   0075 wedge    code to place the adjustment wegdes
	NJ u2 k   0005 wedge

   28 januari 2004: the routine seeks
	   the best suitable place to cast the fixed space:
	   wedges as near as possible to 3/8 position

   26 aug 2004: correcte code in datafix

 */

float fxwrow,   fxdelta, fxdd, fxmin=1000. , fxlw ;
int   fxidelta, fxfu1,  fu2, fxi;
float fxteken;
unsigned char fxrow;
unsigned char fxp[3] = { 0, 1, 4 };


void fixed_space( void )
{

    fxlw = datafix.wsp;

    for (fxi=0;fxi<12;fxi++)
	datafix.code[fxi]=0;

    datafix.code[ 1] = 0xa0; /* GS */
    datafix.code[ 4] = 0x48; /* NK */
    datafix.code[ 5] = 0x04; /* 0075 */
    datafix.code[ 8] = 0x44; /* NJ */
    datafix.code[11] = 0x01; /* 0005 */

    switch ( central.pica_cicero ) {
       case 'd' :   /* didot */
	 fxdelta = datafix.wsp * .0148 ;
	 break;
       case 'f' :   /* fournier */
	 fxdelta = datafix.wsp * .01357;
	 break;
       case 'p' :   /* pica */
	 fxdelta = datafix.wsp * .01389;
	 break;
    }
    datafix.wunits = fxdelta * 5184  / central.set;

    datafix.pos = 0;
    for (fxi=0;fxi<3;fxi++) {
       fxwrow  = wig[ fxp[fxi] ] * central.set ;
       fxwrow /= 5184 ;  /* = 4*1296 */
       fxdd = fxdelta - fxwrow;

       if ( fabsoluut(fxdd) < fabsoluut(fxmin) ) {
	  fxdd  *= 2000;
	  fxteken = (fxdd < 0) ? -1 : 1;
	  fxdd += ( fxteken * .5);
	  fxidelta = (int) fxdd;
	  fxidelta += 53;
	  if (fxidelta >= 16 ) {
	     fxmin = fxdd;
	     datafix.pos = fxi;
	  }
       }
    }
    switch (datafix.pos ) {
       case 0 :
	  datafix.code[2] = 0x40; /* GS1 */
	  break;
       case 4 :
	  datafix.code[2] = 0x04; /* GS5 */
	  break;
       default :
	  datafix.code[2] = 0x20; /* GS2 */
	  break;
    }

    fxwrow  = wig[ datafix.pos ] * central.set ;
    fxwrow /= 5184 ;  /* = 4*1296 */
    fxdelta -= fxwrow;
    fxdelta *= 2000;
    fxteken  = (fxdelta < 0) ? -1 : 1;
    fxdelta += ( fxteken * .5);
    fxidelta = (int) fxdelta;
    fxidelta += 53;

    fxfu1 = fxidelta / 15;
    fu2   = fxidelta % 15;
    if (fu2 == 0) {
       fu2+=15 ; fxfu1 --;
    }
    if (fxfu1>15) fxfu1=15;
    if (fxfu1<1)  fxfu1=1;
    /*
    printf(" uitvulling wordt: %2d / %2d ",fxfu1,fu2);
    ce();
     */

    datafix.u1 = fxfu1;
    datafix.u2 = fu2;

    if ( fxfu1 < 8 )
       datafix.code[6 ] |= tb[fxfu1-1];
    else
       datafix.code[7 ] |= tb[fxfu1-1];
    if ( fu2 < 8 )
       datafix.code[10] |= tb[fu2-1];
    else
       datafix.code[11] |= tb[fu2-1];
}

float  gegoten_dikte ;
unsigned char gn_cc[4];
int    genbufteller ;
int    gen_i, gn_hspi ;
float  gn_delta;
float  gn_epsi ;
int    gn_ccpos;    /* start: actual code for character in buffer */

/*
   23 aug 2004:

      bit setting replaced by adding

*/


float gen_system(  unsigned char k, /* kolom */
		   unsigned char r, /* rij   */
		   float dikte      /* width char in units */
		)

{
    gegoten_dikte = 0.;
    genbufteller = 0;
    gn_hspi=0 ;
    gn_delta = 0. ;
    gn_epsi = 0.0001;
    gn_ccpos=0;    /* start: actual code for character in buffer */
    /* initialize */
    for (gen_i=0; gen_i < 256; gen_i++) cbuff[gen_i] = 0;
    for (gen_i=0; gen_i < 4;   gen_i++) gn_cc[gen_i] = 0;

	/*
       printf("dikte = %7.2f wig %3d  ",dikte,wig[r] );
       printf(" verschil %10.7f ",fabs(dikte - 1.*wig[r]));
       printf(" kleiner %2d ", (fabs(dikte - 1.*wig[r]) < gn_epsi) ? 1 : 0 );
       if ('#'==getchar()) exit(1);
	 */
    if ( dikte ==  wig[r] ) {

	/* printf("width equal to wedge \n"); */

	if ( (central.syst == SHIFT) && (r == 15) ) {
	   gn_cc[1] = 0x08;
	} else {

	   for (gen_i=2;gen_i<4;gen_i++)
	      gn_cc[gen_i] = rijcode[r][gen_i];
	}
	       /* for (gen_i=0;gen_i<=3;gen_i++) {
		    printf(" gn_cc[%1d] = %3d ",gen_i,gn_cc[gen_i]);
		    ce();
		  }
		*/
	gegoten_dikte += dikte;
	genbufteller += 4;
	cbuff[4] = 0xff;
    } else {
	if (dikte < wig[r] ) {

	   /* printf("width smaller d %6.2f w %3d \n",dikte,wig[r]);
	      getchar();
	    */

	   if ( (r>0) && (dikte == wig[r-1]) && (central.syst == SHIFT ) ) {

	       /* printf("eerste tak \n"); */

	       for (gen_i=2;gen_i<4; gen_i++) {
		  gn_cc[gen_i] = rijcode[r-1][gen_i];
	       }

	       if (dikte != wig[r]) {
		  gn_cc[1] |= 0x08 ;  /* D */
	       }
	       gegoten_dikte += dikte;
	       cbuff[4] |= 0xff;
	   } else {

	       /* printf("tweede tak \n"); */

	       gn_delta =  dikte - wig[r] ;



	       adjust ( wig[r], gn_delta);

	       /* printf(" u1 = %2d u2 = %2d ",uitvul[0] ,uitvul[1] ); getchar(); */

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();*/

		  cbuff[genbufteller+ 4] = 0x48; /* NK big wedge */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0] -1][2];
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0] -1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off  */
		  cbuff[genbufteller+12] =  0xff;

	       } else {  /* unit adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] = 0x48; /* NK = pump on */
		  cbuff[genbufteller+ 5] |= 0x04; /* g  */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ = pump off */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;  /* k  */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2; gen_i<4 ; gen_i++) {
		  gn_cc[gen_i] +=  rijcode[r][gen_i];
	       }
	       gn_cc[1] |= 0x20 ; /* S-needle on */
	       gegoten_dikte += dikte;
	   }
	} else {
	   /*
	   print_at(5,1," width is bigger:\n add a high space \n");
	    */
	   gn_hspi = 0;
	   while ( dikte >= (wig[r] + wig[0])) {  /* add high space at: O1 */
	       /*
		print_at(6,1," add a high space ");
		if (getchar()=='#') exit(1);
		*/
	       cbuff[genbufteller  ] = 0x80; /* O   */
	       cbuff[genbufteller+2] = 0x40; /* r=1 */
	       genbufteller  += 4; /* raise genbufteller */
	       gegoten_dikte += wig[0] ;
	       dikte -= wig[0];
	       gn_ccpos +=4;
	       gn_hspi++;

	   } /* at this point desired width is less than 5 units
		this can be done with the adjustment wedges

	   */
	   if ( (central.adding > 0) && (dikte == (wig[r] + central.adding) )) {
	       /* gebruik spatieer-wig */
	       gn_cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */
	       gegoten_dikte += central.adding ;

	   } else {  /* aanspatieren */

	       /* printf(" aanspatieren met uitvul-wiggen \n");*/

	       gn_delta = dikte - wig[r] ;
	       adjust ( wig[r], gn_delta);

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[genbufteller+ 4] = 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] = 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off */
		  cbuff[genbufteller+12] = 0xff;

	       } else {  /* unit-adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] =  0x48;      /* NK */
		  cbuff[genbufteller+ 5] =  0x04;      /* g  pump on */
		  cbuff[genbufteller+ 6] =  rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] =  rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44;      /* NJ */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;      /* k  pump off */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2;gen_i<4; gen_i++)
		  gn_cc[gen_i] = rijcode[r][gen_i];
	       gn_cc[1] |= 0x20 ; /* S on */
	       gegoten_dikte = dikte;
	   }
	}
    }

    /* make column code */
    if ( (central.syst == SHIFT) && ( k == 5 ) ) {
       if ( central.d_style == line_data.c_style)
	  gn_cc[1] =  0x50; /* EF = D */
       else
	  gn_cc[0] = 0x20; /* blank mat in M-row */
    } else {
	  /* 17*15 & 17*16 */
       if ( central.d_style == line_data.c_style) {
	  for (gen_i=0; gen_i<=2; gen_i++)
	     gn_cc[gen_i] |= kolcode[k][gen_i];
	  if ( r == 15) {
	     switch (central.syst ) {
		case MNH :
		   switch (k) {
		      case  0 : gn_cc[0] |= 0x01; break; /* H   */
		      case  1 : gn_cc[0] |= 0x01; break; /* H   */
		      case  9 : gn_cc[0] |= 0x40; break; /* N   */
		      case 15 : gn_cc[0] |= 0x20; break; /* M   */
		      case 16 : gn_cc[0] =  0x61; break; /* HMN */
		      default :
			 gn_cc[0] |= 0x21; break; /* NM  */
		   }
		   break;
		case MNK :
		   /*
		byte 1:      byte 2:     byte 3:     byte 4:
		ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
		   */
		switch (k) {
		   case  0 : gn_cc[0] |= 0x08; break; /* NI+K  */
		   case  1 : gn_cc[0] |= 0x08; break; /* NL+K  */
		   case 12 : gn_cc[0] |= 0x40; break; /* N + K */
		   case 14 : gn_cc[0] |= 0x28; break; /* K + M */
		   case 15 : gn_cc[0] |= 0x20; break; /* N + M */
		   case 16 : gn_cc[0] =  0x68; break; /* NMK   */
		   default : gn_cc[0] |= 0x28; break; /* MK  */
		}
		break;
	     }
	  }
       } else {
	  if ( r == 15) {
	     switch (central.syst ) {
		case MNH :
		   gn_cc[0] =  0x61; break; /* HMN code M rij ???? */
		case MNK :
		   gn_cc[0] =  0x28; break; /* K+M */
	     }
	  } else {
	     if (r == 14 ) {
		gn_cc[0] = 0x20; /* blank in M-rij */
	     }
	  }
       }
    }

    if ((uitvul[0] == 3) && (uitvul[1]  == 8)) {

	  gn_cc[1] &=  ~0x20; /* mask bit 10 to zero */
	  cbuff[gn_ccpos + 4] = 0xff;
    }
	/* printf(" gn_ccpos = %3d ",gn_ccpos); */

    for (gen_i=0;gen_i<=3;gen_i++) {
       cbuff[gn_ccpos+gen_i] = gn_cc[gen_i]; /* fill buffer  */

		/*   printf(" gn_ccpos+gen_i %3d gn_cc[%1d] = %4d ",gn_ccpos+gen_i,gen_i,gn_cc[gen_i]);
		ce();
		*/
    }

    cbuff[gn_ccpos + genbufteller + 4 - gn_hspi*4 ] = 0xff;

    /*
    printf(" totaal = %4d ", gn_ccpos + genbufteller + 4 - gn_hspi*4 );
    ce();
       */
    gegoten_dikte *= ( (float) central.set ) /5184. ;

    return(gegoten_dikte);


}   /* end gen_system  */





/*

   reading: reads a matrix-file from disc

 */


int readp, readi, readj;

char r_eading()
{
    char reda = 0;

    /* global data concerning matrix files */

    /*
    FILE  *finmatrix ;
    size_t mat_recsize = sizeof( matfilerec );
    size_t recs2       = sizeof( cdata  );
    fpos_t *recpos, *fp;
    int  mat_handle;
    long int mat_length, mat_recseek;
    char inpathmatrix[_MAX_PATH];
    long int aantal_records;
	 / * number of records in mat_file */


    cls();

    print_at(10,10,"read matrix file from disk ");

    readi = 0;
    do {
       print_at(13,10,"Enter name input-file : " ); gets( inpathmatrix );
       if( ( finmatrix = fopen( inpathmatrix, "rb" )) == NULL )
       {
	  readi++;
	  if ( readi==1) {
	     print_at(15,10,"Can't open input file");
	     printf(" %2d time\n",readi );
	  } else {
	     print_at(15,10,"Can't open input file");
	     printf(" %2d times\n",readi );
	  }
	  if (readi == 10) return(0) ;
       }
    }
      while ( finmatrix == NULL );

    fclose(finmatrix);

    mat_handle = open( inpathmatrix,O_BINARY |O_RDONLY );

    /* Get and print mat_length. */
    mat_length = filelength( mat_handle );
    printf( "File length of %s is: %ld \n", inpathmatrix, mat_length );

    close(mat_handle);

    finmatrix = fopen( inpathmatrix, "rb" )   ;

    aantal_records = mat_length / mat_recsize ;

    /* global : mnumb = number of mats in the mat-case */

    printf("The file contains %7d records ",aantal_records);
    getchar();
    printf("Now the contents of the file will follow, \n");
    printf("from start to finish \n\n");
    getchar();

    /* first cdata 70 bytes */
    readp =  0 * recs2 ;
    *fp = ( fpos_t ) ( readp ) ;
    fsetpos( finmatrix , fp );
    fread( &cdata, recs2 , 1, finmatrix );

    for (readi=0;readi<34;readi++)
	namestr[readi] =
	cdata.cnaam[readi] ;
    for (readi=0;readi<RIJAANTAL;readi++) wig[readi] = cdata.wedge[readi];
    nrows =
	 ( wig[15]==0 ) ? 15 : 16 ;

    readi = 0;
    for (mat_recseek = 10; mat_recseek <= aantal_records -11;
		      mat_recseek ++ ){

	    readp =  mat_recseek  * mat_recsize;
	    *fp = ( fpos_t ) ( readp ) ;
	    fsetpos( finmatrix , fp );
	    fread( &matfilerec, mat_recsize, 1, finmatrix );

	    for (readj=0;readj<3;readj++)
	       matrix[readi].lig[readj] = matfilerec.lig[readj] ;
	    matrix[readi].srt    = matfilerec.srt;
	    matrix[readi].w      = matfilerec.w  ;
	    matrix[readi].mrij   = matfilerec.mrij ;
	    matrix[readi].mkolom = matfilerec.mkolom ;

	    readi++;
    }
    fclose(finmatrix);
    reda = 1;
    return (reda );

}  /*  r_eading() : read matrix from file */






