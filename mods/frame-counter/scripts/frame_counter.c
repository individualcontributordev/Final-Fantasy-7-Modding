/* Frame counter overlay. Runs at the tail of the SCUS DrawOTag wrapper (FUN_8004433c).
 * Builds a 7-segment readout of VSync(-1) as a contiguous TILE list and queues it
 * behind the scene OT, so it lands in the same draw env on top of the frame. */
#define CACHE ((unsigned *)0x800104dc) /* last drawn frame + 1 */
#define HEAD ((unsigned *)0x80010834)
#define X0 1
#define Y0 1
#define DIGITS 7
#define STEP 4

/* 1 + 1 + 7*7 TILEs (4 words each) from HEAD: dead libcd/libgpu debug strings 0x80010834-0x80010bac, after the live switch table and with "CD001" moved out (build_sites.py) */

extern unsigned FUN_8003cedc(int); /* VSync */

/* x, y, w, h: the backdrop, then segments a b c d e f g of a 3x5 digit, 1 px in from the backdrop edge */
static const unsigned char G[8][4] = {
	{0, 0, 29, 7}, {1, 1, 3, 1}, {3, 1, 1, 3}, {3, 3, 1, 3}, {1, 5, 3, 1}, {1, 3, 1, 3}, {1, 1, 1, 3}, {1, 3, 3, 1}};
static const unsigned char SEG[10] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f};

static void tile(unsigned *p, const unsigned char *r, int dx, unsigned rgb) {
	p[0] = (3u << 24) | ((unsigned)(p + 4) & 0xffffff);
	p[1] = 0x60000000u | rgb;
	p[2] = ((unsigned)(Y0 + r[1]) << 16) | (X0 + dx + r[0]);
	p[3] = ((unsigned)r[3] << 16) | r[2];
}

void FUN_800105a8(void) {
	unsigned n = FUN_8003cedc(-1);
	unsigned *p = HEAD, *q, *e = (unsigned *)0x80062c30; /* DR_ENV packet in libgpu's copy of the last PutDrawEnv: E3 area, E4, E5 offset */
	/* the scene OT may leave any draw area/offset (DR_ENV scrolls): re-pin libgpu's own on every call */
	p[0] = (3u << 24) | ((unsigned)(p + 4) & 0xffffff);
	p[1] = 0xe3000000 | e[2] & 0x7ff | (e[2] >> 11 & 0x3ff) << 10; /* area starts at the offset: battle's own E3 clips y < 8 */
	p[2] = e[1];
	p[3] = e[2];
	p += 4;
	if (*CACHE != n + 1) {
		unsigned char d[DIGITS];
		unsigned v = n;
		int i, s;
		*CACHE = n + 1;
		#pragma clang loop unroll(disable)
		for (i = DIGITS - 1; i >= 0; i--) {
			d[i] = v % 10;
			v /= 10;
		}
		tile(q = p, G[0], 0, 0);
		p += 4;
		#pragma clang loop unroll(disable)
		for (i = 0; i < DIGITS; i++) {
			unsigned m = SEG[d[i]];
			#pragma clang loop unroll(disable)
			for (s = 0; s < 7; s++)
				if (m >> s & 1) {
					tile(q = p, G[s + 1], i * STEP, 0xffffff);
					p += 4;
				}
		}
		*q = (3u << 24) | 0xffffff;
	}
	{
		int *t = *(int **)0x80062bf8; /* same GPU queue call as the wrapper */
		((void (*)(int, void *, int, int))t[2])(t[6], HEAD, 0, 0);
	}
}
