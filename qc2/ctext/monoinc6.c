/* c:\qc2\ctext\monoinc6.c

       control-codes:

       ^00 change to roman
       ^01 change to italic
       ^02 change to small caps
       ^03 change to bold

       ^|1 -- ^|9 add    1-9 units
       ^/1 -- ^/2 remove 1-8 1/4 units

	  allowing finetuning when kerning is wanted

       substracting units inside a word is limited to 1 unit, to prevent
       damage in the character-channel.

       substracting units, is limiting to 2 units minimum,

       for making margins:

       ^#n = add 1-9 squares (18 units) into the line (if possible...)
       ^=n = add 1-9 half squares (9 units) if possible

       ^## all following spaces will be half squares (if possible)


       ^.. all following '...' will be cast as '.','.','.'
	  with 5 units added to the '.' and 5 units placed behind it

       fixed spaces:

       ^Fn -> '_' => fixed spaces = 3 + 0xn /4 points n = hex
	   n = 3 + - 6 points

	   0,1,2,3,4, 5,6,7,8, a,b,c,d, e,f => x/4 points added to 3 points

	   _ is to be recognized as a fixed space

       ^Fd = 6 point ...

       ^mn  the next n lines will have a margin until this point

       ^ln  the length of the ligatures
	    1,2,3

       ^8x ^9x ^ax ^bx ^cx ^dx ^ex ^fx
	   invoegen tweede pagina asc-II table
	   variable deel van de asc-tabel...

       ^Ln line_data.vs, line_data.last

       ^Wn width right margin

       ^Rn repeat-signal line_data.rs

       ^pS start paragraph
       ^pE end paragraph




	float fabsoluut( float d )
	int  iabsoluut( int ii )
	long int labsoluut( long int li )
	double dabsoluut (double db )
	void cls( void)
	void ontsnap(int r, int k, char b[])
	   ce()
	void print_at(int rij, int kolom, char *buf)
	void ce()
	int get_line()
	int testbits( unsigned char  c[], unsigned char  nr)

	int NK_test ( unsigned char  c[] )
	    testbits(c,1)
	int NJ_test ( unsigned char  c[] )
	    testbits( c,i);
	int S_test  (unsigned char  c[] )
	    testbits( c,i);
	int GS2_test(unsigned char  c[])
	    testbits( c,i);
	int GS1_test(unsigned char  c[])
	    testbits( c,i);
	int GS5_test(unsigned char  c[])
	    testbits( c,i);
	int row_test (unsigned char  c[])
	    testbits( c,i);
	void setrow( unsigned char  c[],unsigned char  nr)
	void stcol ( unsigned char c[], unsigned char nr )
	void showbits( unsigned char  c[])
	   testbits(c,i));
	void fixed_space( void )
	float gen_system(  unsigned char k,
		   unsigned char r,
		   float dikte )
	char r_eading()

	   Regular ASCII Chart (character codes 0 - 127)
000   (nul)  016  (dle)  032 sp  048 0  064 @  080 P  096 `  112 p
001   (soh)  017  (dc1)  033 !   049 1  065 A  081 Q  097 a  113 q
002  (stx)  018  (dc2)  034 "   050 2  066 B  082 R  098 b  114 r
003  (etx)  019  (dc3)  035 #   051 3  067 C  083 S  099 c  115 s
004  (eot)  020  (dc4)  036 $   052 4  068 D  084 T  100 d  116 t
005  (enq)  021  (nak)  037 %   053 5  069 E  085 U  101 e  117 u
006  (ack)  022  (syn)  038 &   054 6  070 F  086 V  102 f  118 v
007  (bel)  023  (etb)  039 '   055 7  071 G  087 W  103 g  119 w
008  (bs)   024  (can)  040 (   056 8  072 H  088 X  104 h  120 x
009   (tab)  025  (em)   041 )   057 9  073 I  089 Y  105 i  121 y
010   (lf)   026   (eof)  042 *   058 :  074 J  090 Z  106 j  122 z
011  (vt)   027  (esc)  043 +   059 ;  075 K  091 [  107 k  123 {
012  (np)   028  (fs)   044 ,   060 <  076 L  092 \  108 l  124 |
013   (cr)   029  (gs)   045 -   061 =  077 M  093 ]  109 m  125 }
014  (so)   030  (rs)   046 .   062 >  078 N  094 ^  110 n  126 ~
015  (si)   031  (us)   047 /   063 ?  079 O  095 _  111 o  127 

	    Extended ASCII Chart (character codes 128 - 255)
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



*/

/* vars getline*/

int glc, gli;
int gllimit;



unsigned char kolcode[KOLAANTAL][4] = {
  /*   NI  */   0x42,    0,  0,   0,
  /*   NL  */   0x50,    0,  0,   0,
  /*   A   */      0,    0,  0x80,0,
  /*   B   */      0,    1,  0,   0,
  /*   C   */      0,    2,  0,   0,
  /*   D   */      0,    8,  0,   0,
  /*   E   */      0, 0x10,  0,   0,
  /*   F   */      0, 0x40,  0,   0,
  /*   G   */      0, 0x80,  0,   0,
  /*   H   */      1,    0,  0,   0,
  /*   I   */      2,    0,  0,   0,
  /*   J   */      4,    0,  0,   0,
  /*   K   */      8,    0,  0,   0,
  /*   L   */   0x10,    0,  0,   0,
  /*   M   */   0x20,    0,  0,   0,
  /*   N   */   0x40,    0,  0,   0,
  /*   O   */      0,    0,  0,   0
};

unsigned char rijcode[RIJAANTAL][4] = {
  /*  0  */     0, 0, 0x40, 0,
  /*  1  */     0, 0, 0x20, 0,
  /*  2  */     0, 0, 0x10, 0,
  /*  3  */     0, 0, 0x08, 0,
  /*  4  */     0, 0, 0x04, 0,
  /*  5  */     0, 0,  0x2, 0,
  /*  6  */     0, 0,  0x1, 0,
  /*  7  */     0, 0,    0, 0x80,
  /*  8  */     0, 0,    0, 0x40,
  /*  9  */     0, 0,    0, 0x20,
  /*  a  */     0, 0,    0, 0x10,
  /*  b  */     0, 0,    0,  0x8,
  /*  c  */     0, 0,    0,  0x4,
  /*  d  */     0, 0,    0,  0x2,
  /*  e  */     0, 0,    0,    0,
  /*  f  */     0, 0,    0,    0
};


regel text[8] = {
"^F0^01Beknopte geschiedenis van de vitrage^00Uitvergroting van de br^01ffi^00ffl^01uidssluier filtert\015\12",
"^F0^01De_Twentse_Bank_naast_het_monument_voor_de_gevallenen.\015\012",
"en_boucl^82,_marquisette_in_slingerdraadbinding.\015\012",
"Te_onderscheiden:_polyester,_trevira,_brod^82\015\012" };


struct rec02 stcochin = {
   "Cochin Series                  ",
   5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18, /* 5 wedge... == 0 ? => 17*15 */

   12,16,20,22,24,         26, 28, 0, 0, 0,
   30,34,42,45,50 /* 49*/ ,53, 60, 0, 0, 0
} ;


struct matrijs far matrix[272] = {

"\213",2,5, 0, 0,  "\214",0,5, 0, 1, "\047",0,5, 0, 2, "\140",0,5, 0, 3, ".",0,5, 0, 4,
",",0,5, 0, 5,  "j" ,0,5, 0, 6, "i",0,5, 0, 7, " ",0,5, 0, 8,"l",0,5, 0, 9,
"\241",0,5, 0,10,  "\215",0,5, 0,11,  "i",0,5, 0,12, "i",1,5, 0,13, "l",1,5, 0,14,
"t",1,5, 0,15,  "j",1,5, 0,16,

"", 0,6, 1, 0, "/",0,6, 1, 1, "[",0, 6,1,2, "]",0,6, 1, 3, "(",0,6, 1, 4,
")",0,6, 1, 5, "-",0,6, 1, 6, "f",0,6, 1, 7," ",1,6, 1, 8, "t",0,6, 1, 9,
"e",1,6, 1,10, "f",1,6, 1,11, "#",0,6, 1,12, "r",1,6, 1,13, "s",1,6, 1,14,
"c",1,6, 1,15, "v",1,6, 1,16,

"",0,7, 2, 0, "?",0,7, 2, 1, "?",1,7, 2, 2, "!",0,5, 2, 3, ":",0,5, 2, 4,
";",0,5, 2, 5, "\140",1,7, 2, 6, "'",1,7, 2, 7, "r",0,7, 2, 8, "s",0,7, 2, 9,
"o",1,7, 2,10, "p",1,5, 2,11, "b",1,5, 2,12, "q",1,7, 2,13, ";",1,6, 2,14,
":",1,7, 2,15, "!",1,7, 2,16,

"",0,8, 3, 0, "\212",0,8, 3, 1, "\210",0,8, 3, 2, "\211",0,8, 3, 3, "J",0,8, 3, 4,
"I",0,8, 3, 5, "z",0,8, 3, 6, "c",0,8, 3, 7, "e",0,8, 3, 8, "g",0,8, 3, 9,
"\202",0,8, 3,10, "\207",0,8, 3,11, "u",1,8, 3,12, "n",1,8, 3,13, "d",1,8, 3,14,
"g",1,8, 3,15, "h",1,8, 3,16,

"",0,9, 4, 0,  "(",1,9, 4, 1, ")",1,9, 4, 2, "3",0,9, 4, 3, "6",0,9, 4, 4,
"9",0,9, 4, 5, "\230",0,9, 4, 6, "y",0,9, 4, 7, " ",2,9, 4, 8, "p",0,8, 4, 9,
"b",0,9, 4,10, "\223",0,9, 4,11, "y",1,9, 4,12, "z",1,9, 4,13, "9",1,8, 4,14,
"3",1,9, 4,15, "6",1,9, 4,16,

"\341", 0,9, 5, 0, "\201",0,9, 5, 1, "\243",0,9, 5, 2, "7",0,9, 5, 3, "4",0,9, 5, 4,
"1",0,9, 5, 5, "0",0,9, 5, 6, "q",0,9, 5, 7, "u",0,9, 5, 8, "a",0,9, 5, 9,
"k", 0,9, 5,10, "\226",0,9, 5,11, "x",1,9, 5,12, "0",1,9, 5,13, "1",1,9, 5,14,
"4",1,9, 5,15, "7",1,9, 5,16,

"\242",0,9, 6, 0, "\225",0,9, 6, 1, "\223",0,9, 6, 2, "2",0,9, 6, 3, "5",0,9, 6, 4,
"8",0,9, 6, 5, "--",0,9, 6, 6, "v",0,9, 6, 7, "o",0,9, 6, 8, "h",0,9, 6, 9,
"fi",0,9, 6,10, "\227",0,9, 6,11, "a",1,9, 6,12, "w",1,9, 6,13, "8",1,9, 6,14,
"5",1,9, 6,15, "2",1,9, 6,16,

"",0,9, 7, 0, "",0,9, 7, 1, "+",0,9, 7, 2, "\204",0,9, 7, 3, "\240",0,10, 7, 4,
"n",0,10, 7, 5, "*",0,9, 7, 6, "x",0,9, 7, 7, "n",0,9, 7, 8, "d",0,9, 7, 9,
"fl",0,9, 7,10, "\205",0,9, 7,11, "\203",0,9, 7,12, "k",1,9, 7,13, "I",1,9, 7,14,
"J",1,9, 7,15, "",0,9, 7,16,

"",0,11, 8, 0, "",0,11, 8, 1, "",0,11, 8, 2, "",0,11, 8, 3, "",0,11, 8, 4,
"ff",1,11, 8, 5, "",0,11, 8, 6, "S",0,11, 8, 7, "ff",0,11, 8, 8, "",0,11, 8, 9,
"\221",1,11, 8,10, "oe!",1,11, 8,11, "fl",1,11, 8,12, "fi",1,11, 8,13, "F",1,11, 8,14,
"S",1,11, 8,15, "p",3,11, 8,16,

"",0,12, 9, 0, "",0,12, 9, 1, "",0,12, 9, 2, "",0,12, 9, 3, "F",0,12, 9, 4,
"L",0,12, 9, 5, "P",0,12, 9, 6, "T",0,12, 9, 7, "m",1,12, 9, 8, "O",1,12, 9, 9,
"T",1,12, 9,10, "B",1,12, 9,11, "C",1,12, 9,12, "G",1,12, 9,13, "P",1,12, 9,14,
"Q",1,12, 9,15, "Z",1,12, 9,16,

"E\"",0,13,10, 0, "E`",0,13,10,1, "\234",0,13,10, 2, "Z",0,13,10, 3, "B",0,13,10, 4,
"E",0,13,10, 5,   "ffi",0,13,10, 6,  "ffl",0,13,10, 7, "m",0,13,10, 8, "L'",1,13,10, 9,
"oe!",0,13,10,10, "A",1,13,10,11,  "E",1,13,10,12, "L",1,13,10,13, "R",1,13,10,14,
"",0,13,10,15,    "",0,13,10,16,

"&",0,14,11, 0, "",0,14,11, 1, "\222",0,14,11, 2, "K",0,14,11, 3, "C",0,14,11, 4,
"G",0,14,11, 5, "R",0,14,11, 6, "A",0,14,11, 7, "w",0,14,11, 8, "ffl",1,14,11, 9,
"ffi",1,14,11,10, "D",1,14,11,11, "N",1,14,11,12, "V",1,14,11,13, "Y",1,14,11,14,
"N",1,14,11,15, "",0,14,11,16,

"",0,15,12, 0, "",0,15,12, 1, "",0,15,12,2, "",0,15,12,3, "V",0,15,12, 4,
"X",0,15,12, 5,  "Y",0,15,12, 6,  "N",0,15,12, 7, "U",0,15,12, 8, "U",1,15,12, 9,
"H",1,15,12,10,  "",0,15,12,11,  "",0,15,12,12, "",0,15,12,13, "",0,15,12,14,
"",0,15,12,15, "\232",0,15,12,16,

"",0,16,13, 0, "",0,16,13, 1, "",0,16,13, 2, "",0,16,13, 3, "W",0,16,13, 4,
"Q",0,16,13, 5, "D",0,16,13, 6, "H",0,16,13, 7, "O",0,16,13, 8, "K",1,16,13, 9,
"X",1,16,13,10, "&",1,16,13,11, "O^",3,16,13,12, "O\"",0,16,13,13, "O'",0,16,13,14,
"O`",0,16,13,15, "",0,16,13,16,

"",0,18,14, 0, "---",0,18,14, 1, "+",3,18,14, 2, "",0,18,14, 3, "M",0,18,14, 4,
"",1,20,14, 5, "",0,18,14, 6, "\222",1,18,14, 7, "",0,18,14, 8, "M",1,18,14, 9,
"",0,18,14,10, "OE!",1,18,14,11, "",0,18,14,12, "W",1,18,14,13, "",0,18,14,14,
"\222",0,20,14,15, " ",4,18,14,16,

"",0,18,15, 0, "",0,18,15, 1, "",0,18,15, 2, "",0,18,15, 3, "",0,18,15, 4,
"",0,18,15, 5, "",0,18,15, 6, "",0,18,15, 7, "",0,18,15, 8, "",0,18,15, 9,
"",0,18,15,10, "",0,18,15,11, "",0,18,15,12, "",0,18,15,13, "",0,18,15,14,
"",0,18,15,15, "",0,18,15,16

} ;

struct rec02 stbodoni = {
   "Bodoni Series 135              ",
   5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18, /* 5 wedge... == 0 ? => 17*15 */

   12,15,16,18,20,22, 24,26,28,32,
   25,31,31,34,38,41, 47,47,54,62
} ;


struct matrijs far matrix2[272] = {

"",0,5, 0, 0,  "",0,5, 0, 1, "`",0,5, 0, 2, "\241",0,5, 0, 3, "\215",0,5,0, 4,
"224",0,5, 0, 5,  "\223" ,0,5, 0, 6, "i",0,5, 0, 7, " ",0,5, 0, 8,"l",0,5, 0, 9,
".",0,5, 0,10,  ",",0,5, 0,11,  "'",0,5, 0,12, "t",1,5, 0,13, "l",1,5, 0,14,
"",0,5, 0,15,  "",0,5, 0,16,

"I", 2,6, 1, 0, "/",0,6, 1, 1, "[",0, 6,1,2, "]",0,6, 1, 3, "(",0,6, 1, 4,
")",0,6, 1, 5, "-",0,6, 1, 6, "f",0,6, 1, 7," ",1,6, 1, 8, "j",0,6, 1, 9,
"\241",1,6, 1,10, "\241",1,6, 1,11, "\214",0,6, 1,12, "\213",1,6, 1,13, "i",1,6, 1,14,
"f",1,6, 1,15, "j",1,6, 1,16,

";",0,7, 2, 0, ":",0,7, 2, 1, "t",0,7, 2, 2, "s",0,5, 2, 3, "r",0,5, 2, 4,
";",1,5, 2, 5, ":",1,7, 2, 6, "r",1,7, 2, 7, "e",1,7, 2, 8, "s",1,7, 2, 9,
"c",1,7, 2,10, "z",1,5, 2,11, "\212",1,5, 2,12, "\202",1,7, 2,13, "\210",1,6, 2,14,
"\207",1,7, 2,15, "(",1,7, 2,16,

"z",3,8, 3, 0, "j",3,8, 3, 1, "s",3,8, 3, 2, "I",0,8, 3, 3, "\202",0,8, 3, 4,
"\212",0,8, 3, 5, "\210",0,8, 3, 6, "\207",0,8, 3, 7, "e",0,8, 3, 8, "c",0,8, 3, 9,
"z",0,8, 3,10, "v",1,8, 3,11, "o",1,8, 3,12, "g",1,8, 3,13, "b",1,8, 3,14,
"q",1,8, 3,15, "\242",1,8, 3,16,

"l",3,9, 4, 0, "\257",0,9, 4, 1, "*",0,9, 4, 2, "\256",0,9, 4, 3, "3",0,9, 4, 4,
"6",0,9, 4, 5, "9",0,9, 4, 6, "\223",0,9, 4, 7, " ",2,9, 4, 8, "\205",0,8, 4, 9,
"\204",0,9, 4,10, "\203",0,9, 4,11, "a",0,9, 4,12, ")",1,9, 4,13, "!",1,8, 4,14,
"1",1,9, 4,15, "2",1,9, 4,16,

"f", 2,9, 5, 0,"c",2,9, 5, 1,"--",0,9, 5, 2,"7",0,9, 5, 3, "4",0,9, 5, 4,
"1", 0,9, 5, 5, "0",0,9, 5, 6, "",0,9, 5, 7, "g",0,9, 5, 8, "k",1,9, 5, 9,
"a", 1,9, 5,10, "x",1,9, 5,11, "\205",1,9, 5,12, "I",1,9, 5,13, "y",1,9, 5,14,
"4", 1,9, 5,15, "3",1,9, 5,16,

"\207",2,9, 6, 0, "p",2,9, 6, 1, "t",2,9, 6, 2, ".",3,9, 6, 3, "2",0,9, 6, 4,
"5",0,9, 6, 5, "8",0,9, 6, 6, "\223",0,9, 6, 7, "o",0,9, 6, 8, "\224",0,9, 6, 9,
"h",1,9, 6,10, "d",1,9, 6,11, "\203",1,9, 6,12, "!",1,9, 6,13, "?",1,9, 6,14,
"0",1,9, 6,15, "5",1,9, 6,16,

"\202",2,10, 7, 0, "q",2,10, 7, 1, "b",2,10, 7, 2, "a",2,10, 7, 3, "o",2,10, 7, 4,
"J",0,10, 7, 5, "h",0,10, 7, 6, "u",0,10, 7, 7, "p",0,10, 7, 8, "y",0,10, 7, 9,
"q",0,10, 7,10, "\227",0,10, 7,11, "\226",0,10, 7,12, "u",1,10, 7,13, "p",1,10, 7,14,
"\227",1,10, 7,15, "\226",1,10, 7,16,

"\212",2,10, 8, 0, "g",2,10, 8, 1, "v",2,10, 8, 2, "r",2,10, 8, 3, "e",2,10, 8, 4,
"S",0,10, 8, 5, "b",0,10, 8, 6, "d",0,10, 8, 7, "n",0,10, 8, 8, "v",0,10, 8, 9,
"x",0,10, 8,10, "k",0,10, 8,11, "fi",0,10, 8,12, "fl",0,10, 8,13, "n",1,10, 8,14,
"fi",1,10, 8,15, "fl",3,10, 8,16,

"x",2,11, 9, 0, "k",2,11, 9, 1, "y",2,11, 9, 2, "d",2,11, 9, 3, "h",2,11, 9, 4,
"n",2,11, 9, 5, "u",2,11, 9, 6, "?",0,11, 9, 7, "C",0,11, 9, 8, "Z",0,11, 9, 9,
"\200",0,11, 9,10, "ff",1,11, 9,11, "S",1,11, 9,12, "J",1,11, 9,13, "",0,11, 9,14,
"ff",0,11, 9,15, "",0,11, 9,16,

"",2,12,10, 0, "",0,12,10, 1, "p",2,12,10, 2, "f",2,12,10, 3, "l",2,12,10, 4,
"t",2,12,10, 5, "ae!",0,12,10, 6, "oe!",1,12,10, 7, "w",1,12,10, 8, "ae!",1,12,10, 9,
"O",1,12,10,10, "L",1,12,10,11, "G",1,12,10,12, "C",1,12,10,13, "Q",1,12,10,14,
"Z",1,12,10,15, "\200",0,12,10,16,

"",0,13,11, 0, "V",0,13,11, 1, "Q",0,13,11, 2, "G",0,13,11, 3, "B",0,13,11, 4,
"A",0,13,11, 5, "E",0,13,11, 6, "O",0,13,11, 7, "w",0,13,11, 8, "",1,13,11, 9,
"",0,13,11,10, "E",1,13,11,11, "R",1,13,11,12, "T",1,13,11,13, "B",1,13,11,14,
"F",1,13,11,15, "P",0,13,11,16,

"\221",0,14,12, 0, "oe!",2,14,12, 1, "w",2,14,12, 2, "Y",0,14,12,3, "D",0,14,12, 4,
"R",0,14,12, 5, "N",0,14,12, 6, "U",0,14,12, 7, "oe",0,14,12, 8, "\220",1,14,12, 9,
"E`",1,14,12,10, "m",1,14,12,11, "ffi",0,14,12,12, "ffl",0,14,12,13, "A",1,14,12,14,
"D",1,14,12,15, "V",1,14,12,16,

"",0,15,13, 0, "",0,15,13, 1, "&",0,15,13, 2, "X",0,15,13, 3, "K",0,15,13, 4,
"M",0,15,13, 5, "H",0,15,13, 6, "ffi",0,15,13, 7, "ffl",0,15,13, 8, "m",1,15,13, 9,
"U",1,15,13,10, "N",1,15,13,11, "H",1,15,13,12, "Y",1,15,13,13, "K",1,15,13,14,
"X",1,15,13,15, "&",1,15,13,16,

"",0,18,14, 0, "\222",0,18,14, 1, "",0,18,14, 2, "OE!",0,18,14, 3, "%",0,18,14, 4,
"W",0,20,14, 5, "=",0,18,14, 6, "M",1,18,14, 7, "+",0,18,14, 8, "W",1,18,14, 9,
"",0,18,14,10, "OE!",1,18,14,11, "\222",1,18,14,12, "",1,18,14,13, "",0,18,14,14,
"---",0,20,14,15, " ",4,18,14,16,

"",0,18,15, 0, "",0,18,15, 1, "",0,18,15, 2, "",0,18,15, 3, "",0,18,15, 4,
"",0,18,15, 5, "",0,18,15, 6, "",0,18,15, 7, "",0,18,15, 8, "",0,18,15, 9,
"",0,18,15,10, "",0,18,15,11, "",0,18,15,12, "",0,18,15,13, "",0,18,15,14,
"",0,18,15,15, "",0,18,15,16

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
       readbuffer [gli++]=glc;
   if (glc == '\n')
       readbuffer[gli++] = glc;
   readbuffer[gli] = '\0';
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
       input: row-1
 */
void setrow( unsigned char  c[],unsigned char  nr)
{
   if (nr<7)
     c[2] |= tb[nr];
   else
     c[3] |= tb[nr];
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


 */

float fxwrow,   fxdelta, fxdd, fxmin=1000. , fxlw ;
int   fxidelta, fxfu1,  fu2, fxi;
float fxteken;
unsigned char fxrow;
unsigned char fxp[3] = { 0, 1, 4 };


void fixed_space( void )
{

    fxlw = datafix.wsp;
    /*
    printf("fxlw = %10.3f datafix.wsp %10.3f ",fxlw,datafix.wsp);
    ce();
     */
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
	  fxdd += ( fxteken * .5);  /* rounding off */
	  fxidelta = (int) fxdd;
	  fxidelta += 53;         /* 3/8 position correction wedges */
	  if (fxidelta >= 16 ) {
	     fxmin = fxdd;
	     datafix.pos = fxi;
	     /*printf("fxmin gevonden = %9.6f fxdd %9.6f pos %2d \n",
		      fxmin, fxdd, datafix.pos);*/
	  }
       }
       /*else { printf("else-tak \n");}
	*/
    }
    /*
    printf(" fxdd %9.6f fxdelta %9.6f fxwrow = %9.6f datafix.pos %2d ",
	      fxdd, fxdelta, fxwrow, datafix.pos);
    ce();
    */
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
    /*
    printf ("fxidelta = %4d fxdelta = %20.5f fxteken = %2d \n",fxidelta,fxdelta,fxteken);
      */
    fxidelta += 53; /* 3/8 position correction wedges */

    fxfu1 = fxidelta / 15;
    fu2 = fxidelta % 15;
    if (fu2 == 0) {
       fu2+=15 ; fxfu1 --;
    }
    if (fxfu1>15) fxfu1=15;
    if (fxfu1<1)  fxfu1=1;
    /*
    printf(" uitvulling %2d / %2d ",fxfu1,fu2);
    ce();

     */

    datafix.u1 = fxfu1;
    datafix.u2 = fu2;
    fxrow = datafix.pos;
    for (fxi=2 ; fxi<4 ; fxi++){
       datafix.code[fxi] |= rijcode[fxrow][fxi];
    }
    for (fxi=6 ; fxi<8 ; fxi++) {
       datafix.code[fxi] |= rijcode[fxfu1-1][fxi-5];
    }
    for (fxi=10 ; fxi<12 ; fxi++) {
       datafix.code[fxi] |= rijcode[fu2-1][fxi-10];
    }
}  /* fixed_space */


/***************************************************************

   gen system: last version: 12 feb

   code in: cbuff[]

   returns: the cast width

   last version :

   24 jan: single justification : NKg u1, NJ u2 k
	   only lower case will be small caps
	   ligature not in call function

   9 dec: NMK-system added

   12 feb: rijcode 4 bytes => 2 bytes

****************************************************************/

float  gegoten_dikte ;
unsigned char gn_cc[4];
int    genbufteller ;
int    gen_i, gn_hspi ;
float  gn_delta;
float  gn_epsi ;
int    gn_ccpos;    /* start: actual code for character in buffer */




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
    for (gen_i=0; gen_i < 4; gen_i++)    gn_cc[gen_i]=0;

	/*
       printf("dikte = %7.2f wig %3d  ",dikte,wig[r] );
       printf(" verschil %10.7f ",fabs(dikte - 1.*wig[r]));
       printf(" kleiner %2d ", (fabs(dikte - 1.*wig[r]) < gn_epsi) ? 1 : 0 );
       if ('#'==getchar()) exit(1);
	 */

    if ( dikte ==  wig[r] ) {

	/* printf("width equal to wedge \n"); */

	if ( (central.syst == SHIFT) && (r == 15) ) {
	   gn_cc[1] |= 0x08;
	} else {

	   for (gen_i=2;gen_i<4;gen_i++)
	      gn_cc[gen_i] |= rijcode[r][gen_i];
	}
	       /* for (gen_i=0;gen_i<=3;gen_i++) {
		    printf(" gn_cc[%1d] = %3d ",gen_i,gn_cc[gen_i]);
		    ce();
		  }
		*/
	gegoten_dikte += dikte;
	genbufteller += 4;
	cbuff[4] |= 0xff;
    } else {
	if (dikte < wig[r] ) {

	   /* printf("width smaller d %6.2f w %3d \n",dikte,wig[r]);
	      getchar();
	    */

	   if ( (r>0) && (dikte == wig[r-1]) && (central.syst == SHIFT ) ) {

	       /* printf("eerste tak \n"); */

	       for (gen_i=2;gen_i<4; gen_i++) {
		  gn_cc[gen_i] |= rijcode[r-1][gen_i];
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

		  cbuff[genbufteller+ 4] |= 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 6] |= rijcode[uitvul[0] -1][2];
		  cbuff[genbufteller+ 5] |= 0x04; /* g = pump on */
		  cbuff[genbufteller+ 7] |= rijcode[uitvul[0] -1][3];

		  cbuff[genbufteller+ 8] |= 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off  */
		  cbuff[genbufteller+12] |= 0xff;

	       } else {  /* unit adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] |= 0x48; /* NK = pump on */
		  cbuff[genbufteller+ 5] |= 0x04; /* g  */
		  cbuff[genbufteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] |= 0x44; /* NJ = pump off */
		  cbuff[genbufteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] |= 0x1;  /* k  */
		  cbuff[genbufteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+12] |= 0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2; gen_i<4 ; gen_i++) {
		  gn_cc[gen_i] = gn_cc[gen_i] + rijcode[r][gen_i];
	       }
	       gn_cc[1] |= 0x20 ; /* S-needle on */
	       gegoten_dikte += dikte;
	   }
	} else {
	   /* printf(" width is bigger \n"); */
	   gn_hspi = 0;
	   while ( dikte >= (wig[r] + wig[0])) {  /* add high space at: O1 */

	       cbuff[genbufteller  ] = 0x80; /* O   */
	       cbuff[genbufteller+2] = 0x40; /* r=1 */
	       genbufteller  += 4; /* raise genbufteller */
	       gegoten_dikte += wig[0] ;
	       dikte -= wig[0];
	       gn_ccpos +=4;
	       gn_hspi++;

	   } /* at this point less than 5 units wider */
	   if ( (central.adding > 0) && (dikte == (wig[r] + central.adding) )) {

	       gn_cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */
	       gegoten_dikte += central.adding ;

	   } else {  /* aanspatieren */

	       /* printf(" aanspatieren met wiggen \n");*/

	       gn_delta = dikte - wig[r] ;
	       adjust ( wig[r], gn_delta);

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[genbufteller+ 4] |= 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 5] |= 0x04; /* g = pump on */
		  cbuff[genbufteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] |= 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump on  */
		  cbuff[genbufteller+12] |= 0xff;

	       } else {  /* unit-adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] |= 0x48;      /* NK */
		  cbuff[genbufteller+ 5] |= 0x04;      /* g  */
		  cbuff[genbufteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] |= 0x44;      /* NJ */
		  cbuff[genbufteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] |= 0x01;      /* k  */
		  cbuff[genbufteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+12] |= 0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2;gen_i<4; gen_i++)
		  gn_cc[gen_i] |= rijcode[r][gen_i];
	       gn_cc[1] |= 0x20 ; /* S on */
	       gegoten_dikte = dikte;
	   }
	}
    }  /* make column code */
    if ( (central.syst == SHIFT) && ( k == 5 ) ) {
	  gn_cc[1] |=  0x50; /* EF = D */
    } else {
	  /* 17*15 & 17*16 */
       for (gen_i=0;gen_i<=2;gen_i++) gn_cc[gen_i] |= kolcode[k][gen_i];

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
    }

    if ((uitvul[0] == 3) && (uitvul[1]  == 8)) {
	  gn_cc[1] -=  0x20;
	  cbuff[gn_ccpos + 4] |= 0xff;
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

}  /*  r_eading : read matrix from file */






