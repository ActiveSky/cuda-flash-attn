define protected metaxgpu_kernel void @_Z33paged_decode_reduce_group8_kernelILb1ELb0ELb1ELb1ELb1ELb0ELi0ELb1EEvPKfS1_S1_P15__maca_bfloat16PKiiii(ptr addrspace(1) noalias nocapture noundef readonly %partial_m.coerce, ptr addrspace(1) noalias nocapture noundef readonly %partial_l.coerce, ptr addrspace(1) noalias nocapture noundef readonly %partial_acc.coerce, ptr addrspace(1) noalias nocapture noundef writeonly %out.coerce, ptr addrspace(1) noalias nocapture noundef readonly %cache_seqlens.coerce, i32 noundef %batch_size, i32 noundef %pages_per_split, i32 noundef %n_split) local_unnamed_addr #18 comdat {
entry:
  %0 = tail call noundef range(i32 0, 1024) i32 @llvm.mxc.thread.id.x(), !range !26
  %1 = tail call noundef range(i32 0, 1024) i32 @llvm.mxc.thread.id.y(), !range !26
  %2 = tail call noundef range(i32 0, 2147483647) i32 @llvm.mxc.block.id.x(), !range !15
  %shr = lshr i32 %2, 2
  %and = shl i32 %2, 3
  %shl = and i32 %and, 24
  %add = add nuw nsw i32 %shl, %1
  %idxprom = zext nneg i32 %shr to i64
  %arrayidx = getelementptr inbounds i32, ptr addrspace(1) %cache_seqlens.coerce, i64 %idxprom
  %3 = load i32, ptr addrspace(1) %arrayidx, align 4, !tbaa !16
  %cmp = icmp sgt i32 %3, 15
  br i1 %cmp, label %cond.true, label %cond.false

cond.true:                                        ; preds = %entry
  %div425426 = lshr i32 %3, 4
  %add9 = add i32 %pages_per_split, -1
  %sub = add i32 %add9, %div425426
  %div10 = sdiv i32 %sub, %pages_per_split
  %cond.i.i = tail call noundef i32 @llvm.smin.i32(i32 %n_split, i32 %div10), !call_argsrelate !262
  br label %cond.end

cond.false:                                       ; preds = %entry
  %and12 = and i32 %3, 15
  %cmp13 = icmp ne i32 %and12, 0
  %conv = zext i1 %cmp13 to i32
  br label %cond.end

cond.end:                                         ; preds = %cond.false, %cond.true
  %cond = phi i32 [ %cond.i.i, %cond.true ], [ %conv, %cond.false ]
  %mul = shl nsw i32 %shr, 5
  %add14 = add nuw nsw i32 %add, %mul
  %mul15 = shl nsw i32 %add14, 7
  %idx.ext = zext nneg i32 %mul15 to i64
  %add.ptr = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %out.coerce, i64 %idx.ext
  %mul16 = shl nuw nsw i32 %0, 3
  %idx.ext17 = zext nneg i32 %mul16 to i64
  %add.ptr18 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %add.ptr, i64 %idx.ext17
  %cmp19 = icmp slt i32 %cond, 2
  br i1 %cmp19, label %if.then, label %if.end78

if.then:                                          ; preds = %cond.end
  %cmp20 = icmp eq i32 %cond, 1
  br i1 %cmp20, label %if.then21, label %if.end

if.then21:                                        ; preds = %if.then
  %idxprom24 = zext nneg i32 %add14 to i64
  %arrayidx25 = getelementptr inbounds float, ptr addrspace(1) %partial_l.coerce, i64 %idxprom24
  %4 = load float, ptr addrspace(1) %arrayidx25, align 4, !tbaa !73
  %cmp26 = fcmp contract ogt float %4, 0.000000e+00
  %div28 = fdiv contract float 1.000000e+00, %4
  %cond31 = select contract i1 %cmp26, float %div28, float 0.000000e+00
  %add.ptr34 = getelementptr inbounds float, ptr addrspace(1) %partial_acc.coerce, i64 %idx.ext
  %add.ptr37 = getelementptr inbounds float, ptr addrspace(1) %add.ptr34, i64 %idx.ext17
  %a0.sroa.0.0.copyload = load float, ptr addrspace(1) %add.ptr37, align 16, !tbaa !73
  %a0.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 4
  %a0.sroa.4.0.copyload = load float, ptr addrspace(1) %a0.sroa.4.0..sroa_idx, align 4, !tbaa !73
  %a0.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 8
  %a0.sroa.5.0.copyload = load float, ptr addrspace(1) %a0.sroa.5.0..sroa_idx, align 8, !tbaa !73
  %a0.sroa.6.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 12
  %a0.sroa.6.0.copyload = load float, ptr addrspace(1) %a0.sroa.6.0..sroa_idx, align 4, !tbaa !73
  %add.ptr38 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 16
  %a1.sroa.0.0.copyload = load float, ptr addrspace(1) %add.ptr38, align 16, !tbaa !73
  %a1.sroa.4.0.add.ptr38.sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 20
  %a1.sroa.4.0.copyload = load float, ptr addrspace(1) %a1.sroa.4.0.add.ptr38.sroa_idx, align 4, !tbaa !73
  %a1.sroa.5.0.add.ptr38.sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 24
  %a1.sroa.5.0.copyload = load float, ptr addrspace(1) %a1.sroa.5.0.add.ptr38.sroa_idx, align 8, !tbaa !73
  %a1.sroa.6.0.add.ptr38.sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %add.ptr37, i64 28
  %a1.sroa.6.0.copyload = load float, ptr addrspace(1) %a1.sroa.6.0.add.ptr38.sroa_idx, align 4, !tbaa !73
  %mul39 = fmul contract float %a0.sroa.0.0.copyload, %cond31
  %mul41 = fmul contract float %a0.sroa.4.0.copyload, %cond31
  %mul43 = fmul contract float %cond31, %a0.sroa.5.0.copyload
  %mul45 = fmul contract float %cond31, %a0.sroa.6.0.copyload
  %mul48 = fmul contract float %cond31, %a1.sroa.0.0.copyload
  %mul51 = fmul contract float %cond31, %a1.sroa.4.0.copyload
  %mul54 = fmul contract float %cond31, %a1.sroa.5.0.copyload
  %mul57 = fmul contract float %cond31, %a1.sroa.6.0.copyload
  br label %if.end

if.end:                                           ; preds = %if.then21, %if.then
  %value.sroa.17.0 = phi float [ %mul57, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.15.0 = phi float [ %mul54, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.13.0 = phi float [ %mul51, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.11.0 = phi float [ %mul48, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.9.0 = phi float [ %mul45, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.7.0 = phi float [ %mul43, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.5.0 = phi float [ %mul41, %if.then21 ], [ 0.000000e+00, %if.then ]
  %value.sroa.0.0 = phi float [ %mul39, %if.then21 ], [ 0.000000e+00, %if.then ]
  %cmp.i.i.i = fcmp contract uno float %value.sroa.0.0, 0.000000e+00
  %5 = select i1 %cmp.i.i.i, float 0x7FFFE00000000000, float %value.sroa.0.0
  %6 = bitcast float %5 to i32
  %shr.i.i.i.i.i = lshr i32 %6, 16
  %and.i.i.i.i.i = and i32 %shr.i.i.i.i.i, 1
  %add.i.i.i.i.i = add i32 %6, 32767
  %add1.i.i.i.i.i = add i32 %add.i.i.i.i.i, %and.i.i.i.i.i
  %shr2.i.i.i.i.i = lshr i32 %add1.i.i.i.i.i, 16
  %conv.i.i.i.i.i = trunc nuw i32 %shr2.i.i.i.i.i to i16
  %cmp.i1.i.i = fcmp contract uno float %value.sroa.5.0, 0.000000e+00
  %7 = select i1 %cmp.i1.i.i, float 0x7FFFE00000000000, float %value.sroa.5.0
  %8 = bitcast float %7 to i32
  %shr.i.i.i2.i.i = lshr i32 %8, 16
  %and.i.i.i3.i.i = and i32 %shr.i.i.i2.i.i, 1
  %add.i.i.i4.i.i = add i32 %8, 32767
  %add1.i.i.i5.i.i = add i32 %add.i.i.i4.i.i, %and.i.i.i3.i.i
  %shr2.i.i.i6.i.i = lshr i32 %add1.i.i.i5.i.i, 16
  %conv.i.i.i7.i.i = trunc nuw i32 %shr2.i.i.i6.i.i to i16
  store i16 %conv.i.i.i.i.i, ptr addrspace(1) %add.ptr18, align 4, !tbaa !27
  %y3.i = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 2
  store i16 %conv.i.i.i7.i.i, ptr addrspace(1) %y3.i, align 2, !tbaa !27
  %cmp.i.i.i290 = fcmp contract uno float %value.sroa.7.0, 0.000000e+00
  %9 = select i1 %cmp.i.i.i290, float 0x7FFFE00000000000, float %value.sroa.7.0
  %10 = bitcast float %9 to i32
  %shr.i.i.i.i.i291 = lshr i32 %10, 16
  %and.i.i.i.i.i292 = and i32 %shr.i.i.i.i.i291, 1
  %add.i.i.i.i.i293 = add i32 %10, 32767
  %add1.i.i.i.i.i294 = add i32 %add.i.i.i.i.i293, %and.i.i.i.i.i292
  %shr2.i.i.i.i.i295 = lshr i32 %add1.i.i.i.i.i294, 16
  %conv.i.i.i.i.i296 = trunc nuw i32 %shr2.i.i.i.i.i295 to i16
  %cmp.i1.i.i297 = fcmp contract uno float %value.sroa.9.0, 0.000000e+00
  %11 = select i1 %cmp.i1.i.i297, float 0x7FFFE00000000000, float %value.sroa.9.0
  %12 = bitcast float %11 to i32
  %shr.i.i.i2.i.i298 = lshr i32 %12, 16
  %and.i.i.i3.i.i299 = and i32 %shr.i.i.i2.i.i298, 1
  %add.i.i.i4.i.i300 = add i32 %12, 32767
  %add1.i.i.i5.i.i301 = add i32 %add.i.i.i4.i.i300, %and.i.i.i3.i.i299
  %shr2.i.i.i6.i.i302 = lshr i32 %add1.i.i.i5.i.i301, 16
  %conv.i.i.i7.i.i303 = trunc nuw i32 %shr2.i.i.i6.i.i302 to i16
  %arrayidx66 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 4
  store i16 %conv.i.i.i.i.i296, ptr addrspace(1) %arrayidx66, align 4, !tbaa !27
  %y3.i306 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 6
  store i16 %conv.i.i.i7.i.i303, ptr addrspace(1) %y3.i306, align 2, !tbaa !27
  %cmp.i.i.i307 = fcmp contract uno float %value.sroa.11.0, 0.000000e+00
  %13 = select i1 %cmp.i.i.i307, float 0x7FFFE00000000000, float %value.sroa.11.0
  %14 = bitcast float %13 to i32
  %shr.i.i.i.i.i308 = lshr i32 %14, 16
  %and.i.i.i.i.i309 = and i32 %shr.i.i.i.i.i308, 1
  %add.i.i.i.i.i310 = add i32 %14, 32767
  %add1.i.i.i.i.i311 = add i32 %add.i.i.i.i.i310, %and.i.i.i.i.i309
  %shr2.i.i.i.i.i312 = lshr i32 %add1.i.i.i.i.i311, 16
  %conv.i.i.i.i.i313 = trunc nuw i32 %shr2.i.i.i.i.i312 to i16
  %cmp.i1.i.i314 = fcmp contract uno float %value.sroa.13.0, 0.000000e+00
  %15 = select i1 %cmp.i1.i.i314, float 0x7FFFE00000000000, float %value.sroa.13.0
  %16 = bitcast float %15 to i32
  %shr.i.i.i2.i.i315 = lshr i32 %16, 16
  %and.i.i.i3.i.i316 = and i32 %shr.i.i.i2.i.i315, 1
  %add.i.i.i4.i.i317 = add i32 %16, 32767
  %add1.i.i.i5.i.i318 = add i32 %add.i.i.i4.i.i317, %and.i.i.i3.i.i316
  %shr2.i.i.i6.i.i319 = lshr i32 %add1.i.i.i5.i.i318, 16
  %conv.i.i.i7.i.i320 = trunc nuw i32 %shr2.i.i.i6.i.i319 to i16
  %arrayidx71 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 8
  store i16 %conv.i.i.i.i.i313, ptr addrspace(1) %arrayidx71, align 4, !tbaa !27
  %y3.i323 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 10
  store i16 %conv.i.i.i7.i.i320, ptr addrspace(1) %y3.i323, align 2, !tbaa !27
  br label %cleanup

if.end78:                                         ; preds = %cond.end
  %cmp86 = icmp slt i32 %0, %cond
  br i1 %cmp86, label %if.then87, label %if.end95

if.then87:                                        ; preds = %if.end78
  %mul89 = mul nsw i32 %0, %batch_size
  %add90 = add nsw i32 %mul89, %shr
  %mul91 = shl nsw i32 %add90, 5
  %add92 = add nsw i32 %mul91, %add
  %idxprom93 = sext i32 %add92 to i64
  %arrayidx94 = getelementptr inbounds float, ptr addrspace(1) %partial_m.coerce, i64 %idxprom93
  %17 = load float, ptr addrspace(1) %arrayidx94, align 4, !tbaa !73
  br label %if.end95

if.end95:                                         ; preds = %if.then87, %if.end78
  %ms_lane.0 = phi float [ %17, %if.then87 ], [ 0xFFF0000000000000, %if.end78 ]
  %18 = bitcast float %ms_lane.0 to i32
  %19 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %18, i32 296, i32 15, i32 15, i1 false)
  %20 = bitcast i32 %19 to float
  %21 = tail call contract noundef float @llvm.maxnum.f32(float %ms_lane.0, float %20)
  %22 = bitcast float %21 to i32
  %23 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %22, i32 292, i32 15, i32 15, i1 false)
  %24 = bitcast i32 %23 to float
  %25 = tail call contract noundef float @llvm.maxnum.f32(float %21, float %24)
  %26 = bitcast float %25 to i32
  %27 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %26, i32 78, i32 15, i32 15, i1 false)
  %28 = bitcast i32 %27 to float
  %29 = tail call contract noundef float @llvm.maxnum.f32(float %25, float %28)
  %30 = bitcast float %29 to i32
  %31 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %30, i32 177, i32 15, i32 15, i1 false)
  br i1 %cmp86, label %if.then98, label %if.end110

if.then98:                                        ; preds = %if.end95
  %32 = bitcast i32 %31 to float
  %33 = tail call contract noundef float @llvm.maxnum.f32(float %29, float %32)
  %mul100 = mul nsw i32 %0, %batch_size
  %add101 = add nsw i32 %mul100, %shr
  %mul102 = shl nsw i32 %add101, 5
  %add103 = add nsw i32 %mul102, %add
  %sub104 = fsub contract float %ms_lane.0, %33
  %34 = tail call contract noundef float @llvm.exp2.f32(float %sub104)
  %idxprom107 = sext i32 %add103 to i64
  %arrayidx108 = getelementptr inbounds float, ptr addrspace(1) %partial_l.coerce, i64 %idxprom107
  %35 = load float, ptr addrspace(1) %arrayidx108, align 4, !tbaa !73
  %mul109 = fmul contract float %34, %35
  %36 = bitcast float %34 to i32
  br label %if.end110

if.end110:                                        ; preds = %if.then98, %if.end95
  %w_lane.0 = phi i32 [ %36, %if.then98 ], [ 0, %if.end95 ]
  %l_sum.0 = phi float [ %mul109, %if.then98 ], [ 0.000000e+00, %if.end95 ]
  %37 = bitcast float %l_sum.0 to i32
  %38 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %37, i32 296, i32 15, i32 15, i1 false)
  %39 = bitcast i32 %38 to float
  %add.i = fadd contract float %l_sum.0, %39
  %40 = bitcast float %add.i to i32
  %41 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %40, i32 292, i32 15, i32 15, i1 false)
  %42 = bitcast i32 %41 to float
  %add2.i = fadd contract float %add.i, %42
  %43 = bitcast float %add2.i to i32
  %44 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %43, i32 78, i32 15, i32 15, i1 false)
  %45 = bitcast i32 %44 to float
  %add4.i = fadd contract float %add2.i, %45
  %46 = bitcast float %add4.i to i32
  %47 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %46, i32 177, i32 15, i32 15, i1 false)
  %48 = bitcast i32 %47 to float
  %add6.i = fadd contract float %add4.i, %48
  %invariant.gep = getelementptr float, ptr addrspace(1) %partial_acc.coerce, i64 %idx.ext17
  %49 = shl nuw nsw i32 %add, 7
  %smax = tail call i32 @llvm.smax.i32(i32 %cond, i32 1)
  %wide.trip.count = zext nneg i32 %smax to i64
  br label %for.body

for.cond.cleanup:                                 ; preds = %_Z14__shfl_sync_16mfi.exit
  %cmp159 = fcmp contract ogt float %add6.i, 0.000000e+00
  %div161 = fdiv contract float 1.000000e+00, %add6.i
  %cond164 = select contract i1 %cmp159, float %div161, float 0.000000e+00
  %acc.sroa.0.0.vec.extract410 = extractelement <2 x float> %84, i64 0
  %mul168 = fmul contract float %cond164, %acc.sroa.0.0.vec.extract410
  %acc.sroa.0.4.vec.extract412 = extractelement <2 x float> %84, i64 1
  %mul170 = fmul contract float %cond164, %acc.sroa.0.4.vec.extract412
  %cmp.i.i.i341 = fcmp contract uno float %mul168, 0.000000e+00
  %50 = select i1 %cmp.i.i.i341, float 0x7FFFE00000000000, float %mul168
  %51 = bitcast float %50 to i32
  %shr.i.i.i.i.i342 = lshr i32 %51, 16
  %and.i.i.i.i.i343 = and i32 %shr.i.i.i.i.i342, 1
  %add.i.i.i.i.i344 = add i32 %51, 32767
  %add1.i.i.i.i.i345 = add i32 %add.i.i.i.i.i344, %and.i.i.i.i.i343
  %shr2.i.i.i.i.i346 = lshr i32 %add1.i.i.i.i.i345, 16
  %conv.i.i.i.i.i347 = trunc nuw i32 %shr2.i.i.i.i.i346 to i16
  %cmp.i1.i.i348 = fcmp contract uno float %mul170, 0.000000e+00
  %52 = select i1 %cmp.i1.i.i348, float 0x7FFFE00000000000, float %mul170
  %53 = bitcast float %52 to i32
  %shr.i.i.i2.i.i349 = lshr i32 %53, 16
  %and.i.i.i3.i.i350 = and i32 %shr.i.i.i2.i.i349, 1
  %add.i.i.i4.i.i351 = add i32 %53, 32767
  %add1.i.i.i5.i.i352 = add i32 %add.i.i.i4.i.i351, %and.i.i.i3.i.i350
  %shr2.i.i.i6.i.i353 = lshr i32 %add1.i.i.i5.i.i352, 16
  %conv.i.i.i7.i.i354 = trunc nuw i32 %shr2.i.i.i6.i.i353 to i16
  store i16 %conv.i.i.i.i.i347, ptr addrspace(1) %add.ptr18, align 4, !tbaa !27
  %y3.i357 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 2
  store i16 %conv.i.i.i7.i.i354, ptr addrspace(1) %y3.i357, align 2, !tbaa !27
  %acc.sroa.8.8.vec.extract414 = extractelement <2 x float> %85, i64 0
  %mul175 = fmul contract float %cond164, %acc.sroa.8.8.vec.extract414
  %acc.sroa.8.12.vec.extract416 = extractelement <2 x float> %85, i64 1
  %mul177 = fmul contract float %cond164, %acc.sroa.8.12.vec.extract416
  %cmp.i.i.i358 = fcmp contract uno float %mul175, 0.000000e+00
  %54 = select i1 %cmp.i.i.i358, float 0x7FFFE00000000000, float %mul175
  %55 = bitcast float %54 to i32
  %shr.i.i.i.i.i359 = lshr i32 %55, 16
  %and.i.i.i.i.i360 = and i32 %shr.i.i.i.i.i359, 1
  %add.i.i.i.i.i361 = add i32 %55, 32767
  %add1.i.i.i.i.i362 = add i32 %add.i.i.i.i.i361, %and.i.i.i.i.i360
  %shr2.i.i.i.i.i363 = lshr i32 %add1.i.i.i.i.i362, 16
  %conv.i.i.i.i.i364 = trunc nuw i32 %shr2.i.i.i.i.i363 to i16
  %cmp.i1.i.i365 = fcmp contract uno float %mul177, 0.000000e+00
  %56 = select i1 %cmp.i1.i.i365, float 0x7FFFE00000000000, float %mul177
  %57 = bitcast float %56 to i32
  %shr.i.i.i2.i.i366 = lshr i32 %57, 16
  %and.i.i.i3.i.i367 = and i32 %shr.i.i.i2.i.i366, 1
  %add.i.i.i4.i.i368 = add i32 %57, 32767
  %add1.i.i.i5.i.i369 = add i32 %add.i.i.i4.i.i368, %and.i.i.i3.i.i367
  %shr2.i.i.i6.i.i370 = lshr i32 %add1.i.i.i5.i.i369, 16
  %conv.i.i.i7.i.i371 = trunc nuw i32 %shr2.i.i.i6.i.i370 to i16
  %arrayidx178 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 4
  store i16 %conv.i.i.i.i.i364, ptr addrspace(1) %arrayidx178, align 4, !tbaa !27
  %y3.i374 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 6
  store i16 %conv.i.i.i7.i.i371, ptr addrspace(1) %y3.i374, align 2, !tbaa !27
  %acc.sroa.13.16.vec.extract418 = extractelement <2 x float> %86, i64 0
  %mul182 = fmul contract float %cond164, %acc.sroa.13.16.vec.extract418
  %acc.sroa.13.20.vec.extract420 = extractelement <2 x float> %86, i64 1
  %mul184 = fmul contract float %cond164, %acc.sroa.13.20.vec.extract420
  %cmp.i.i.i375 = fcmp contract uno float %mul182, 0.000000e+00
  %58 = select i1 %cmp.i.i.i375, float 0x7FFFE00000000000, float %mul182
  %59 = bitcast float %58 to i32
  %shr.i.i.i.i.i376 = lshr i32 %59, 16
  %and.i.i.i.i.i377 = and i32 %shr.i.i.i.i.i376, 1
  %add.i.i.i.i.i378 = add i32 %59, 32767
  %add1.i.i.i.i.i379 = add i32 %add.i.i.i.i.i378, %and.i.i.i.i.i377
  %shr2.i.i.i.i.i380 = lshr i32 %add1.i.i.i.i.i379, 16
  %conv.i.i.i.i.i381 = trunc nuw i32 %shr2.i.i.i.i.i380 to i16
  %cmp.i1.i.i382 = fcmp contract uno float %mul184, 0.000000e+00
  %60 = select i1 %cmp.i1.i.i382, float 0x7FFFE00000000000, float %mul184
  %61 = bitcast float %60 to i32
  %shr.i.i.i2.i.i383 = lshr i32 %61, 16
  %and.i.i.i3.i.i384 = and i32 %shr.i.i.i2.i.i383, 1
  %add.i.i.i4.i.i385 = add i32 %61, 32767
  %add1.i.i.i5.i.i386 = add i32 %add.i.i.i4.i.i385, %and.i.i.i3.i.i384
  %shr2.i.i.i6.i.i387 = lshr i32 %add1.i.i.i5.i.i386, 16
  %conv.i.i.i7.i.i388 = trunc nuw i32 %shr2.i.i.i6.i.i387 to i16
  %arrayidx185 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 8
  store i16 %conv.i.i.i.i.i381, ptr addrspace(1) %arrayidx185, align 4, !tbaa !27
  %y3.i391 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 10
  store i16 %conv.i.i.i7.i.i388, ptr addrspace(1) %y3.i391, align 2, !tbaa !27
  %acc.sroa.18.24.vec.extract422 = extractelement <2 x float> %87, i64 0
  %mul189 = fmul contract float %cond164, %acc.sroa.18.24.vec.extract422
  %acc.sroa.18.28.vec.extract424 = extractelement <2 x float> %87, i64 1
  %mul191 = fmul contract float %cond164, %acc.sroa.18.28.vec.extract424
  br label %cleanup

for.body:                                         ; preds = %if.end110, %_Z14__shfl_sync_16mfi.exit
  %indvars.iv = phi i64 [ 0, %if.end110 ], [ %indvars.iv.next, %_Z14__shfl_sync_16mfi.exit ]
  %acc.sroa.18.0435 = phi <2 x float> [ zeroinitializer, %if.end110 ], [ %87, %_Z14__shfl_sync_16mfi.exit ]
  %acc.sroa.13.0434 = phi <2 x float> [ zeroinitializer, %if.end110 ], [ %86, %_Z14__shfl_sync_16mfi.exit ]
  %acc.sroa.8.0433 = phi <2 x float> [ zeroinitializer, %if.end110 ], [ %85, %_Z14__shfl_sync_16mfi.exit ]
  %acc.sroa.0.0432 = phi <2 x float> [ zeroinitializer, %if.end110 ], [ %84, %_Z14__shfl_sync_16mfi.exit ]
  %62 = trunc i64 %indvars.iv to i32
  %63 = mul i32 %62, %batch_size
  %64 = add i32 %63, %shr
  %65 = shl i32 %64, 12
  %mul119 = add i32 %65, %49
  %idx.ext120 = sext i32 %mul119 to i64
  %gep = getelementptr float, ptr addrspace(1) %invariant.gep, i64 %idx.ext120
  %a0125.sroa.0.0.copyload = load float, ptr addrspace(1) %gep, align 16, !tbaa !73
  %a0125.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 4
  %a0125.sroa.4.0.copyload = load float, ptr addrspace(1) %a0125.sroa.4.0..sroa_idx, align 4, !tbaa !73
  %a0125.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 8
  %a0125.sroa.5.0.copyload = load float, ptr addrspace(1) %a0125.sroa.5.0..sroa_idx, align 8, !tbaa !73
  %a0125.sroa.6.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 12
  %a0125.sroa.6.0.copyload = load float, ptr addrspace(1) %a0125.sroa.6.0..sroa_idx, align 4, !tbaa !73
  %add.ptr127 = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 16
  %a1126.sroa.0.0.copyload = load float, ptr addrspace(1) %add.ptr127, align 16, !tbaa !73
  %a1126.sroa.4.0.add.ptr127.sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 20
  %a1126.sroa.4.0.copyload = load float, ptr addrspace(1) %a1126.sroa.4.0.add.ptr127.sroa_idx, align 4, !tbaa !73
  %a1126.sroa.5.0.add.ptr127.sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 24
  %a1126.sroa.5.0.copyload = load float, ptr addrspace(1) %a1126.sroa.5.0.add.ptr127.sroa_idx, align 8, !tbaa !73
  %a1126.sroa.6.0.add.ptr127.sroa_idx = getelementptr inbounds i8, ptr addrspace(1) %gep, i64 28
  %a1126.sroa.6.0.copyload = load float, ptr addrspace(1) %a1126.sroa.6.0.add.ptr127.sroa_idx, align 4, !tbaa !73
  %66 = trunc nsw i64 %indvars.iv to i32
  %rem.i.i = and i32 %66, 15
  switch i32 %rem.i.i, label %default.unreachable [
    i32 0, label %if.then.i.i
    i32 1, label %if.then3.i.i
    i32 2, label %if.then7.i.i
    i32 3, label %if.then11.i.i
    i32 4, label %if.then15.i.i
    i32 5, label %if.then19.i.i
    i32 6, label %if.then23.i.i
    i32 7, label %if.then27.i.i
    i32 8, label %if.then31.i.i
    i32 9, label %if.then35.i.i
    i32 10, label %if.then39.i.i
    i32 11, label %if.then43.i.i
    i32 12, label %if.then47.i.i
    i32 13, label %if.then51.i.i
    i32 14, label %if.then55.i.i
    i32 15, label %if.else56.i.i
  ]

if.then.i.i:                                      ; preds = %for.body
  %67 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 336, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then3.i.i:                                     ; preds = %for.body
  %68 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 337, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then7.i.i:                                     ; preds = %for.body
  %69 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 338, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then11.i.i:                                    ; preds = %for.body
  %70 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 339, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then15.i.i:                                    ; preds = %for.body
  %71 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 340, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then19.i.i:                                    ; preds = %for.body
  %72 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 341, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then23.i.i:                                    ; preds = %for.body
  %73 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 342, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then27.i.i:                                    ; preds = %for.body
  %74 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 343, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then31.i.i:                                    ; preds = %for.body
  %75 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 344, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then35.i.i:                                    ; preds = %for.body
  %76 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 345, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then39.i.i:                                    ; preds = %for.body
  %77 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 346, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then43.i.i:                                    ; preds = %for.body
  %78 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 347, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then47.i.i:                                    ; preds = %for.body
  %79 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 348, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then51.i.i:                                    ; preds = %for.body
  %80 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 349, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

if.then55.i.i:                                    ; preds = %for.body
  %81 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 350, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

default.unreachable:                              ; preds = %for.body
  unreachable

if.else56.i.i:                                    ; preds = %for.body
  %82 = tail call i32 @llvm.mxc.mov.shfl.i32(i32 %w_lane.0, i32 351, i32 15, i32 15, i1 false)
  br label %_Z14__shfl_sync_16mfi.exit

_Z14__shfl_sync_16mfi.exit:                       ; preds = %if.then.i.i, %if.then3.i.i, %if.then7.i.i, %if.then11.i.i, %if.then15.i.i, %if.then19.i.i, %if.then23.i.i, %if.then27.i.i, %if.then31.i.i, %if.then35.i.i, %if.then39.i.i, %if.then43.i.i, %if.then47.i.i, %if.then51.i.i, %if.then55.i.i, %if.else56.i.i
  %retval.0.i.i = phi i32 [ %67, %if.then.i.i ], [ %68, %if.then3.i.i ], [ %69, %if.then7.i.i ], [ %70, %if.then11.i.i ], [ %71, %if.then15.i.i ], [ %72, %if.then19.i.i ], [ %73, %if.then23.i.i ], [ %74, %if.then27.i.i ], [ %75, %if.then31.i.i ], [ %76, %if.then35.i.i ], [ %77, %if.then39.i.i ], [ %78, %if.then43.i.i ], [ %79, %if.then47.i.i ], [ %80, %if.then51.i.i ], [ %81, %if.then55.i.i ], [ %82, %if.else56.i.i ]
  %vecinit.i282 = insertelement <2 x float> poison, float %a0125.sroa.0.0.copyload, i64 0
  %vecinit2.i284 = insertelement <2 x float> %vecinit.i282, float %a0125.sroa.4.0.copyload, i64 1
  %83 = insertelement <2 x i32> poison, i32 %retval.0.i.i, i64 0
  %vecinit3.i285 = bitcast <2 x i32> %83 to <2 x float>
  %vecinit4.i286 = shufflevector <2 x float> %vecinit3.i285, <2 x float> poison, <2 x i32> zeroinitializer
  %84 = tail call contract <2 x float> @llvm.mxc.pk.fma.f32(<2 x float> %vecinit2.i284, <2 x float> %vecinit4.i286, <2 x float> %acc.sroa.0.0432)
  %vecinit.i274 = insertelement <2 x float> poison, float %a0125.sroa.5.0.copyload, i64 0
  %vecinit2.i276 = insertelement <2 x float> %vecinit.i274, float %a0125.sroa.6.0.copyload, i64 1
  %85 = tail call contract <2 x float> @llvm.mxc.pk.fma.f32(<2 x float> %vecinit2.i276, <2 x float> %vecinit4.i286, <2 x float> %acc.sroa.8.0433)
  %vecinit.i266 = insertelement <2 x float> poison, float %a1126.sroa.0.0.copyload, i64 0
  %vecinit2.i268 = insertelement <2 x float> %vecinit.i266, float %a1126.sroa.4.0.copyload, i64 1
  %86 = tail call contract <2 x float> @llvm.mxc.pk.fma.f32(<2 x float> %vecinit2.i268, <2 x float> %vecinit4.i286, <2 x float> %acc.sroa.13.0434)
  %vecinit.i = insertelement <2 x float> poison, float %a1126.sroa.5.0.copyload, i64 0
  %vecinit2.i = insertelement <2 x float> %vecinit.i, float %a1126.sroa.6.0.copyload, i64 1
  %87 = tail call contract <2 x float> @llvm.mxc.pk.fma.f32(<2 x float> %vecinit2.i, <2 x float> %vecinit4.i286, <2 x float> %acc.sroa.18.0435)
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond.not, label %for.cond.cleanup, label %for.body, !llvm.loop !268

cleanup:                                          ; preds = %for.cond.cleanup, %if.end
  %mul189.sink454 = phi float [ %mul189, %for.cond.cleanup ], [ %value.sroa.15.0, %if.end ]
  %mul191.sink451 = phi float [ %mul191, %for.cond.cleanup ], [ %value.sroa.17.0, %if.end ]
  %cmp.i.i.i392 = fcmp contract uno float %mul189.sink454, 0.000000e+00
  %88 = select i1 %cmp.i.i.i392, float 0x7FFFE00000000000, float %mul189.sink454
  %89 = bitcast float %88 to i32
  %shr.i.i.i.i.i393 = lshr i32 %89, 16
  %and.i.i.i.i.i394 = and i32 %shr.i.i.i.i.i393, 1
  %add.i.i.i.i.i395 = add i32 %89, 32767
  %add1.i.i.i.i.i396 = add i32 %add.i.i.i.i.i395, %and.i.i.i.i.i394
  %shr2.i.i.i.i.i397 = lshr i32 %add1.i.i.i.i.i396, 16
  %conv.i.i.i.i.i398 = trunc nuw i32 %shr2.i.i.i.i.i397 to i16
  %cmp.i1.i.i399 = fcmp contract uno float %mul191.sink451, 0.000000e+00
  %90 = select i1 %cmp.i1.i.i399, float 0x7FFFE00000000000, float %mul191.sink451
  %91 = bitcast float %90 to i32
  %shr.i.i.i2.i.i400 = lshr i32 %91, 16
  %and.i.i.i3.i.i401 = and i32 %shr.i.i.i2.i.i400, 1
  %add.i.i.i4.i.i402 = add i32 %91, 32767
  %add1.i.i.i5.i.i403 = add i32 %add.i.i.i4.i.i402, %and.i.i.i3.i.i401
  %shr2.i.i.i6.i.i404 = lshr i32 %add1.i.i.i5.i.i403, 16
  %conv.i.i.i7.i.i405 = trunc nuw i32 %shr2.i.i.i6.i.i404 to i16
  %arrayidx192 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 12
  store i16 %conv.i.i.i.i.i398, ptr addrspace(1) %arrayidx192, align 4, !tbaa !27
  %y3.i408 = getelementptr inbounds i8, ptr addrspace(1) %add.ptr18, i64 14
  store i16 %conv.i.i.i7.i.i405, ptr addrspace(1) %y3.i408, align 2, !tbaa !27
  ret void
}

; Function Attrs: convergent mustprogress nofree norecurse nounwind memory(argmem: readwrite)
