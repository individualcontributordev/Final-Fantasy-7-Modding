# Ghidra pastes - BATRES victory / fanfare path

Source: operator paste in docs/INSTRUCTIONS.md (28c2c5c), cleaned.

Programs: BATRES @ 801B0000, BATTLE @ 800A0000, SCUS @ 80010000.

## batres_clear_battle_ui

```c
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
```

## FUN_800a7254

```c
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
```

## FUN_800a3354

```c
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
```

## FUN_800b1060

```c
void FUN_800b1060(undefined4 param_1)

{
  FUN_800a31a0(10,2,1,param_1);
  return;
}
```

## FUN_800a56b0

```c
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
```

## FUN_80014540

```c
void FUN_80014540(void)

{
  FUN_80033e34(_DAT_80071744,_DAT_80095dd8,_DAT_800722c8,0);
  return;
}
```

## FUN_80033e34

```c
undefined4 FUN_80033e34(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_80033cb8(3,param_1,param_2,param_3,param_4);
  return 0;
}
```

## batres_victory

```c
void batres_victory(void)

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
```
