# Task: Paste Ghidra decompiles (BATRES victory path)

You already have three programs imported (BATRES / BATTLE / SCUS).
Setup guide: [ghidra-battle-overlays.md](ghidra-battle-overlays.md)

**Put evidence in this file** under **Evidence** (paste decompiler text).
Do not only say check with empty evidence.

## Goal

Get decompiler output so we can name what starts fanfare/poses and design the
next skip patch. Chat-only copies get lost — **the repo is the source of truth.**

## What to collect

### A. BATRES (base `801B0000`)

| Go to | Action |
|-------|--------|
| **`801B0000`** | Create function if needed; name **`batres_victory`**. Copy **full** decompile. |

see end of file

| **`801B0E20`** | Own function; name e.g. **`batres_clear_battle_ui`**. Copy decompile. |





/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void batres_clear_battle_ui(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = 0;
  iVar3 = 0;
  iVar1 = 0;
  _DAT_8009d7d8 = 0;
  _DAT_8009d7dc = 0;
  _DAT_8009d7e0 = 0;
  do {
    *(undefined2 *)(iVar1 + -0x7ff627f8) = 0xffff;
    *(undefined2 *)(iVar1 + -0x7ff627f4) = 0;
    iVar3 = iVar3 + 1;
    iVar1 = iVar1 + 6;
  } while (iVar3 < 4);
  iVar3 = 0;
  iVar1 = 0;
  do {
    *(undefined2 *)(iVar1 + -0x7ff62812) = 0;
    *(undefined1 *)(iVar1 + -0x7ff62813) = 0;
    iVar3 = iVar3 + 1;
    iVar1 = iVar1 + 0xc;
  } while (iVar3 < 3);
  uVar4 = 0;
  do {
    if (*(char *)(uVar4 + 0x8009cbdc) == -1) {
      uVar2 = uVar2 | 1 << (uVar4 & 0x1f);
    }
    uVar4 = uVar4 + 1;
  } while ((int)uVar4 < 3);
  func_0x80015654(uVar2);
  return;
}

                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined batres_clear_battle_ui()
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     801b0e34(W), 
                                                                                                   801b0ee8(R)  
                             batres_clear_battle_ui                          XREF[1]:     801b0278(c)  
        801b0e20 e8 ff bd 27     addiu      sp,sp,-0x18
        801b0e24 21 20 00 00     clear      a0
        801b0e28 21 28 00 00     clear      a1
        801b0e30 21 18 00 00     clear      v1
        801b0e3c d8 d7 20 ac     sw         zero,-0x2828(at)=>DAT_8009d7d8
        801b0e44 dc d7 20 ac     sw         zero,-0x2824(at)=>DAT_8009d7dc
        801b0e4c e0 d7 20 ac     sw         zero,-0x2820(at)=>DAT_8009d7e0
        801b0e58 08 d8 26 a4     sh         a2,-0x27f8(at)
        801b0e64 0c d8 20 a4     sh         zero,-0x27f4(at)
        801b0e68 01 00 a5 24     addiu      a1,a1,0x1
        801b0e6c 04 00 a2 28     slti       v0,a1,0x4
        801b0e70 f7 ff 40 14     bne        v0,zero,LAB_801b0e50
        801b0e78 21 28 00 00     clear      a1
        801b0e7c 21 18 00 00     clear      v1
        801b0e88 ee d7 20 a4     sh         zero,-0x2812(at)
        801b0e94 ed d7 20 a0     sb         zero,-0x2813(at)
        801b0e98 01 00 a5 24     addiu      a1,a1,0x1
        801b0e9c 03 00 a2 28     slti       v0,a1,0x3
        801b0ea0 f7 ff 40 14     bne        v0,zero,LAB_801b0e80
        801b0ea8 21 28 00 00     clear      a1
        801b0ebc dc cb 22 90     lbu        v0,-0x3424(at)
        801b0ec4 02 00 46 14     bne        v0,a2,LAB_801b0ed0
        801b0ecc 25 20 82 00     or         a0,a0,v0
                             LAB_801b0ed0                                    XREF[1]:     801b0ec4(j)  
        801b0ed0 01 00 a5 24     addiu      a1,a1,0x1
        801b0ed4 03 00 a2 28     slti       v0,a1,0x3
        801b0ed8 f6 ff 40 14     bne        v0,zero,LAB_801b0eb4
        801b0ee0 95 55 00 0c     jal        SUB_80015654
        801b0ef0 08 00 e0 03     jr         ra


If `batres_victory` is huge, full function is still preferred. Minimum range in
listing terms: **`801B0270`–`801B0560`** behavior must appear in the paste.

### B. BATTLE (base `800A0000`)

For each address: **G** to address, then **D** if needed, then **Function → Create Function**, then copy decompile.

| Address | Suggested name (optional) |
|---------|---------------------------|
| **`800A7254`** | (pose/anim candidate; called a2=4 x10) |


void FUN_800a7254(int param_1,char param_2,char param_3,undefined2 param_4)

{
  char *pcVar1;
  int iVar2;
  int *piVar3;
  
  piVar3 = (int *)(param_1 * 4 + -0x7ff0b6ec);
  iVar2 = *piVar3;
  pcVar1 = (char *)(param_1 * 0x200 + iVar2 * 4 + -0x7ff0bcf8);
  if (*pcVar1 == -1) {
    *(undefined2 *)(pcVar1 + 2) = param_4;
    pcVar1[1] = param_3;
    *pcVar1 = param_2;
    iVar2 = FUN_800a71e8(iVar2);
    *piVar3 = iVar2;
  }
  return;
}


                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_800a7254()
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x4]:4  local_4                                 XREF[2]:     800a7270(W), 
                                                                                                   800a72b4(R)  
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     800a7264(W), 
                                                                                                   800a72b8(R)  
                             FUN_800a7254                                    XREF[20]:    FUN_800a22c0:800a2398(c), 
                                                                                          FUN_800a23e0:800a2738(c), 
                                                                                          FUN_800a2974:800a2abc(c), 
                                                                                          FUN_800a2db0:800a2e88(c), 
                                                                                          FUN_800a32c0:800a333c(c), 
                                                                                          FUN_800a38fc:800a3cbc(c), 
                                                                                          FUN_800a4860:800a48a0(c), 
                                                                                          FUN_800a4954:800a4994(c), 
                                                                                          FUN_800a4954:800a4a30(c), 
                                                                                          FUN_800a5990:800a5a34(c), 
                                                                                          FUN_800a68fc:800a6a20(c), 
                                                                                          FUN_800a6c5c:800a6c80(c), 
                                                                                          FUN_800a6e0c:800a6e54(c), 
                                                                                          FUN_800a6e6c:800a6e84(c), 
                                                                                          FUN_800a6e9c:800a6fdc(c), 
                                                                                          FUN_800a7060:800a7078(c), 
                                                                                          FUN_800a778c:800a7834(c), 
                                                                                          FUN_800a79cc:800a7c54(c), 
                                                                                          FUN_800a79cc:800a7cb4(c), 
                                                                                          FUN_800a79cc:800a7d18(c), [more]
        800a7254 e8 ff bd 27     addiu      sp,sp,-0x18
        800a7258 0f 80 03 3c     lui        v1,0x800f
        800a725c 14 49 63 24     addiu      v1,v1,0x4914
        800a7260 80 10 04 00     sll        v0,a0,0x2
        800a7264 10 00 b0 af     sw         s0,local_8(sp)
        800a7268 21 80 43 00     addu       s0,v0,v1
        800a726c 40 22 04 00     sll        a0,a0,0x9
        800a7270 14 00 bf af     sw         ra,local_4(sp)
        800a7274 00 00 08 8e     lw         t0,0x0(s0)
        800a7278 0f 80 03 3c     lui        v1,0x800f
        800a727c 08 43 63 24     addiu      v1,v1,0x4308
        800a7280 80 10 08 00     sll        v0,t0,0x2
        800a7284 21 10 43 00     addu       v0,v0,v1
        800a7288 21 20 82 00     addu       a0,a0,v0
        800a728c 00 00 83 90     lbu        v1,0x0(a0)
        800a7290 ff 00 02 34     ori        v0,zero,0xff
        800a7294 07 00 62 14     bne        v1,v0,LAB_800a72b4
        800a7298 00 00 00 00     _nop
        800a729c 02 00 87 a4     sh         a3,0x2(a0)
        800a72a0 01 00 86 a0     sb         a2,0x1(a0)
        800a72a4 00 00 85 a0     sb         a1,0x0(a0)
        800a72a8 7a 9c 02 0c     jal        FUN_800a71e8                                     undefined FUN_800a71e8()
        800a72ac 21 20 00 01     _move      a0,t0
        800a72b0 00 00 02 ae     sw         v0,0x0(s0)



| **`800A3354`** | wait-frame (ceremony x s4) |


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_800a3354(void)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  FUN_800a32c0(_DAT_800f3944);
  if (_DAT_800f3944 != 0) {
    puVar1 = (undefined1 *)FUN_800a2f4c();
    *puVar1 = 0xff;
  }
  func_0x800155b0();
  iVar3 = 0;
  iVar4 = 0;
  do {
    iVar2 = (int)(char)(&DAT_80163798)[iVar4];
    if (iVar2 == -1) break;
    if (iVar2 - 4U < 6) {
      *(undefined1 *)(iVar2 * 0x10 + -0x7fe9c947) = (&DAT_800f83f0)[iVar2 * 0x68];
    }
    iVar3 = iVar3 + 1;
    iVar4 = iVar4 + 0xc;
  } while (iVar3 < 0x40);
  FUN_800b6d6c();
  FUN_800a3278();
  iVar2 = 4;
  iVar4 = 0x1a0;
  iVar3 = 0x40;
  do {
    puVar1 = &DAT_800f83f0 + iVar4;
    iVar4 = iVar4 + 0x68;
    iVar2 = iVar2 + 1;
    *(undefined1 *)(iVar3 + -0x7fe9c947) = *puVar1;
    iVar3 = iVar3 + 0x10;
  } while (iVar2 < 10);
  return;
}

                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_800a3354()
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     800a3360(W), 
                                                                                                   800a344c(R)  
                             FUN_800a3354                                    XREF[6]:     FUN_800a345c:800a3470(c), 
                                                                                          FUN_800a35f8:800a3674(*), 
                                                                                          FUN_800a4860:800a48bc(c), 
                                                                                          FUN_800a4860:800a48fc(c), 
                                                                                          FUN_800a4954:800a49b0(c), 
                                                                                          FUN_800a4954:800a49f0(c)  
        800a3354 0f 80 04 3c     lui        a0,0x800f
        800a3358 44 39 84 8c     lw         a0,offset DAT_800f3944(a0)
        800a335c e8 ff bd 27     addiu      sp,sp,-0x18
        800a3360 10 00 bf af     sw         ra,local_8(sp)
        800a3364 b0 8c 02 0c     jal        FUN_800a32c0                                     undefined FUN_800a32c0()
        800a3368 00 00 00 00     _nop
        800a336c 0f 80 02 3c     lui        v0,0x800f
        800a3370 44 39 42 8c     lw         v0,offset DAT_800f3944(v0)
        800a3374 00 00 00 00     nop
        800a3378 05 00 40 10     beq        v0,zero,LAB_800a3390
        800a337c 00 00 00 00     _nop
        800a3380 d3 8b 02 0c     jal        FUN_800a2f4c                                     undefined FUN_800a2f4c()
        800a3384 00 00 00 00     _nop
        800a3388 ff ff 03 24     li         v1,-0x1
        800a338c 00 00 43 a0     sb         v1,0x0(v0)
                             LAB_800a3390                                    XREF[1]:     800a3378(j)  
        800a3390 6c 55 00 0c     jal        SUB_800155b0
        800a3394 00 00 00 00     _nop
        800a3398 21 28 00 00     clear      a1
        800a339c ff ff 07 24     li         a3,-0x1
        800a33a0 21 30 00 00     clear      a2
                             LAB_800a33a4                                    XREF[1]:     800a33fc(j)  
        800a33a4 16 80 01 3c     lui        at,0x8016
        800a33a8 21 08 26 00     addu       at,at,a2
        800a33ac 98 37 24 80     lb         a0,offset DAT_80163798(at)
        800a33b0 00 00 00 00     nop
        800a33b4 13 00 87 10     beq        a0,a3,LAB_800a3404
        800a33b8 fc ff 82 24     _addiu     v0,a0,-0x4
        800a33bc 06 00 42 2c     sltiu      v0,v0,0x6
        800a33c0 0c 00 40 10     beq        v0,zero,LAB_800a33f4
        800a33c4 40 10 04 00     _sll       v0,a0,0x1
        800a33c8 21 10 44 00     addu       v0,v0,a0
        800a33cc 80 10 02 00     sll        v0,v0,0x2
        800a33d0 21 10 44 00     addu       v0,v0,a0
        800a33d4 c0 10 02 00     sll        v0,v0,0x3
        800a33d8 10 80 01 3c     lui        at,0x8010
        800a33dc 21 08 22 00     addu       at,at,v0
        800a33e0 f0 83 23 90     lbu        v1,-0x7c10(at)=>DAT_800f83f0
        800a33e4 00 11 04 00     sll        v0,a0,0x4
        800a33e8 16 80 01 3c     lui        at,0x8016
        800a33ec 21 08 22 00     addu       at,at,v0
        800a33f0 b9 36 23 a0     sb         v1,0x36b9(at)
                             LAB_800a33f4                                    XREF[1]:     800a33c0(j)  
        800a33f4 01 00 a5 24     addiu      a1,a1,0x1
        800a33f8 40 00 a2 28     slti       v0,a1,0x40
        800a33fc e9 ff 40 14     bne        v0,zero,LAB_800a33a4
        800a3400 0c 00 c6 24     _addiu     a2,a2,0xc
                             LAB_800a3404                                    XREF[1]:     800a33b4(j)  
        800a3404 5b db 02 0c     jal        FUN_800b6d6c                                     undefined FUN_800b6d6c()
        800a3408 00 00 00 00     _nop
        800a340c 9e 8c 02 0c     jal        FUN_800a3278                                     undefined FUN_800a3278()
        800a3410 00 00 00 00     _nop
        800a3414 04 00 05 34     ori        a1,zero,0x4
        800a3418 a0 01 04 34     ori        a0,zero,0x1a0
        800a341c 40 00 03 34     ori        v1,zero,0x40
                             LAB_800a3420                                    XREF[1]:     800a3444(j)  
        800a3420 10 80 01 3c     lui        at,0x8010
        800a3424 21 08 24 00     addu       at,at,a0
        800a3428 f0 83 22 90     lbu        v0,-0x7c10(at)=>DAT_800f8590
        800a342c 68 00 84 24     addiu      a0,a0,0x68
        800a3430 01 00 a5 24     addiu      a1,a1,0x1
        800a3434 16 80 01 3c     lui        at,0x8016
        800a3438 21 08 23 00     addu       at,at,v1
        800a343c b9 36 22 a0     sb         v0,0x36b9(at)=>DAT_801636f9
        800a3440 0a 00 a2 28     slti       v0,a1,0xa
        800a3444 f6 ff 40 14     bne        v0,zero,LAB_800a3420
        800a3448 10 00 63 24     _addiu     v1,v1,0x10
        800a344c 10 00 bf 8f     lw         ra,local_8(sp)
        800a3450 18 00 bd 27     addiu      sp,sp,0x18
        800a3454 08 00 e0 03     jr         ra
        800a3458 00 00 00 00     _nop


| **`800B1060`** | conditional a0=8 |

void FUN_800b1060(undefined4 param_1)

{
  FUN_800a31a0(10,2,1,param_1);
  return;
}

                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_800b1060()
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     800b1064(W), 
                                                                                                   800b107c(R)  
                             FUN_800b1060                                    XREF[3]:     FUN_800a795c:800a7970(c), 
                                                                                          FUN_800aabbc:800ab2d0(c), 
                                                                                          FUN_800aca4c:800acafc(c)  
        800b1060 e8 ff bd 27     addiu      sp,sp,-0x18
        800b1064 10 00 bf af     sw         ra,local_8(sp)
        800b1068 21 38 80 00     move       a3,a0
        800b106c 0a 00 04 34     ori        a0,zero,0xa
        800b1070 02 00 05 34     ori        a1,zero,0x2
        800b1074 68 8c 02 0c     jal        FUN_800a31a0                                     undefined FUN_800a31a0()
        800b1078 01 00 06 34     _ori       a2,zero,0x1
        800b107c 10 00 bf 8f     lw         ra,local_8(sp)
        800b1080 18 00 bd 27     addiu      sp,sp,0x18
        800b1084 08 00 e0 03     jr         ra
        800b1088 00 00 00 00     _nop


| **`800A56B0`** | rewards UI |

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_800a56b0(short param_1)

{
  int iVar1;
  short *psVar2;
  short *psVar3;
  int iVar4;
  
  iVar4 = 0;
  psVar2 = (short *)&DAT_800f3a42;
  psVar3 = (short *)&DAT_800f3a40;
  do {
    if ((*psVar2 != -1) && (*psVar3 == param_1)) {
      iVar1 = _DAT_800f3a1c * 2;
      _DAT_800f3a1c = _DAT_800f3a1c + 1 & 0xf;
      *(short *)(iVar1 + -0x7ff0c5e0) = *psVar2;
      *psVar3 = -1;
      *psVar2 = -1;
    }
    psVar2 = psVar2 + 2;
    iVar4 = iVar4 + 1;
    psVar3 = psVar3 + 2;
  } while (iVar4 < 0x10);
  return;
}

                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_800a56b0()
             undefined         <UNASSIGNED>   <RETURN>
                             FUN_800a56b0                                    XREF[3]:     FUN_800a22c0:800a2380(c), 
                                                                                          FUN_800a6e9c:800a6fc8(c), 
                                                                                          FUN_800aec10:800aedf4(c)  
        800a56b0 f8 ff bd 27     addiu      sp,sp,-0x8
        800a56b4 21 40 00 00     clear      t0
        800a56b8 ff ff 09 24     li         t1,-0x1
        800a56bc 00 24 04 00     sll        a0,a0,0x10
        800a56c0 03 24 04 00     sra        a0,a0,0x10
        800a56c4 0f 80 0a 3c     lui        t2,0x800f
        800a56c8 20 3a 4a 25     addiu      t2,t2,0x3a20
        800a56cc 0f 80 05 3c     lui        a1,0x800f
        800a56d0 42 3a a5 24     addiu      a1,a1,0x3a42
        800a56d4 fe ff a6 24     addiu      a2,a1,-0x2
                             LAB_800a56d8                                    XREF[1]:     800a573c(j)  
        800a56d8 00 00 a2 84     lh         v0,0x0(a1)=>DAT_800f3a42
        800a56dc 00 00 00 00     nop
        800a56e0 13 00 49 10     beq        v0,t1,LAB_800a5730
        800a56e4 21 38 40 00     _move      a3,v0
        800a56e8 00 00 c2 84     lh         v0,0x0(a2)=>DAT_800f3a40
        800a56ec 00 00 00 00     nop
        800a56f0 0f 00 44 14     bne        v0,a0,LAB_800a5730
        800a56f4 00 00 00 00     _nop
        800a56f8 0f 80 02 3c     lui        v0,0x800f
        800a56fc 1c 3a 42 8c     lw         v0,offset DAT_800f3a1c(v0)
        800a5700 00 00 00 00     nop
        800a5704 01 00 43 24     addiu      v1,v0,0x1
        800a5708 40 10 02 00     sll        v0,v0,0x1
        800a570c 21 10 4a 00     addu       v0,v0,t2
        800a5710 0f 80 01 3c     lui        at,0x800f
        800a5714 1c 3a 23 ac     sw         v1,offset DAT_800f3a1c(at)
        800a5718 0f 00 63 30     andi       v1,v1,0xf
        800a571c 00 00 47 a4     sh         a3,0x0(v0)
        800a5720 0f 80 01 3c     lui        at,0x800f
        800a5724 1c 3a 23 ac     sw         v1,offset DAT_800f3a1c(at)
        800a5728 00 00 c9 a4     sh         t1,0x0(a2)=>DAT_800f3a40
        800a572c 00 00 a9 a4     sh         t1,0x0(a1)=>DAT_800f3a42
                             LAB_800a5730                                    XREF[2]:     800a56e0(j), 800a56f0(j)  
        800a5730 04 00 a5 24     addiu      a1,a1,0x4
        800a5734 01 00 08 25     addiu      t0,t0,0x1
        800a5738 10 00 02 29     slti       v0,t0,0x10
        800a573c e6 ff 40 14     bne        v0,zero,LAB_800a56d8
        800a5740 04 00 c6 24     _addiu     a2,a2,0x4
        800a5744 08 00 bd 27     addiu      sp,sp,0x8
        800a5748 08 00 e0 03     jr         ra
        800a574c 00 00 00 00     _nop


### C. SCUS (base `80010000`)

| Address | Suggested name (optional) |
|---------|---------------------------|
| **`80014540`** | thin wrapper to 33E34 |


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_80014540(void)

{
  FUN_80033e34(_DAT_80071744,_DAT_80095dd8,_DAT_800722c8,0);
  return;
}

                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_80014540()
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     8001455c(W), 
                                                                                                   80014568(R)  
                             FUN_80014540
        80014540 e8 ff bd 27     addiu      sp,sp,-0x18
        80014544 07 80 04 3c     lui        a0,0x8007
        80014548 44 17 84 8c     lw         a0,offset DAT_80071744(a0)
        8001454c 09 80 05 3c     lui        a1,0x8009
        80014550 d8 5d a5 8c     lw         a1,offset DAT_80095dd8(a1)
        80014554 07 80 06 3c     lui        a2,0x8007
        80014558 c8 22 c6 8c     lw         a2,offset DAT_800722c8(a2)
        8001455c 10 00 bf af     sw         ra,local_8(sp)
        80014560 8d cf 00 0c     jal        FUN_80033e34                                     undefined FUN_80033e34()
        80014564 21 38 00 00     _clear     a3
        80014568 10 00 bf 8f     lw         ra,local_8(sp)
        8001456c 18 00 bd 27     addiu      sp,sp,0x18
        80014570 08 00 e0 03     jr         ra
        80014574 00 00 00 00     _nop


| **`80033E34`** | frame pump (one level deep is enough) |


undefined4 FUN_80033e34(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_80033cb8(3,param_1,param_2,param_3,param_4);
  return 0;
}

                              **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_80033e34()
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     80033e54(W), 
                                                                                                   80033e64(R)  
             undefined4        Stack[-0x10]:4 local_10                                XREF[1]:     80033e50(W)  
                             FUN_80033e34                                    XREF[20]:    FUN_80011274:80011290(c), 
                                                                                          FUN_80011274:800112b8(c), 
                                                                                          FUN_800112e8:80011340(c), 
                                                                                          FUN_80011860:800118c8(c), 
                                                                                          FUN_80011938:80011954(c), 
                                                                                          FUN_80011938:8001197c(c), 
                                                                                          FUN_80011938:800119a8(c), 
                                                                                          FUN_80011c1c:8001251c(c), 
                                                                                          FUN_80011c1c:80012560(c), 
                                                                                          FUN_80011c1c:800125a4(c), 
                                                                                          FUN_80011c1c:800125e8(c), 
                                                                                          FUN_80011c1c:8001262c(c), 
                                                                                          FUN_80011c1c:80012670(c), 
                                                                                          FUN_80011c1c:800126d0(c), 
                                                                                          FUN_80014540:80014560(c), 
                                                                                          FUN_80014578:800145a4(c), 
                                                                                          FUN_80014610:80014624(c), 
                                                                                          FUN_800211c4:800211ec(c), 
                                                                                          FUN_80033f40:80033f74(c), 
                                                                                          FUN_80034fc8:800353f4(c)  
        80033e34 e0 ff bd 27     addiu      sp,sp,-0x20
        80033e38 21 10 80 00     move       v0,a0
        80033e3c 21 18 a0 00     move       v1,a1
        80033e40 21 40 c0 00     move       t0,a2
        80033e44 03 00 04 34     ori        a0,zero,0x3
        80033e48 21 28 40 00     move       a1,v0
        80033e4c 21 30 60 00     move       a2,v1
        80033e50 10 00 a7 af     sw         a3,local_10(sp)
        80033e54 18 00 bf af     sw         ra,local_8(sp)
        80033e58 2e cf 00 0c     jal        FUN_80033cb8                                     undefined FUN_80033cb8()
        80033e5c 21 38 00 01     _move      a3,t0
        80033e60 21 10 00 00     clear      v0
        80033e64 18 00 bf 8f     lw         ra,local_8(sp)
        80033e68 20 00 bd 27     addiu      sp,sp,0x20
        80033e6c 08 00 e0 03     jr         ra
        80033e70 00 00 00 00     _nop


### Minimum if short on time

Paste only these three:

1. `batres_victory` (`801B0000`)
2. `800A7254`
3. `800A3354`

## How to paste

In Ghidra Decompiler window: select all text, copy, paste into **Evidence**
below inside the fenced block. One section per function.

Do **not** commit large .dec / .bin binaries. Decompiler **text** in this
file (or docs/ghidra-pastes/*.md) is what we need.

## Evidence

```
### batres_victory (801B0000)

### batres_clear_battle_ui (801B0E20)

### 800A7254

### 800A3354

### 800B1060

### 800A56B0

### 80014540

### 80033E34

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
# optional longer pastes:
# mkdir -p docs/ghidra-pastes && git add docs/ghidra-pastes/
git commit -m "ops: Ghidra decompiles for BATRES victory / fanfare path"
git push
```

Then say **check**.

## Refs

- Overlay import / decompress / SCUS: [ghidra-battle-overlays.md](ghidra-battle-overlays.md)
- Fanfare finding: [findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md](findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md)



/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void UndefinedFunction_801b0000(void)

{
  undefined4 *puVar1;
  short sVar2;
  short sVar3;
  ushort uVar4;
  undefined2 uVar5;
  uint uVar6;
  undefined4 *puVar7;
  uint *puVar8;
  ushort *puVar9;
  int iVar10;
  ushort *puVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  ushort uVar15;
  undefined1 *puVar16;
  int iVar17;
  int iVar18;
  short sStack_78;
  uint uStack_70;
  int iStack_68;
  int iStack_60;
  int iStack_30;
  
  uVar4 = _DAT_800f83c6;
  uStack_70 = (uint)_DAT_8009d78a;
  iVar17 = 0;
  iVar18 = 0;
  iVar13 = 0;
  iVar12 = 0;
  sStack_78 = 0;
  iStack_68 = 0;
  iStack_60 = 0;
  do {
    if (*(char *)(iVar12 + -0x7ff07c18) != -1) {
      func_0x800a6000(iVar13,6,6);
    }
    iVar13 = iVar13 + 1;
    iVar12 = iVar12 + 0x68;
  } while (iVar13 < 10);
  if ((_DAT_800f83d0 & 4) != 0) {
    iVar13 = 0;
    iVar12 = 0x1a0;
    puVar7 = (undefined4 *)(_DAT_80075d08 * 0x18 + -0x7ff8a2f4);
    do {
      puVar1 = (undefined4 *)(iVar12 + -0x7ff07bf4);
      iVar12 = iVar12 + 0x68;
      iVar13 = iVar13 + 1;
      *puVar7 = *puVar1;
      puVar7 = puVar7 + 1;
    } while (iVar13 < 6);
  }
  if (_DAT_800f7dd2 != 0) {
    iVar14 = 0;
    iVar12 = func_0x80014a58();
    iVar10 = 0;
    iVar13 = 0;
    do {
      if (*(char *)(iVar13 + -0x7ff07c18) != -1) {
        iStack_68 = iStack_68 + *(int *)(iVar13 + -0x7ff07bf4);
        iVar10 = iVar10 + 1;
        iStack_60 = iStack_60 + (uint)*(ushort *)(iVar13 + -0x7ff07bf8);
      }
      iVar14 = iVar14 + 1;
      iVar13 = iVar13 + 0x68;
    } while (iVar14 < 4);
    iVar13 = iStack_68 / iVar12;
    if (iVar12 == 0) {
      trap(0x1c00);
    }
    if ((iVar12 == -1) && (iStack_68 == -0x80000000)) {
      trap(0x1800);
    }
    iVar14 = iStack_60 / iVar12;
    if (iVar12 == 0) {
      trap(0x1c00);
    }
    if ((iVar12 == -1) && (iStack_60 == -0x80000000)) {
      trap(0x1800);
    }
    iStack_68 = iVar13;
    iStack_60 = iVar14;
    if (iVar10 == 0) {
      _DAT_800f7dd2 = 0;
    }
  }
  if ((_DAT_8016376a & 0x40) != 0) {
    uVar4 = uVar4 | 0x40;
  }
  uVar15 = uVar4;
  if ((_DAT_8016376a & 0x80) != 0) {
    uVar15 = uVar4 | 0x80;
  }
  if ((uVar4 & 0x40) != 0) {
    uVar15 = uVar15 & 0xffdf;
  }
  if ((uVar15 & 0x20) != 0) {
    uVar15 = uVar15 & 0xfffb;
  }
  uVar4 = uVar15;
  if (((uVar15 & 2) != 0) && (uVar4 = uVar15 & 0xfff7, (_DAT_800f7dcc & 0xf) != 0)) {
    uVar4 = uVar15 & 0xfff5 | 8;
  }
  iVar12 = 0;
  FUN_801b0e20();
  do {
    func_0x800a7254(0,iVar12,4,0);
    iVar12 = iVar12 + 1;
    iVar13 = 0;
  } while (iVar12 < 10);
  puVar8 = (uint *)&DAT_801636c0;
  do {
    uVar6 = *puVar8;
    *puVar8 = uVar6 & 0x1831;
    puVar8 = puVar8 + 4;
    *(uint *)(iVar13 + -0x7fe9c93c) = uVar6 & 0x1831;
    iVar13 = iVar13 + 0x10;
  } while ((int)puVar8 < -0x7fe9c910);
  if ((uVar4 & 8) == 0) {
    if ((uVar4 & 2) == 0) {
      if ((uVar4 & 4) == 0) {
        if (((_DAT_80163624 & 8) != 0) && ((_DAT_8016376a & 0x100) == 0)) {
          iVar12 = 0xd0;
          do {
            *(undefined1 *)(iVar12 + -0x7ff07c0a) = 0xc;
            iVar12 = iVar12 + -0x68;
          } while (-1 < iVar12);
          iVar17 = 0x31;
          _DAT_800fa6b8 = 1;
        }
      }
      else if ((uVar4 & 0x40) == 0) {
        iVar17 = 8;
        iVar12 = 0xd0;
        do {
          *(undefined1 *)(iVar12 + -0x7ff07c0a) = 0xe;
          iVar12 = iVar12 + -0x68;
        } while (-1 < iVar12);
      }
    }
    else if ((uVar4 & 0x40) == 0) {
      iVar17 = 0x1e;
      func_0x800b1060(8);
      _DAT_80163b80 = 1;
    }
  }
  sVar3 = _DAT_80163b80;
  sVar2 = _DAT_800fa6b8;
  if (_DAT_800fa6b8 == 0 && _DAT_80163b80 == 0) {
    func_0x80014540();
  }
  iVar12 = 0;
  if (iVar17 != 0) {
    do {
      iVar12 = iVar12 + 1;
      func_0x800a3354();
    } while (iVar12 < iVar17);
  }
  while (_DAT_800fa6b8 != 0 || _DAT_80163b80 != 0) {
    func_0x800a3354();
  }
  if (sVar2 != 0 || sVar3 != 0) {
    func_0x80014540();
  }
  if ((_DAT_800f83d0 & 8) == 0) {
    func_0x800a31a0(0,0,0,0);
  }
  if ((uVar4 & 2) == 0) {
    if ((uVar4 & 0xc) != 0) {
      _DAT_800707be = _DAT_800707be | 8;
    }
  }
  else {
    _DAT_800707be = _DAT_800707be | 1;
  }
  iVar13 = 0;
  iVar12 = 0x1a0;
  do {
    if ((*(char *)(iVar12 + -0x7ff07c18) != -1) &&
       (((int)(uint)_DAT_800f7dcc >> (iVar13 + 4U & 0x1f) & 1U) == 0)) break;
    iVar13 = iVar13 + 1;
    iVar12 = iVar12 + 0x68;
  } while (iVar13 < 6);
  iVar12 = 0;
  if (iVar13 == 6) {
    _DAT_800707be = _DAT_800707be | 8;
  }
  do {
    iVar13 = 0;
    func_0x800a3354();
    func_0x800a56b0(10);
    do {
      func_0x800a56b0((int)(short)iVar13);
      iVar13 = iVar13 + 1;
    } while (iVar13 < 3);
    iVar12 = iVar12 + 1;
  } while (iVar12 < 0x10);
  func_0x800dcf94(0xffffffff);
  iVar12 = 0;
  puVar11 = (ushort *)&DAT_8009cbe0;
  puVar9 = (ushort *)&DAT_801671b8;
  do {
    *puVar11 = 0xffff;
    if (*puVar9 != 0xffff) {
      *puVar11 = *puVar9 & 0x1ff | (ushort)(byte)puVar9[1] << 9;
    }
    puVar11 = puVar11 + 1;
    iVar12 = iVar12 + 1;
    puVar9 = puVar9 + 3;
  } while (iVar12 < 0x140);
  if (((uVar4 & 0xde) == 0) && ((_DAT_800f83d0 & 0x20) == 0)) {
    sStack_78 = 4;
    iVar12 = 0;
    iVar13 = 0x1a0;
    iVar17 = 0;
    do {
      if (*(short *)(iVar17 + -0x7fe9c9a8) != -1) {
        iVar10 = *(short *)(iVar17 + -0x7fe9c9a8) * 0xb8;
        if (((*(uint *)(iVar13 + -0x7ff07c20) & 0x4001) != 0) &&
           (((int)(uint)_DAT_800f7dcc >> (iVar12 + 4U & 0x1f) & 1U) == 0)) {
          _DAT_8009d7d8 = _DAT_8009d7d8 + *(int *)(iVar13 + -0x7ff07bc4);
          _DAT_8009d7e0 = _DAT_8009d7e0 + *(int *)(iVar13 + -0x7ff07bc8);
          _DAT_8009d7dc = _DAT_8009d7dc + (uint)*(ushort *)(iVar10 + -0x7ff0a01e);
          if ((*(byte *)((iVar12 + 4U) * 0x44 + -0x7ff0a41f) & 0x11) == 0) {
            uVar4 = func_0x800b0f04(iVar10 + -0x7ff0a0bc,0,0,0x100);
            if (uVar4 != 0xffff) {
              iVar10 = 0;
              if (0 < iVar18) {
                iVar14 = 0;
                puVar16 = &DAT_8009d7d8;
                do {
                  if ((int)*(short *)(iVar14 + -0x7ff627f8) == (uint)uVar4) {
                    *(short *)(puVar16 + 0x32) = *(short *)(&DAT_8009d80a + iVar14) + 1;
                    break;
                  }
                  puVar16 = puVar16 + 6;
                  iVar10 = iVar10 + 1;
                  iVar14 = iVar14 + 6;
                } while (iVar10 < iVar18);
              }
              if (iVar10 == iVar18) {
                iVar18 = iVar10 + 1;
                *(ushort *)(iVar10 * 6 + -0x7ff627f8) = uVar4;
                *(undefined2 *)(&DAT_8009d80a + iVar10 * 6) = 1;
              }
            }
          }
        }
      }
      iVar13 = iVar13 + 0x68;
      iVar12 = iVar12 + 1;
      iVar17 = iVar17 + 0x10;
    } while (iVar12 < 6);
    if (DAT_80062f18 != 0) {
      _DAT_8009d7e0 = (int)(_DAT_8009d7e0 * (uint)DAT_80062f18) >> 4;
    }
    iVar12 = 0;
    func_0x800254d8();
    iStack_30 = 0;
    iVar18 = 0;
    iVar17 = 0;
    iVar13 = 0;
    do {
      iVar10 = 0;
      iVar14 = 0;
      do {
        if ((uint)*(byte *)(iVar12 + -0x7ff63424) == (uint)(byte)(&DAT_8009c738)[iVar14]) {
          uStack_70 = uStack_70 & ~(1 << (*(byte *)(iVar12 + -0x7ff63424) & 0x1f));
          puVar16 = &DAT_8009c738 + iVar14;
          uVar6 = 0;
          if ((*(uint *)(iVar18 + -0x7ff07c20) & 0x4001) == 0) {
            func_0x800a4acc(iVar12,_DAT_8009d7dc);
            uVar6 = _DAT_8009d7d8;
            if (*(byte *)(iVar13 + -0x7ff627b4) != 0) {
              uVar6 = _DAT_8009d7d8 * *(byte *)(iVar13 + -0x7ff627b4) >> 4;
            }
          }
          FUN_801b0ef8(puVar16,uVar6,iVar12);
          uVar5 = FUN_801b17cc(puVar16,*(undefined1 *)(iStack_30 + -0x7ff0a199),
                               *(undefined1 *)(iStack_30 + -0x7ff0a19c));
          *(undefined2 *)(iVar17 + -0x7ff62812) = uVar5;
          if (*(int *)(iStack_30 + -0x7ff0a17c) != *(int *)(iStack_30 + -0x7ff0a178)) {
            FUN_801b0c74(puVar16);
          }
        }
        iVar10 = iVar10 + 1;
        iVar14 = iVar14 + 0x84;
      } while (iVar10 < 9);
      iVar18 = iVar18 + 0x68;
      iVar17 = iVar17 + 0xc;
      iVar13 = iVar13 + 0x440;
      iVar12 = iVar12 + 1;
      iStack_30 = iStack_30 + 0x34;
    } while (iVar12 < 3);
    FUN_801b0d14(uStack_70);
  }
  FUN_801b09c0(iStack_68,iStack_60);
  func_0x800bb944();
  _DAT_80095dd4 = sStack_78;
  if (sStack_78 == 4) {
    func_0x80022de4();
  }
  return;
}

                             //
                             // ram
                             // ram:801b0000-ram:801b193b
                             //
                             batres_victory
        801b0000 78 ff bd 27     addiu      sp,sp,-0x88
        801b0014 8a d7 08 95     lhu        t0,-0x2876(t0)=>DAT_8009d78a
        801b001c 21 a0 00 00     clear      s4
        801b0024 21 a8 00 00     clear      s5
        801b002c 21 88 00 00     clear      s1
        801b003c 21 80 00 00     clear      s0
        801b0050 10 00 a0 af     sw         zero,0x10(sp)
        801b0054 20 00 a0 af     sw         zero,0x20(sp)
        801b0058 28 00 a0 af     sw         zero,0x28(sp)
        801b0068 e8 83 22 80     lb         v0,-0x7c18(at)
        801b0070 04 00 53 10     beq        v0,s3,LAB_801b0084
        801b007c 00 98 02 0c     jal        SUB_800a6000
                             LAB_801b0084                                    XREF[1]:     801b0070(j)  
        801b0084 01 00 31 26     addiu      s1,s1,0x1
        801b0088 0a 00 22 2a     slti       v0,s1,0xa
        801b008c f4 ff 40 14     bne        v0,zero,LAB_801b0060
        801b00a0 04 00 42 30     andi       v0,v0,0x4
        801b00a4 14 00 40 10     beq        v0,zero,LAB_801b00f8
        801b00ac 21 88 00 00     clear      s1
        801b00b0 a0 01 05 34     ori        a1,zero,0x1a0
        801b00cc c0 18 03 00     sll        v1,v1,0x3
        801b00d0 21 18 62 00     addu       v1,v1,v0
        801b00dc 0c 84 22 8c     lw         v0,-0x7bf4(at)=>DAT_800f85ac
        801b00e0 68 00 a5 24     addiu      a1,a1,0x68
        801b00e4 01 00 31 26     addiu      s1,s1,0x1
        801b00e8 00 00 62 ac     sw         v0,0x0(v1)
        801b00ec 06 00 22 2a     slti       v0,s1,0x6
        801b00f0 f8 ff 40 14     bne        v0,zero,LAB_801b00d4
        801b0104 3e 00 80 10     beq        a0,zero,LAB_801b0200
        801b010c 96 52 00 0c     jal        SUB_80014a58
        801b0118 21 28 00 00     clear      a1
        801b0120 21 20 00 00     clear      a0
        801b012c e8 83 22 80     lb         v0,-0x7c18(at)
        801b0134 0e 00 47 10     beq        v0,a3,LAB_801b0170
        801b0144 0c 84 22 8c     lw         v0,-0x7bf4(at)
        801b0154 08 84 23 94     lhu        v1,-0x7bf8(at)
        801b0158 21 40 02 01     addu       t0,t0,v0
        801b0164 01 00 a5 24     addiu      a1,a1,0x1
        801b0168 21 40 03 01     addu       t0,t0,v1
                             LAB_801b0170                                    XREF[1]:     801b0134(j)  
        801b0170 01 00 31 26     addiu      s1,s1,0x1
        801b0174 04 00 22 2a     slti       v0,s1,0x4
        801b0178 ea ff 40 14     bne        v0,zero,LAB_801b0124
        801b0188 1a 00 06 01     div        t0,a2
        801b018c 02 00 c0 14     bne        a2,zero,LAB_801b0198
        801b0194 0d 00 07 00     break      0x1c00
        801b019c 04 00 c1 14     bne        a2,at,LAB_801b01b0
        801b01a4 02 00 01 15     bne        t0,at,LAB_801b01b0
        801b01ac 0d 00 06 00     break      0x1800
        801b01c4 1a 00 06 01     div        t0,a2
        801b01c8 02 00 c0 14     bne        a2,zero,LAB_801b01d4
        801b01d0 0d 00 07 00     break      0x1c00
        801b01d8 04 00 c1 14     bne        a2,at,LAB_801b01ec
        801b01e0 02 00 01 15     bne        t0,at,LAB_801b01ec
        801b01e8 0d 00 06 00     break      0x1800
        801b01f0 03 00 a0 14     bne        a1,zero,LAB_801b0200
        801b01fc d2 7d 20 a4     sh         zero,offset DAT_800f7dd2(at)
        801b020c 40 00 62 30     andi       v0,v1,0x40
        801b0210 02 00 40 10     beq        v0,zero,LAB_801b021c
        801b0218 40 00 52 36     ori        s2,s2,0x40
                             LAB_801b021c                                    XREF[1]:     801b0210(j)  
        801b021c 03 00 40 10     beq        v0,zero,LAB_801b022c
        801b0224 80 00 52 36     ori        s2,s2,0x80
                             LAB_801b022c                                    XREF[1]:     801b021c(j)  
        801b022c 02 00 40 10     beq        v0,zero,LAB_801b0238
        801b0234 24 90 42 02     and        s2,s2,v0
                             LAB_801b0238                                    XREF[1]:     801b022c(j)  
        801b0238 20 00 42 32     andi       v0,s2,0x20
        801b023c 02 00 40 10     beq        v0,zero,LAB_801b0248
        801b0244 24 90 42 02     and        s2,s2,v0
                             LAB_801b0248                                    XREF[1]:     801b023c(j)  
        801b0248 02 00 42 32     andi       v0,s2,0x2
        801b024c 0a 00 40 10     beq        v0,zero,LAB_801b0278
        801b0260 0f 00 42 30     andi       v0,v0,0xf
        801b0264 04 00 40 10     beq        v0,zero,LAB_801b0278
        801b0270 24 90 42 02     and        s2,s2,v0
        801b0274 08 00 52 36     ori        s2,s2,0x8
                             LAB_801b0278                                    XREF[2]:     801b024c(j), 801b0264(j)  
        801b0278 88 c3 06 0c     jal        batres_clear_battle_ui                           undefined batres_clear_battle_ui()
        801b028c 95 9c 02 0c     jal        SUB_800a7254
        801b0294 01 00 31 26     addiu      s1,s1,0x1
        801b0298 0a 00 22 2a     slti       v0,s1,0xa
        801b029c f8 ff 40 14     bne        v0,zero,LAB_801b0280
        801b02a8 c0 36 63 24     addiu      v1,v1,0x36c0
                             LAB_801b02b0                                    XREF[1]:     801b02d4(j)  
        801b02b0 00 00 62 8c     lw         v0,0x0(v1)=>DAT_801636c0
        801b02b8 31 18 42 30     andi       v0,v0,0x1831
        801b02bc 00 00 62 ac     sw         v0,0x0(v1)=>DAT_801636c0
        801b02c0 10 00 63 24     addiu      v1,v1,0x10
        801b02cc c4 36 22 ac     sw         v0,0x36c4(at)
        801b02d0 2a 10 65 00     slt        v0,v1,a1
        801b02d4 f6 ff 40 14     bne        v0,zero,LAB_801b02b0
        801b02dc 08 00 42 32     andi       v0,s2,0x8
        801b02e0 33 00 40 14     bne        v0,zero,LAB_801b03b0
        801b02e8 0b 00 40 10     beq        v0,zero,LAB_801b0318
        801b02f0 2f 00 40 14     bne        v0,zero,LAB_801b03b0
        801b02f8 1e 00 14 34     ori        s4,zero,0x1e
        801b02fc 18 c4 02 0c     jal        SUB_800b1060
        801b030c 80 3b 22 a4     sh         v0,offset DAT_80163b80(at)
                             LAB_801b0318                                    XREF[1]:     801b02e8(j)  
        801b0318 04 00 42 32     andi       v0,s2,0x4
        801b031c 0d 00 40 10     beq        v0,zero,LAB_801b0354
        801b0324 22 00 40 14     bne        v0,zero,LAB_801b03b0
        801b032c 08 00 14 34     ori        s4,zero,0x8
        801b0330 d0 00 02 34     ori        v0,zero,0xd0
        801b033c f6 83 23 a0     sb         v1,-0x7c0a(at)=>DAT_800f84c6
        801b0340 98 ff 42 24     addiu      v0,v0,-0x68
        801b0344 1a 00 40 04     bltz       v0,LAB_801b03b0
        801b0360 08 00 42 30     andi       v0,v0,0x8
        801b0364 12 00 40 10     beq        v0,zero,LAB_801b03b0
        801b0378 00 01 42 30     andi       v0,v0,0x100
        801b037c 0c 00 40 14     bne        v0,zero,LAB_801b03b0
        801b0384 d0 00 02 34     ori        v0,zero,0xd0
        801b0390 f6 83 23 a0     sb         v1,-0x7c0a(at)=>DAT_800f84c6
        801b0394 98 ff 42 24     addiu      v0,v0,-0x68
        801b0398 fb ff 41 04     bgez       v0,LAB_801b0388
        801b03a0 31 00 14 34     ori        s4,zero,0x31
        801b03ac b8 a6 22 a4     sh         v0,-0x5948(at)=>DAT_800fa6b8
                             LAB_801b03b0                                    XREF[7]:     801b02e0(j), 801b02f0(j), 
                                                                                          801b0310(j), 801b0324(j), 
                                                                                          801b0344(j), 801b0364(j), 
                                                                                          801b037c(j)  
        801b03b0 10 80 03 3c     lui        v1,0x8010
        801b03c8 03 00 00 16     bne        s0,zero,LAB_801b03d8
        801b03d0 50 51 00 0c     jal        SUB_80014540
                             LAB_801b03d8                                    XREF[1]:     801b03c8(j)  
        801b03d8 0a 00 80 12     beq        s4,zero,LAB_801b0404
                             LAB_801b03e0                                    XREF[1]:     801b03f4(j)  
        801b03e0 d5 8c 02 0c     jal        SUB_800a3354
        801b03e8 2a 10 34 02     slt        v0,s1,s4
        801b03ec 05 00 40 10     beq        v0,zero,LAB_801b0404
                             LAB_801b03fc                                    XREF[1]:     801b041c(j)  
        801b03fc d5 8c 02 0c     jal        SUB_800a3354
        801b041c f7 ff 40 14     bne        v0,zero,LAB_801b03fc
        801b0424 03 00 00 12     beq        s0,zero,LAB_801b0434
        801b042c 50 51 00 0c     jal        SUB_80014540
        801b0440 08 00 42 30     andi       v0,v0,0x8
        801b0444 07 00 40 14     bne        v0,zero,LAB_801b0464
        801b0458 68 8c 02 0c     jal        SUB_800a31a0
                             LAB_801b0464                                    XREF[1]:     801b0444(j)  
        801b0464 06 00 40 10     beq        v0,zero,LAB_801b0480
        801b0478 28 c1 06 08     j          LAB_801b04a0
                             LAB_801b0480                                    XREF[1]:     801b0464(j)  
        801b0480 0c 00 42 32     andi       v0,s2,0xc
        801b0484 08 00 40 10     beq        v0,zero,LAB_801b04a8
        801b049c 08 00 42 34     ori        v0,v0,0x8
                             LAB_801b04a8                                    XREF[1]:     801b0484(j)  
        801b04a8 ff ff 06 24     li         a2,-0x1
        801b04b4 a0 01 04 34     ori        a0,zero,0x1a0
        801b04c0 e8 83 22 80     lb         v0,-0x7c18(at)=>DAT_800f8588
        801b04c8 07 00 46 10     beq        v0,a2,LAB_801b04e8
        801b04d0 00 00 a2 94     lhu        v0,0x0(a1)=>DAT_800f7dcc
        801b04d8 07 10 62 00     srav       v0,v0,v1
        801b04dc 01 00 42 30     andi       v0,v0,0x1
        801b04e0 06 00 40 10     beq        v0,zero,LAB_801b04fc
                             LAB_801b04e8                                    XREF[1]:     801b04c8(j)  
        801b04e8 01 00 31 26     addiu      s1,s1,0x1
        801b04ec 06 00 22 2a     slti       v0,s1,0x6
        801b04f0 f1 ff 40 14     bne        v0,zero,LAB_801b04b8
                             LAB_801b04fc                                    XREF[1]:     801b04e0(j)  
        801b04fc 07 00 22 16     bne        s1,v0,LAB_801b051c
        801b0514 08 00 42 34     ori        v0,v0,0x8
                             LAB_801b051c                                    XREF[2]:     801b04fc(j), 801b0550(j)  
        801b051c d5 8c 02 0c     jal        SUB_800a3354
        801b0524 ac 95 02 0c     jal        SUB_800a56b0
                             LAB_801b052c                                    XREF[1]:     801b0540(j)  
        801b052c 00 24 10 00     sll        a0,s0,0x10
        801b0530 ac 95 02 0c     jal        SUB_800a56b0
        801b0538 01 00 10 26     addiu      s0,s0,0x1
        801b053c 03 00 02 2a     slti       v0,s0,0x3
        801b0540 fa ff 40 14     bne        v0,zero,LAB_801b052c
        801b0548 01 00 31 26     addiu      s1,s1,0x1
        801b054c 10 00 22 2a     slti       v0,s1,0x10
        801b0550 f2 ff 40 14     bne        v0,zero,LAB_801b051c
        801b0558 e5 73 03 0c     jal        SUB_800dcf94
        801b0560 21 88 00 00     clear      s1
        801b0570 e0 cb a5 24     addiu      a1,a1,-0x3420
        801b0578 b8 71 84 24     addiu      a0,a0,0x71b8
                             LAB_801b057c                                    XREF[1]:     801b05b4(j)  
        801b057c 00 00 a6 a4     sh         a2,0x0(a1)=>DAT_8009cbe0
        801b0580 00 00 83 94     lhu        v1,0x0(a0)=>DAT_801671b8
        801b0588 07 00 66 10     beq        v1,a2,LAB_801b05a8
        801b0590 02 00 82 90     lbu        v0,0x2(a0)=>DAT_801671ba
        801b059c 24 10 47 00     and        v0,v0,a3
        801b05a0 25 18 62 00     or         v1,v1,v0
        801b05a4 00 00 a3 a4     sh         v1,0x0(a1)=>DAT_8009cbe0
                             LAB_801b05a8                                    XREF[1]:     801b0588(j)  
        801b05a8 02 00 a5 24     addiu      a1,a1,0x2
        801b05ac 01 00 31 26     addiu      s1,s1,0x1
        801b05b0 40 01 22 2a     slti       v0,s1,0x140
        801b05b4 f1 ff 40 14     bne        v0,zero,LAB_801b057c
        801b05bc de 00 42 32     andi       v0,s2,0xde
        801b05c0 e0 00 40 14     bne        v0,zero,LAB_801b0944
        801b05d4 20 00 42 30     andi       v0,v0,0x20
        801b05d8 da 00 40 14     bne        v0,zero,LAB_801b0944
        801b05e0 10 00 a8 af     sw         t0,0x10(sp)
        801b05e4 21 88 00 00     clear      s1
        801b05f4 d8 d7 73 26     addiu      s3,s3,-0x2828
        801b05f8 a0 01 12 34     ori        s2,zero,0x1a0
        801b05fc 21 a0 00 00     clear      s4
        801b0608 58 36 23 84     lh         v1,0x3658(at)
        801b0610 5b 00 62 10     beq        v1,v0,LAB_801b0780
        801b0624 c0 10 02 00     sll        v0,v0,0x3
        801b0628 21 20 56 00     addu       a0,v0,s6
        801b0634 e0 83 22 8c     lw         v0,-0x7c20(at)=>DAT_800f8580
        801b063c 01 40 42 30     andi       v0,v0,0x4001
        801b0640 4f 00 40 10     beq        v0,zero,LAB_801b0780
        801b0648 88 1e c2 96     lhu        v0,0x1e88(s6)=>DAT_800f7dcc
        801b0650 07 10 a2 00     srav       v0,v0,a1
        801b0654 01 00 42 30     andi       v0,v0,0x1
        801b0658 49 00 40 14     bne        v0,zero,LAB_801b0780
        801b066c 3c 84 23 8c     lw         v1,-0x7bc4(at)=>DAT_800f85dc
        801b0674 21 10 43 00     addu       v0,v0,v1
        801b0688 38 84 23 8c     lw         v1,-0x7bc8(at)=>DAT_800f85d8
        801b0690 21 10 43 00     addu       v0,v0,v1
        801b0698 9e 00 83 94     lhu        v1,0x9e(a0)
        801b06a4 21 10 43 00     addu       v0,v0,v1
        801b06b4 80 10 02 00     sll        v0,v0,0x2
        801b06c0 e1 5b 22 90     lbu        v0,0x5be1(at)
        801b06c8 11 00 42 30     andi       v0,v0,0x11
        801b06cc 2c 00 40 14     bne        v0,zero,LAB_801b0780
        801b06d8 c1 c3 02 0c     jal        SUB_800b0f04
        801b06e4 ff ff c3 30     andi       v1,a2,0xffff
        801b06ec 24 00 62 10     beq        v1,v0,LAB_801b0780
        801b06f4 16 00 a0 1a     blez       s5,LAB_801b0750
        801b0704 21 18 00 00     clear      v1
        801b0710 08 d8 22 84     lh         v0,-0x27f8(at)
        801b0718 08 00 45 14     bne        v0,a1,LAB_801b073c
        801b0728 0a d8 22 94     lhu        v0,-0x27f6(at)
        801b0730 01 00 42 24     addiu      v0,v0,0x1
        801b0734 d4 c1 06 08     j          LAB_801b0750
                             LAB_801b073c                                    XREF[1]:     801b0718(j)  
        801b073c 06 00 84 24     addiu      a0,a0,0x6
        801b0740 01 00 10 26     addiu      s0,s0,0x1
        801b0744 2a 10 15 02     slt        v0,s0,s5
        801b0748 ef ff 40 14     bne        v0,zero,LAB_801b0708
                             LAB_801b0750                                    XREF[2]:     801b06f4(j), 801b0734(j)  
        801b0750 0b 00 15 16     bne        s0,s5,LAB_801b0780
        801b0758 01 00 15 26     addiu      s5,s0,0x1
        801b0760 40 10 02 00     sll        v0,v0,0x1
        801b0770 08 d8 26 a4     sh         a2,-0x27f8(at)
        801b077c 0a d8 23 a4     sh         v1,-0x27f6(at)=>DAT_8009d80a
                             LAB_801b0780                                    XREF[6]:     801b0610(j), 801b0640(j), 
                                                                                          801b0658(j), 801b06cc(j), 
                                                                                          801b06ec(j), 801b0750(j)  
        801b0780 68 00 52 26     addiu      s2,s2,0x68
        801b0784 01 00 31 26     addiu      s1,s1,0x1
        801b0788 06 00 22 2a     slti       v0,s1,0x6
        801b078c 9c ff 40 14     bne        v0,zero,LAB_801b0600
        801b0798 18 2f 84 90     lbu        a0,offset DAT_80062f18(a0)
        801b07a0 09 00 80 10     beq        a0,zero,LAB_801b07c8
        801b07b8 18 00 44 00     mult       v0,a0
        801b07c0 03 11 08 00     sra        v0,t0,0x4
                             LAB_801b07c8                                    XREF[1]:     801b07a0(j)  
        801b07c8 36 95 00 0c     jal        SUB_800254d8
        801b07d0 58 00 a0 af     sw         zero,0x58(sp)
        801b07d4 21 f0 00 00     clear      s8
        801b07d8 21 b8 00 00     clear      s7
        801b07dc 21 b0 00 00     clear      s6
                             LAB_801b07e0                                    XREF[1]:     801b0930(j)  
        801b07e0 21 80 00 00     clear      s0
        801b07e8 21 a0 00 00     clear      s4
        801b0800 dc cb 23 90     lbu        v1,-0x3424(at)
        801b080c 38 c7 22 90     lbu        v0,-0x38c8(at)=>DAT_8009c738
        801b0814 3b 00 62 14     bne        v1,v0,LAB_801b0904
        801b0820 04 10 62 00     sllv       v0,v0,v1
        801b0828 27 10 02 00     nor        v0,zero,v0
        801b082c 24 40 02 01     and        t0,t0,v0
        801b0840 21 98 82 02     addu       s3,s4,v0
        801b084c e0 83 22 8c     lw         v0,-0x7c20(at)
        801b085c 01 40 42 30     andi       v0,v0,0x4001
        801b0860 0c 00 40 14     bne        v0,zero,LAB_801b0894
        801b0870 b3 92 02 0c     jal        SUB_800a4acc
        801b0878 00 00 45 92     lbu        a1,0x0(s2)
        801b0884 03 00 a0 10     beq        a1,zero,LAB_801b0894
        801b0890 02 31 08 00     srl        a2,t0,0x4
        801b089c be c3 06 0c     jal        FUN_801b0ef8                                     undefined FUN_801b0ef8()
        801b08ac 67 5e 25 90     lbu        a1,0x5e67(at)
        801b08b8 64 5e 26 90     lbu        a2,0x5e64(at)
        801b08bc f3 c5 06 0c     jal        FUN_801b17cc                                     undefined FUN_801b17cc()
        801b08d0 ee d7 22 a4     sh         v0,-0x2812(at)
        801b08dc 84 5e 23 8c     lw         v1,0x5e84(at)
        801b08e8 88 5e 22 8c     lw         v0,0x5e88(at)
        801b08f4 03 00 a0 10     beq        a1,zero,LAB_801b0904
        801b08fc 1d c3 06 0c     jal        FUN_801b0c74                                     undefined FUN_801b0c74()
                             LAB_801b0904                                    XREF[2]:     801b0814(j), 801b08f4(j)  
        801b0904 01 00 10 26     addiu      s0,s0,0x1
        801b0908 09 00 02 2a     slti       v0,s0,0x9
        801b090c ba ff 40 14     bne        v0,zero,LAB_801b07f8
        801b0914 68 00 de 27     addiu      s8,s8,0x68
        801b0918 0c 00 f7 26     addiu      s7,s7,0xc
        801b091c 40 04 d6 26     addiu      s6,s6,0x440
        801b0920 01 00 31 26     addiu      s1,s1,0x1
        801b0928 03 00 22 2a     slti       v0,s1,0x3
        801b092c 34 00 08 25     addiu      t0,t0,0x34
        801b0930 ab ff 40 14     bne        v0,zero,LAB_801b07e0
        801b093c 45 c3 06 0c     jal        FUN_801b0d14                                     undefined FUN_801b0d14()
        801b094c 70 c2 06 0c     jal        FUN_801b09c0                                     undefined FUN_801b09c0()
        801b0954 51 ee 02 0c     jal        SUB_800bb944
        801b0964 d4 5d 28 a4     sh         t0,offset DAT_80095dd4(at)
        801b097c 03 00 43 14     bne        v0,v1,LAB_801b098c
        801b0984 79 8b 00 0c     jal        SUB_80022de4
        801b09b8 08 00 e0 03     jr         ra
